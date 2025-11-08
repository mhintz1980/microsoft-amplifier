"""
Tests for CAD analyzer functionality.
"""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from ..core.analyzer import CADAnalyzer
from ..core.models import (
    AcousticAnalysis,
    AnalysisConfig,
    AnalysisType,
    CADFileType,
    CADMetadata,
    ManufacturingAnalysis,
    RecommendationType,
    SeverityLevel,
    StructuralAnalysis,
)


class TestCADAnalyzer:
    """Test CADAnalyzer class."""

    @pytest.fixture
    def analyzer(self):
        """Create a CADAnalyzer instance for testing."""
        return CADAnalyzer()

    @pytest.fixture
    def sample_config(self):
        """Create a sample analysis configuration."""
        return AnalysisConfig(analysis_type=AnalysisType.COMPREHENSIVE, confidence_threshold=0.7, output_format="json")

    @pytest.fixture
    def sample_cad_data(self):
        """Create sample CAD data for testing."""
        return {
            "image_data": np.random.randint(0, 255, (400, 400, 3), dtype=np.uint8),
            "geometry": {"surface_area": 10000.0, "volume": 5000.0, "bounding_box_volume": 6000.0},
            "material_properties": {"density": 7850, "youngs_modulus": 200000, "poisson_ratio": 0.3},
        }

    @pytest.fixture
    def sample_metadata(self):
        """Create sample CAD metadata."""
        return CADMetadata(
            file_name="test_model.step",
            file_type=CADFileType.STEP,
            file_size=1000000,
            software_detected="SolidWorks",
            units="mm",
        )

    @pytest.mark.asyncio
    async def test_analyze_file_success(self, analyzer, sample_config, sample_cad_data, sample_metadata):
        """Test successful file analysis."""
        with patch.object(analyzer.file_handler, "load_cad_file", new_callable=AsyncMock) as mock_load:
            with patch.object(analyzer, "_extract_metadata", new_callable=AsyncMock) as mock_extract:
                with patch.object(analyzer, "_analyze_acoustics", new_callable=AsyncMock) as mock_acoustic:
                    with patch.object(analyzer, "_analyze_structural", new_callable=AsyncMock) as mock_structural:
                        with patch.object(
                            analyzer, "_analyze_manufacturing", new_callable=AsyncMock
                        ) as mock_manufacturing:
                            with patch.object(
                                analyzer, "_calculate_overall_scores", new_callable=AsyncMock
                            ) as mock_scores:
                                # Setup mocks
                                mock_load.return_value = sample_cad_data
                                mock_extract.return_value = sample_metadata

                                mock_acoustic.return_value = AcousticAnalysis(
                                    predicted_stc=45.0, weak_points=["opening"], overall_rating=7.5
                                )

                                mock_structural.return_value = StructuralAnalysis(
                                    safety_factors={"overall": 2.5}, overall_rating=8.0
                                )

                                mock_manufacturing.return_value = ManufacturingAnalysis(
                                    cnc_feasibility=0.8, overall_rating=7.0
                                )

                                mock_scores.return_value = (0.8, 0.85)

                                # Execute analysis
                                result = await analyzer.analyze_file(Path("test.step"), sample_config)

                                # Verify results
                                assert result.metadata.file_name == "test_model.step"
                                assert result.overall_score == 0.8
                                assert result.confidence == 0.85
                                assert result.acoustic_analysis.predicted_stc == 45.0
                                assert result.structural_analysis.safety_factors["overall"] == 2.5
                                assert result.manufacturing_analysis.cnc_feasibility == 0.8

    @pytest.mark.asyncio
    async def test_extract_metadata(self, analyzer):
        """Test metadata extraction."""
        with patch.object(analyzer.file_handler, "detect_software", new_callable=AsyncMock) as mock_software:
            with patch.object(analyzer.file_handler, "detect_units", new_callable=AsyncMock) as mock_units:
                with patch.object(analyzer.file_handler, "extract_bounding_box", new_callable=AsyncMock) as mock_bbox:
                    mock_software.return_value = "SolidWorks"
                    mock_units.return_value = "mm"
                    mock_bbox.return_value = {"min_x": 0, "max_x": 100}

                    metadata = await analyzer._extract_metadata(Path("test.step"))

                    assert metadata.file_name == "test.step"
                    assert metadata.file_type == CADFileType.STEP
                    assert metadata.software_detected == "SolidWorks"
                    assert metadata.units == "mm"

    @pytest.mark.asyncio
    async def test_analyze_acoustics(self, analyzer, sample_cad_data):
        """Test acoustic analysis."""
        with patch.object(analyzer.vision_analyzer, "analyze_acoustic_features", new_callable=AsyncMock) as mock_vision:
            with patch.object(analyzer.ml_predictor, "predict_acoustic_performance", new_callable=AsyncMock) as mock_ml:
                with patch.object(analyzer, "_generate_acoustic_recommendations", new_callable=AsyncMock) as mock_recs:
                    with patch.object(analyzer, "_calculate_acoustic_rating", new_callable=AsyncMock) as mock_rating:
                        mock_vision.return_value = {
                            "weak_points": ["opening"],
                            "thin_sections": ["wall"],
                            "material_transitions": ["joint"],
                        }

                        mock_ml.return_value = {
                            "predicted_stc": 45.0,
                            "resonance_frequencies": [125.0, 250.0],
                            "transmission_loss_spectrum": {"125Hz": 25.0},
                        }

                        mock_recs.return_value = []
                        mock_rating.return_value = 7.5

                        result = await analyzer._analyze_acoustics(sample_cad_data, AnalysisConfig())

                        assert result.predicted_stc == 45.0
                        assert len(result.weak_points) == 1
                        assert result.resonance_frequencies == [125.0, 250.0]
                        assert result.overall_rating == 7.5

    @pytest.mark.asyncio
    async def test_analyze_structural(self, analyzer, sample_cad_data):
        """Test structural analysis."""
        with patch.object(
            analyzer.vision_analyzer, "analyze_structural_features", new_callable=AsyncMock
        ) as mock_vision:
            with patch.object(
                analyzer.ml_predictor, "predict_structural_performance", new_callable=AsyncMock
            ) as mock_ml:
                with patch.object(
                    analyzer, "_generate_structural_recommendations", new_callable=AsyncMock
                ) as mock_recs:
                    mock_vision.return_value = {
                        "stress_concentrations": [{"location": "corner", "max_stress": 150.0}],
                        "load_paths": [{"path": "main_load"}],
                        "connections": [{"location": "joint"}],
                    }

                    mock_ml.return_value = {
                        "safety_factors": {"overall": 2.5, "critical": 2.0},
                        "critical_loads": [{"case": "operating", "load": 1000.0}],
                        "deformation_analysis": {"max_deformation": 0.1},
                    }

                    mock_recs.return_value = []

                    result = await analyzer._analyze_structural(sample_cad_data, AnalysisConfig())

                    assert len(result.stress_concentrations) == 1
                    assert result.safety_factors["overall"] == 2.5
                    assert len(result.critical_loads) == 1

    @pytest.mark.asyncio
    async def test_analyze_manufacturing(self, analyzer, sample_cad_data):
        """Test manufacturing analysis."""
        with patch.object(
            analyzer.vision_analyzer, "analyze_manufacturing_features", new_callable=AsyncMock
        ) as mock_vision:
            with patch.object(analyzer.ml_predictor, "predict_manufacturability", new_callable=AsyncMock) as mock_ml:
                with patch.object(
                    analyzer, "_generate_manufacturing_recommendations", new_callable=AsyncMock
                ) as mock_recs:
                    with patch.object(analyzer, "_determine_setup_complexity", new_callable=AsyncMock) as mock_setup:
                        mock_vision.return_value = {
                            "tool_access_issues": ["deep_pocket"],
                            "complex_features": ["curved_surface"],
                            "tolerance_critical_areas": ["hole"],
                        }

                        mock_ml.return_value = {
                            "cnc_feasibility": 0.8,
                            "estimated_cost": 150.0,
                            "machining_time": 3.5,
                            "material_waste": 20.0,
                        }

                        mock_recs.return_value = []
                        mock_setup.return_value = "Medium"

                        result = await analyzer._analyze_manufacturing(sample_cad_data, AnalysisConfig())

                        assert result.cnc_feasibility == 0.8
                        assert result.estimated_cost == 150.0
                        assert len(result.tool_access_issues) == 1
                        assert result.setup_complexity == "Medium"

    @pytest.mark.asyncio
    async def test_calculate_overall_scores(self, analyzer):
        """Test overall score calculation."""
        acoustic = AcousticAnalysis(overall_rating=7.5)
        structural = StructuralAnalysis(overall_rating=8.0)
        manufacturing = ManufacturingAnalysis(overall_rating=7.0)

        score, confidence = await analyzer._calculate_overall_scores(acoustic, structural, manufacturing)

        assert score == (7.5 + 8.0 + 7.0) / 30.0  # Normalized to 0-1
        assert confidence == (0.8 + 0.9 + 0.85) / 3.0

    @pytest.mark.asyncio
    async def test_calculate_overall_scores_partial(self, analyzer):
        """Test overall score calculation with partial data."""
        acoustic = AcousticAnalysis(overall_rating=7.5)
        structural = None  # Missing structural analysis
        manufacturing = ManufacturingAnalysis(overall_rating=7.0)

        score, confidence = await analyzer._calculate_overall_scores(acoustic, structural, manufacturing)

        assert score == (7.5 + 7.0) / 20.0  # Only two analyses
        assert confidence == (0.8 + 0.85) / 2.0

    @pytest.mark.asyncio
    async def test_calculate_overall_scores_empty(self, analyzer):
        """Test overall score calculation with no data."""
        score, confidence = await analyzer._calculate_overall_scores(None, None, None)

        assert score == 0.0
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_generate_acoustic_recommendations(self, analyzer):
        """Test acoustic recommendation generation."""
        weak_points = ["opening at edge", "thin wall"]
        resonance_frequencies = [125.0, 250.0]
        predicted_stc = 40.0

        recommendations = await analyzer._generate_acoustic_recommendations(
            weak_points, resonance_frequencies, predicted_stc
        )

        assert len(recommendations) >= 1  # Should have at least one recommendation for low STC

        # Check for low STC recommendation
        low_stc_recs = [r for r in recommendations if "Low Sound Transmission Class" in r.title]
        assert len(low_stc_recs) == 1

        rec = low_stc_recs[0]
        assert rec.type == RecommendationType.ACOUSTIC_IMPROVEMENT
        assert rec.severity == SeverityLevel.HIGH
        assert rec.confidence > 0.8
        assert len(rec.sources) > 0

    @pytest.mark.asyncio
    async def test_generate_structural_recommendations(self, analyzer):
        """Test structural recommendation generation."""
        stress_concentrations = [{"location": "corner", "max_stress": 200.0, "yield_strength": 250.0}]
        safety_factors = {"main_component": 1.8}  # Below 2.0 threshold
        fatigue_life = 500000  # Below 1M threshold

        recommendations = await analyzer._generate_structural_recommendations(
            stress_concentrations, safety_factors, fatigue_life
        )

        # Should have recommendations for low safety factor and fatigue life
        assert len(recommendations) >= 2

        # Check for low safety factor recommendation
        safety_recs = [r for r in recommendations if "Low Safety Factor" in r.title]
        assert len(safety_recs) == 1

        rec = safety_recs[0]
        assert rec.type == RecommendationType.STRUCTURAL_REINFORCEMENT
        assert rec.severity == SeverityLevel.HIGH
        assert "main_component" in rec.description

    @pytest.mark.asyncio
    async def test_generate_manufacturing_recommendations(self, analyzer):
        """Test manufacturing recommendation generation."""
        cnc_feasibility = 0.6  # Below 0.7 threshold
        tool_access_issues = ["deep pocket requiring long tool"]
        material_waste = 35.0  # Above 30% threshold

        recommendations = await analyzer._generate_manufacturing_recommendations(
            cnc_feasibility, tool_access_issues, material_waste
        )

        # Should have recommendations for all three issues
        assert len(recommendations) >= 3

        # Check for low CNC feasibility recommendation
        cnc_recs = [r for r in recommendations if "Low CNC Machining Feasibility" in r.title]
        assert len(cnc_recs) == 1

        rec = cnc_recs[0]
        assert rec.type == RecommendationType.MANUFACTURING_OPTIMIZATION
        assert rec.severity == SeverityLevel.HIGH
        assert str(cnc_feasibility) in rec.description
