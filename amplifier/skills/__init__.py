"""
Amplifier Skills Framework

A minimal, token-efficient framework for context management and skill discovery.
Follows ruthless simplicity principles with progressive disclosure.
"""

from .context_management.context_compactor_skill import ContextCompactorSkill
from .discovery.skill_matcher import find_and_execute_skill
from .discovery.skill_matcher import get_skill_matcher
from .discovery.skill_matcher import get_skill_recommendations
from .skills_framework.skill_template import BaseSkill
from .skills_framework.skill_template import SkillContext
from .skills_framework.skill_template import SkillLevel
from .skills_framework.skill_template import SkillResult
from .skills_framework.skill_template import get_skill_registry
from .skills_framework.skill_template import register_skill

# Auto-register core skills
register_skill(ContextCompactorSkill())

__all__ = [
    "BaseSkill",
    "SkillContext",
    "SkillLevel",
    "SkillResult",
    "get_skill_registry",
    "register_skill",
    "get_skill_matcher",
    "find_and_execute_skill",
    "get_skill_recommendations",
    "ContextCompactorSkill",
]
