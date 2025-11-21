"""
Content Analyzer Module

Safe file content analysis for intelligent categorization.
Provides text extraction, keyword analysis, and content-based features
while maintaining security best practices.
"""

import hashlib
import logging
import mimetypes
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Union
import asyncio
from datetime import datetime

import chardet

from ..models.file_models import FileInfo, CategoryType
from .models.learning_models import FeatureVector

logger = logging.getLogger(__name__)


class ContentAnalysisError(Exception):
    """Raised when content analysis fails due to security or technical issues."""

    pass


class ContentAnalyzer:
    """
    Safe file content analyzer for extracting features used in ML categorization.

    This module provides secure content analysis with the following security features:
    - File size limits to prevent resource exhaustion
    - Content type validation
    - Safe text extraction with encoding detection
    - Keyword and pattern matching without execution
    - Memory-efficient processing for large files
    """

    def __init__(
        self,
        max_file_size_mb: float = 50.0,
        max_content_length: int = 100000,
        safe_extensions: Optional[Set[str]] = None,
    ):
        """
        Initialize the content analyzer with security constraints.

        Args:
            max_file_size_mb: Maximum file size to analyze (MB)
            max_content_length: Maximum content length to process (characters)
            safe_extensions: Set of file extensions considered safe to analyze
        """
        self.max_file_size_bytes = int(max_file_size_mb * 1024 * 1024)
        self.max_content_length = max_content_length

        # Default safe extensions for content analysis
        self.safe_extensions = safe_extensions or {
            "txt",
            "md",
            "py",
            "js",
            "ts",
            "html",
            "css",
            "json",
            "xml",
            "csv",
            "log",
            "ini",
            "cfg",
            "yaml",
            "yml",
            "rtf",
            "doc",
            "docx",
            "pdf",
        }

        # Pre-compiled regex patterns for efficient matching
        self._compile_patterns()

    def _compile_patterns(self) -> None:
        """Pre-compile regex patterns for performance."""
        # Document patterns
        self.document_patterns = {
            "contract": re.compile(r"\b(contract|agreement|terms)\b", re.IGNORECASE),
            "invoice": re.compile(r"\b(invoice|bill|receipt)\b", re.IGNORECASE),
            "report": re.compile(r"\b(report|analysis|summary)\b", re.IGNORECASE),
            "documentation": re.compile(r"\b(documentation|manual|guide)\b", re.IGNORECASE),
        }

        # Code patterns
        self.code_patterns = {
            "function": re.compile(r"\b(def|function|func|class)\s+\w+", re.IGNORECASE),
            "import": re.compile(r"\b(import|include|require|using)\b", re.IGNORECASE),
            "variable": re.compile(r"\b(var|let|const)\s+\w+", re.IGNORECASE),
        }

        # Configuration patterns
        self.config_patterns = {
            "database": re.compile(r"\b(database|db_host|db_user)\b", re.IGNORECASE),
            "api_key": re.compile(r"\b(api_key|secret|token)\b", re.IGNORECASE),
            "server": re.compile(r"\b(server|host|port)\b", re.IGNORECASE),
        }

        # Date patterns
        self.date_patterns = [
            re.compile(r"\d{4}-\d{2}-\d{2}"),  # YYYY-MM-DD
            re.compile(r"\d{2}/\d{2}/\d{4}"),  # MM/DD/YYYY
            re.compile(r"\d{1,2}\s+\w+\s+\d{4}"),  # DD Month YYYY
        ]

    def can_analyze_file(self, file_info: FileInfo) -> bool:
        """
        Check if a file can be safely analyzed.

        Args:
            file_info: File information object

        Returns:
            True if file is safe to analyze, False otherwise
        """
        # Check file size
        if file_info.size > self.max_file_size_bytes:
            logger.debug(f"File too large for analysis: {file_info.path} ({file_info.size_mb}MB)")
            return False

        # Check file extension
        if file_info.extension:
            ext_lower = file_info.extension.lower()
            if ext_lower not in self.safe_extensions:
                logger.debug(f"File extension not safe for analysis: {ext_lower}")
                return False

        # Check if file exists and is readable
        if not file_info.path.exists() or not file_info.path.is_file():
            logger.debug(f"File not accessible: {file_info.path}")
            return False

        return True

    async def extract_text_content(self, file_path: Path) -> str:
        """
        Safely extract text content from a file.

        Args:
            file_path: Path to the file to analyze

        Returns:
            Extracted text content (truncated if too long)

        Raises:
            ContentAnalysisError: If extraction fails or is unsafe
        """
        try:
            # Security check: ensure file is within expected size limits
            file_size = file_path.stat().st_size
            if file_size > self.max_file_size_bytes:
                raise ContentAnalysisError(f"File too large: {file_size} bytes")

            # Detect encoding safely
            try:
                with open(file_path, "rb") as f:
                    raw_data = f.read(min(10240, file_size))  # Read first 10KB for detection

                if not raw_data:
                    return ""

                encoding_result = chardet.detect(raw_data)
                encoding = encoding_result.get("encoding", "utf-8")
                confidence = encoding_result.get("confidence", 0.0)

                # Use UTF-8 as fallback if detection is unreliable
                if not encoding or confidence < 0.7:
                    encoding = "utf-8"

            except Exception as e:
                logger.warning(f"Encoding detection failed for {file_path}: {e}")
                encoding = "utf-8"

            # Extract text content with size limit
            try:
                with open(file_path, "r", encoding=encoding, errors="ignore") as f:
                    content = f.read(self.max_content_length)

                # Additional safety: truncate if somehow longer than expected
                if len(content) > self.max_content_length:
                    content = content[: self.max_content_length]
                    logger.debug(f"Truncated content for {file_path}")

                return content

            except UnicodeDecodeError as e:
                logger.debug(f"Text extraction failed for {file_path}: {e}")
                return ""

        except Exception as e:
            if not isinstance(e, ContentAnalysisError):
                raise ContentAnalysisError(f"Text extraction failed: {e}")
            raise

    def extract_keywords(self, content: str) -> Dict[str, int]:
        """
        Extract keyword frequencies from text content.

        Args:
            content: Text content to analyze

        Returns:
            Dictionary of keyword frequencies
        """
        if not content or len(content) < 10:
            return {}

        # Common technical and business keywords
        keywords = {
            "invoice",
            "contract",
            "agreement",
            "report",
            "analysis",
            "summary",
            "documentation",
            "manual",
            "guide",
            "tutorial",
            "example",
            "sample",
            "database",
            "server",
            "client",
            "user",
            "admin",
            "config",
            "settings",
            "import",
            "export",
            "backup",
            "archive",
            "temp",
            "cache",
            "log",
            "project",
            "source",
            "code",
            "script",
            "function",
            "class",
            "method",
            "test",
            "demo",
            "development",
            "production",
            "staging",
            "deploy",
        }

        # Tokenize content safely (simple word boundary splitting)
        words = re.findall(r"\b\w+\b", content.lower())

        keyword_counts = {}
        for word in words:
            if word in keywords:
                keyword_counts[word] = keyword_counts.get(word, 0) + 1

        return keyword_counts

    def detect_content_patterns(self, content: str) -> Dict[str, float]:
        """
        Detect content patterns using regex matching.

        Args:
            content: Text content to analyze

        Returns:
            Dictionary of pattern matches with confidence scores
        """
        if not content:
            return {}

        pattern_scores = {}
        content_lower = content.lower()

        # Document patterns
        for pattern_name, pattern in self.document_patterns.items():
            matches = pattern.findall(content)
            if matches:
                pattern_scores[f"doc_{pattern_name}"] = min(len(matches) * 0.2, 1.0)

        # Code patterns
        for pattern_name, pattern in self.code_patterns.items():
            matches = pattern.findall(content)
            if matches:
                pattern_scores[f"code_{pattern_name}"] = min(len(matches) * 0.3, 1.0)

        # Configuration patterns
        for pattern_name, pattern in self.config_patterns.items():
            matches = pattern.findall(content)
            if matches:
                pattern_scores[f"config_{pattern_name}"] = min(len(matches) * 0.4, 1.0)

        # Date patterns (presence of dates suggests documents)
        date_count = sum(len(pattern.findall(content)) for pattern in self.date_patterns)
        if date_count > 0:
            pattern_scores["has_dates"] = min(date_count * 0.1, 1.0)

        # Language detection based on common words
        language_indicators = {
            "python": ["def ", "import ", "class ", "__init__", "self."],
            "javascript": ["function ", "const ", "let ", "var ", "=>"],
            "html": ["<html", "<div", "<body", "</html>", "href="],
            "css": ["{", "}", "margin:", "padding:", "color:"],
            "json": ['"{', '"id":', '"name":', '"type":', "}"],
            "yaml": ["-", "key:", "value:", "true:", "false:"],
        }

        for language, indicators in language_indicators.items():
            count = sum(content_lower.count(indicator) for indicator in indicators)
            if count > 0:
                pattern_scores[f"lang_{language}"] = min(count * 0.2, 1.0)

        return pattern_scores

    def calculate_content_features(self, file_info: FileInfo) -> Dict[str, float]:
        """
        Calculate content-based features for ML analysis.

        Args:
            file_info: File information object

        Returns:
            Dictionary of content features
        """
        features = {
            "is_readable": 0.0,
            "has_keywords": 0.0,
            "has_patterns": 0.0,
            "text_density": 0.0,
            "language_score": 0.0,
        }

        if not self.can_analyze_file(file_info):
            return features

        try:
            # Use asyncio to run potentially blocking I/O
            content = asyncio.run(self.extract_text_content(file_info.path))

            if content and len(content) > 0:
                features["is_readable"] = 1.0

                # Keyword analysis
                keywords = self.extract_keywords(content)
                if keywords:
                    features["has_keywords"] = min(len(keywords) * 0.1, 1.0)

                # Pattern analysis
                patterns = self.detect_content_patterns(content)
                if patterns:
                    features["has_patterns"] = min(len(patterns) * 0.2, 1.0)

                    # Language detection score
                    lang_scores = [v for k, v in patterns.items() if k.startswith("lang_")]
                    if lang_scores:
                        features["language_score"] = max(lang_scores)

                # Text density (content length vs file size)
                if file_info.size > 0:
                    features["text_density"] = min(len(content) / file_info.size, 1.0)

        except Exception as e:
            logger.debug(f"Content analysis failed for {file_info.path}: {e}")
            # Return default features (all 0.0)

        return features

    def create_feature_vector(self, file_info: FileInfo) -> FeatureVector:
        """
        Create a complete feature vector for ML analysis.

        Args:
            file_info: File information object

        Returns:
            FeatureVector with all calculated features
        """
        # Basic file features
        file_size_norm = min(file_info.size_mb / 100.0, 1.0)  # Normalize to 0-1 (100MB max)

        # Extension features (one-hot encoding)
        extension_features = {}
        if file_info.extension:
            ext_lower = file_info.extension.lower()
            # Common extensions as features
            common_exts = ["pdf", "doc", "txt", "jpg", "mp4", "py", "js", "zip", "exe"]
            for ext in common_exts:
                extension_features[f"ext_{ext}"] = 1.0 if ext_lower == ext else 0.0

        # Path depth
        path_depth = len(file_info.path.parts)

        # Content-based features
        content_features = self.calculate_content_features(file_info)

        # Name patterns
        name_patterns = {}
        name_lower = file_info.name.lower()

        # Common naming patterns
        pattern_indicators = {
            "temp_file": ["temp", "tmp", "~$", ".bak"],
            "backup_file": ["backup", "copy", "old"],
            "version_file": ["v1", "v2", "ver1", "version"],
            "date_pattern": ["2023", "2024", "2025"],
        }

        for pattern_name, indicators in pattern_indicators.items():
            count = sum(name_lower.count(indicator) for indicator in indicators)
            if count > 0:
                name_patterns[pattern_name] = min(count * 0.5, 1.0)

        return FeatureVector(
            file_size_norm=file_size_norm,
            extension_features=extension_features,
            path_depth=path_depth,
            text_length=len(file_info.name),  # Basic text length
            keyword_features={k: v * 0.1 for k, v in self.extract_keywords("").items()},
            language_score=content_features.get("language_score", 0.0),
            name_patterns=name_patterns,
            date_features={},
            user_category_history=0.0,  # Will be populated by learning engine
            correction_frequency=0.0,  # Will be populated by learning engine
        )

    def get_file_summary(self, file_info: FileInfo) -> Dict[str, Union[str, int, float]]:
        """
        Get a summary of file analysis results.

        Args:
            file_info: File information object

        Returns:
            Dictionary with analysis summary
        """
        summary = {
            "file_path": str(file_info.path),
            "can_analyze": self.can_analyze_file(file_info),
            "file_size_mb": file_info.size_mb,
            "extension": file_info.extension,
        }

        if self.can_analyze_file(file_info):
            try:
                content = asyncio.run(self.extract_text_content(file_info.path))
                if content:
                    keywords = self.extract_keywords(content)
                    patterns = self.detect_content_patterns(content)

                    summary.update(
                        {
                            "content_length": len(content),
                            "keyword_count": len(keywords),
                            "pattern_count": len(patterns),
                            "top_keywords": sorted(keywords.items(), key=lambda x: x[1], reverse=True)[:5],
                            "detected_patterns": list(patterns.keys()),
                        }
                    )
                else:
                    summary["content_length"] = 0
                    summary["keyword_count"] = 0
                    summary["pattern_count"] = 0
            except Exception as e:
                summary["analysis_error"] = str(e)
        else:
            summary["reason"] = "File not safe for analysis"

        return summary
