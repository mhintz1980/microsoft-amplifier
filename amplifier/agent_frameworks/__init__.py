#!/usr/bin/env python3
"""
Agent Framework Integration Package

Provides seamless multi-framework integration for agent systems with
framework-agnostic interfaces, advanced data transformation, and
cross-framework interoperability.

This package embodies the amplifier philosophy:
- Ruthless simplicity in framework integration
- Modular "bricks & studs" design
- Framework independence and portability
- Clear contracts between layers

Core Components:
- Multi-Framework Integration: Unified adapters for LangChain, OpenAI SDK, AutoGen, CrewAI
- Advanced Adapters: Specialized data transformation for mechanical engineering domains
- Framework-Agnostic Layer: Universal interfaces and task scheduling
- Framework Optimizations: Training integration and performance optimization
- Interoperability Layer: Cross-framework migration and hybrid architectures
"""

from .advanced_adapters import AdapterComposition  # Composition and pipelines
from .advanced_adapters import CADDataAdapter
from .advanced_adapters import DataFormat  # Data format and domain types
from .advanced_adapters import EngineeringData
from .advanced_adapters import EngineeringDataAdapter  # Specialized adapters
from .advanced_adapters import EngineeringDomain
from .advanced_adapters import EngineeringFeatures
from .advanced_adapters import TechnicalDocumentAdapter
from .advanced_adapters import TrainingDataPipeline
from .advanced_adapters import UIComponentAdapter
from .advanced_adapters import create_manufacturing_pipeline
from .advanced_adapters import create_mechanical_engineering_pipeline  # Factory functions
from .advanced_adapters import create_quality_assurance_pipeline
from .framework_agnostic_layer import AgentCapabilities
from .framework_agnostic_layer import CapabilityType  # Task and capability types
from .framework_agnostic_layer import FrameworkDetector  # Framework detection and management
from .framework_agnostic_layer import TaskDefinition
from .framework_agnostic_layer import TaskResult
from .framework_agnostic_layer import TaskType
from .framework_agnostic_layer import UniversalAgentInterface  # Universal interfaces
from .framework_agnostic_layer import UniversalAgentManager
from .framework_agnostic_layer import UniversalTaskScheduler
from .framework_agnostic_layer import UniversalTrainingInterface
from .framework_agnostic_layer import create_mechanical_engineering_tasks
from .framework_agnostic_layer import create_universal_system  # Factory functions
from .framework_optimizations import AutoGenOptimizer
from .framework_optimizations import CrewAIOptimizer
from .framework_optimizations import FrameworkOptimizer  # Framework optimizers
from .framework_optimizations import LangChainOptimizer
from .framework_optimizations import OpenAIOptimizer
from .framework_optimizations import OptimizationManager  # Management and analysis
from .framework_optimizations import OptimizationResult
from .framework_optimizations import OptimizationStrategy  # Optimization types and configurations
from .framework_optimizations import TrainingConfiguration
from .framework_optimizations import TrainingMetrics
from .framework_optimizations import TrainingMode
from .framework_optimizations import create_mechanical_engineering_optimization  # Factory functions
from .framework_optimizations import optimize_all_frameworks_for_mechanical_engineering
from .interoperability_layer import AgentProfile
from .interoperability_layer import ArchitectureType
from .interoperability_layer import FrameworkMigrator
from .interoperability_layer import HybridArchitecture
from .interoperability_layer import HybridOrchestrator
from .interoperability_layer import MigrationAnalyzer  # Migration and orchestration
from .interoperability_layer import MigrationDirection  # Migration and architecture types
from .interoperability_layer import MigrationPlan
from .interoperability_layer import PerformanceMonitor
from .interoperability_layer import UniversalDataFormat  # Universal data format
from .interoperability_layer import create_mechanical_engineering_hybrid_architecture  # Factory functions
from .interoperability_layer import demonstrate_framework_migration
from .interoperability_layer import demonstrate_hybrid_architecture
from .multi_framework_integration import AgentConfig
from .multi_framework_integration import AgentInteraction
from .multi_framework_integration import AgentMetrics
from .multi_framework_integration import AutoGenAdapter
from .multi_framework_integration import CrewAIAdapter
from .multi_framework_integration import FrameworkAdapter
from .multi_framework_integration import FrameworkRegistry  # Orchestration and management
from .multi_framework_integration import FrameworkType  # Core integration classes
from .multi_framework_integration import LangChainAdapter  # Framework adapters
from .multi_framework_integration import MultiFrameworkOrchestrator
from .multi_framework_integration import OpenAIAdapter
from .multi_framework_integration import create_mechanical_engineering_config  # Factory functions
from .multi_framework_integration import create_multi_framework_system

# Version and metadata
__version__ = "1.0.0"
__author__ = "Agent Framework Integration Team"
__description__ = "Multi-framework agent integration with mechanical engineering domain expertise"

# Public API
__all__ = [
    # Multi-framework integration
    "FrameworkType",
    "AgentConfig",
    "AgentInteraction",
    "AgentMetrics",
    "FrameworkAdapter",
    "LangChainAdapter",
    "OpenAIAdapter",
    "AutoGenAdapter",
    "CrewAIAdapter",
    "FrameworkRegistry",
    "MultiFrameworkOrchestrator",
    "create_mechanical_engineering_config",
    "create_multi_framework_system",
    # Advanced adapters
    "DataFormat",
    "EngineeringDomain",
    "EngineeringData",
    "EngineeringFeatures",
    "EngineeringDataAdapter",
    "CADDataAdapter",
    "TechnicalDocumentAdapter",
    "UIComponentAdapter",
    "AdapterComposition",
    "TrainingDataPipeline",
    "create_mechanical_engineering_pipeline",
    "create_quality_assurance_pipeline",
    "create_manufacturing_pipeline",
    # Framework-agnostic layer
    "CapabilityType",
    "TaskType",
    "TaskDefinition",
    "TaskResult",
    "AgentCapabilities",
    "UniversalAgentInterface",
    "UniversalTaskScheduler",
    "UniversalTrainingInterface",
    "FrameworkDetector",
    "UniversalAgentManager",
    "create_universal_system",
    "create_mechanical_engineering_tasks",
    # Framework optimizations
    "OptimizationStrategy",
    "TrainingMode",
    "TrainingConfiguration",
    "TrainingMetrics",
    "OptimizationResult",
    "FrameworkOptimizer",
    "LangChainOptimizer",
    "OpenAIOptimizer",
    "AutoGenOptimizer",
    "CrewAIOptimizer",
    "OptimizationManager",
    "create_mechanical_engineering_optimization",
    "optimize_all_frameworks_for_mechanical_engineering",
    # Interoperability
    "MigrationDirection",
    "ArchitectureType",
    "AgentProfile",
    "MigrationPlan",
    "HybridArchitecture",
    "UniversalDataFormat",
    "MigrationAnalyzer",
    "FrameworkMigrator",
    "HybridOrchestrator",
    "PerformanceMonitor",
    "create_mechanical_engineering_hybrid_architecture",
    "demonstrate_framework_migration",
    "demonstrate_hybrid_architecture",
]


def get_available_frameworks() -> list[str]:
    """Get list of available frameworks based on installed dependencies."""
    frameworks = []

    # Check LangChain
    try:
        import langchain

        frameworks.append("langchain")
    except ImportError:
        pass

    # Check OpenAI SDK
    try:
        import openai

        frameworks.append("openai_sdk")
    except ImportError:
        pass

    # Check AutoGen
    try:
        import autogen

        frameworks.append("autogen")
    except ImportError:
        pass

    # Check CrewAI
    try:
        import crewai

        frameworks.append("crewai")
    except ImportError:
        pass

    return frameworks


def create_simple_agent_system(framework: str, task_type: str = "mechanical_engineering") -> UniversalAgentManager:
    """
    Create a simple agent system for the specified framework.

    This is the easiest entry point for getting started with multi-framework integration.

    Args:
        framework: The framework to use (langchain, openai_sdk, autogen, crewai)
        task_type: The type of tasks the agent will handle

    Returns:
        Configured UniversalAgentManager ready to use

    Example:
        >>> manager = create_simple_agent_system("langchain", "mechanical_engineering")
        >>> await manager.start_system()
        >>> result = await scheduler.execute_task(task)
    """
    from amplifier.utils.logger import get_logger

    logger = get_logger(__name__)

    available_frameworks = get_available_frameworks()
    if framework not in available_frameworks:
        logger.error(f"Framework {framework} not available. Install dependencies first.")
        logger.info(f"Available frameworks: {available_frameworks}")
        raise ImportError(f"Framework {framework} not available")

    # Create basic configuration
    config = {
        "id": f"{framework}_simple_agent",
        "framework": framework,
        "model_config": {"model": "gpt-3.5-turbo", "temperature": 0.1},
        "task_config": {"type": task_type, "capabilities": ["text_generation", "analysis"]},
    }

    # Create and return manager
    manager = UniversalAgentManager()

    async def setup_manager():
        await manager.add_agent(framework, config)
        await manager.start_system()
        return manager

    # In a real implementation, this would be handled differently
    # For now, return the manager with setup instructions
    logger.info(f"Agent system created for {framework}. Call setup_manager() to initialize.")
    manager.setup_manager = setup_manager

    return manager


# Convenience functions for quick start


async def quick_mechanical_engineering_agent(framework: str = "langchain") -> UniversalAgentManager:
    """
    Quick start function for mechanical engineering agents.

    Args:
        framework: Framework to use (defaults to langchain)

    Returns:
        Initialized and ready-to-use agent manager
    """
    manager = create_simple_agent_system(framework, "mechanical_engineering")
    await manager.setup_manager()
    return manager


def analyze_framework_compatibility(source_framework: str, target_framework: str) -> dict:
    """
    Analyze compatibility between two frameworks for migration.

    Args:
        source_framework: Current framework
        target_framework: Target framework

    Returns:
        Compatibility analysis with success probability and recommendations
    """
    analyzer = MigrationAnalyzer()

    # Create a sample profile for analysis
    sample_profile = AgentProfile(
        agent_id="sample_agent",
        name="Sample Agent",
        description="Sample for compatibility analysis",
        capabilities=["text_generation", "analysis"],
        current_framework=source_framework,
        performance_metrics={"accuracy": 0.8},
        configuration={"model": "gpt-3.5-turbo"},
    )

    plan = analyzer.analyze_migration_feasibility(sample_profile, target_framework)

    return {
        "compatibility_score": plan.estimated_success_rate,
        "estimated_time": plan.estimated_time,
        "compatibility_issues": plan.compatibility_issues,
        "migration_steps": plan.migration_steps,
        "recommendations": plan.required_configurations,
    }


# Package information and help


def print_framework_status():
    """Print status of available frameworks and dependencies."""
    frameworks = get_available_frameworks()

    print("=== Agent Framework Integration Status ===")
    print(f"Available frameworks: {len(frameworks)}")
    for fw in frameworks:
        print(f"  ✓ {fw}")

    missing = ["langchain", "openai_sdk", "autogen", "crewai"]
    missing = [fw for fw in missing if fw not in frameworks]
    if missing:
        print(f"Missing frameworks: {len(missing)}")
        for fw in missing:
            print(f"  ✗ {fw}")

    print("\n=== Installation Commands ===")
    print("For missing frameworks, install with:")
    print("  pip install langchain          # For LangChain")
    print("  pip install openai             # For OpenAI SDK")
    print("  pip install pyautogen          # For AutoGen")
    print("  pip install crewai             # For CrewAI")


def get_package_info() -> dict:
    """Get comprehensive package information."""
    return {
        "name": "agent_frameworks",
        "version": __version__,
        "description": __description__,
        "author": __author__,
        "available_frameworks": get_available_frameworks(),
        "supported_domains": ["mechanical_engineering", "manufacturing", "quality_assurance", "safety_engineering"],
        "key_features": [
            "Multi-framework integration",
            "Framework-agnostic interfaces",
            "Cross-framework migration",
            "Advanced data transformation",
            "Hybrid agent architectures",
            "Agent Lightning training integration",
        ],
        "quick_start": {
            "simple_agent": "create_simple_agent_system(framework)",
            "mechanical_engineering": "quick_mechanical_engineering_agent()",
            "compatibility_check": "analyze_framework_compatibility(src, tgt)",
        },
    }


# Initialize package with status check
if __name__ == "__main__":
    print_framework_status()
