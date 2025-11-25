"""
Enhanced PDF Processor with OCR Capabilities

This module provides advanced PDF processing capabilities including:
- Text extraction using multiple engines
- OCR for scanned documents and images
- Code block detection and extraction
- Table extraction and analysis
- Metadata extraction
- Security validation
"""

import asyncio
import logging
import os
import re
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum

# PDF processing libraries
try:
    import pdfplumber

    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logging.warning("pdfplumber not available - PDF text extraction will be limited")

try:
    import PyPDF2

    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logging.warning("PyPDF2 not available - falling back to pdfplumber")

try:
    import pytesseract
    from PIL import Image
    import pdf2image

    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False
    logging.warning("OCR dependencies not available - scanned PDFs cannot be processed")

# Advanced processing
try:
    import cv2
    import numpy as np

    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False
    logging.warning("OpenCV not available - advanced image processing disabled")


class ProcessingMode(Enum):
    """PDF processing modes."""

    TEXT_ONLY = "text_only"  # Extract text only (fastest)
    OCR_ENABLED = "ocr_enabled"  # Include OCR for scanned pages
    ADVANCED = "advanced"  # Full processing with tables, images, etc.
    CODE_FOCUSED = "code_focused"  # Optimize for code extraction


@dataclass
class PDFPage:
    """Represents a single page from a PDF document."""

    page_number: int
    text_content: str
    images: List[Dict[str, Any]] = None
    tables: List[Dict[str, Any]] = None
    code_blocks: List[Dict[str, str]] = None
    metadata: Dict[str, Any] = None
    ocr_text: Optional[str] = None
    processing_mode: str = ProcessingMode.TEXT_ONLY.value

    def __post_init__(self):
        if self.images is None:
            self.images = []
        if self.tables is None:
            self.tables = []
        if self.code_blocks is None:
            self.code_blocks = []
        if self.metadata is None:
            self.metadata = {}

    def get_full_text(self) -> str:
        """Get combined text from all sources."""
        full_text = self.text_content or ""

        if self.ocr_text:
            full_text += f"\n\n[OCR Text]\n{self.ocr_text}"

        return full_text.strip()


@dataclass
class PDFAnalysisResult:
    """Result of PDF analysis and processing."""

    file_path: str
    total_pages: int
    processed_pages: List[PDFPage]
    metadata: Dict[str, Any]
    code_samples: List[Dict[str, str]]
    processing_time: float
    quality_score: float
    security_issues: List[str] = None
    warnings: List[str] = None

    def __post_init__(self):
        if self.security_issues is None:
            self.security_issues = []
        if self.warnings is None:
            self.warnings = []

    def get_all_text(self) -> str:
        """Get all text content from the PDF."""
        return "\n\n".join(page.get_full_text() for page in self.processed_pages)

    def get_code_samples(self) -> List[Dict[str, str]]:
        """Get all code samples extracted from the PDF."""
        all_code = []

        for page in self.processed_pages:
            for code_block in page.code_blocks:
                all_code.append(
                    {
                        "code": code_block["code"],
                        "language": code_block.get("language", "unknown"),
                        "page": page.page_number,
                        "context": code_block.get("context", ""),
                    }
                )

        return all_code


class PDFProcessor:
    """
    Advanced PDF processor with OCR and code extraction capabilities.

    Features:
    - Multi-engine text extraction (pdfplumber, PyPDF2)
    - OCR support for scanned documents (Tesseract)
    - Code block detection and extraction
    - Table extraction and analysis
    - Image processing and enhancement
    - Security validation
    - Quality assessment
    """

    def __init__(self, processing_mode: ProcessingMode = ProcessingMode.ADVANCED):
        self.processing_mode = processing_mode
        self.temp_dir = None

        # Initialize processing capabilities
        self.text_extractors = []
        self._initialize_extractors()

        # Code detection patterns
        self.code_patterns = {
            "python": [r"def\s+\w+\s*\([^)]*\)\s*:", r"class\s+\w+\s*\:", r"import\s+\w+", r"from\s+\w+\s+import"],
            "javascript": [r"function\s+\w+\s*\([^)]*\)\s*{", r"const\s+\w+\s*=", r"let\s+\w+\s*=", r"class\s+\w+\s*{"],
            "java": [r"public\s+class\s+\w+", r"public\s+\w+\s+\w+\s*\([^)]*\)\s*{", r"import\s+\w+"],
            "cpp": [r"#include\s*<[^>]+>", r"int\s+main\s*\(", r"class\s+\w+\s*{"],
            "sql": [r"SELECT\s+.+\s+FROM", r"INSERT\s+INTO", r"UPDATE\s+.+\s+SET", r"CREATE\s+TABLE"],
        }

        # Security patterns
        self.security_patterns = [
            r"password\s*[:=]\s*[\"'][^\"']+[\"']",
            r"api[_-]?key\s*[:=]\s*[\"'][^\"']+[\"']",
            r"secret\s*[:=]\s*[\"'][^\"']+[\"']",
            r"token\s*[:=]\s*[\"'][^\"']+[\"']",
        ]

    def _initialize_extractors(self):
        """Initialize available text extractors."""
        if PDFPLUMBER_AVAILABLE:
            self.text_extractors.append("pdfplumber")

        if PYPDF2_AVAILABLE:
            self.text_extractors.append("pypdf2")

        if not self.text_extractors:
            logging.error("No PDF text extractors available")

    async def process_pdf(
        self, pdf_path: Union[str, Path], output_dir: Optional[Union[str, Path]] = None
    ) -> PDFAnalysisResult:
        """
        Process a PDF file with full analysis.

        Args:
            pdf_path: Path to the PDF file
            output_dir: Optional output directory for intermediate files

        Returns:
            PDFAnalysisResult: Complete analysis result
        """
        import time

        start_time = time.time()

        pdf_path = Path(pdf_path)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

        # Validate file size
        file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
        if file_size_mb > 100:  # 100MB limit
            raise ValueError(f"PDF file too large: {file_size_mb:.1f}MB")

        logging.info(f"Processing PDF: {pdf_path} ({file_size_mb:.1f}MB)")

        try:
            # Create temporary directory if needed
            self.temp_dir = Path(tempfile.mkdtemp(prefix="pdf_processing_"))
            if output_dir:
                Path(output_dir).mkdir(parents=True, exist_ok=True)

            # Extract basic metadata
            metadata = await self._extract_metadata(pdf_path)

            # Process pages
            processed_pages = await self._process_pages(pdf_path)

            # Extract code samples
            code_samples = await self._extract_code_samples(processed_pages)

            # Security validation
            security_issues = await self._validate_security(processed_pages, code_samples)

            # Quality assessment
            quality_score = await self._assess_quality(processed_pages, code_samples)

            processing_time = time.time() - start_time

            result = PDFAnalysisResult(
                file_path=str(pdf_path),
                total_pages=len(processed_pages),
                processed_pages=processed_pages,
                metadata=metadata,
                code_samples=code_samples,
                processing_time=processing_time,
                quality_score=quality_score,
                security_issues=security_issues,
            )

            logging.info(f"PDF processing completed in {processing_time:.2f}s")
            return result

        except Exception as e:
            logging.error(f"PDF processing failed: {e}")
            raise
        finally:
            await self._cleanup()

    async def _extract_metadata(self, pdf_path: Path) -> Dict[str, Any]:
        """Extract metadata from PDF file."""
        metadata = {"file_name": pdf_path.name, "file_size": pdf_path.stat().st_size}

        try:
            if PYPDF2_AVAILABLE:
                with open(pdf_path, "rb") as file:
                    pdf_reader = PyPDF2.PdfReader(file)
                    metadata.update(
                        {
                            "page_count": len(pdf_reader.pages),
                            "title": pdf_reader.metadata.get("/Title", "") if pdf_reader.metadata else "",
                            "author": pdf_reader.metadata.get("/Author", "") if pdf_reader.metadata else "",
                            "creator": pdf_reader.metadata.get("/Creator", "") if pdf_reader.metadata else "",
                            "producer": pdf_reader.metadata.get("/Producer", "") if pdf_reader.metadata else "",
                        }
                    )

        except Exception as e:
            logging.warning(f"Failed to extract PDF metadata: {e}")

        return metadata

    async def _process_pages(self, pdf_path: Path) -> List[PDFPage]:
        """Process all pages in the PDF."""
        processed_pages = []

        try:
            if PDFPLUMBER_AVAILABLE:
                processed_pages = await self._process_with_pdfplumber(pdf_path)
            elif PYPDF2_AVAILABLE:
                processed_pages = await self._process_with_pypdf2(pdf_path)
            else:
                raise RuntimeError("No PDF processing library available")

            # Apply OCR if enabled and available
            if self.processing_mode in [ProcessingMode.OCR_ENABLED, ProcessingMode.ADVANCED] and TESSERACT_AVAILABLE:
                processed_pages = await self._apply_ocr(pdf_path, processed_pages)

        except Exception as e:
            logging.error(f"Failed to process PDF pages: {e}")
            raise

        return processed_pages

    async def _process_with_pdfplumber(self, pdf_path: Path) -> List[PDFPage]:
        """Process PDF using pdfplumber."""
        pages = []

        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    text = page.extract_text() or ""

                    # Extract tables
                    tables = []
                    for table in page.extract_tables():
                        tables.append({"data": table, "rows": len(table), "cols": len(table[0]) if table else 0})

                    # Extract images (basic detection)
                    images = []
                    if hasattr(page, "images"):
                        for img in page.images:
                            images.append(
                                {
                                    "x0": img.get("x0", 0),
                                    "y0": img.get("y0", 0),
                                    "x1": img.get("x1", 0),
                                    "y1": img.get("y1", 0),
                                    "width": img.get("width", 0),
                                    "height": img.get("height", 0),
                                }
                            )

                    pdf_page = PDFPage(
                        page_number=page_num,
                        text_content=text,
                        tables=tables,
                        images=images,
                        processing_mode=self.processing_mode.value,
                    )

                    pages.append(pdf_page)

        except Exception as e:
            logging.error(f"pdfplumber processing failed: {e}")
            raise

        return pages

    async def _process_with_pypdf2(self, pdf_path: Path) -> List[PDFPage]:
        """Process PDF using PyPDF2 (fallback)."""
        pages = []

        try:
            with open(pdf_path, "rb") as file:
                pdf_reader = PyPDF2.PdfReader(file)

                for page_num, page in enumerate(pdf_reader.pages, 1):
                    text = page.extract_text() or ""

                    pdf_page = PDFPage(
                        page_number=page_num, text_content=text, processing_mode=self.processing_mode.value
                    )

                    pages.append(pdf_page)

        except Exception as e:
            logging.error(f"PyPDF2 processing failed: {e}")
            raise

        return pages

    async def _apply_ocr(self, pdf_path: Path, pages: List[PDFPage]) -> List[PDFPage]:
        """Apply OCR to pages with little or no text."""
        if not TESSERACT_AVAILABLE:
            return pages

        try:
            # Convert PDF to images
            images = pdf2image.convert_from_path(str(pdf_path), dpi=300, output_folder=self.temp_dir, fmt="jpeg")

            for i, (image, page) in enumerate(zip(images, pages)):
                # Check if OCR is needed (low text content)
                if len(page.text_content.strip()) < 100:
                    try:
                        # Preprocess image for better OCR
                        if OPENCV_AVAILABLE:
                            processed_image = self._preprocess_image(image)
                            ocr_text = pytesseract.image_to_string(processed_image)
                        else:
                            ocr_text = pytesseract.image_to_string(image)

                        page.ocr_text = ocr_text.strip()

                    except Exception as e:
                        logging.warning(f"OCR failed for page {page.page_number}: {e}")

        except Exception as e:
            logging.warning(f"OCR processing failed: {e}")

        return pages

    def _preprocess_image(self, image) -> Any:
        """Preprocess image for better OCR results."""
        if not OPENCV_AVAILABLE:
            return image

        try:
            # Convert PIL to OpenCV format
            img_array = np.array(image)

            # Convert to grayscale
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array

            # Apply threshold to get better OCR
            _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Denoise
            denoised = cv2.medianBlur(thresh, 5)

            return denoised

        except Exception as e:
            logging.warning(f"Image preprocessing failed: {e}")
            return image

    async def _extract_code_samples(self, pages: List[PDFPage]) -> List[Dict[str, str]]:
        """Extract code samples from processed pages."""
        all_code_samples = []

        for page in pages:
            page_text = page.get_full_text()

            # Detect code blocks using multiple strategies
            code_blocks = []

            # Strategy 1: Look for code-like patterns
            for language, patterns in self.code_patterns.items():
                for pattern in patterns:
                    matches = re.finditer(pattern, page_text, re.MULTILINE | re.IGNORECASE)
                    for match in matches:
                        # Extract context around the match
                        start = max(0, match.start() - 200)
                        end = min(len(page_text), match.end() + 500)
                        context = page_text[start:end].strip()

                        # Try to extract a complete code block
                        code_block = self._extract_code_block(context, match.start() - start)
                        if code_block:
                            code_blocks.append(
                                {"code": code_block, "language": language, "context": context, "confidence": 0.7}
                            )

            # Strategy 2: Look for indented blocks (common in documentation)
            lines = page_text.split("\n")
            for i, line in enumerate(lines):
                if line.startswith("    ") or line.startswith("\t"):
                    # Start of indented block
                    block_lines = [line]
                    j = i + 1

                    # Collect subsequent indented lines
                    while j < len(lines) and (
                        lines[j].startswith("    ") or lines[j].startswith("\t") or lines[j].strip() == ""
                    ):
                        block_lines.append(lines[j])
                        j += 1

                    if len(block_lines) > 2:  # Minimum block size
                        code_block = "\n".join(block_lines)
                        language = self._detect_language_from_code(code_block)

                        code_blocks.append(
                            {
                                "code": code_block,
                                "language": language,
                                "context": f"Lines {i + 1}-{j}",
                                "confidence": 0.6,
                            }
                        )

            # Strategy 3: Look for backtick code blocks
            backtick_blocks = re.findall(r"```(\w+)?\n(.*?)\n```", page_text, re.DOTALL)
            for language, code in backtick_blocks:
                if language:
                    code_blocks.append(
                        {
                            "code": code.strip(),
                            "language": language.lower(),
                            "context": "Backtick code block",
                            "confidence": 0.9,
                        }
                    )

            # Remove duplicates and add to page
            unique_blocks = []
            seen_code = set()

            for block in code_blocks:
                code_hash = hash(block["code"])
                if code_hash not in seen_code:
                    seen_code.add(code_hash)
                    unique_blocks.append(block)

            page.code_blocks = unique_blocks
            all_code_samples.extend(unique_blocks)

        return all_code_samples

    def _extract_code_block(self, context: str, match_pos: int) -> Optional[str]:
        """Extract a complete code block from context."""
        lines = context.split("\n")
        code_lines = []
        in_code_block = False

        for line in lines:
            stripped = line.strip()

            # Simple heuristics for code detection
            if any(char in line for char in ["{", "}", "(", ")", ";", ":", "=", "[", "]"]):
                in_code_block = True

            if in_code_block:
                code_lines.append(line)

                # End of code block (heuristic)
                if stripped.endswith(("{", ";", ")", ":")) or (
                    stripped and not any(char in line for char in ["{", "}", "(", ")", ";", "=", "[", "]"])
                ):
                    if len(code_lines) > 1:  # Ensure we have meaningful content
                        break

        return "\n".join(code_lines) if len(code_lines) > 1 else None

    def _detect_language_from_code(self, code: str) -> str:
        """Detect programming language from code sample."""
        language_scores = {}

        for language, patterns in self.code_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, code, re.IGNORECASE))
                score += matches
            language_scores[language] = score

        # Return language with highest score
        if language_scores:
            best_language = max(language_scores, key=language_scores.get)
            if language_scores[best_language] > 0:
                return best_language

        return "unknown"

    async def _validate_security(self, pages: List[PDFPage], code_samples: List[Dict[str, str]]) -> List[str]:
        """Validate security of extracted content."""
        security_issues = []

        # Check text content for security patterns
        all_text = "\n".join(page.get_full_text() for page in pages)

        for pattern in self.security_patterns:
            matches = re.findall(pattern, all_text, re.IGNORECASE)
            for match in matches:
                security_issues.append(f"Potential sensitive information detected: {match[:50]}...")

        # Check code samples for dangerous patterns
        dangerous_patterns = [r"eval\s*\(", r"exec\s*\(", r"system\s*\(", r"subprocess\.call", r"os\.system"]

        for sample in code_samples:
            code = sample.get("code", "")
            for pattern in dangerous_patterns:
                if re.search(pattern, code, re.IGNORECASE):
                    security_issues.append(
                        f"Potentially dangerous code pattern: {pattern} in {sample.get('language', 'unknown')} code"
                    )

        return security_issues

    async def _assess_quality(self, pages: List[PDFPage], code_samples: List[Dict[str, str]]) -> float:
        """Assess quality of PDF processing."""
        score = 0.0

        # Text extraction quality (0-40 points)
        total_pages = len(pages)
        pages_with_text = sum(1 for page in pages if len(page.get_full_text()) > 100)
        text_quality = (pages_with_text / total_pages) * 40 if total_pages > 0 else 0
        score += text_quality

        # Code extraction quality (0-30 points)
        if code_samples:
            high_confidence_samples = sum(1 for sample in code_samples if sample.get("confidence", 0) > 0.7)
            code_quality = (high_confidence_samples / len(code_samples)) * 30
            score += code_quality

        # Structure detection (0-20 points)
        pages_with_tables = sum(1 for page in pages if page.tables)
        pages_with_images = sum(1 for page in pages if page.images)
        structure_score = min(20, (pages_with_tables + pages_with_images) * 2)
        score += structure_score

        # OCR quality (0-10 points)
        pages_with_ocr = sum(1 for page in pages if page.ocr_text)
        ocr_score = min(10, pages_with_ocr * 2)
        score += ocr_score

        return min(100.0, score)

    async def _cleanup(self):
        """Clean up temporary files."""
        if self.temp_dir and self.temp_dir.exists():
            try:
                import shutil

                shutil.rmtree(self.temp_dir)
                logging.info("Cleaned up temporary files")
            except Exception as e:
                logging.warning(f"Failed to cleanup temporary files: {e}")


# Export main classes
__all__ = ["PDFProcessor", "PDFPage", "PDFAnalysisResult", "ProcessingMode"]
