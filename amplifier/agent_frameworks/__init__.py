# pyright: reportGeneralTypeIssues=false
# pyright: reportUnknownMemberType=false
# pyright: reportUnknownVariableType=false
# pyright: reportUnknownArgumentType=false
# pyright: reportUnknownParameterType=false

#!/usr/bin/env python3
"""
Agent Framework Integration Package

Provides seamless multi-framework integration for agent systems with
framework-agnostic interfaces, advanced data transformation, and
cross-framework interoperability.  # type: ignore

This package embodies the amplifier philosophy:  # type: ignore
- Ruthless simplicity in framework integration
- Modular "bricks & studs" design
- Framework independence and portability
- Clear contracts between layers

Core Components:  # type: ignore
- Multi-Framework Integration: Unified adapters for LangChain, OpenAI SDK, AutoGen, CrewAI  # type: ignore
- Advanced Adapters: Specialized data transformation for mechanical engineering domains  # type: ignore
- Framework-Agnostic Layer: Universal interfaces and task scheduling  # type: ignore
- Framework Optimizations: Training integration and performance optimization  # type: ignore
- Interoperability Layer: Cross-framework migration and hybrid architectures  # type: ignore
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

# FIXME: from .framework_optimizations import create_mechanical_engineering_optimization  # Factory functions  # Unknown symbol: create_mechanical_engineering_optimization
# FIXME: from .framework_optimizations import optimize_all_frameworks_for_mechanical_engineering  # Unknown symbol: optimize_all_frameworks_for_mechanical_engineering
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
__version__ = "1.0.0"  # type: ignore
__author__ = "Agent Framework Integration Team"  # type: ignore
__description__ = "Multi-framework agent integration with mechanical engineering domain expertise"  # type: ignore

# Public API
__all__ = [  # type: ignore
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


def get_available_frameworks() -> list[str]:  # type: ignore
    """Get list of available frameworks based on installed dependencies."""  # type: ignore
    frameworks = []  # type: ignore

    # Check LangChain
    try:  # type: ignore
        import langchain

        frameworks.append("langchain")  # type: ignore
    except ImportError:  # type: ignore
        pass

    # Check OpenAI SDK
    try:  # type: ignore
        import openai

        frameworks.append("openai_sdk")  # type: ignore
    except ImportError:  # type: ignore
        pass

    # Check AutoGen
    try:  # type: ignore
        import autogen

        frameworks.append("autogen")  # type: ignore
    except ImportError:  # type: ignore
        pass

    # Check CrewAI
    try:  # type: ignore
        import crewai

        frameworks.append("crewai")  # type: ignore
    except ImportError:  # type: ignore
        pass

    return frameworks  # type: ignore


def create_simple_agent_system(framework: str, task_type: str = "mechanical_engineering") -> UniversalAgentManager:  # type: ignore
    """
    Create a simple agent system for the specified framework.  # type: ignore

    This is the easiest entry point for getting started with multi-framework integration.  # type: ignore

    Args:  # type: ignore
        framework: The framework to use (langchain, openai_sdk, autogen, crewai)  # type: ignore
        task_type: The type of tasks the agent will handle  # type: ignore

    Returns:  # type: ignore
        Configured UniversalAgentManager ready to use

    Example:  # type: ignore
        >>> manager = create_simple_agent_system("langchain", "mechanical_engineering")  # type: ignore
        >>> await manager.start_system()  # type: ignore
        >>> result = await scheduler.execute_task(task)  # type: ignore
    """
    from amplifier.utils.logger import get_logger

    logger = get_logger(__name__)  # type: ignore

    available_frameworks = get_available_frameworks()  # type: ignore
    if framework not in available_frameworks:  # type: ignore
        logger.error(f"Framework {framework} not available. Install dependencies first.")  # type: ignore
        logger.info(f"Available frameworks: {available_frameworks}")  # type: ignore
        raise ImportError(f"Framework {framework} not available")

    # Create basic configuration
    config = {  # type: ignore
        "id": f"{framework}_simple_agent",  # type: ignore
        "framework": framework,  # type: ignore
        "model_config": {"model": "gpt-3.5-turbo", "temperature": 0.1},  # type: ignore
        "task_config": {"type": task_type, "capabilities": ["text_generation", "analysis"]},  # type: ignore
    }

    # Create and return manager
    manager = UniversalAgentManager()  # type: ignore

    async def setup_manager():  # type: ignore
        await manager.add_agent(framework, config)  # type: ignore
        await manager.start_system()  # type: ignore
        return manager  # type: ignore

    # In a real implementation, this would be handled differently
    # For now, return the manager with setup instructions
    logger.info(f"Agent system created for {framework}. Call setup_manager() to initialize.")  # type: ignore
    manager.setup_manager = setup_manager  # type: ignore[attribute]

    return manager  # type: ignore


# Convenience functions for quick start


async def quick_mechanical_engineering_agent(framework: str = "langchain") -> UniversalAgentManager:  # type: ignore
    """
    Quick start function for mechanical engineering agents.  # type: ignore

    Args:  # type: ignore
        framework: Framework to use (defaults to langchain)  # type: ignore

    Returns:  # type: ignore
        Initialized and ready-to-use agent manager
    """
    manager = create_simple_agent_system(framework, "mechanical_engineering")  # type: ignore
    await manager.setup_manager()  # type: ignore[attribute]
    return manager  # type: ignore


def analyze_framework_compatibility(source_framework: str, target_framework: str) -> dict:  # type: ignore
    """
    Analyze compatibility between two frameworks for migration.  # type: ignore

    Args:  # type: ignore
        source_framework: Current framework  # type: ignore
        target_framework: Target framework  # type: ignore

    Returns:  # type: ignore
        Compatibility analysis with success probability and recommendations
    """
    analyzer = MigrationAnalyzer()  # type: ignore

    # Create a sample profile for analysis
    sample_profile = AgentProfile(  # type: ignore
        agent_id="sample_agent",  # type: ignore
        name="Sample Agent",  # type: ignore
        description="Sample for compatibility analysis",  # type: ignore
        capabilities=["text_generation", "analysis"],  # type: ignore
        current_framework=source_framework,  # type: ignore
        performance_metrics={"accuracy": 0.8},  # type: ignore
        configuration={"model": "gpt-3.5-turbo"},  # type: ignore
    )

    plan = analyzer.analyze_migration_feasibility(sample_profile, target_framework)  # type: ignore

    return {  # type: ignore
        "compatibility_score": plan.estimated_success_rate,  # type: ignore
        "estimated_time": plan.estimated_time,  # type: ignore
        "compatibility_issues": plan.compatibility_issues,  # type: ignore
        "migration_steps": plan.migration_steps,  # type: ignore
        "recommendations": plan.required_configurations,  # type: ignore
    }


# Package information and help


def print_framework_status():  # type: ignore
    """Print status of available frameworks and dependencies."""  # type: ignore
    frameworks = get_available_frameworks()  # type: ignore

    print("=== Agent Framework Integration Status ===")  # type: ignore
    print(f"Available frameworks: {len(frameworks)}")  # type: ignore
    for fw in frameworks:  # type: ignore
        print(f"  ✓ {fw}")

    missing = ["langchain", "openai_sdk", "autogen", "crewai"]  # type: ignore
    missing = [fw for fw in missing if fw not in frameworks]  # type: ignore
    if missing:  # type: ignore
        print(f"Missing frameworks: {len(missing)}")  # type: ignore
        for fw in missing:  # type: ignore
            print(f"  ✗ {fw}")

    print("\n=== Installation Commands ===")  # type: ignore
    print("For missing frameworks, install with:")  # type: ignore
    print("  pip install langchain          # For LangChain")
    print("  pip install openai             # For OpenAI SDK")
    print("  pip install pyautogen          # For AutoGen")
    print("  pip install crewai             # For CrewAI")


def get_package_info() -> dict:  # type: ignore
    """Get comprehensive package information."""  # type: ignore
    return {  # type: ignore
        "name": "agent_frameworks",  # type: ignore
        "version": __version__,  # type: ignore
        "description": __description__,  # type: ignore
        "author": __author__,  # type: ignore
        "available_frameworks": get_available_frameworks(),  # type: ignore
        "supported_domains": ["mechanical_engineering", "manufacturing", "quality_assurance", "safety_engineering"],  # type: ignore
        "key_features": [  # type: ignore
            "Multi-framework integration",
            "Framework-agnostic interfaces",
            "Cross-framework migration",
            "Advanced data transformation",
            "Hybrid agent architectures",
            "Agent Lightning training integration",
        ],
        "quick_start": {  # type: ignore
            "simple_agent": "create_simple_agent_system(framework)",  # type: ignore
            "mechanical_engineering": "quick_mechanical_engineering_agent()",  # type: ignore
            "compatibility_check": "analyze_framework_compatibility(src, tgt)",  # type: ignore
        },
    }


# Initialize package with status check
if __name__ == "__main__":  # type: ignore
    print_framework_status()
