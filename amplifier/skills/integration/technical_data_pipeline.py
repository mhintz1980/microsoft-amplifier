"""
Automated Technical Data Processing Pipeline

This module provides a complete automated pipeline for converting various
technical data sources (documentation, PDFs, repositories) into Claude skills
with advanced conflict detection and safety measures.
"""

import asyncio
import json
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime

from .skill_seekers_integration import (
    SkillSeekersIntegrationSkill,
    TechnicalDataSource,
    SkillGenerationRequest,
    GeneratedSkill,
)


@dataclass
class PipelineConfig:
    """Configuration for the technical data processing pipeline."""

    # Processing limits
    max_documentation_pages: int = 1000
    max_pdf_size_mb: int = 50
    max_repo_size_mb: int = 100

    # Quality settings
    enhancement_level: str = "standard"  # "basic", "standard", "advanced"
    conflict_detection: bool = True
    safety_level: str = "high"  # "low", "medium", "high"

    # Output settings
    output_format: str = "claude_skill"  # "claude_skill", "amplifier_skill"
    include_references: bool = True
    package_as_zip: bool = True

    # Processing options
    parallel_processing: bool = True
    retry_failed_sources: bool = True
    max_retries: int = 3

    # Enhancement options
    enable_ai_enhancement: bool = True
    extract_code_patterns: bool = True
    generate_examples: bool = True

    # Virtual environment safety
    isolated_processing: bool = True
    temp_cleanup: bool = True
    validate_inputs: bool = True


@dataclass
class ProcessingResult:
    """Result of processing a technical data source."""

    source_url: str
    source_type: str
    status: str  # "success", "failed", "partial"
    pages_processed: int = 0
    files_extracted: int = 0
    errors: List[str] = None
    warnings: List[str] = None
    processing_time: float = 0.0
    content_size: int = 0

    def __post_init__(self):
        if self.errors is None:
            self.errors = []
        if self.warnings is None:
            self.warnings = []


@dataclass
class PipelineReport:
    """Comprehensive report of pipeline execution."""

    skill_name: str
    total_sources: int
    successful_sources: int
    failed_sources: int
    partial_sources: int
    total_pages: int
    total_files: int
    conflicts_detected: int
    safety_issues: int
    quality_score: float
    processing_time: float
    generated_files: Dict[str, str]
    package_path: Optional[str] = None
    results: List[ProcessingResult] = None

    def __post_init__(self):
        if self.results is None:
            self.results = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)

    def save_to_file(self, file_path: Union[str, Path]) -> None:
        """Save report to JSON file."""
        with open(file_path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)


class TechnicalDataPipeline:
    """
    Automated pipeline for processing technical data sources into Claude skills.

    This pipeline provides:
    - Multi-source processing (documentation, PDFs, repositories)
    - Advanced conflict detection
    - Safety validation
    - Quality assessment
    - Automated packaging
    - Comprehensive reporting
    """

    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        self.integration_skill = None
        self.processing_log = []

        # Statistics tracking
        self.stats = {
            "sources_processed": 0,
            "pages_scraped": 0,
            "files_extracted": 0,
            "conflicts_detected": 0,
            "safety_issues": 0,
            "processing_time": 0.0,
        }

    async def initialize(self) -> None:
        """Initialize the pipeline and integration skill."""
        logging.info("Initializing Technical Data Pipeline")

        try:
            self.integration_skill = SkillSeekersIntegrationSkill()
            await self.integration_skill.initialize()

            # Create necessary directories
            Path("output").mkdir(exist_ok=True)
            Path("temp_repos").mkdir(exist_ok=True)
            Path("reports").mkdir(exist_ok=True)

            logging.info("Pipeline initialized successfully")

        except Exception as e:
            logging.error(f"Failed to initialize pipeline: {e}")
            raise

    async def process_sources(
        self, sources: List[Dict[str, Any]], skill_name: str, skill_description: str
    ) -> PipelineReport:
        """
        Process multiple technical data sources into a skill.

        Args:
            sources: List of data source configurations
            skill_name: Name for the generated skill
            skill_description: Description of the skill's purpose

        Returns:
            PipelineReport: Comprehensive report of processing results
        """
        start_time = datetime.now()

        logging.info(f"Starting pipeline for skill: {skill_name}")
        logging.info(f"Processing {len(sources)} data sources")

        try:
            # Step 1: Validate and prepare sources
            validated_sources = await self._prepare_sources(sources)

            # Step 2: Create skill generation request
            request = SkillGenerationRequest(
                sources=validated_sources,
                skill_name=skill_name,
                skill_description=skill_description,
                enhancement_level=self.config.enhancement_level,
                conflict_detection=self.config.conflict_detection,
                output_format=self.config.output_format,
                safety_level=self.config.safety_level,
            )

            # Step 3: Execute skill generation
            generated_skill = await self.integration_skill.execute(request)

            # Step 4: Generate comprehensive report
            processing_time = (datetime.now() - start_time).total_seconds()

            report = PipelineReport(
                skill_name=skill_name,
                total_sources=len(sources),
                successful_sources=len([s for s in sources if s.get("status") != "failed"]),
                failed_sources=len([s for s in sources if s.get("status") == "failed"]),
                partial_sources=0,  # TODO: Implement partial detection
                total_pages=self.stats["pages_scraped"],
                total_files=self.stats["files_extracted"],
                conflicts_detected=len(generated_skill.conflicts_detected),
                safety_issues=len(generated_skill.metadata.get("safety_result", {}).get("issues", [])),
                quality_score=generated_skill.quality_score,
                processing_time=processing_time,
                generated_files=generated_skill.skill_files,
                package_path=str(generated_skill.get_skill_package_path())
                if generated_skill.get_skill_package_path()
                else None,
            )

            # Step 5: Save report
            await self._save_report(report)

            # Step 6: Cleanup if configured
            if self.config.temp_cleanup:
                await self._cleanup_temp_files()

            logging.info(f"Pipeline completed for skill: {skill_name}")
            return report

        except Exception as e:
            logging.error(f"Pipeline failed for skill {skill_name}: {e}")
            raise

    async def _prepare_sources(self, sources: List[Dict[str, Any]]) -> List[TechnicalDataSource]:
        """Validate and prepare data sources for processing."""
        validated_sources = []

        for source_config in sources:
            try:
                # Validate source configuration
                if not self._validate_source_config(source_config):
                    logging.warning(f"Skipping invalid source config: {source_config}")
                    continue

                # Create TechnicalDataSource
                source = TechnicalDataSource(
                    source_type=source_config["type"],
                    source_url=source_config["url"],
                    config=source_config.get("config", {}),
                )

                # Add metadata
                source.metadata = {
                    "name": source_config.get("name", ""),
                    "description": source_config.get("description", ""),
                    "priority": source_config.get("priority", "medium"),
                }

                validated_sources.append(source)
                self.stats["sources_processed"] += 1

            except Exception as e:
                logging.error(f"Failed to prepare source {source_config}: {e}")
                continue

        return validated_sources

    def _validate_source_config(self, source_config: Dict[str, Any]) -> bool:
        """Validate a single source configuration."""
        required_fields = ["type", "url"]

        for field in required_fields:
            if field not in source_config:
                logging.error(f"Missing required field '{field}' in source config")
                return False

        source_type = source_config["type"]
        if source_type not in ["docs", "pdf", "github", "repo"]:
            logging.error(f"Unsupported source type: {source_type}")
            return False

        source_url = source_config["url"]

        # Validate URL based on type
        if source_type == "docs" and not source_url.startswith("http"):
            logging.error(f"Documentation URL must start with http/https: {source_url}")
            return False

        if source_type == "pdf":
            pdf_path = Path(source_url)
            if not pdf_path.exists():
                logging.error(f"PDF file not found: {source_url}")
                return False

            # Check file size
            size_mb = pdf_path.stat().st_size / (1024 * 1024)
            if size_mb > self.config.max_pdf_size_mb:
                logging.error(f"PDF file too large: {size_mb:.1f}MB > {self.config.max_pdf_size_mb}MB")
                return False

        if source_type in ["github", "repo"] and "github.com" not in source_url:
            logging.error(f"Invalid GitHub repository URL: {source_url}")
            return False

        return True

    async def _save_report(self, report: PipelineReport) -> None:
        """Save pipeline report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = Path("reports") / f"{report.skill_name}_{timestamp}_report.json"

        try:
            report.save_to_file(report_file)
            logging.info(f"Report saved to: {report_file}")
        except Exception as e:
            logging.error(f"Failed to save report: {e}")

    async def _cleanup_temp_files(self) -> None:
        """Clean up temporary files and directories."""
        try:
            import shutil

            # Clean up temporary repositories
            temp_repos_dir = Path("temp_repos")
            if temp_repos_dir.exists():
                shutil.rmtree(temp_repos_dir)
                logging.info("Cleaned up temporary repositories")

        except Exception as e:
            logging.warning(f"Failed to cleanup temp files: {e}")

    async def batch_process(self, batch_config: List[Dict[str, Any]]) -> List[PipelineReport]:
        """
        Process multiple skills in batch.

        Args:
            batch_config: List of skill processing configurations

        Returns:
            List[PipelineReport]: Reports for each processed skill
        """
        reports = []

        if self.config.parallel_processing:
            # Process skills in parallel
            tasks = []
            for skill_config in batch_config:
                task = self.process_sources(
                    sources=skill_config["sources"],
                    skill_name=skill_config["skill_name"],
                    skill_description=skill_config["skill_description"],
                )
                tasks.append(task)

            reports = await asyncio.gather(*tasks, return_exceptions=True)

            # Handle exceptions
            processed_reports = []
            for i, result in enumerate(reports):
                if isinstance(result, Exception):
                    logging.error(f"Failed to process skill {batch_config[i]['skill_name']}: {result}")
                    # Create error report
                    error_report = PipelineReport(
                        skill_name=batch_config[i]["skill_name"],
                        total_sources=0,
                        successful_sources=0,
                        failed_sources=len(batch_config[i]["sources"]),
                        partial_sources=0,
                        total_pages=0,
                        total_files=0,
                        conflicts_detected=0,
                        safety_issues=0,
                        quality_score=0.0,
                        processing_time=0.0,
                        generated_files={},
                    )
                    processed_reports.append(error_report)
                else:
                    processed_reports.append(result)

            reports = processed_reports
        else:
            # Process skills sequentially
            for skill_config in batch_config:
                try:
                    report = await self.process_sources(
                        sources=skill_config["sources"],
                        skill_name=skill_config["skill_name"],
                        skill_description=skill_config["skill_description"],
                    )
                    reports.append(report)
                except Exception as e:
                    logging.error(f"Failed to process skill {skill_config['skill_name']}: {e}")
                    continue

        return reports

    def get_stats(self) -> Dict[str, Any]:
        """Get current pipeline statistics."""
        return {
            "config": asdict(self.config),
            "stats": self.stats,
            "integration_skill_available": self.integration_skill is not None,
        }


# Convenience functions for common use cases


async def create_skill_from_documentation(
    docs_url: str, skill_name: str, skill_description: str, config: Optional[PipelineConfig] = None
) -> PipelineReport:
    """
    Create a skill from a single documentation source.

    Args:
        docs_url: URL of the documentation website
        skill_name: Name for the generated skill
        skill_description: Description of the skill's purpose
        config: Optional pipeline configuration

    Returns:
        PipelineReport: Processing report
    """
    pipeline = TechnicalDataPipeline(config)
    await pipeline.initialize()

    sources = [{"type": "docs", "url": docs_url, "name": skill_name, "config": {"max_pages": 500, "rate_limit": 0.5}}]

    return await pipeline.process_sources(sources, skill_name, skill_description)


async def create_skill_from_github_repo(
    github_url: str, skill_name: str, skill_description: str, config: Optional[PipelineConfig] = None
) -> PipelineReport:
    """
    Create a skill from a GitHub repository.

    Args:
        github_url: URL of the GitHub repository
        skill_name: Name for the generated skill
        skill_description: Description of the skill's purpose
        config: Optional pipeline configuration

    Returns:
        PipelineReport: Processing report
    """
    pipeline = TechnicalDataPipeline(config)
    await pipeline.initialize()

    sources = [
        {
            "type": "github",
            "url": github_url,
            "name": skill_name,
            "config": {"include_docs": True, "include_code": True, "max_files": 100},
        }
    ]

    return await pipeline.process_sources(sources, skill_name, skill_description)


async def create_skill_from_pdf(
    pdf_path: str, skill_name: str, skill_description: str, config: Optional[PipelineConfig] = None
) -> PipelineReport:
    """
    Create a skill from a PDF file.

    Args:
        pdf_path: Path to the PDF file
        skill_name: Name for the generated skill
        skill_description: Description of the skill's purpose
        config: Optional pipeline configuration

    Returns:
        PipelineReport: Processing report
    """
    pipeline = TechnicalDataPipeline(config)
    await pipeline.initialize()

    sources = [
        {"type": "pdf", "url": pdf_path, "name": skill_name, "config": {"enable_ocr": True, "extract_code": True}}
    ]

    return await pipeline.process_sources(sources, skill_name, skill_description)


# Export main classes
__all__ = [
    "TechnicalDataPipeline",
    "PipelineConfig",
    "ProcessingResult",
    "PipelineReport",
    "create_skill_from_documentation",
    "create_skill_from_github_repo",
    "create_skill_from_pdf",
]
