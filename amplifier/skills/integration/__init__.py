"""
Lean-Agentic Integration Layer

Seamless integration between optimization components and the signature framework
with Agent Lightning optimization hooks and zero-hallucination enforcement.
"""

import logging

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

# Skill Seekers Integration Components (NEW)
try:
    from .skill_seekers_integration import (
        SkillSeekersIntegrationSkill,
        TechnicalDataSource,
        SkillGenerationRequest,
        GeneratedSkill,
    )
    from .technical_data_pipeline import (
        TechnicalDataPipeline,
        PipelineConfig,
        ProcessingResult,
        PipelineReport,
        create_skill_from_documentation,
        create_skill_from_github_repo,
        create_skill_from_pdf,
    )
    from .ast_conflict_analyzer import (
        ASTAnalyzer,
        ConflictDetector,
        CodeElement,
        Conflict,
        ConflictType,
        ConflictSeverity,
    )
    from .pdf_ocr_processor import PDFProcessor, PDFPage, PDFAnalysisResult, ProcessingMode
    from .github_analyzer import GitHubAnalyzer, GitHubRepo, RepositoryAnalysis, AnalysisDepth, RepositoryType
    from .skill_packager import SkillPackager, SkillMetadata, PackageResult, SkillFormat, UploadStatus
    from .core_skills_integration import CoreSkillsIntegrator, SkillEnhancementRequest, EnhancedSkill, CoreSkillCategory
    from .virtual_environment_safety import (
        VirtualEnvironmentSafety,
        SafetyLevel,
        SecurityViolationType,
        ResourceLimits,
        SecurityViolation,
        ExecutionResult,
    )

    SKILL_SEEKERS_AVAILABLE = True
except ImportError as e:
    # Set all to None for graceful fallback
    SkillSeekersIntegrationSkill = None
    TechnicalDataSource = None
    SkillGenerationRequest = None
    GeneratedSkill = None
    TechnicalDataPipeline = None
    PipelineConfig = None
    ProcessingResult = None
    PipelineReport = None
    ASTAnalyzer = None
    ConflictDetector = None
    CodeElement = None
    Conflict = None
    ConflictType = None
    ConflictSeverity = None
    PDFProcessor = None
    PDFPage = None
    PDFAnalysisResult = None
    ProcessingMode = None
    GitHubAnalyzer = None
    GitHubRepo = None
    RepositoryAnalysis = None
    AnalysisDepth = None
    RepositoryType = None
    SkillPackager = None
    SkillMetadata = None
    PackageResult = None
    SkillFormat = None
    UploadStatus = None
    CoreSkillsIntegrator = None
    SkillEnhancementRequest = None
    EnhancedSkill = None
    CoreSkillCategory = None
    VirtualEnvironmentSafety = None
    SafetyLevel = None
    SecurityViolationType = None
    ResourceLimits = None
    SecurityViolation = None
    ExecutionResult = None
    SKILL_SEEKERS_AVAILABLE = False

# Convenience functions
create_skill_from_documentation = None
create_skill_from_github_repo = None
create_skill_from_pdf = None

if SKILL_SEEKERS_AVAILABLE:
    try:
        from .technical_data_pipeline import (
            create_skill_from_documentation,
            create_skill_from_github_repo,
            create_skill_from_pdf,
        )
    except ImportError:
        pass

__all__ = (
    [
        # Legacy components
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
    ]
    + LEGACY_SKILLS
    + [
        # Skill Seekers Integration (NEW)
        "SkillSeekersIntegrationSkill",
        "TechnicalDataSource",
        "SkillGenerationRequest",
        "GeneratedSkill",
        "TechnicalDataPipeline",
        "PipelineConfig",
        "ProcessingResult",
        "PipelineReport",
        "ASTAnalyzer",
        "ConflictDetector",
        "CodeElement",
        "Conflict",
        "ConflictType",
        "ConflictSeverity",
        "PDFProcessor",
        "PDFPage",
        "PDFAnalysisResult",
        "ProcessingMode",
        "GitHubAnalyzer",
        "GitHubRepo",
        "RepositoryAnalysis",
        "AnalysisDepth",
        "RepositoryType",
        "SkillPackager",
        "SkillMetadata",
        "PackageResult",
        "SkillFormat",
        "UploadStatus",
        "CoreSkillsIntegrator",
        "SkillEnhancementRequest",
        "EnhancedSkill",
        "CoreSkillCategory",
        "VirtualEnvironmentSafety",
        "SafetyLevel",
        "SecurityViolationType",
        "ResourceLimits",
        "SecurityViolation",
        "ExecutionResult",
        "SKILL_SEEKERS_AVAILABLE",
        "create_skill_from_documentation",
        "create_skill_from_github_repo",
        "create_skill_from_pdf",
    ]
)
