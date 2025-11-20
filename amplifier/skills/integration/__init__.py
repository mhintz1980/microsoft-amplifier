"""
Lean-Agentic Integration Layer

Seamless integration between optimization components and the signature framework
with Agent Lightning optimization hooks and zero-hallucination enforcement.
"""

from .agent_lightning_hooks import AgentLightningHooks
from .agent_lightning_hooks import execute_with_lightning
from .agent_lightning_hooks import get_agent_lightning_hooks
from .meta_skill_coordinator import MetaSkillCoordinator
from .meta_skill_coordinator import get_meta_skill_coordinator
from .performance_monitoring import PerformanceMonitor
from .performance_monitoring import get_performance_dashboard
from .performance_monitoring import get_performance_monitor
from .resource_optimizer import ResourceOptimizer
from .resource_optimizer import execute_optimized_skill
from .resource_optimizer import get_resource_optimizer

# Legacy integration skills
try:
    from .api_design_expert import ApiDesignExpertSkill
    from .full_stack_integration_expert import FullStackIntegrationExpertSkill
    from .graphql_expert import GraphQLExpertSkill

    LEGACY_SKILLS = ["FullStackIntegrationExpertSkill", "ApiDesignExpertSkill", "GraphQLExpertSkill"]
except ImportError:
    LEGACY_SKILLS = []

__all__ = [
    "ResourceOptimizer",
    "get_resource_optimizer",
    "execute_optimized_skill",
    "MetaSkillCoordinator",
    "get_meta_skill_coordinator",
    "AgentLightningHooks",
    "get_agent_lightning_hooks",
    "execute_with_lightning",
    "PerformanceMonitor",
    "get_performance_monitor",
    "get_performance_dashboard",
] + LEGACY_SKILLS
