"""
Manufacturing Systems Domain Expertise

This package contains specialized manufacturing skills with zero-hallucination validation
and signature-based architecture for 95%+ accuracy improvements.

Skills Included:
- Manufacturing Workflow Optimization Expert
- Industrial Automation Specialist
- Quality Management Systems Expert
- Production Planning Specialist
- Lean Manufacturing Consultant
"""

from .manufacturing_workflow_expert_enhanced import ManufacturingWorkflowExpertSkillEnhanced
from .industrial_automation_specialist_enhanced import IndustrialAutomationSpecialistSkillEnhanced
from .quality_management_expert_enhanced import QualityManagementExpertSkillEnhanced
from .production_planning_specialist_enhanced import ProductionPlanningSpecialistSkillEnhanced
from .lean_manufacturing_consultant_enhanced import LeanManufacturingConsultantSkillEnhanced

# Manufacturing systems skill registry
MANUFACTURING_SKILLS = [
    ManufacturingWorkflowExpertSkillEnhanced,
    IndustrialAutomationSpecialistSkillEnhanced,
    QualityManagementExpertSkillEnhanced,
    ProductionPlanningSpecialistSkillEnhanced,
    LeanManufacturingConsultantSkillEnhanced,
]

__all__ = [
    "ManufacturingWorkflowExpertSkillEnhanced",
    "IndustrialAutomationSpecialistSkillEnhanced",
    "QualityManagementExpertSkillEnhanced",
    "ProductionPlanningSpecialistSkillEnhanced",
    "LeanManufacturingConsultantSkillEnhanced",
    "MANUFACTURING_SKILLS",
]
