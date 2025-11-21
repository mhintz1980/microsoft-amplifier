"""
Amplifier Skills Framework

A comprehensive, type-safe framework for AI skill development with signature-based
execution, zero-hallucination enforcement, and BootstrapFewShot optimization.
"""

# Legacy skill system
try:
    from .skills_framework.base_skill import BaseSkill
    from .skills_framework.base_skill import SkillContext
    from .skills_framework.base_skill import SkillMetrics
    from .skills_framework.base_skill import SkillResult
    from .skills_framework.base_skill import SkillStatus
    from .skills_framework.skill_template import SkillLevel
    from .skills_framework.skill_template import get_skill_registry
    from .skills_framework.skill_template import register_skill
except ImportError:
    # Fallback for missing legacy framework
    BaseSkill = None
    SkillContext = None
    SkillResult = None
    SkillMetrics = None
    SkillStatus = None
    SkillLevel = None
    get_skill_registry = None
    register_skill = None

# Import domain expertise skills
try:
    from .domain_expertise.theme_factory_skill import ThemeFactorySkill
except ImportError:
    ThemeFactorySkill = None

# Import core technology skills with optional imports to handle circular dependencies
try:
    from .core_technology.database_design_expert import DatabaseDesignExpertSkill
except ImportError:
    DatabaseDesignExpertSkill = None

try:
    from .core_technology.nodejs_expert import NodeJSExpertSkill
except ImportError:
    NodeJSExpertSkill = None

try:
    from .core_technology.typescript_expert import TypeScriptExpertSkill
except ImportError:
    TypeScriptExpertSkill = None

try:
    from .core_technology.vite_expert import ViteExpertSkill
except ImportError:
    ViteExpertSkill = None

try:
    from .core_technology.performance_testing_expert import PerformanceTestingExpertSkill
except ImportError:
    PerformanceTestingExpertSkill = None

# Discovery system
try:
    from .discovery.skill_matcher import find_and_execute_skill
    from .discovery.skill_matcher import get_skill_matcher
    from .discovery.skill_matcher import get_skill_recommendations
except ImportError:
    find_and_execute_skill = None
    get_skill_matcher = None
    get_skill_recommendations = None

# Integration skills with optional imports
try:
    from .integration.api_design_expert import ApiDesignExpertSkill
except ImportError:
    ApiDesignExpertSkill = None

try:
    from .integration.full_stack_integration_expert import FullStackIntegrationExpertSkill
except ImportError:
    FullStackIntegrationExpertSkill = None

try:
    from .integration.graphql_expert import GraphQLExpertSkill
except ImportError:
    GraphQLExpertSkill = None

# Import meta-skills with optional imports - disabled due to circular dependencies
# try:
#     from .meta_skills.intelligent_routing_design_specialist import get_intelligent_routing_specialist
# except ImportError:
#     get_intelligent_routing_specialist = None

# try:
#     from .meta_skills.skill_testing_validation_specialist import get_skill_testing_validation_specialist
# except ImportError:
#     get_skill_testing_validation_specialist = None

# Set to None to avoid import issues
get_intelligent_routing_specialist = None
get_skill_testing_validation_specialist = None


def register_all_skills():
    """Register all available skills in the framework."""
    registered_count = 0

    try:
        # Auto-register domain expertise skills
        if ThemeFactorySkill is not None and register_skill is not None:
            register_skill(ThemeFactorySkill())
            registered_count += 1

        # Auto-register core technology skills
        if DatabaseDesignExpertSkill is not None and register_skill is not None:
            register_skill(DatabaseDesignExpertSkill())
            registered_count += 1

        if NodeJSExpertSkill is not None and register_skill is not None:
            register_skill(NodeJSExpertSkill())
            registered_count += 1

        if TypeScriptExpertSkill is not None and register_skill is not None:
            register_skill(TypeScriptExpertSkill())
            registered_count += 1

        if ViteExpertSkill is not None and register_skill is not None:
            register_skill(ViteExpertSkill())
            registered_count += 1

        if PerformanceTestingExpertSkill is not None and register_skill is not None:
            register_skill(PerformanceTestingExpertSkill())
            registered_count += 1

        # Auto-register integration skills
        if FullStackIntegrationExpertSkill is not None and register_skill is not None:
            register_skill(FullStackIntegrationExpertSkill())
            registered_count += 1

        if ApiDesignExpertSkill is not None and register_skill is not None:
            register_skill(ApiDesignExpertSkill())
            registered_count += 1

        if GraphQLExpertSkill is not None and register_skill is not None:
            register_skill(GraphQLExpertSkill())
            registered_count += 1

        return registered_count

    except Exception as e:
        import logging

        logging.getLogger(__name__).warning(f"Skill registration failed: {e}")
        return registered_count


# Signature framework imports
try:
    from .signature_framework import BootstrapOptimizer
    from .signature_framework import CompositionStrategy
    from .signature_framework import ConfidenceLevel
    from .signature_framework import ExecutionContext
except ImportError:
    BootstrapOptimizer = None
    CompositionStrategy = None
    ConfidenceLevel = None
    ExecutionContext = None

# Additional signature framework imports with fallbacks
try:
    from .signature_framework import LegacySkillWrapper
except ImportError:
    LegacySkillWrapper = None

try:
    from .signature_framework import MetaSkill  # Meta-skills
except ImportError:
    MetaSkill = None

try:
    from .signature_framework import MigrationStrategy
except ImportError:
    MigrationStrategy = None

try:
    from .signature_framework import OptimizationConfig
except ImportError:
    OptimizationConfig = None

try:
    from .signature_framework import PydanticContract
except ImportError:
    PydanticContract = None

try:
    from .signature_framework import RuntimeValidator  # Validation
except ImportError:
    RuntimeValidator = None

# New signature framework with fallbacks
try:
    from .signature_framework import SignatureSkill  # Core classes
except ImportError:
    SignatureSkill = None

try:
    from .signature_framework import SkillConfig
except ImportError:
    SkillConfig = None

try:
    from .signature_framework import SkillInterface
except ImportError:
    SkillInterface = None

try:
    from .signature_framework import SkillPriority
except ImportError:
    SkillPriority = None

try:
    from .signature_framework import SkillResult
except ImportError:
    SkillResult = None

try:
    from .signature_framework import SkillRole
except ImportError:
    SkillRole = None

try:
    from .signature_framework import T_Input  # Type system
except ImportError:
    T_Input = None

try:
    from .signature_framework import T_Output
except ImportError:
    T_Output = None
try:
    from .signature_framework import TypeContract
except ImportError:
    TypeContract = None

try:
    from .signature_framework import ValidationMode
except ImportError:
    ValidationMode = None

try:
    from .signature_framework import ValidationResult
except ImportError:
    ValidationResult = None

try:
    from .signature_framework import ZeroHallucinationEnforcer  # Zero-hallucination
except ImportError:
    ZeroHallucinationEnforcer = None
# Remaining signature framework imports with fallbacks
try:
    from .signature_framework import create_execution_context
except ImportError:
    create_execution_context = None

try:
    from .signature_framework import create_meta_skill
except ImportError:
    create_meta_skill = None

try:
    from .signature_framework import create_skill_component
except ImportError:
    create_skill_component = None

try:
    from .signature_framework import create_skill_config
except ImportError:
    create_skill_config = None

try:
    from .signature_framework import enforce_zero_hallucination  # decorators
except ImportError:
    enforce_zero_hallucination = None

try:
    from .signature_framework import get_bootstrap_optimizer
except ImportError:
    get_bootstrap_optimizer = None

try:
    from .signature_framework import get_framework_stats
except ImportError:
    get_framework_stats = None

try:
    from .signature_framework import get_runtime_validator
except ImportError:
    get_runtime_validator = None

try:
    from .signature_framework import get_zero_hallucination_enforcer
except ImportError:
    get_zero_hallucination_enforcer = None

try:
    from .signature_framework import initialize_framework
except ImportError:
    initialize_framework = None

try:
    from .signature_framework import migrate_skill
except ImportError:
    migrate_skill = None

try:
    from .signature_framework import signature_skill  # Utilities
except ImportError:
    signature_skill = None

try:
    from .signature_framework import validate_output
except ImportError:
    validate_output = None

try:
    from .signature_framework import wrap_legacy_skill
except ImportError:
    wrap_legacy_skill = None

# Initialize the framework
if initialize_framework is not None:
    try:
        initialize_framework()
    except Exception as e:
        # Framework initialization is optional for backward compatibility
        import logging

        logging.getLogger(__name__).warning(f"Framework initialization failed: {e}")

# Auto-register core skills (only if registry is available and skills are not None)
if register_skill is not None:
    try:
        # Auto-register domain expertise skills
        if ThemeFactorySkill is not None:
            register_skill(ThemeFactorySkill())

        if ViteExpertSkill is not None:
            register_skill(ViteExpertSkill())
        if TypeScriptExpertSkill is not None:
            register_skill(TypeScriptExpertSkill())
        if DatabaseDesignExpertSkill is not None:
            register_skill(DatabaseDesignExpertSkill())
        if NodeJSExpertSkill is not None:
            register_skill(NodeJSExpertSkill())
        if PerformanceTestingExpertSkill is not None:
            register_skill(PerformanceTestingExpertSkill())

        # Auto-register integration skills (optimized with Agent Lightning)
        if FullStackIntegrationExpertSkill is not None:
            register_skill(FullStackIntegrationExpertSkill())
        if ApiDesignExpertSkill is not None:
            register_skill(ApiDesignExpertSkill())
        if GraphQLExpertSkill is not None:
            register_skill(GraphQLExpertSkill())
    except Exception as e:
        # Registration errors should not break the module
        import logging

        logging.getLogger(__name__).warning(f"Skill registration failed: {e}")

# Build __all__ dynamically based on what's actually available
__all__ = [
    # New signature framework (always available)
    "SignatureSkill",
    "SkillInterface",
    "ExecutionContext",
    "SkillConfig",
    "T_Input",
    "T_Output",
    "TypeContract",
    "PydanticContract",
    "ValidationResult",
    "ValidationMode",
    "ConfidenceLevel",
    "SkillPriority",
    # Validation system
    "RuntimeValidator",
    "get_runtime_validator",
    "validate_output",
    # Bootstrap optimization
    "BootstrapOptimizer",
    "get_bootstrap_optimizer",
    "OptimizationConfig",
    # Zero-hallucination enforcement
    "ZeroHallucinationEnforcer",
    "get_zero_hallucination_enforcer",
    "enforce_zero_hallucination",
    # Integration layer
    "LegacySkillWrapper",
    "migrate_skill",
    "MigrationStrategy",
    "wrap_legacy_skill",
    # Meta-skills
    "MetaSkill",
    "create_meta_skill",
    "create_skill_component",
    "SkillRole",
    "CompositionStrategy",
    # Utilities and decorators
    "signature_skill",
    "create_skill_config",
    "create_execution_context",
    "initialize_framework",
    "get_framework_stats",
    # Discovery system
    "get_skill_matcher",
    "find_and_execute_skill",
    "get_skill_recommendations",
    # Registration system
    "register_all_skills",
]

# Add legacy components only if they're available
if BaseSkill is not None:
    __all__.extend(
        [
            "BaseSkill",
            "SkillContext",
            "SkillResult",
            "SkillMetrics",
            "SkillStatus",
            "SkillLevel",
            "get_skill_registry",
            "register_skill",
        ]
    )

# Add specific skills only if they're available
try:
    from .domain_expertise.theme_factory_skill import ThemeFactorySkill
    from .core_technology.database_design_expert import DatabaseDesignExpertSkill
    from .core_technology.nodejs_expert import NodeJSExpertSkill
    from .core_technology.typescript_expert import TypeScriptExpertSkill
    from .core_technology.vite_expert import ViteExpertSkill
    from .integration.api_design_expert import ApiDesignExpertSkill
    from .integration.full_stack_integration_expert import FullStackIntegrationExpertSkill
    from .integration.graphql_expert import GraphQLExpertSkill
    from .meta_skills.intelligent_routing_design_specialist import get_intelligent_routing_specialist
    from .meta_skills.skill_testing_validation_specialist import get_skill_testing_validation_specialist

    __all__.extend(
        [
            "get_intelligent_routing_specialist",
            "get_skill_testing_validation_specialist",
            "ThemeFactorySkill",
            "ViteExpertSkill",
            "TypeScriptExpertSkill",
            "DatabaseDesignExpertSkill",
            "NodeJSExpertSkill",
            "FullStackIntegrationExpertSkill",
            "ApiDesignExpertSkill",
            "GraphQLExpertSkill",
        ]
    )
except ImportError:
    # Skills not available, skip them
    pass
