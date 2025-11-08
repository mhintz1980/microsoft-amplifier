# CAD Design Review Agent

A specialized AI agent for analyzing SolidWorks designs of industrial dewatering pumps and sound-attenuating enclosures. Provides expert feedback on mechanical designs with focus on acoustic performance, structural integrity, and manufacturability.

## Purpose

This module analyzes CAD files and provides expert recommendations for:
- **Acoustic Performance**: Sound transmission loss prediction and weak point identification
- **Structural Analysis**: Stress point assessment and material requirements
- **Manufacturability**: CNC machining feasibility and cost optimization
- **Design Guidelines**: Industry best practices and standards compliance

## Inputs

- CAD files: STEP (.stp, .step), IGES (.igs, .iges), images (.png, .jpg, .svg)
- Design specifications and requirements
- Performance criteria and constraints

## Outputs

- Comprehensive design analysis report
- Confidence scores for each recommendation
- Source attribution for analysis decisions
- Actionable improvement suggestions

## Side Effects

- Creates analysis reports in output directory
- Trains machine learning models on design data
- Logs analysis decisions and confidence scores

## Dependencies

- Agent Lightning for ML training
- OpenCV for computer vision
- NumPy/SciPy for numerical analysis
- Plotly for visualization

## Installation

```bash
# Install dependencies
pip install -e ./scenarios/industrial_agents/cad_reviewer

# Install ML dependencies
pip install agent-lightning opencv-python numpy scipy plotly
```

## Quick Start

```bash
# Analyze a CAD design
python -m cad_reviewer analyze design.step --output report/

# Train on existing designs
python -m cad_reviewer train --data training_data/ --model models/

# Review multiple designs
python -m cad_reviewer batch-review designs/ --format step --output reports/
```

## Public Interface

```python
from cad_reviewer import CADReviewer, analyze_design

# Direct API usage
reviewer = CADReviewer()
result = reviewer.analyze_file("design.step")

# Simple analysis function
result = analyze_design("design.step", analysis_type="comprehensive")
```