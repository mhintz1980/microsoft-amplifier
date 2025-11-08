"""
Report generation utilities for CAD analysis results.
"""

import json
from pathlib import Path

from ..core.models import AnalysisResult, DesignRecommendation
from .logger import get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Generator for analysis reports in various formats."""

    async def generate_html(self, result: AnalysisResult, output_dir: Path) -> Path:
        """Generate HTML analysis report."""
        report_path = output_dir / f"{result.metadata.file_name}_analysis.html"

        html_content = await self._create_html_report(result)

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        logger.info(f"HTML report generated: {report_path}")
        return report_path

    async def generate_pdf(self, result: AnalysisResult, output_dir: Path) -> Path:
        """Generate PDF analysis report."""
        # For now, generate HTML and note PDF conversion would be needed
        html_path = await self.generate_html(result, output_dir)
        pdf_path = output_dir / f"{result.metadata.file_name}_analysis.pdf"

        # In a real implementation, you'd use a library like WeasyPrint or ReportLab
        # to convert HTML to PDF. For now, we'll create a placeholder.
        logger.info(f"PDF generation not fully implemented. HTML available at: {html_path}")

        return pdf_path

    async def _create_html_report(self, result: AnalysisResult) -> str:
        """Create HTML content for analysis report."""
        html_template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CAD Analysis Report - {file_name}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }}
        .header {{ border-bottom: 2px solid #007acc; padding-bottom: 20px; margin-bottom: 30px; }}
        .score {{ font-size: 2em; font-weight: bold; color: #007acc; }}
        .score.excellent {{ color: #28a745; }}
        .score.good {{ color: #17a2b8; }}
        .score.fair {{ color: #ffc107; }}
        .score.poor {{ color: #dc3545; }}
        .section {{ margin: 30px 0; padding: 20px; border: 1px solid #ddd; border-radius: 5px; }}
        .recommendation {{ margin: 15px 0; padding: 15px; border-left: 4px solid #007acc; background-color: #f8f9fa; }}
        .critical {{ border-left-color: #dc3545; }}
        .high {{ border-left-color: #fd7e14; }}
        .medium {{ border-left-color: #ffc107; }}
        .low {{ border-left-color: #28a745; }}
        .severity {{ font-weight: bold; text-transform: uppercase; }}
        .confidence {{ float: right; color: #666; }}
        .metadata {{ background-color: #f8f9fa; padding: 15px; border-radius: 5px; }}
        .analysis-results {{ display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 20px; margin: 20px 0; }}
        .analysis-card {{ border: 1px solid #ddd; padding: 15px; border-radius: 5px; }}
        .rating {{ font-size: 1.5em; font-weight: bold; }}
        table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>CAD Design Analysis Report</h1>
        <div class="metadata">
            <p><strong>File:</strong> {file_name}</p>
            <p><strong>Analysis Date:</strong> {analysis_date}</p>
            <p><strong>File Type:</strong> {file_type}</p>
            <p><strong>File Size:</strong> {file_size} bytes</p>
            {software_info}
        </div>
        <div class="score {score_class}">
            Overall Score: {overall_score:.2f}/1.00 (Confidence: {confidence:.2f})
        </div>
    </div>

    {analysis_summary}

    {recommendations_section}

    {detailed_analysis}

    <div class="section">
        <h2>Analysis Details</h2>
        <p><strong>Processing Time:</strong> {processing_time:.2f} seconds</p>
        <p><strong>Analysis Type:</strong> {analysis_type}</p>
        <p><strong>Confidence Threshold:</strong> {confidence_threshold}</p>
    </div>

    <div class="section">
        <h2>Source Attribution</h2>
        <p>This analysis was performed using a combination of computer vision, machine learning,
        and rule-based algorithms. Each recommendation includes source attribution indicating
        the confidence and reasoning behind the analysis decision.</p>
    </div>
</body>
</html>
        """

        # Format the template
        html_content = html_template.format(
            file_name=result.metadata.file_name,
            analysis_date=result.metadata.analysis_timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            file_type=result.metadata.file_type.value,
            file_size=result.metadata.file_size,
            software_info=f"<p><strong>Software:</strong> {result.metadata.software_detected}</p>"
            if result.metadata.software_detected
            else "",
            overall_score=result.overall_score,
            confidence=result.confidence,
            score_class=self._get_score_class(result.overall_score),
            analysis_summary=await self._create_analysis_summary(result),
            recommendations_section=await self._create_recommendations_section(result),
            detailed_analysis=await self._create_detailed_analysis(result),
            processing_time=result.processing_time or 0,
            analysis_type=result.config.analysis_type.value,
            confidence_threshold=result.config.confidence_threshold,
        )

        return html_content

    def _get_score_class(self, score: float) -> str:
        """Get CSS class for score display."""
        if score >= 0.8:
            return "excellent"
        elif score >= 0.6:
            return "good"
        elif score >= 0.4:
            return "fair"
        else:
            return "poor"

    async def _create_analysis_summary(self, result: AnalysisResult) -> str:
        """Create analysis summary section."""
        summary_html = """
        <div class="section">
            <h2>Analysis Summary</h2>
            <div class="analysis-results">
        """

        # Acoustic analysis summary
        if result.acoustic_analysis:
            acoustic = result.acoustic_analysis
            summary_html += f"""
                <div class="analysis-card">
                    <h3>Acoustic Performance</h3>
                    <div class="rating">{acoustic.overall_rating or "N/A"}/10</div>
                    <p><strong>Predicted STC:</strong> {acoustic.predicted_stc or "N/A"}</p>
                    <p><strong>Weak Points:</strong> {len(acoustic.weak_points)}</p>
                    <p><strong>Resonances:</strong> {len(acoustic.resonance_frequencies)}</p>
                </div>
            """

        # Structural analysis summary
        if result.structural_analysis:
            structural = result.structural_analysis
            summary_html += f"""
                <div class="analysis-card">
                    <h3>Structural Integrity</h3>
                    <div class="rating">{structural.overall_rating or "N/A"}/10</div>
                    <p><strong>Stress Points:</strong> {len(structural.stress_concentrations)}</p>
                    <p><strong>Critical Loads:</strong> {len(structural.critical_loads)}</p>
                    <p><strong>Fatigue Life:</strong> {structural.fatigue_life_estimate or "N/A"} cycles</p>
                </div>
            """

        # Manufacturing analysis summary
        if result.manufacturing_analysis:
            manufacturing = result.manufacturing_analysis
            summary_html += f"""
                <div class="analysis-card">
                    <h3>Manufacturability</h3>
                    <div class="rating">{manufacturing.overall_rating or "N/A"}/10</div>
                    <p><strong>CNC Feasibility:</strong> {manufacturing.cnc_feasibility:.2f}</p>
                    <p><strong>Tool Access Issues:</strong> {len(manufacturing.tool_access_issues)}</p>
                    <p><strong>Material Waste:</strong> {manufacturing.material_waste or "N/A"}%</p>
                </div>
            """

        summary_html += "</div></div>"
        return summary_html

    async def _create_recommendations_section(self, result: AnalysisResult) -> str:
        """Create recommendations section."""
        if not result.recommendations:
            return '<div class="section"><h2>Recommendations</h2><p>No recommendations found - design meets all criteria!</p></div>'

        recommendations_html = '<div class="section"><h2>Design Recommendations</h2>'

        # Group recommendations by severity
        critical_recs = [r for r in result.recommendations if r.severity.value == "critical"]
        high_recs = [r for r in result.recommendations if r.severity.value == "high"]
        medium_recs = [r for r in result.recommendations if r.severity.value == "medium"]
        low_recs = [r for r in result.recommendations if r.severity.value == "low"]

        for severity, recs in [
            ("critical", critical_recs),
            ("high", high_recs),
            ("medium", medium_recs),
            ("low", low_recs),
        ]:
            if recs:
                recommendations_html += f"<h3>{severity.title()} Priority</h3>"
                for rec in recs:
                    recommendations_html += await self._create_recommendation_html(rec)

        recommendations_html += "</div>"
        return recommendations_html

    async def _create_recommendation_html(self, rec: DesignRecommendation) -> str:
        """Create HTML for a single recommendation."""
        sources_html = ""
        if rec.sources:
            sources_html = "<h4>Sources:</h4><ul>"
            for source in rec.sources:
                sources_html += f"<li><strong>{source.source}</strong> (Confidence: {source.confidence:.2f}): {source.reasoning}</li>"
            sources_html += "</ul>"

        return f"""
        <div class="recommendation {rec.severity.value}">
            <div class="confidence">Confidence: {rec.confidence:.2f}</div>
            <h4>{rec.title}</h4>
            <span class="severity {rec.severity.value}">{rec.severity.value}</span>
            <p>{rec.description}</p>
            {f"<p><strong>Estimated Impact:</strong> {rec.estimated_impact}</p>" if rec.estimated_impact else ""}
            {f"<p><strong>Implementation Cost:</strong> {rec.implementation_cost}</p>" if rec.implementation_cost else ""}
            {f"<p><strong>Location:</strong> {rec.location}</p>" if rec.location else ""}
            {sources_html}
        </div>
        """

    async def _create_detailed_analysis(self, result: AnalysisResult) -> str:
        """Create detailed analysis section."""
        detailed_html = '<div class="section"><h2>Detailed Analysis Results</h2>'

        # Acoustic details
        if result.acoustic_analysis:
            acoustic = result.acoustic_analysis
            detailed_html += f"""
            <h3>Acoustic Analysis Details</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Predicted STC Rating</td><td>{acoustic.predicted_stc or "N/A"}</td></tr>
                <tr><td>Overall Acoustic Rating</td><td>{acoustic.overall_rating or "N/A"}/10</td></tr>
                <tr><td>Weak Points Identified</td><td>{len(acoustic.weak_points)}</td></tr>
                <tr><td>Resonance Frequencies</td><td>{", ".join([f"{f:.1f} Hz" for f in acoustic.resonance_frequencies[:5]])}</td></tr>
            </table>
            """

            if acoustic.transmission_loss_spectrum:
                detailed_html += "<h4>Transmission Loss Spectrum</h4><table><tr><th>Frequency</th><th>TL (dB)</th></tr>"
                for freq, tl in acoustic.transmission_loss_spectrum.items():
                    detailed_html += f"<tr><td>{freq}</td><td>{tl:.1f}</td></tr>"
                detailed_html += "</table>"

        # Structural details
        if result.structural_analysis:
            structural = result.structural_analysis
            detailed_html += f"""
            <h3>Structural Analysis Details</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>Overall Structural Rating</td><td>{structural.overall_rating or "N/A"}/10</td></tr>
                <tr><td>Stress Concentrations</td><td>{len(structural.stress_concentrations)}</td></tr>
                <tr><td>Critical Load Cases</td><td>{len(structural.critical_loads)}</td></tr>
                <tr><td>Estimated Fatigue Life</td><td>{structural.fatigue_life_estimate or "N/A"} cycles</td></tr>
            </table>
            """

            if structural.safety_factors:
                detailed_html += (
                    "<h4>Safety Factors by Component</h4><table><tr><th>Component</th><th>Safety Factor</th></tr>"
                )
                for component, sf in structural.safety_factors.items():
                    detailed_html += f"<tr><td>{component}</td><td>{sf:.2f}</td></tr>"
                detailed_html += "</table>"

        # Manufacturing details
        if result.manufacturing_analysis:
            manufacturing = result.manufacturing_analysis
            detailed_html += f"""
            <h3>Manufacturing Analysis Details</h3>
            <table>
                <tr><th>Metric</th><th>Value</th></tr>
                <tr><td>CNC Machining Feasibility</td><td>{manufacturing.cnc_feasibility:.2f}</td></tr>
                <tr><td>Overall Manufacturing Rating</td><td>{manufacturing.overall_rating or "N/A"}/10</td></tr>
                <tr><td>Estimated Machining Time</td><td>{manufacturing.machining_time or "N/A"} hours</td></tr>
                <tr><td>Tool Access Issues</td><td>{len(manufacturing.tool_access_issues)}</td></tr>
                <tr><td>Setup Complexity</td><td>{manufacturing.setup_complexity or "N/A"}</td></tr>
            </table>
            """

        detailed_html += "</div>"
        return detailed_html

    async def export_json(self, result: AnalysisResult, output_path: Path) -> None:
        """Export analysis result as JSON."""
        with open(output_path, "w") as f:
            json.dump(result.model_dump(), f, indent=2, default=str)

        logger.info(f"JSON report exported to {output_path}")

    async def create_batch_summary(self, results: list, output_path: Path) -> None:
        """Create a batch analysis summary report."""
        if not results:
            return

        # Calculate summary statistics
        total_files = len(results)
        avg_score = sum(r.overall_score for r in results) / total_files
        avg_confidence = sum(r.confidence for r in results) / total_files
        total_recommendations = sum(len(r.recommendations) for r in results)

        summary_html = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Batch CAD Analysis Summary</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 40px; }}
        .summary {{ background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        table {{ width: 100%; border-collapse: collapse; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
    </style>
</head>
<body>
    <h1>Batch CAD Analysis Summary</h1>
    <div class="summary">
        <h2>Overview</h2>
        <p><strong>Total Files Analyzed:</strong> {total_files}</p>
        <p><strong>Average Score:</strong> {avg_score:.2f}/1.00</p>
        <p><strong>Average Confidence:</strong> {avg_confidence:.2f}</p>
        <p><strong>Total Recommendations:</strong> {total_recommendations}</p>
    </div>

    <h2>Detailed Results</h2>
    <table>
        <tr>
            <th>File Name</th>
            <th>Score</th>
            <th>Confidence</th>
            <th>Recommendations</th>
            <th>Processing Time</th>
        </tr>
        """

        for result in results:
            summary_html += f"""
        <tr>
            <td>{result.metadata.file_name}</td>
            <td>{result.overall_score:.2f}</td>
            <td>{result.confidence:.2f}</td>
            <td>{len(result.recommendations)}</td>
            <td>{result.processing_time or 0:.2f}s</td>
        </tr>
            """

        summary_html += """
    </table>
</body>
</html>
        """

        with open(output_path, "w", encoding="utf-8") as f:
            f.write(summary_html)

        logger.info(f"Batch summary report generated: {output_path}")
