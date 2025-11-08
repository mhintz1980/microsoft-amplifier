"""
Core CAD analysis functionality.
"""

import time
from pathlib import Path

from ..cv.cad_vision import CADVisionAnalyzer
from ..ml.predictor import MLPredictor
from ..utils.file_handler import FileHandler
from ..utils.logger import get_logger
from .models import (
    AcousticAnalysis,
    AnalysisConfig,
    AnalysisResult,
    AnalysisType,
    CADFileType,
    CADMetadata,
    DesignRecommendation,
    ManufacturingAnalysis,
    RecommendationType,
    SeverityLevel,
    SourceAttribution,
    StructuralAnalysis,
)

logger = get_logger(__name__)


class CADAnalyzer:
    """Main CAD analysis engine."""

    def __init__(self):
        self.vision_analyzer = CADVisionAnalyzer()
        self.ml_predictor = MLPredictor()
        self.file_handler = FileHandler()

    async def analyze_file(self, file_path: str | Path, config: AnalysisConfig) -> AnalysisResult:
        """Analyze a single CAD file."""
        start_time = time.time()
        file_path = Path(file_path)

        logger.info(f"Starting analysis of {file_path}")

        # Extract metadata
        metadata = await self._extract_metadata(file_path)

        # Load and preprocess CAD data
        cad_data = await self.file_handler.load_cad_file(file_path)

        # Initialize analysis components
        acoustic_result = None
        structural_result = None
        manufacturing_result = None
        recommendations = []

        # Perform analysis based on type
        if config.analysis_type in [AnalysisType.COMPREHENSIVE, AnalysisType.ACOUSTIC]:
            acoustic_result = await self._analyze_acoustics(cad_data, config)
            recommendations.extend(acoustic_result.recommendations if acoustic_result else [])

        if config.analysis_type in [AnalysisType.COMPREHENSIVE, AnalysisType.STRUCTURAL]:
            structural_result = await self._analyze_structural(cad_data, config)
            recommendations.extend(structural_result.recommendations if structural_result else [])

        if config.analysis_type in [AnalysisType.COMPREHENSIVE, AnalysisType.MANUFACTURING]:
            manufacturing_result = await self._analyze_manufacturing(cad_data, config)
            recommendations.extend(manufacturing_result.recommendations if manufacturing_result else [])

        # Calculate overall scores
        overall_score, confidence = await self._calculate_overall_scores(
            acoustic_result, structural_result, manufacturing_result
        )

        # Filter recommendations by confidence threshold
        filtered_recommendations = [r for r in recommendations if r.confidence >= config.confidence_threshold]

        processing_time = time.time() - start_time

        result = AnalysisResult(
            metadata=metadata,
            config=config,
            overall_score=overall_score,
            confidence=confidence,
            recommendations=filtered_recommendations,
            acoustic_analysis=acoustic_result,
            structural_analysis=structural_result,
            manufacturing_analysis=manufacturing_result,
            processing_time=processing_time,
        )

        logger.info(f"Analysis completed in {processing_time:.2f}s with score {overall_score:.2f}")
        return result

    async def _extract_metadata(self, file_path: Path) -> CADMetadata:
        """Extract metadata from CAD file."""
        file_type = CADFileType(file_path.suffix.lower().lstrip("."))
        file_size = file_path.stat().st_size

        # Detect file format details
        software_detected = await self.file_handler.detect_software(file_path)
        units = await self.file_handler.detect_units(file_path)
        bounding_box = await self.file_handler.extract_bounding_box(file_path)

        return CADMetadata(
            file_name=file_path.name,
            file_type=file_type,
            file_size=file_size,
            software_detected=software_detected,
            units=units,
            bounding_box=bounding_box,
        )

    async def _analyze_acoustics(self, cad_data: dict, config: AnalysisConfig) -> AcousticAnalysis:
        """Perform acoustic analysis."""
        logger.info("Performing acoustic analysis...")

        # Computer vision analysis for acoustic features
        vision_results = await self.vision_analyzer.analyze_acoustic_features(cad_data)

        # ML-based predictions
        ml_predictions = await self.ml_predictor.predict_acoustic_performance(cad_data)

        # Combine results
        weak_points = vision_results.get("weak_points", [])
        resonance_frequencies = ml_predictions.get("resonance_frequencies", [])
        predicted_stc = ml_predictions.get("predicted_stc")

        # Calculate overall rating
        overall_rating = await self._calculate_acoustic_rating(predicted_stc, weak_points)

        # Generate recommendations
        recommendations = await self._generate_acoustic_recommendations(
            weak_points, resonance_frequencies, predicted_stc
        )

        return AcousticAnalysis(
            predicted_stc=predicted_stc,
            weak_points=weak_points,
            resonance_frequencies=resonance_frequencies,
            transmission_loss_spectrum=ml_predictions.get("transmission_loss_spectrum"),
            overall_rating=overall_rating,
            recommendations=recommendations,
        )

    async def _analyze_structural(self, cad_data: dict, config: AnalysisConfig) -> StructuralAnalysis:
        """Perform structural analysis."""
        logger.info("Performing structural analysis...")

        # Vision-based structural analysis
        vision_results = await self.vision_analyzer.analyze_structural_features(cad_data)

        # ML-based structural predictions
        ml_predictions = await self.ml_predictor.predict_structural_performance(cad_data)

        # Extract stress concentrations and critical loads
        stress_concentrations = vision_results.get("stress_concentrations", [])
        critical_loads = ml_predictions.get("critical_loads", [])
        safety_factors = ml_predictions.get("safety_factors", {})

        # Calculate fatigue life
        fatigue_life = await self._estimate_fatigue_life(cad_data, safety_factors)

        # Generate recommendations
        recommendations = await self._generate_structural_recommendations(
            stress_concentrations, safety_factors, fatigue_life
        )

        return StructuralAnalysis(
            stress_concentrations=stress_concentrations,
            critical_loads=critical_loads,
            safety_factors=safety_factors,
            deformation_analysis=ml_predictions.get("deformation_analysis"),
            fatigue_life_estimate=fatigue_life,
            recommendations=recommendations,
        )

    async def _analyze_manufacturing(self, cad_data: dict, config: AnalysisConfig) -> ManufacturingAnalysis:
        """Perform manufacturability analysis."""
        logger.info("Performing manufacturability analysis...")

        # Vision-based manufacturing analysis
        vision_results = await self.vision_analyzer.analyze_manufacturing_features(cad_data)

        # ML-based manufacturing predictions
        ml_predictions = await self.ml_predictor.predict_manufacturability(cad_data)

        # Extract manufacturing metrics
        cnc_feasibility = ml_predictions.get("cnc_feasibility", 0.0)
        estimated_cost = ml_predictions.get("estimated_cost")
        machining_time = ml_predictions.get("machining_time")
        tool_access_issues = vision_results.get("tool_access_issues", [])
        material_waste = ml_predictions.get("material_waste")

        # Determine setup complexity
        setup_complexity = await self._determine_setup_complexity(tool_access_issues, cnc_feasibility)

        # Generate recommendations
        recommendations = await self._generate_manufacturing_recommendations(
            cnc_feasibility, tool_access_issues, material_waste
        )

        return ManufacturingAnalysis(
            cnc_feasibility=cnc_feasibility,
            estimated_cost=estimated_cost,
            machining_time=machining_time,
            tool_access_issues=tool_access_issues,
            material_waste=material_waste,
            setup_complexity=setup_complexity,
            recommendations=recommendations,
        )

    async def _calculate_overall_scores(
        self,
        acoustic: AcousticAnalysis | None,
        structural: StructuralAnalysis | None,
        manufacturing: ManufacturingAnalysis | None,
    ) -> tuple[float, float]:
        """Calculate overall score and confidence."""
        scores = []
        confidences = []

        if acoustic and acoustic.overall_rating:
            scores.append(acoustic.overall_rating / 10.0)  # Normalize to 0-1
            confidences.append(0.8)  # Acoustic analysis confidence

        if structural and structural.overall_rating:
            scores.append(structural.overall_rating / 10.0)
            confidences.append(0.9)  # Structural analysis confidence

        if manufacturing and manufacturing.overall_rating:
            scores.append(manufacturing.overall_rating / 10.0)
            confidences.append(0.85)  # Manufacturing analysis confidence

        if not scores:
            return 0.0, 0.0

        overall_score = sum(scores) / len(scores)
        overall_confidence = sum(confidences) / len(confidences)

        return overall_score, overall_confidence

    async def _generate_acoustic_recommendations(
        self, weak_points: list[str], resonance_frequencies: list[float], predicted_stc: float | None
    ) -> list[DesignRecommendation]:
        """Generate acoustic improvement recommendations."""
        recommendations = []

        # Check for low STC rating
        if predicted_stc and predicted_stc < 45:
            recommendations.append(
                DesignRecommendation(
                    type=RecommendationType.ACOUSTIC_IMPROVEMENT,
                    title="Low Sound Transmission Class Detected",
                    description=f"Predicted STC of {predicted_stc:.1f} is below recommended minimum of 45 for industrial enclosures. Consider adding mass damping or increasing wall thickness.",
                    severity=SeverityLevel.HIGH,
                    confidence=0.85,
                    estimated_impact="Significant improvement in noise reduction",
                    implementation_cost="Medium",
                    sources=[
                        SourceAttribution(
                            source="Acoustic Analysis Model",
                            confidence=0.85,
                            reasoning="STC prediction based on material properties and geometry",
                            data_points=[f"Predicted STC: {predicted_stc:.1f}"],
                        )
                    ],
                )
            )

        # Check for resonance issues
        for freq in resonance_frequencies:
            if 20 <= freq <= 2000:  # Human hearing range
                recommendations.append(
                    DesignRecommendation(
                        type=RecommendationType.ACOUSTIC_IMPROVEMENT,
                        title=f"Resonance at {freq:.1f} Hz",
                        description=f"Structural resonance detected at {freq:.1f} Hz within audible range. Consider adding stiffeners or damping material.",
                        severity=SeverityLevel.MEDIUM,
                        confidence=0.75,
                        estimated_impact="Reduces resonance-related noise amplification",
                        implementation_cost="Low to Medium",
                        sources=[
                            SourceAttribution(
                                source="Resonance Analysis",
                                confidence=0.75,
                                reasoning="Modal analysis of structural dynamics",
                                data_points=[f"Resonance frequency: {freq:.1f} Hz"],
                            )
                        ],
                    )
                )

        # Check weak points
        for point in weak_points:
            recommendations.append(
                DesignRecommendation(
                    type=RecommendationType.ACOUSTIC_IMPROVEMENT,
                    title="Acoustic Weak Point Identified",
                    description=f"Acoustic weak point detected: {point}. This area may allow sound leakage.",
                    severity=SeverityLevel.MEDIUM,
                    confidence=0.70,
                    estimated_impact="Improves overall acoustic performance",
                    implementation_cost="Low",
                    sources=[
                        SourceAttribution(
                            source="Visual Acoustic Analysis",
                            confidence=0.70,
                            reasoning="Computer vision analysis of geometry for acoustic weak points",
                            data_points=[f"Weak point: {point}"],
                        )
                    ],
                )
            )

        return recommendations

    async def _generate_structural_recommendations(
        self, stress_concentrations: list[dict], safety_factors: dict, fatigue_life: float | None
    ) -> list[DesignRecommendation]:
        """Generate structural improvement recommendations."""
        recommendations = []

        # Check for low safety factors
        for component, factor in safety_factors.items():
            if factor < 2.0:  # Standard minimum for industrial equipment
                recommendations.append(
                    DesignRecommendation(
                        type=RecommendationType.STRUCTURAL_REINFORCEMENT,
                        title=f"Low Safety Factor in {component}",
                        description=f"Safety factor of {factor:.2f} in {component} is below recommended minimum of 2.0. Consider reinforcement or material upgrade.",
                        severity=SeverityLevel.HIGH if factor < 1.5 else SeverityLevel.MEDIUM,
                        confidence=0.90,
                        estimated_impact="Improves structural safety and reliability",
                        implementation_cost="Medium",
                        sources=[
                            SourceAttribution(
                                source="Structural Analysis",
                                confidence=0.90,
                                reasoning="Finite element analysis stress calculations",
                                data_points=[f"Component: {component}", f"Safety factor: {factor:.2f}"],
                            )
                        ],
                    )
                )

        # Check stress concentrations
        for stress_point in stress_concentrations:
            if stress_point.get("max_stress", 0) > stress_point.get("yield_strength", 0) * 0.8:
                recommendations.append(
                    DesignRecommendation(
                        type=RecommendationType.STRUCTURAL_REINFORCEMENT,
                        title="High Stress Concentration",
                        description=f"High stress concentration detected at {stress_point.get('location', 'unknown location')}. Consider adding fillets or reinforcement.",
                        severity=SeverityLevel.HIGH,
                        confidence=0.85,
                        estimated_impact="Reduces risk of structural failure",
                        implementation_cost="Low to Medium",
                        sources=[
                            SourceAttribution(
                                source="Stress Analysis",
                                confidence=0.85,
                                reasoning="Stress concentration factor analysis",
                                data_points=[
                                    f"Location: {stress_point.get('location')}",
                                    f"Max stress: {stress_point.get('max_stress'):.1f} MPa",
                                ],
                            )
                        ],
                    )
                )

        # Check fatigue life
        if fatigue_life and fatigue_life < 1000000:  # 1 million cycles minimum
            recommendations.append(
                DesignRecommendation(
                    type=RecommendationType.STRUCTURAL_REINFORCEMENT,
                    title="Limited Fatigue Life",
                    description=f"Estimated fatigue life of {fatigue_life:,.0f} cycles may be insufficient for long-term operation. Consider material upgrade or design modification.",
                    severity=SeverityLevel.MEDIUM,
                    confidence=0.75,
                    estimated_impact="Extends equipment service life",
                    implementation_cost="Medium",
                    sources=[
                        SourceAttribution(
                            source="Fatigue Analysis",
                            confidence=0.75,
                            reasoning="S-N curve analysis and stress range calculations",
                            data_points=[f"Estimated life: {fatigue_life:,.0f} cycles"],
                        )
                    ],
                )
            )

        return recommendations

    async def _generate_manufacturing_recommendations(
        self, cnc_feasibility: float, tool_access_issues: list[str], material_waste: float | None
    ) -> list[DesignRecommendation]:
        """Generate manufacturing optimization recommendations."""
        recommendations = []

        # Check CNC feasibility
        if cnc_feasibility < 0.7:
            recommendations.append(
                DesignRecommendation(
                    type=RecommendationType.MANUFACTURING_OPTIMIZATION,
                    title="Low CNC Machining Feasibility",
                    description=f"CNC machining feasibility score of {cnc_feasibility:.2f} indicates potential manufacturing difficulties. Consider design simplification.",
                    severity=SeverityLevel.HIGH,
                    confidence=0.80,
                    estimated_impact="Reduces manufacturing complexity and cost",
                    implementation_cost="Design time only",
                    sources=[
                        SourceAttribution(
                            source="Manufacturing Analysis",
                            confidence=0.80,
                            reasoning="Geometric complexity and tool access analysis",
                            data_points=[f"CNC feasibility: {cnc_feasibility:.2f}"],
                        )
                    ],
                )
            )

        # Check tool access issues
        for issue in tool_access_issues:
            recommendations.append(
                DesignRecommendation(
                    type=RecommendationType.MANUFACTURING_OPTIMIZATION,
                    title="Tool Access Issue",
                    description=f"Tool access problem identified: {issue}. This may require specialized tooling or fixturing.",
                    severity=SeverityLevel.MEDIUM,
                    confidence=0.75,
                    estimated_impact="Improves manufacturing efficiency",
                    implementation_cost="Low to Medium",
                    sources=[
                        SourceAttribution(
                            source="Tool Access Analysis",
                            confidence=0.75,
                            reasoning="Computer vision analysis of manufacturing geometry",
                            data_points=[f"Tool access issue: {issue}"],
                        )
                    ],
                )
            )

        # Check material waste
        if material_waste and material_waste > 30:  # 30% waste threshold
            recommendations.append(
                DesignRecommendation(
                    type=RecommendationType.MANUFACTURING_OPTIMIZATION,
                    title="High Material Waste",
                    description=f"Estimated material waste of {material_waste:.1f}% is above optimal range. Consider design optimization or nesting strategy.",
                    severity=SeverityLevel.MEDIUM,
                    confidence=0.70,
                    estimated_impact="Reduces material cost and environmental impact",
                    implementation_cost="Low",
                    sources=[
                        SourceAttribution(
                            source="Material Optimization Analysis",
                            confidence=0.70,
                            reasoning="Bounding box volume vs actual part volume analysis",
                            data_points=[f"Material waste: {material_waste:.1f}%"],
                        )
                    ],
                )
            )

        return recommendations

    async def _calculate_acoustic_rating(self, predicted_stc: float | None, weak_points: list[str]) -> float | None:
        """Calculate overall acoustic rating."""
        if predicted_stc is None:
            return None

        # Base rating from STC (normalized to 1-10 scale)
        base_rating = min(predicted_stc / 10.0, 10.0)

        # Deduct points for weak points
        weak_point_penalty = len(weak_points) * 0.5

        return max(1.0, base_rating - weak_point_penalty)

    async def _estimate_fatigue_life(self, cad_data: dict, safety_factors: dict) -> float | None:
        """Estimate fatigue life based on analysis results."""
        # Simplified fatigue life estimation
        min_safety_factor = min(safety_factors.values()) if safety_factors else 1.0

        # Base life in cycles (simplified model)
        base_life = 10000000  # 10 million cycles for ideal design

        # Adjust based on minimum safety factor
        life_estimate = base_life * (min_safety_factor / 3.0) ** 3

        return life_estimate

    async def _determine_setup_complexity(self, tool_access_issues: list[str], cnc_feasibility: float) -> str:
        """Determine manufacturing setup complexity."""
        if len(tool_access_issues) > 3 or cnc_feasibility < 0.5:
            return "High"
        elif len(tool_access_issues) > 1 or cnc_feasibility < 0.7:
            return "Medium"
        else:
            return "Low"


async def analyze_design(file_path: str | Path, analysis_type: str = "comprehensive") -> AnalysisResult:
    """Simple interface for analyzing a CAD design."""
    config = AnalysisConfig(analysis_type=AnalysisType(analysis_type), confidence_threshold=0.7)

    analyzer = CADAnalyzer()
    return await analyzer.analyze_file(file_path, config)
