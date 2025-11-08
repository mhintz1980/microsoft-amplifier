"""
Tests for data models.
"""

import pytest
from pydantic import ValidationError

from ..core.models import (
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


class TestAnalysisType:
    """Test AnalysisType enum."""

    def test_values(self):
        assert AnalysisType.COMPREHENSIVE.value == "comprehensive"
        assert AnalysisType.ACOUSTIC.value == "acoustic"
        assert AnalysisType.STRUCTURAL.value == "structural"
        assert AnalysisType.MANUFACTURING.value == "manufacturing"


class TestSeverityLevel:
    """Test SeverityLevel enum."""

    def test_values(self):
        assert SeverityLevel.CRITICAL.value == "critical"
        assert SeverityLevel.HIGH.value == "high"
        assert SeverityLevel.MEDIUM.value == "medium"
        assert SeverityLevel.LOW.value == "low"
        assert SeverityLevel.INFO.value == "info"


class TestRecommendationType:
    """Test RecommendationType enum."""

    def test_values(self):
        assert RecommendationType.ACOUSTIC_IMPROVEMENT.value == "acoustic_improvement"
        assert RecommendationType.STRUCTURAL_REINFORCEMENT.value == "structural_reinforcement"
        assert RecommendationType.MANUFACTURING_OPTIMIZATION.value == "manufacturing_optimization"


class TestSourceAttribution:
    """Test SourceAttribution model."""

    def test_valid_attribution(self):
        attribution = SourceAttribution(
            source="Test Model", confidence=0.85, reasoning="Test reasoning", data_points=["point1", "point2"]
        )

        assert attribution.source == "Test Model"
        assert attribution.confidence == 0.85
        assert attribution.reasoning == "Test reasoning"
        assert attribution.data_points == ["point1", "point2"]

    def test_invalid_confidence(self):
        with pytest.raises(ValidationError):
            SourceAttribution(
                source="Test Model",
                confidence=1.5,  # Invalid: > 1.0
                reasoning="Test reasoning",
            )

        with pytest.raises(ValidationError):
            SourceAttribution(
                source="Test Model",
                confidence=-0.1,  # Invalid: < 0.0
                reasoning="Test reasoning",
            )


class TestDesignRecommendation:
    """Test DesignRecommendation model."""

    def test_valid_recommendation(self):
        source = SourceAttribution(source="Test Model", confidence=0.8, reasoning="Test reasoning")

        rec = DesignRecommendation(
            type=RecommendationType.ACOUSTIC_IMPROVEMENT,
            title="Test Recommendation",
            description="This is a test recommendation",
            severity=SeverityLevel.MEDIUM,
            confidence=0.75,
            sources=[source],
        )

        assert rec.type == RecommendationType.ACOUSTIC_IMPROVEMENT
        assert rec.title == "Test Recommendation"
        assert rec.severity == SeverityLevel.MEDIUM
        assert rec.confidence == 0.75
        assert len(rec.sources) == 1

    def test_recommendation_with_optional_fields(self):
        rec = DesignRecommendation(
            type=RecommendationType.STRUCTURAL_REINFORCEMENT,
            title="Test Recommendation",
            description="This is a test recommendation",
            severity=SeverityLevel.HIGH,
            confidence=0.9,
            location="Component A",
            estimated_impact="Improves safety",
            implementation_cost="Medium",
        )

        assert rec.location == "Component A"
        assert rec.estimated_impact == "Improves safety"
        assert rec.implementation_cost == "Medium"


class TestAcousticAnalysis:
    """Test AcousticAnalysis model."""

    def test_acoustic_analysis(self):
        acoustic = AcousticAnalysis(
            predicted_stc=45.5,
            weak_points=["Opening at panel edge", "Thin section"],
            resonance_frequencies=[125.0, 250.0, 500.0],
            transmission_loss_spectrum={"125Hz": 25.0, "250Hz": 30.0},
            overall_rating=7.5,
        )

        assert acoustic.predicted_stc == 45.5
        assert len(acoustic.weak_points) == 2
        assert acoustic.resonance_frequencies == [125.0, 250.0, 500.0]
        assert acoustic.overall_rating == 7.5

    def test_minimal_acoustic_analysis(self):
        acoustic = AcousticAnalysis()
        assert acoustic.predicted_stc is None
        assert acoustic.weak_points == []
        assert acoustic.resonance_frequencies == []


class TestStructuralAnalysis:
    """Test StructuralAnalysis model."""

    def test_structural_analysis(self):
        structural = StructuralAnalysis(
            stress_concentrations=[{"location": "corner", "max_stress": 150.0}],
            critical_loads=[{"case": "operating", "load": 1000.0}],
            safety_factors={"overall": 2.5, "critical": 2.0},
            deformation_analysis={"max_deflection": 0.1},
            fatigue_life_estimate=1000000,
            overall_rating=8.0,
        )

        assert len(structural.stress_concentrations) == 1
        assert structural.safety_factors["overall"] == 2.5
        assert structural.fatigue_life_estimate == 1000000
        assert structural.overall_rating == 8.0


class TestManufacturingAnalysis:
    """Test ManufacturingAnalysis model."""

    def test_manufacturing_analysis(self):
        manufacturing = ManufacturingAnalysis(
            cnc_feasibility=0.85,
            estimated_cost=150.0,
            machining_time=3.5,
            tool_access_issues=["Deep pocket", "Tight corner"],
            material_waste=20.0,
            setup_complexity="Medium",
            overall_rating=7.0,
        )

        assert manufacturing.cnc_feasibility == 0.85
        assert manufacturing.estimated_cost == 150.0
        assert len(manufacturing.tool_access_issues) == 2
        assert manufacturing.setup_complexity == "Medium"
        assert manufacturing.overall_rating == 7.0


class TestCADMetadata:
    """Test CADMetadata model."""

    def test_cad_metadata(self):
        metadata = CADMetadata(
            file_name="test_model.step",
            file_type=CADFileType.STEP,
            file_size=1024000,
            software_detected="SolidWorks",
            version="2023",
            units="mm",
            bounding_box={"min_x": 0, "max_x": 100, "min_y": 0, "max_y": 100, "min_z": 0, "max_z": 50},
        )

        assert metadata.file_name == "test_model.step"
        assert metadata.file_type == CADFileType.STEP
        assert metadata.file_size == 1024000
        assert metadata.software_detected == "SolidWorks"
        assert metadata.units == "mm"

    def test_minimal_metadata(self):
        metadata = CADMetadata(file_name="test.png", file_type=CADFileType.PNG, file_size=50000)

        assert metadata.file_name == "test.png"
        assert metadata.file_type == CADFileType.PNG
        assert metadata.software_detected is None
        assert metadata.units is None


class TestAnalysisConfig:
    """Test AnalysisConfig model."""

    def test_analysis_config(self):
        config = AnalysisConfig(
            analysis_type=AnalysisType.COMPREHENSIVE,
            confidence_threshold=0.8,
            output_format="html",
            include_visualization=True,
            focus_areas=["acoustic", "structural"],
            material_properties={"density": 7850, "youngs_modulus": 200000},
        )

        assert config.analysis_type == AnalysisType.COMPREHENSIVE
        assert config.confidence_threshold == 0.8
        assert config.output_format == "html"
        assert config.include_visualization is True
        assert "acoustic" in config.focus_areas

    def test_default_config(self):
        config = AnalysisConfig()
        assert config.analysis_type == AnalysisType.COMPREHENSIVE
        assert config.confidence_threshold == 0.7
        assert config.output_format == "json"
        assert config.include_visualization is True


class TestAnalysisResult:
    """Test AnalysisResult model."""

    def test_analysis_result(self):
        metadata = CADMetadata(file_name="test.step", file_type=CADFileType.STEP, file_size=1000000)

        config = AnalysisConfig(analysis_type=AnalysisType.COMPREHENSIVE, confidence_threshold=0.8)

        source = SourceAttribution(source="Test Model", confidence=0.9, reasoning="Test reasoning")

        recommendation = DesignRecommendation(
            type=RecommendationType.ACOUSTIC_IMPROVEMENT,
            title="Test Recommendation",
            description="Test description",
            severity=SeverityLevel.MEDIUM,
            confidence=0.8,
            sources=[source],
        )

        acoustic = AcousticAnalysis(predicted_stc=45.0, overall_rating=7.5)

        result = AnalysisResult(
            metadata=metadata,
            config=config,
            overall_score=0.8,
            confidence=0.85,
            recommendations=[recommendation],
            acoustic_analysis=acoustic,
            processing_time=5.2,
        )

        assert result.metadata.file_name == "test.step"
        assert result.overall_score == 0.8
        assert result.confidence == 0.85
        assert len(result.recommendations) == 1
        assert result.acoustic_analysis.predicted_stc == 45.0
        assert result.processing_time == 5.2

    def test_minimal_result(self):
        metadata = CADMetadata(file_name="test.png", file_type=CADFileType.PNG, file_size=50000)

        config = AnalysisConfig()

        result = AnalysisResult(metadata=metadata, config=config, overall_score=0.6, confidence=0.7)

        assert result.overall_score == 0.6
        assert result.confidence == 0.7
        assert result.recommendations == []
        assert result.acoustic_analysis is None
        assert result.structural_analysis is None
        assert result.manufacturing_analysis is None
