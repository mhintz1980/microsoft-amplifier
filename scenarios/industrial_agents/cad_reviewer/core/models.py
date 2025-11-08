"""
Data models for CAD analysis results and configurations.
"""

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, validator


class AnalysisType(str, Enum):
    """Types of CAD analysis available."""

    COMPREHENSIVE = "comprehensive"
    ACOUSTIC = "acoustic"
    STRUCTURAL = "structural"
    MANUFACTURING = "manufacturing"


class SeverityLevel(str, Enum):
    """Severity levels for design recommendations."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class RecommendationType(str, Enum):
    """Types of design recommendations."""

    ACOUSTIC_IMPROVEMENT = "acoustic_improvement"
    STRUCTURAL_REINFORCEMENT = "structural_reinforcement"
    MANUFACTURING_OPTIMIZATION = "manufacturing_optimization"
    MATERIAL_CHANGE = "material_change"
    DESIGN_MODIFICATION = "design_modification"
    COMPLIANCE_ISSUE = "compliance_issue"


class CADFileType(str, Enum):
    """Supported CAD file types."""

    STEP = "step"
    IGES = "iges"
    PNG = "png"
    JPG = "jpg"
    SVG = "svg"


class SourceAttribution(BaseModel):
    """Source attribution for analysis decisions."""

    source: str = Field(..., description="Source of the analysis decision")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence in this source")
    reasoning: str = Field(..., description="Reasoning behind this decision")
    data_points: list[str] = Field(default_factory=list, description="Specific data points used")


class DesignRecommendation(BaseModel):
    """A design recommendation with confidence scoring."""

    type: RecommendationType = Field(..., description="Type of recommendation")
    title: str = Field(..., description="Brief title of the recommendation")
    description: str = Field(..., description="Detailed description of the recommendation")
    severity: SeverityLevel = Field(..., description="Severity level")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    location: str | None = Field(None, description="Location in CAD file if applicable")
    estimated_impact: str | None = Field(None, description="Estimated impact of the recommendation")
    implementation_cost: str | None = Field(None, description="Relative implementation cost")
    sources: list[SourceAttribution] = Field(default_factory=list, description="Sources for this recommendation")

    @validator("confidence")
    def validate_confidence(cls, v):
        if not 0.0 <= v <= 1.0:
            raise ValueError("Confidence must be between 0.0 and 1.0")
        return v


class AcousticAnalysis(BaseModel):
    """Results of acoustic performance analysis."""

    predicted_stc: float | None = Field(None, description="Predicted Sound Transmission Class")
    weak_points: list[str] = Field(default_factory=list, description="Identified acoustic weak points")
    resonance_frequencies: list[float] = Field(default_factory=list, description="Resonance frequencies in Hz")
    transmission_loss_spectrum: dict[str, float] | None = Field(None, description="TL values by frequency band")
    overall_rating: float | None = Field(None, ge=1.0, le=10.0, description="Overall acoustic rating (1-10)")


class StructuralAnalysis(BaseModel):
    """Results of structural integrity analysis."""

    stress_concentrations: list[dict[str, Any]] = Field(default_factory=list, description="Stress concentration points")
    critical_loads: list[dict[str, Any]] = Field(default_factory=list, description="Critical load conditions")
    safety_factors: dict[str, float] = Field(default_factory=dict, description="Safety factors by component")
    deformation_analysis: dict[str, float] | None = Field(None, description="Deformation under load")
    fatigue_life_estimate: float | None = Field(None, description="Estimated fatigue life in cycles")
    overall_rating: float | None = Field(None, ge=1.0, le=10.0, description="Overall structural rating (1-10)")


class ManufacturingAnalysis(BaseModel):
    """Results of manufacturability analysis."""

    cnc_feasibility: float = Field(..., ge=0.0, le=1.0, description="CNC machining feasibility score")
    estimated_cost: float | None = Field(None, description="Estimated manufacturing cost")
    machining_time: float | None = Field(None, description="Estimated machining time in hours")
    tool_access_issues: list[str] = Field(default_factory=list, description="Tool access problems")
    material_waste: float | None = Field(None, description="Estimated material waste percentage")
    setup_complexity: str | None = Field(None, description="Setup complexity rating")
    overall_rating: float | None = Field(None, ge=1.0, le=10.0, description="Overall manufacturing rating (1-10)")


class CADMetadata(BaseModel):
    """Metadata about the analyzed CAD file."""

    file_name: str = Field(..., description="Original file name")
    file_type: CADFileType = Field(..., description="File type")
    file_size: int = Field(..., description="File size in bytes")
    analysis_timestamp: datetime = Field(default_factory=datetime.now, description="When analysis was performed")
    software_detected: str | None = Field(None, description="CAD software that created the file")
    version: str | None = Field(None, description="File version or format version")
    units: str | None = Field(None, description="Units used in the CAD file")
    bounding_box: dict[str, float] | None = Field(None, description="3D bounding box dimensions")


class AnalysisConfig(BaseModel):
    """Configuration for CAD analysis."""

    analysis_type: AnalysisType = Field(AnalysisType.COMPREHENSIVE, description="Type of analysis to perform")
    confidence_threshold: float = Field(0.7, ge=0.0, le=1.0, description="Minimum confidence threshold")
    output_format: str = Field("json", description="Output format for results")
    include_visualization: bool = Field(True, description="Include visual analysis outputs")
    focus_areas: list[str] = Field(default_factory=list, description="Specific areas to focus on")
    material_properties: dict[str, Any] | None = Field(None, description="Material properties if known")
    operating_conditions: dict[str, Any] | None = Field(None, description="Operating conditions")


class AnalysisResult(BaseModel):
    """Complete result of CAD analysis."""

    metadata: CADMetadata = Field(..., description="File metadata")
    config: AnalysisConfig = Field(..., description="Analysis configuration used")
    overall_score: float = Field(..., ge=0.0, le=1.0, description="Overall design quality score")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Overall confidence in analysis")
    recommendations: list[DesignRecommendation] = Field(default_factory=list, description="Design recommendations")
    acoustic_analysis: AcousticAnalysis | None = Field(None, description="Acoustic performance results")
    structural_analysis: StructuralAnalysis | None = Field(None, description="Structural analysis results")
    manufacturing_analysis: ManufacturingAnalysis | None = Field(None, description="Manufacturing analysis results")
    processing_time: float | None = Field(None, description="Analysis processing time in seconds")
    error_log: list[str] = Field(default_factory=list, description="Any errors encountered during analysis")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}


class TrainingData(BaseModel):
    """Training data sample for ML models."""

    cad_file_path: str = Field(..., description="Path to CAD file")
    expert_rating: float = Field(..., ge=0.0, le=1.0, description="Expert rating of design quality")
    expert_recommendations: list[DesignRecommendation] = Field(..., description="Expert recommendations")
    acoustic_data: AcousticAnalysis | None = Field(None, description="Acoustic test data if available")
    structural_data: StructuralAnalysis | None = Field(None, description="Structural test data if available")
    manufacturing_data: ManufacturingAnalysis | None = Field(None, description="Manufacturing data if available")
    tags: list[str] = Field(default_factory=list, description="Tags for categorization")
    notes: str | None = Field(None, description="Additional notes")


class ModelMetrics(BaseModel):
    """Model performance metrics."""

    accuracy: float = Field(..., ge=0.0, le=1.0, description="Model accuracy")
    precision: float = Field(..., ge=0.0, le=1.0, description="Model precision")
    recall: float = Field(..., ge=0.0, le=1.0, description="Model recall")
    f1_score: float = Field(..., ge=0.0, le=1.0, description="F1 score")
    loss: float = Field(..., description="Model loss")
    training_time: float | None = Field(None, description="Training time in seconds")
    validation_accuracy: float | None = Field(None, description="Validation accuracy")
    test_accuracy: float | None = Field(None, description="Test accuracy")


class BatchAnalysisSummary(BaseModel):
    """Summary of batch analysis results."""

    total_files: int = Field(..., description="Total files processed")
    successful_analyses: int = Field(..., description="Successfully analyzed files")
    failed_analyses: int = Field(..., description="Failed analyses")
    average_score: float = Field(..., ge=0.0, le=1.0, description="Average overall score")
    average_confidence: float = Field(..., ge=0.0, le=1.0, description="Average confidence")
    total_recommendations: int = Field(..., description="Total recommendations generated")
    processing_time: float = Field(..., description="Total processing time in seconds")
    results: list[AnalysisResult] = Field(default_factory=list, description="Individual analysis results")
