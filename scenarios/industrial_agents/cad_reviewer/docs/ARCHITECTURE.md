# CAD Reviewer Agent Architecture

## Overview

The CAD Reviewer Agent is a specialized AI system for analyzing SolidWorks designs of industrial dewatering pumps and sound-attenuating enclosures. It provides expert feedback on mechanical designs with focus on acoustic performance, structural integrity, and manufacturability.

## System Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI Interface │────│   Core Engine    │────│   Analysis      │
│   (main.py)     │    │   (reviewer.py)  │    │   Modules       │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                       │
                              ┌─────────────────────────────────────────┐
                              │            Analysis Components           │
                              ├─────────────────┬─────────────────┬─────────┤
                              │ Computer Vision │ Machine Learning│ Rule-   │
                              │   (cv/)         │   (ml/)         │ based  │
                              └─────────────────┴─────────────────┴─────────┘
                                                       │
                       ┌─────────────────────────────────────────────────────┐
                       │                  Utilities                         │
                       ├─────────────────┬─────────────────┬─────────────────┤
                       │ File Handler     │ Report Generator │ Logger          │
                       │ (file_handler.py)│(report_generator.py)│(logger.py)      │
                       └─────────────────┴─────────────────┴─────────────────┘
```

## Core Components

### 1. CLI Interface (`main.py`)
- **Purpose**: Command-line interface for user interaction
- **Commands**: `analyze`, `batch-review`, `train`, `validate`
- **Features**:
  - Single file analysis
  - Batch processing with parallel execution
  - ML model training and validation
  - Multiple output formats (JSON, HTML, PDF)

### 2. Core Engine (`core/`)
- **CADReviewer** (`reviewer.py`): Main orchestrator
  - Coordinates all analysis components
  - Handles batch processing
  - Manages report generation
  - Enhances recommendations with cross-references

- **CADAnalyzer** (`analyzer.py`): Analysis engine
  - Performs comprehensive CAD analysis
  - Coordinates vision, ML, and rule-based analysis
  - Calculates overall scores and confidence
  - Generates design recommendations

- **Models** (`models.py`): Data structures
  - Pydantic models for type safety
  - Analysis results and configurations
  - Source attribution and confidence scoring
  - Complete type annotations

### 3. Computer Vision (`cv/`)
- **CADVisionAnalyzer**: Image and geometric analysis
  - Acoustic feature detection (openings, thin sections)
  - Structural feature identification (stress points, load paths)
  - Manufacturing analysis (tool access, complexity)
  - OpenCV-based image processing

### 4. Machine Learning (`ml/`)
- **MLPredictor**: Inference engine
  - Agent Lightning integration
  - Mock implementations for development
  - Rule-based fallbacks
  - Feature extraction and prediction

- **ModelTrainer**: Training pipeline
  - Supervised learning on expert ratings
  - Model validation and metrics
  - Training data management
  - Performance tracking

### 5. Utilities (`utils/`)
- **FileHandler**: CAD file processing
  - STEP/IGES file parsing
  - Image loading and preprocessing
  - Software detection and metadata extraction
  - Format conversion support

- **ReportGenerator**: Output generation
  - HTML report generation
  - PDF export (placeholder)
  - Batch summary reports
  - JSON data export

- **Logger**: Logging system
  - Structured logging configuration
  - File and console output
  - Debug and error tracking

## Data Flow

```
CAD File → File Handler → CAD Analyzer → Vision + ML + Rules → Recommendations → Report
    ↓              ↓              ↓              ↓                    ↓           ↓
Metadata     Preprocessing   Feature       Analysis           Enhancement  Generation
Extraction     & Parsing     Extraction   Fusion             & Scoring   & Export
```

## Analysis Pipeline

### 1. File Processing
- Load CAD file (STEP, IGES, PNG, JPG)
- Extract metadata and geometric data
- Detect software and units
- Generate preview images

### 2. Feature Extraction
- **Computer Vision**: Edge detection, contour analysis, geometry extraction
- **ML Features**: Acoustic, structural, manufacturing feature vectors
- **Rule-based**: Standards compliance checks

### 3. Analysis Execution
- **Acoustic**: STC prediction, resonance analysis, weak point detection
- **Structural**: Safety factor analysis, stress concentration, fatigue life
- **Manufacturing**: CNC feasibility, tool access, cost estimation

### 4. Recommendation Generation
- Confidence scoring based on multiple sources
- Cross-referencing between analysis types
- Priority-based sorting (severity + confidence)
- Source attribution for transparency

### 5. Report Generation
- Comprehensive HTML reports
- JSON data export
- Batch analysis summaries
- Visual analytics and charts

## Machine Learning Integration

### Agent Lightning Integration
```python
# Training with Agent Lightning
metrics = await trainer.train(
    data_dir=data_dir,
    model_dir=model_dir,
    epochs=100,
    validation_split=0.2
)

# Prediction with trained models
prediction = await predictor.predict_acoustic_performance(cad_data)
```

### Mock Implementation
When Agent Lightning is unavailable, the system provides mock implementations that:
- Simulate realistic analysis results
- Maintain full functionality for development
- Provide consistent interfaces
- Generate reasonable confidence scores

### Training Pipeline
1. **Data Collection**: Expert-rated CAD designs
2. **Feature Engineering**: Geometric, material, and performance features
3. **Model Training**: Multi-task learning for different analysis types
4. **Validation**: Cross-validation and performance metrics
5. **Deployment**: Model packaging and versioning

## Confidence Scoring System

### Source Attribution
Each recommendation includes:
- **Source**: Analysis method (Vision, ML, Rules)
- **Confidence**: Method-specific confidence score
- **Reasoning**: Explanation of the analysis decision
- **Data Points**: Specific inputs used for the decision

### Overall Confidence Calculation
- Weighted average of method confidences
- Boosted by cross-validation between methods
- Adjusted for data quality and completeness
- Capped at 0.95 for safety margins

## Error Handling and Resilience

### Graceful Degradation
- Missing ML models → Rule-based fallbacks
- File parsing errors → Continue with available data
- Vision analysis failures → Use ML predictions only
- Network issues → Local processing only

### Error Recovery
- Retry logic for transient failures
- Partial result preservation
- Error logging and reporting
- User-friendly error messages

## Performance Considerations

### Parallel Processing
- Batch file analysis with configurable workers
- Independent parallel analysis modules
- Async I/O for file operations
- Memory-efficient streaming for large files

### Caching Strategy
- Feature extraction caching
- Model loading optimization
- Report template caching
- File system caching for repeated analyses

## Extensibility

### New Analysis Types
- Plugin architecture for new analysis modules
- Configurable analysis pipelines
- Extensible data models
- Custom recommendation types

### New File Formats
- Modular file handler system
- Format-specific parsers
- Automatic format detection
- Conversion pipeline support

## Security and Safety

### Input Validation
- File type validation
- Size limits and quotas
- Malicious file detection
- Safe file parsing

### Output Safety
- Confidence limits for critical recommendations
- Expert review requirements for high-impact changes
- Audit trail for all decisions
- Reversible recommendation application

This architecture enables robust, extensible CAD analysis with clear separation of concerns and comprehensive error handling.