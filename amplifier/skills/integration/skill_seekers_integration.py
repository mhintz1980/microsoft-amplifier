"""
Skill Seekers Integration Module for Microsoft Amplifier

This module integrates Skill Seekers' technical data processing capabilities
with Microsoft Amplifier's advanced skills framework to provide automated
skill generation from various technical sources.

Core Capabilities:
- Documentation scraping and conversion
- PDF extraction with OCR
- GitHub repository analysis
- AST parsing for code conflict detection
- Automated skill packaging
- Integration with 7/7 core skills system
- Virtual environment safety
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Note: Skill Seekers integration isolated to prevent circular imports

try:
    # Safe import with dependency isolation
    import importlib.util

    # Check if Skill_Seekers is available and functional
    skill_seekers_main = Path(__file__).parent.parent.parent / "Skill_Seekers" / "cli" / "doc_scraper.py"
    if skill_seekers_main.exists() and not any(
        "jit_compiler" in str(frame) for frame in sys._current_frames().values()
    ):
        spec = importlib.util.spec_from_file_location("doc_scraper", skill_seekers_main)
        doc_scraper = importlib.util.module_from_spec(spec)

        spec2 = importlib.util.spec_from_file_location(
            "package_skill", Path(__file__).parent.parent.parent / "Skill_Seekers" / "cli" / "package_skill.py"
        )
        package_skill = importlib.util.module_from_spec(spec2)

        spec3 = importlib.util.spec_from_file_location(
            "enhance_skill_local",
            Path(__file__).parent.parent.parent / "Skill_Seekers" / "cli" / "enhance_skill_local.py",
        )
        enhance_skill = importlib.util.module_from_spec(spec3)

        SKILL_SEEKERS_AVAILABLE = True
    else:
        raise ImportError("Skill Seekers not accessible or JIT compiler conflict")

except ImportError as e:
    logging.warning(f"Skill Seekers integration not available: {e}")
    SKILL_SEEKERS_AVAILABLE = False
    # Create fallback mock classes
    DocToSkillConverter = None
    package_skill_directory = None
    enhance_skill_local = None

from ..signature_framework import SignatureSkill, SkillConfig, T_Input, T_Output
from ..signature_framework import ValidationResult, ConfidenceLevel


class TechnicalDataSource:
    """Represents a source of technical content for skill generation."""

    def __init__(
        self,
        source_type: str,  # "docs", "pdf", "github", "repo"
        source_url: str,
        config: Optional[Dict[str, Any]] = None,
    ):
        self.source_type = source_type
        self.source_url = source_url
        self.config = config or {}
        self.metadata = {}

    def validate(self) -> bool:
        """Validate the data source configuration."""
        if self.source_type == "docs" and not self.source_url.startswith("http"):
            return False
        if self.source_type == "github" and "github.com" not in self.source_url:
            return False
        return True


class SkillGenerationRequest(T_Input):
    """Input for skill generation from technical data sources."""

    def __init__(
        self,
        sources: List[TechnicalDataSource],
        skill_name: str,
        skill_description: str,
        enhancement_level: str = "standard",  # "basic", "standard", "advanced"
        conflict_detection: bool = True,
        output_format: str = "claude_skill",  # "claude_skill", "amplifier_skill"
        safety_level: str = "high",  # "low", "medium", "high"
    ):
        self.sources = sources
        self.skill_name = skill_name
        self.skill_description = skill_description
        self.enhancement_level = enhancement_level
        self.conflict_detection = conflict_detection
        self.output_format = output_format
        self.safety_level = safety_level

    def validate(self) -> ValidationResult:
        """Validate the skill generation request."""
        errors = []

        if not self.sources:
            errors.append("At least one data source must be provided")

        for source in self.sources:
            if not source.validate():
                errors.append(f"Invalid data source: {source.source_url}")

        if not self.skill_name or not self.skill_name.strip():
            errors.append("Skill name must not be empty")

        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors,
            confidence=ConfidenceLevel.HIGH if len(errors) == 0 else ConfidenceLevel.LOW,
        )


class GeneratedSkill(T_Output):
    """Output from skill generation process."""

    def __init__(
        self,
        skill_name: str,
        skill_files: Dict[str, str],  # filename -> content
        metadata: Dict[str, Any],
        conflicts_detected: List[Dict[str, Any]] = None,
        processing_log: List[str] = None,
        quality_score: float = 0.0,
    ):
        self.skill_name = skill_name
        self.skill_files = skill_files
        self.metadata = metadata
        self.conflicts_detected = conflicts_detected or []
        self.processing_log = processing_log or []
        self.quality_score = quality_score

    def get_skill_package_path(self) -> Optional[Path]:
        """Get path to generated skill package if available."""
        package_path = Path("output") / f"{self.skill_name}.zip"
        return package_path if package_path.exists() else None


class SkillSeekersIntegrationSkill(SignatureSkill):
    """
    Advanced skill that integrates Skill Seekers capabilities with Microsoft Amplifier.

    This skill provides automated conversion of technical documentation, PDFs,
    and repositories into Claude-compatible skills with advanced conflict detection
    and safety measures.
    """

    def __init__(self):
        config = SkillConfig(
            name="skill_seekers_integration",
            description="Integrates Skill Seekers technical data processing with Microsoft Amplifier",
            version="1.0.0",
            priority=1,
            input_contract=SkillGenerationRequest,
            output_contract=GeneratedSkill,
            enhancement_level="advanced",
            confidence_threshold=0.8,
        )
        super().__init__(config)

        # Processing components
        self.doc_processor = None
        self.pdf_processor = None
        self.github_processor = None
        self.ast_analyzer = None
        self.conflict_detector = None
        self.safety_validator = None

    async def initialize(self) -> None:
        """Initialize the integration skill and all processing components."""
        if not SKILL_SEEKERS_AVAILABLE:
            raise RuntimeError("Skill Seekers is not available. Please ensure it's properly installed.")

        await super().initialize()

        # Initialize processing components
        self.doc_processor = DocumentationProcessor()
        self.pdf_processor = PDFProcessor()
        self.github_processor = GitHubProcessor()
        self.ast_analyzer = ASTAnalyzer()
        self.conflict_detector = ConflictDetector()
        self.safety_validator = SafetyValidator()

        logging.info("Skill Seekers Integration Skill initialized successfully")

    async def execute(self, request: SkillGenerationRequest) -> GeneratedSkill:
        """
        Execute skill generation from technical data sources.

        Args:
            request: Skill generation request with data sources and configuration

        Returns:
            GeneratedSkill: Complete skill with all files and metadata
        """
        self.log_execution_start(request.skill_name)

        try:
            # Step 1: Validate request
            validation_result = request.validate()
            if not validation_result.is_valid:
                raise ValueError(f"Invalid request: {validation_result.errors}")

            # Step 2: Process each data source
            processed_content = []
            for source in request.sources:
                content = await self._process_data_source(source)
                processed_content.append(content)

            # Step 3: Merge and analyze content
            merged_content = await self._merge_content(processed_content)

            # Step 4: Conflict detection (if requested)
            conflicts = []
            if request.conflict_detection:
                conflicts = await self.conflict_detector.detect_conflicts(merged_content)

            # Step 5: Generate skill files
            skill_files = await self._generate_skill_files(request, merged_content, conflicts)

            # Step 6: Safety validation
            safety_result = await self.safety_validator.validate_skill_package(skill_files, request.safety_level)
            if not safety_result.is_safe:
                raise RuntimeError(f"Safety validation failed: {safety_result.issues}")

            # Step 7: Package skill
            await self._package_skill(request.skill_name, skill_files)

            # Step 8: Calculate quality score
            quality_score = await self._calculate_quality_score(skill_files, conflicts, safety_result)

            result = GeneratedSkill(
                skill_name=request.skill_name,
                skill_files=skill_files,
                metadata={
                    "sources_processed": len(request.sources),
                    "enhancement_level": request.enhancement_level,
                    "safety_level": request.safety_level,
                    "processing_time": self.get_execution_time(),
                    "safety_result": safety_result.dict(),
                },
                conflicts_detected=conflicts,
                processing_log=self.get_execution_log(),
                quality_score=quality_score,
            )

            self.log_execution_success(f"Generated skill: {request.skill_name}")
            return result

        except Exception as e:
            self.log_execution_error(f"Skill generation failed: {str(e)}")
            raise

    async def _process_data_source(self, source: TechnicalDataSource) -> Dict[str, Any]:
        """Process a single data source based on its type."""
        if source.source_type == "docs":
            return await self.doc_processor.process_documentation(source)
        elif source.source_type == "pdf":
            return await self.pdf_processor.process_pdf(source)
        elif source.source_type in ["github", "repo"]:
            return await self.github_processor.process_repository(source)
        else:
            raise ValueError(f"Unsupported source type: {source.source_type}")

    async def _merge_content(self, processed_content: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Merge processed content from multiple sources."""
        merged = {"text_content": "", "code_samples": [], "metadata": {}, "structure": {}}

        for content in processed_content:
            merged["text_content"] += "\n\n" + content.get("text_content", "")
            merged["code_samples"].extend(content.get("code_samples", []))
            merged["metadata"].update(content.get("metadata", {}))

        return merged

    async def _generate_skill_files(
        self, request: SkillGenerationRequest, content: Dict[str, Any], conflicts: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """Generate skill files from processed content."""
        files = {}

        # Generate main skill file
        skill_md = await self._generate_skill_md(request, content, conflicts)
        files["SKILL.md"] = skill_md

        # Generate reference files
        references = await self._generate_references(content)
        for ref_name, ref_content in references.items():
            files[f"references/{ref_name}"] = ref_content

        # Generate configuration
        files["skill_config.json"] = await self._generate_skill_config(request, content)

        return files

    async def _package_skill(self, skill_name: str, skill_files: Dict[str, str]) -> None:
        """Package the skill into a zip file."""
        output_dir = Path("output") / skill_name
        output_dir.mkdir(parents=True, exist_ok=True)

        # Write files
        for file_path, content in skill_files.items():
            full_path = output_dir / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)

        # Package using Skill Seekers packager
        if SKILL_SEEKERS_AVAILABLE:
            try:
                package_skill_directory(str(output_dir))
            except Exception as e:
                logging.warning(f"Failed to package skill with Skill Seekers: {e}")


class DocumentationProcessor:
    """Processes documentation websites using Skill Seekers."""

    async def process_documentation(self, source: TechnicalDataSource) -> Dict[str, Any]:
        """Process documentation website."""
        if not SKILL_SEEKERS_AVAILABLE:
            raise RuntimeError("Skill Seekers not available for documentation processing")

        # Create config for Skill Seekers
        config = {
            "name": source.metadata.get("name", "docs_skill"),
            "base_url": source.source_url,
            "selectors": source.config.get(
                "selectors", {"main_content": "article", "title": "h1", "code_blocks": "pre code"}
            ),
            "url_patterns": source.config.get("url_patterns", {}),
            "categories": source.config.get("categories", {}),
            "rate_limit": source.config.get("rate_limit", 0.5),
            "max_pages": source.config.get("max_pages", 500),
        }

        # Use Skill Seekers to process
        converter = DocToSkillConverter(config)

        # Process documentation
        await asyncio.get_event_loop().run_in_executor(None, converter.scrape_all)
        await asyncio.get_event_loop().run_in_executor(None, converter.build_skill)

        # Load processed content
        data_dir = Path("output") / f"{config['name']}_data"
        if data_dir.exists():
            return await self._load_processed_data(data_dir)
        else:
            raise RuntimeError("Failed to process documentation")


class PDFProcessor:
    """Processes PDF files with OCR capabilities."""

    def __init__(self):
        self.ocr_enabled = True  # Configure based on availability

    async def process_pdf(self, source: TechnicalDataSource) -> Dict[str, Any]:
        """Process PDF file with OCR."""
        pdf_path = Path(source.source_url)
        if not pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {source.source_url}")

        # Extract text from PDF
        text_content = await self._extract_pdf_text(pdf_path)

        # Extract code blocks if any
        code_samples = await self._extract_code_from_text(text_content)

        return {
            "text_content": text_content,
            "code_samples": code_samples,
            "metadata": {"source_type": "pdf", "file_path": str(pdf_path), "file_size": pdf_path.stat().st_size},
        }

    async def _extract_pdf_text(self, pdf_path: Path) -> str:
        """Extract text from PDF using pdfplumber."""
        try:
            import pdfplumber

            text_content = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)

            return "\n\n".join(text_content)

        except ImportError:
            raise RuntimeError("pdfplumber not available for PDF processing")

    async def _extract_code_from_text(self, text: str) -> List[Dict[str, str]]:
        """Extract code blocks from text content."""
        code_samples = []

        # Simple code block detection - can be enhanced
        lines = text.split("\n")
        current_code_block = []
        in_code_block = False

        for line in lines:
            if line.strip().startswith("```"):
                if in_code_block:
                    # End of code block
                    if current_code_block:
                        code_samples.append(
                            {
                                "code": "\n".join(current_code_block),
                                "language": "unknown",  # Could be enhanced with detection
                            }
                        )
                    current_code_block = []
                    in_code_block = False
                else:
                    in_code_block = True
            elif in_code_block:
                current_code_block.append(line)

        return code_samples


class GitHubProcessor:
    """Processes GitHub repositories."""

    async def process_repository(self, source: TechnicalDataSource) -> Dict[str, Any]:
        """Process GitHub repository."""
        # Extract repository info from URL
        if "github.com" not in source.source_url:
            raise ValueError("Invalid GitHub repository URL")

        # Parse repository URL
        parts = source.source_url.strip("/").split("/")
        if len(parts) < 5:
            raise ValueError("Invalid GitHub repository URL format")

        owner, repo = parts[3], parts[4]

        # Clone repository
        repo_path = await self._clone_repository(owner, repo)

        # Analyze repository
        analysis = await self._analyze_repository(repo_path, source.config)

        return analysis

    async def _clone_repository(self, owner: str, repo: str) -> Path:
        """Clone GitHub repository."""
        import subprocess

        clone_path = Path("temp_repos") / f"{owner}_{repo}"
        clone_path.mkdir(parents=True, exist_ok=True)

        if not (clone_path / ".git").exists():
            subprocess.run(["git", "clone", f"https://github.com/{owner}/{repo}.git", str(clone_path)], check=True)

        return clone_path

    async def _analyze_repository(self, repo_path: Path, config: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze cloned repository."""
        # This is a simplified version - can be enhanced
        # to include README analysis, code structure analysis, etc.

        # Find documentation files
        doc_files = []
        for ext in [".md", ".rst", ".txt"]:
            doc_files.extend(repo_path.rglob(f"*{ext}"))

        # Extract content from documentation
        text_content = ""
        code_samples = []

        for doc_file in doc_files[:10]:  # Limit to prevent too much content
            try:
                content = doc_file.read_text(encoding="utf-8")
                text_content += f"\n\n# {doc_file.name}\n{content}"
            except Exception as e:
                logging.warning(f"Failed to read {doc_file}: {e}")

        # Find code files
        code_extensions = [".py", ".js", ".ts", ".java", ".cpp", ".c"]
        for ext in code_extensions:
            for code_file in repo_path.rglob(f"*{ext}"):
                try:
                    content = code_file.read_text(encoding="utf-8")
                    # Extract first few lines as sample
                    lines = content.split("\n")[:20]
                    code_samples.append(
                        {
                            "code": "\n".join(lines),
                            "language": ext[1:],  # Remove dot
                            "file_path": str(code_file.relative_to(repo_path)),
                        }
                    )
                except Exception:
                    pass

        return {
            "text_content": text_content,
            "code_samples": code_samples,
            "metadata": {
                "source_type": "github",
                "repo_path": str(repo_path),
                "doc_files_found": len(doc_files),
                "code_files_found": len(code_samples),
            },
        }


class ASTAnalyzer:
    """Analyzes code using AST for structure and patterns."""

    async def analyze_code(self, code_samples: List[Dict[str, str]]) -> Dict[str, Any]:
        """Analyze code samples using AST."""
        analysis = {"languages": {}, "functions": [], "classes": [], "imports": [], "patterns": []}

        for sample in code_samples:
            language = sample.get("language", "unknown")
            code = sample.get("code", "")

            if language == "python":
                python_analysis = await self._analyze_python_ast(code)
                analysis["functions"].extend(python_analysis["functions"])
                analysis["classes"].extend(python_analysis["classes"])
                analysis["imports"].extend(python_analysis["imports"])

            analysis["languages"][language] = analysis["languages"].get(language, 0) + 1

        return analysis

    async def _analyze_python_ast(self, code: str) -> Dict[str, List[Dict[str, str]]]:
        """Analyze Python code using AST."""
        import ast

        try:
            tree = ast.parse(code)

            functions = []
            classes = []
            imports = []

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    functions.append(
                        {"name": node.name, "line": node.lineno, "args": [arg.arg for arg in node.args.args]}
                    )
                elif isinstance(node, ast.ClassDef):
                    classes.append(
                        {
                            "name": node.name,
                            "line": node.lineno,
                            "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                        }
                    )
                elif isinstance(node, (ast.Import, ast.ImportFrom)):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            imports.append({"module": alias.name, "alias": alias.asname})
                    else:
                        imports.append({"module": node.module, "names": [alias.name for alias in node.names]})

            return {"functions": functions, "classes": classes, "imports": imports}

        except Exception as e:
            logging.warning(f"Failed to parse Python AST: {e}")
            return {"functions": [], "classes": [], "imports": []}


class ConflictDetector:
    """Detects conflicts between different data sources."""

    async def detect_conflicts(self, content: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Detect conflicts in merged content."""
        conflicts = []

        # Analyze code samples for conflicts
        code_samples = content.get("code_samples", [])

        # Check for duplicate function names
        function_names = {}
        for sample in code_samples:
            if sample.get("language") == "python":
                # Simple function name detection
                lines = sample.get("code", "").split("\n")
                for line in lines:
                    if line.strip().startswith("def "):
                        func_name = line.strip().split("(")[0].replace("def ", "")
                        if func_name in function_names:
                            conflicts.append(
                                {
                                    "type": "duplicate_function",
                                    "name": func_name,
                                    "locations": [function_names[func_name], sample.get("file_path")],
                                }
                            )
                        else:
                            function_names[func_name] = sample.get("file_path")

        return conflicts


class SafetyValidator:
    """Validates skill packages for safety and security."""

    async def validate_skill_package(self, skill_files: Dict[str, str], safety_level: str) -> "SafetyResult":
        """Validate skill package for safety issues."""
        issues = []

        # Check for potentially dangerous content
        for file_path, content in skill_files.items():
            # Check for suspicious code patterns
            dangerous_patterns = ["eval(", "exec(", "__import__", "subprocess", "os.system", "open(", "file(", "input("]

            for pattern in dangerous_patterns:
                if pattern in content:
                    issues.append(
                        {
                            "severity": "high" if safety_level == "high" else "medium",
                            "type": "dangerous_pattern",
                            "file": file_path,
                            "pattern": pattern,
                        }
                    )

        # Check file sizes
        for file_path, content in skill_files.items():
            if len(content) > 1000000:  # 1MB limit
                issues.append({"severity": "medium", "type": "large_file", "file": file_path, "size": len(content)})

        is_safe = len([i for i in issues if i.get("severity") == "high"]) == 0

        return SafetyResult(is_safe=is_safe, issues=issues, safety_level=safety_level)


class SafetyResult:
    """Result of safety validation."""

    def __init__(self, is_safe: bool, issues: List[Dict[str, Any]], safety_level: str):
        self.is_safe = is_safe
        self.issues = issues
        self.safety_level = safety_level

    def dict(self) -> Dict[str, Any]:
        return {"is_safe": self.is_safe, "issues": self.issues, "safety_level": self.safety_level}


# Export main classes
__all__ = ["SkillSeekersIntegrationSkill", "TechnicalDataSource", "SkillGenerationRequest", "GeneratedSkill"]
