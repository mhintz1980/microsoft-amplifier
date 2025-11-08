"""
Main CAD reviewer orchestrator.
"""

import asyncio
import concurrent.futures
import json
from pathlib import Path

from ..ml.predictor import MLPredictor
from ..utils.file_handler import FileHandler
from ..utils.logger import get_logger
from ..utils.report_generator import ReportGenerator
from .analyzer import CADAnalyzer
from .models import (
    AnalysisConfig,
    AnalysisResult,
    BatchAnalysisSummary,
    DesignRecommendation,
    SourceAttribution,
)

logger = get_logger(__name__)


class CADReviewer:
    """Main CAD reviewer orchestrator."""

    def __init__(self, model_dir: Path | None = None):
        self.analyzer = CADAnalyzer()
        self.predictor = MLPredictor()
        self.file_handler = FileHandler()
        self.report_generator = ReportGenerator()

        # Load ML models if model directory provided
        if model_dir:
            asyncio.create_task(self.predictor.load_models(model_dir))

    async def analyze_file(self, file_path: str | Path, config: AnalysisConfig) -> AnalysisResult:
        """Analyze a single CAD file."""
        logger.info(f"Starting CAD analysis for {file_path}")

        try:
            result = await self.analyzer.analyze_file(file_path, config)

            # Post-process recommendations
            result.recommendations = await self._enhance_recommendations(result.recommendations, result)

            logger.info(f"CAD analysis completed for {file_path}")
            return result

        except Exception as e:
            logger.error(f"Error analyzing {file_path}: {e}")
            raise

    async def batch_analyze(
        self, file_paths: list[Path], config: AnalysisConfig, max_workers: int = 4
    ) -> list[AnalysisResult]:
        """Analyze multiple CAD files in parallel."""
        logger.info(f"Starting batch analysis of {len(file_paths)} files")

        results = []
        failed_files = []

        # Process files in parallel
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            loop = asyncio.get_event_loop()

            # Create tasks for all files
            tasks = [
                loop.run_in_executor(executor, self._analyze_file_sync, file_path, config) for file_path in file_paths
            ]

            # Wait for all tasks to complete
            for future in asyncio.as_completed(tasks):
                try:
                    result = await future
                    results.append(result)
                    logger.info(f"Completed analysis for {result.metadata.file_name}")
                except Exception as e:
                    failed_files.append(str(e))
                    logger.error(f"Failed to analyze file: {e}")

        logger.info(f"Batch analysis completed: {len(results)} successful, {len(failed_files)} failed")

        if failed_files:
            logger.warning(f"Failed files: {failed_files}")

        return results

    def _analyze_file_sync(self, file_path: Path, config: AnalysisConfig) -> AnalysisResult:
        """Synchronous wrapper for analyze_file (used in thread pool)."""
        return asyncio.run(self.analyze_file(file_path, config))

    async def generate_html_report(self, result: AnalysisResult, output_dir: Path) -> Path:
        """Generate HTML analysis report."""
        report_path = await self.report_generator.generate_html(result, output_dir)
        return report_path

    async def generate_pdf_report(self, result: AnalysisResult, output_dir: Path) -> Path:
        """Generate PDF analysis report."""
        report_path = await self.report_generator.generate_pdf(result, output_dir)
        return report_path

    async def _enhance_recommendations(
        self, recommendations: list[DesignRecommendation], result: AnalysisResult
    ) -> list[DesignRecommendation]:
        """Enhance recommendations with additional context and prioritization."""
        enhanced = []

        for rec in recommendations:
            # Add context from analysis results
            if rec.type.value == "acoustic_improvement" and result.acoustic_analysis:
                enhanced_rec = await self._enhance_acoustic_recommendation(rec, result)
            elif rec.type.value == "structural_reinforcement" and result.structural_analysis:
                enhanced_rec = await self._enhance_structural_recommendation(rec, result)
            elif rec.type.value == "manufacturing_optimization" and result.manufacturing_analysis:
                enhanced_rec = await self._enhance_manufacturing_recommendation(rec, result)
            else:
                enhanced_rec = rec

            # Add cross-references to related recommendations
            enhanced_rec = await self._add_cross_references(enhanced_rec, recommendations)

            enhanced.append(enhanced_rec)

        # Sort by priority (severity and confidence)
        enhanced.sort(key=lambda r: (r.severity.value, r.confidence), reverse=True)

        return enhanced

    async def _enhance_acoustic_recommendation(
        self, rec: DesignRecommendation, result: AnalysisResult
    ) -> DesignRecommendation:
        """Enhance acoustic recommendation with additional context."""
        if not result.acoustic_analysis:
            return rec

        acoustic = result.acoustic_analysis

        # Add specific improvement suggestions based on STC rating
        if acoustic.predicted_stc and acoustic.predicted_stc < 40:
            rec.description += " Consider adding mass-loaded vinyl or increasing wall thickness by 25%."

        # Add resonance-related suggestions
        if acoustic.resonance_frequencies:
            low_freq_resonances = [f for f in acoustic.resonance_frequencies if f < 200]
            if low_freq_resonances:
                rec.description += (
                    f" Add stiffeners to address low-frequency resonances at {min(low_freq_resonances):.0f} Hz."
                )

        # Add additional source attribution
        rec.sources.append(
            SourceAttribution(
                source="Acoustic Analysis Engine",
                confidence=0.9,
                reasoning="Enhanced with acoustic performance metrics",
                data_points=[
                    f"STC Rating: {acoustic.predicted_stc:.1f}" if acoustic.predicted_stc else "STC: Not calculated",
                    f"Weak Points: {len(acoustic.weak_points)}",
                    f"Resonances: {len(acoustic.resonance_frequencies)}",
                ],
            )
        )

        return rec

    async def _enhance_structural_recommendation(
        self, rec: DesignRecommendation, result: AnalysisResult
    ) -> DesignRecommendation:
        """Enhance structural recommendation with additional context."""
        if not result.structural_analysis:
            return rec

        structural = result.structural_analysis

        # Add specific reinforcement suggestions
        min_safety_factor = min(structural.safety_factors.values()) if structural.safety_factors else 2.0
        if min_safety_factor < 1.5:
            rec.description += (
                " Immediate action required - consider increasing material thickness or adding reinforcement ribs."
            )

        # Add fatigue life considerations
        if structural.fatigue_life_estimate and structural.fatigue_life_estimate < 1000000:
            rec.description += " This improvement will also extend fatigue life expectancy."

        # Add additional source attribution
        rec.sources.append(
            SourceAttribution(
                source="Structural Analysis Engine",
                confidence=0.95,
                reasoning="Enhanced with structural analysis metrics",
                data_points=[
                    f"Min Safety Factor: {min_safety_factor:.2f}",
                    f"Stress Points: {len(structural.stress_concentrations)}",
                    f"Fatigue Life: {structural.fatigue_life_estimate:,.0f} cycles"
                    if structural.fatigue_life_estimate
                    else "Fatigue: Not calculated",
                ],
            )
        )

        return rec

    async def _enhance_manufacturing_recommendation(
        self, rec: DesignRecommendation, result: AnalysisResult
    ) -> DesignRecommendation:
        """Enhance manufacturing recommendation with additional context."""
        if not result.manufacturing_analysis:
            return rec

        manufacturing = result.manufacturing_analysis

        # Add specific optimization suggestions
        if manufacturing.cnc_feasibility < 0.6:
            rec.description += (
                " Consider breaking this into multiple components or using alternative manufacturing methods."
            )

        # Add cost optimization suggestions
        if manufacturing.material_waste and manufacturing.material_waste > 25:
            rec.description += " This change could reduce material waste by approximately 15%."

        # Add setup complexity considerations
        if manufacturing.setup_complexity == "High":
            rec.description += " This modification will significantly reduce setup time and tooling costs."

        # Add additional source attribution
        rec.sources.append(
            SourceAttribution(
                source="Manufacturing Analysis Engine",
                confidence=0.85,
                reasoning="Enhanced with manufacturing analysis metrics",
                data_points=[
                    f"CNC Feasibility: {manufacturing.cnc_feasibility:.2f}",
                    f"Tool Access Issues: {len(manufacturing.tool_access_issues)}",
                    f"Material Waste: {manufacturing.material_waste:.1f}%"
                    if manufacturing.material_waste
                    else "Waste: Not calculated",
                ],
            )
        )

        return rec

    async def _add_cross_references(
        self, rec: DesignRecommendation, all_recommendations: list[DesignRecommendation]
    ) -> DesignRecommendation:
        """Add cross-references to related recommendations."""
        related_types = {
            "acoustic_improvement": ["structural_reinforcement", "material_change"],
            "structural_reinforcement": ["acoustic_improvement", "manufacturing_optimization"],
            "manufacturing_optimization": ["structural_reinforcement", "design_modification"],
            "material_change": ["acoustic_improvement", "structural_reinforcement"],
        }

        related_recs = [
            r for r in all_recommendations if r != rec and r.type.value in related_types.get(rec.type.value, [])
        ]

        if related_recs:
            related_info = f"Related improvements: {', '.join([r.title for r in related_recs[:2]])}"
            if len(related_recs) > 2:
                related_info += f" and {len(related_recs) - 2} others"

            rec.description += f" [Note: {related_info}]"

        return rec

    async def export_analysis_data(self, results: list[AnalysisResult], output_path: Path) -> None:
        """Export analysis data for training or documentation."""
        export_data = {
            "export_timestamp": results[0].metadata.analysis_timestamp.isoformat() if results else None,
            "total_analyses": len(results),
            "results": [result.model_dump() for result in results],
        }

        with open(output_path, "w") as f:
            json.dump(export_data, f, indent=2, default=str)

        logger.info(f"Analysis data exported to {output_path}")

    async def get_analysis_summary(self, results: list[AnalysisResult]) -> BatchAnalysisSummary:
        """Generate summary statistics for batch analysis."""
        if not results:
            return BatchAnalysisSummary(
                total_files=0,
                successful_analyses=0,
                failed_analyses=0,
                average_score=0.0,
                average_confidence=0.0,
                total_recommendations=0,
                processing_time=0.0,
            )

        successful = len(results)
        total_recommendations = sum(len(r.recommendations) for r in results)
        avg_score = sum(r.overall_score for r in results) / len(results)
        avg_confidence = sum(r.confidence for r in results) / len(results)
        total_time = sum(r.processing_time or 0 for r in results)

        return BatchAnalysisSummary(
            total_files=len(results),
            successful_analyses=successful,
            failed_analyses=0,  # Failed files aren't included in results
            average_score=avg_score,
            average_confidence=avg_confidence,
            total_recommendations=total_recommendations,
            processing_time=total_time,
            results=results,
        )
