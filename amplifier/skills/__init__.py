"""
Amplifier Skills Framework

A minimal, token-efficient framework for context management and skill discovery.
Follows ruthless simplicity principles with progressive disclosure.
"""

# Temporarily comment out imports to test creation pipeline
# from .context_management.context_compactor_skill import ContextCompactorSkill
from .discovery.skill_matcher import find_and_execute_skill
from .discovery.skill_matcher import get_skill_matcher
from .discovery.skill_matcher import get_skill_recommendations
from .skills_framework.base_skill import BaseSkill, SkillContext, SkillResult, SkillMetrics, SkillStatus
from .skills_framework.skill_template import SkillLevel
from .skills_framework.skill_template import get_skill_registry
from .skills_framework.skill_template import register_skill

# Import meta-skills
from .meta_skills.intelligent_routing_design_specialist import get_intelligent_routing_specialist
from .meta_skills.skill_testing_validation_specialist import get_skill_testing_validation_specialist

# Import core technology skills
from .core_technology.vite_expert import ViteExpertSkill
from .core_technology.typescript_expert import TypeScriptExpertSkill
from .core_technology.database_design_expert import DatabaseDesignExpertSkill
from .core_technology.nodejs_expert import NodeJSExpertSkill

# Import integration skills
from .integration.full_stack_integration_expert import FullStackIntegrationExpertSkill
from .integration.api_design_expert import ApiDesignExpertSkill
from .integration.graphql_expert import GraphQLExpertSkill

# Auto-register core skills
register_skill(ViteExpertSkill())
register_skill(TypeScriptExpertSkill())
register_skill(DatabaseDesignExpertSkill())
register_skill(NodeJSExpertSkill())

# Auto-register integration skills (optimized with Agent Lightning)
register_skill(FullStackIntegrationExpertSkill())
register_skill(ApiDesignExpertSkill())
register_skill(GraphQLExpertSkill())

# Temporarily comment out auto-registration
# register_skill(ContextCompactorSkill())

__all__ = [
    "BaseSkill",
    "SkillContext",
    "SkillResult",
    "SkillMetrics",
    "SkillStatus",
    "SkillLevel",
    "get_skill_registry",
    "register_skill",
    "get_skill_matcher",
    "find_and_execute_skill",
    "get_skill_recommendations",
    "get_intelligent_routing_specialist",
    "get_skill_testing_validation_specialist",
    "ViteExpertSkill",
    "TypeScriptExpertSkill",
    "DatabaseDesignExpertSkill",
    "NodeJSExpertSkill",
    "FullStackIntegrationExpertSkill",
    "ApiDesignExpertSkill",
    "GraphQLExpertSkill",
    # "ContextCompactorSkill",
]
