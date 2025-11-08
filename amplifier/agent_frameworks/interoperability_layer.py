#!/usr/bin/env python3
"""
Cross-Framework Interoperability and Migration Patterns

Enables agent migration between frameworks, universal data exchange formats,
framework-agnostic performance monitoring, and hybrid agent architectures.

Following amplifier philosophy:
- Framework independence and portability
- Universal data formats for seamless migration
- Simple but powerful interoperability patterns
- Modular design allowing framework combinations
"""

import asyncio
import time
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


class MigrationDirection(Enum):
    """Direction of agent migration."""

    LANGCHAIN_TO_OPENAI = "langchain_to_openai_sdk"
    LANGCHAIN_TO_AUTOGEN = "langchain_to_autogen"
    LANGCHAIN_TO_CREWAI = "langchain_to_crewai"
    OPENAI_TO_LANGCHAIN = "openai_sdk_to_langchain"
    OPENAI_TO_AUTOGEN = "openai_sdk_to_autogen"
    OPENAI_TO_CREWAI = "openai_sdk_to_crewai"
    AUTOGEN_TO_LANGCHAIN = "autogen_to_langchain"
    AUTOGEN_TO_OPENAI = "autogen_to_openai_sdk"
    AUTOGEN_TO_CREWAI = "autogen_to_crewai"
    CREWAI_TO_LANGCHAIN = "crewai_to_langchain"
    CREWAI_TO_OPENAI = "crewai_to_openai_sdk"
    CREWAI_TO_AUTOGEN = "crewai_to_autogen"


class ArchitectureType(Enum):
    """Types of hybrid agent architectures."""

    SINGLE_FRAMEWORK = "single_framework"
    ENSEMBLE = "ensemble"  # Multiple frameworks vote
    PIPELINE = "pipeline"  # Sequential framework processing
    HIERARCHICAL = "hierarchical"  # Frameworks coordinate at different levels
    SPECIALIZED = "specialized"  # Each framework handles specific tasks
    FALLBACK = "fallback"  # Primary with backup frameworks


@dataclass
class AgentProfile:
    """Universal profile of an agent that can be migrated."""

    agent_id: str
    name: str
    description: str
    capabilities: list[str]
    current_framework: str
    performance_metrics: dict[str, float]
    configuration: dict[str, Any]
    training_history: list[dict[str, Any]] = field(default_factory=list)
    migration_history: list[dict[str, Any]] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_updated: datetime = field(default_factory=datetime.now)


@dataclass
class MigrationPlan:
    """Plan for migrating an agent between frameworks."""

    source_framework: str
    target_framework: str
    agent_profile: AgentProfile
    migration_steps: list[str]
    compatibility_issues: list[str] = field(default_factory=list)
    required_configurations: dict[str, Any] = field(default_factory=dict)
    estimated_success_rate: float = 0.0
    estimated_time: float = 0.0


@dataclass
class HybridArchitecture:
    """Configuration for hybrid agent architecture."""

    architecture_type: ArchitectureType
    participating_frameworks: list[str]
    coordination_strategy: str
    task_distribution: dict[str, list[str]] = field(default_factory=dict)
    fallback_order: list[str] = field(default_factory=list)
    voting_weights: dict[str, float] = field(default_factory=dict)
    performance_thresholds: dict[str, float] = field(default_factory=dict)


class UniversalDataFormat:
    """Universal data format for cross-framework communication."""

    @staticmethod
    def serialize_agent_profile(profile: AgentProfile) -> dict[str, Any]:
        """Serialize agent profile to universal format."""
        return {
            "agent_id": profile.agent_id,
            "name": profile.name,
            "description": profile.description,
            "capabilities": profile.capabilities,
            "current_framework": profile.current_framework,
            "performance_metrics": profile.performance_metrics,
            "configuration": profile.configuration,
            "training_history": profile.training_history,
            "migration_history": profile.migration_history,
            "created_at": profile.created_at.isoformat(),
            "last_updated": profile.last_updated.isoformat(),
            "version": "1.0",
        }

    @staticmethod
    def deserialize_agent_profile(data: dict[str, Any]) -> AgentProfile:
        """Deserialize agent profile from universal format."""
        return AgentProfile(
            agent_id=data["agent_id"],
            name=data["name"],
            description=data["description"],
            capabilities=data["capabilities"],
            current_framework=data["current_framework"],
            performance_metrics=data["performance_metrics"],
            configuration=data["configuration"],
            training_history=data.get("training_history", []),
            migration_history=data.get("migration_history", []),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_updated=datetime.fromisoformat(data["last_updated"]),
        )

    @staticmethod
    def serialize_interaction(interaction_data: dict[str, Any]) -> dict[str, Any]:
        """Serialize agent interaction to universal format."""
        return {
            "interaction_id": interaction_data.get("id", f"int_{int(time.time())}"),
            "agent_id": interaction_data.get("agent_id"),
            "framework": interaction_data.get("framework"),
            "input": interaction_data.get("input"),
            "output": interaction_data.get("output"),
            "metadata": interaction_data.get("metadata", {}),
            "performance": {
                "latency": interaction_data.get("latency", 0.0),
                "token_usage": interaction_data.get("token_usage", {}),
                "success": interaction_data.get("success", True),
            },
            "timestamp": interaction_data.get("timestamp", datetime.now().isoformat()),
            "version": "1.0",
        }


class MigrationAnalyzer:
    """Analyzes migration feasibility and creates migration plans."""

    def __init__(self):
        self.compatibility_matrix = self._build_compatibility_matrix()
        self.migration_templates = self._build_migration_templates()

    def _build_compatibility_matrix(self) -> dict[str, dict[str, float]]:
        """Build compatibility matrix between frameworks."""
        return {
            "langchain": {
                "openai_sdk": 0.9,  # High compatibility
                "autogen": 0.7,  # Medium compatibility
                "crewai": 0.6,  # Medium compatibility
            },
            "openai_sdk": {
                "langchain": 0.85,  # High compatibility
                "autogen": 0.65,  # Medium compatibility
                "crewai": 0.6,  # Medium compatibility
            },
            "autogen": {
                "langchain": 0.6,  # Medium compatibility
                "openai_sdk": 0.65,  # Medium compatibility
                "crewai": 0.8,  # High compatibility (both multi-agent)
            },
            "crewai": {
                "langchain": 0.55,  # Low-medium compatibility
                "openai_sdk": 0.6,  # Medium compatibility
                "autogen": 0.85,  # High compatibility
            },
        }

    def _build_migration_templates(self) -> dict[str, list[str]]:
        """Build migration step templates."""
        return {
            "langchain_to_openai_sdk": [
                "Extract LangChain agent configuration",
                "Convert chain structure to prompt templates",
                "Map LangChain tools to OpenAI function calling",
                "Adapt conversation memory format",
                "Test OpenAI integration",
                "Validate performance equivalence",
            ],
            "openai_sdk_to_langchain": [
                "Analyze OpenAI prompt patterns",
                "Create equivalent LangChain chains",
                "Map OpenAI functions to LangChain tools",
                "Implement LangChain memory",
                "Test LangChain execution",
                "Performance validation",
            ],
            "autogen_to_crewai": [
                "Extract AutoGen agent roles",
                "Convert to CrewAI role definitions",
                "Map conversation patterns to CrewAI tasks",
                "Adapt group chat coordination",
                "Test CrewAI crew execution",
                "Validate multi-agent coordination",
            ],
            "langchain_to_autogen": [
                "Identify single-agent vs multi-agent needs",
                "Convert LangChain chains to AutoGen agents",
                "Design AutoGen conversation flow",
                "Implement group chat manager",
                "Test multi-agent coordination",
                "Performance validation",
            ],
        }

    def analyze_migration_feasibility(self, profile: AgentProfile, target_framework: str) -> MigrationPlan:
        """Analyze feasibility of migrating agent to target framework."""
        source_framework = profile.current_framework
        compatibility_score = self.compatibility_matrix.get(source_framework, {}).get(target_framework, 0.0)

        # Check compatibility issues
        compatibility_issues = self._identify_compatibility_issues(profile, target_framework)

        # Get migration steps
        migration_key = f"{source_framework}_to_{target_framework}"
        migration_steps = self.migration_templates.get(
            migration_key,
            [
                f"Generic migration from {source_framework} to {target_framework}",
                "Configuration adaptation",
                "Testing and validation",
            ],
        )

        # Calculate success rate and time
        estimated_success_rate = compatibility_score * (1 - len(compatibility_issues) * 0.1)
        estimated_success_rate = max(0.1, min(0.95, estimated_success_rate))
        estimated_time = len(migration_steps) * 2.0  # 2 hours per step average

        # Determine required configurations
        required_configurations = self._get_required_configurations(profile, target_framework)

        return MigrationPlan(
            source_framework=source_framework,
            target_framework=target_framework,
            agent_profile=profile,
            migration_steps=migration_steps,
            compatibility_issues=compatibility_issues,
            required_configurations=required_configurations,
            estimated_success_rate=estimated_success_rate,
            estimated_time=estimated_time,
        )

    def _identify_compatibility_issues(self, profile: AgentProfile, target_framework: str) -> list[str]:
        """Identify potential compatibility issues."""
        issues = []

        # Check for framework-specific capabilities
        if target_framework == "autogen" and "multi_agent" not in profile.capabilities:
            issues.append("Target framework (AutoGen) optimized for multi-agent coordination")

        if target_framework == "crewai" and len(profile.capabilities) < 3:
            issues.append("CrewAI works best with specialized role capabilities")

        if target_framework == "langchain" and profile.configuration.get("requires_low_latency", False):
            issues.append("LangChain may have higher latency than direct API calls")

        # Check for complex tool usage
        if profile.configuration.get("complex_tool_chains", False) and target_framework == "openai_sdk":
            issues.append("OpenAI SDK has limited native tool chaining capabilities")

        return issues

    def _get_required_configurations(self, profile: AgentProfile, target_framework: str) -> dict[str, Any]:
        """Get required configurations for target framework."""
        base_config = {
            "model": profile.configuration.get("model", "gpt-3.5-turbo"),
            "temperature": profile.configuration.get("temperature", 0.1),
            "max_tokens": profile.configuration.get("max_tokens", 1000),
        }

        if target_framework == "langchain":
            base_config.update(
                {
                    "agent_type": "chat-conversational-react-description",
                    "memory": "conversation_buffer",
                    "verbose": True,
                }
            )
        elif target_framework == "autogen":
            base_config.update({"max_round": 10, "human_input_mode": "NEVER", "code_execution_config": False})
        elif target_framework == "crewai":
            base_config.update({"process": "hierarchical", "verbose": True, "manager_llm": base_config["model"]})

        return base_config


class FrameworkMigrator:
    """Handles actual migration of agents between frameworks."""

    def __init__(self, analyzer: MigrationAnalyzer):
        self.analyzer = analyzer
        self.migration_history: list[dict[str, Any]] = []

    async def migrate_agent(self, profile: AgentProfile, target_framework: str) -> tuple[bool, AgentProfile]:
        """Migrate agent to target framework."""
        logger.info(f"Starting migration of {profile.agent_id} from {profile.current_framework} to {target_framework}")

        # Analyze migration feasibility
        plan = self.analyzer.analyze_migration_feasibility(profile, target_framework)

        if plan.estimated_success_rate < 0.5:
            logger.warning(f"Migration has low success rate ({plan.estimated_success_rate:.2f})")
            # Continue anyway but with warning

        # Execute migration steps
        migrated_profile = await self._execute_migration_plan(plan)

        # Record migration
        migration_record = {
            "source_framework": plan.source_framework,
            "target_framework": plan.target_framework,
            "agent_id": profile.agent_id,
            "timestamp": datetime.now().isoformat(),
            "success": migrated_profile.current_framework == target_framework,
            "issues_encountered": plan.compatibility_issues,
            "migration_time": plan.estimated_time,
        }

        self.migration_history.append(migration_record)
        migrated_profile.migration_history.append(migration_record)

        logger.info(f"Migration completed: {migrated_profile.current_framework == target_framework}")
        return migrated_profile.current_framework == target_framework, migrated_profile

    async def _execute_migration_plan(self, plan: MigrationPlan) -> AgentProfile:
        """Execute the migration plan step by step."""
        profile = plan.agent_profile
        logger.info(f"Executing {len(plan.migration_steps)} migration steps")

        for i, step in enumerate(plan.migration_steps):
            logger.info(f"Step {i + 1}/{len(plan.migration_steps)}: {step}")

            try:
                # Simulate migration step execution
                await asyncio.sleep(0.1)  # Simulate processing time

                # Update profile based on migration step
                profile = self._apply_migration_step(profile, step, plan.target_framework)

            except Exception as e:
                logger.error(f"Migration step failed: {step} - {e}")
                # Continue with next step but note the issue

        # Update profile with new framework
        profile.current_framework = plan.target_framework
        profile.last_updated = datetime.now()
        profile.configuration.update(plan.required_configurations)

        return profile

    def _apply_migration_step(self, profile: AgentProfile, step: str, target_framework: str) -> AgentProfile:
        """Apply a single migration step to the profile."""
        # Simulate step application
        if "Extract" in step or "Analyze" in step:
            # Extraction steps don't modify profile
            pass
        elif "Convert" in step or "Map" in step:
            # Conversion steps modify configuration
            profile.configuration[f"migrated_to_{target_framework}"] = True
        elif "Test" in step or "Validate" in step:
            # Testing steps might update performance metrics
            profile.performance_metrics[f"{target_framework}_test_score"] = 0.85

        return profile

    def get_migration_statistics(self) -> dict[str, Any]:
        """Get migration statistics and success rates."""
        if not self.migration_history:
            return {"message": "No migrations performed yet"}

        total_migrations = len(self.migration_history)
        successful_migrations = sum(1 for m in self.migration_history if m["success"])

        framework_pairs = {}
        for migration in self.migration_history:
            pair = f"{migration['source_framework']} -> {migration['target_framework']}"
            if pair not in framework_pairs:
                framework_pairs[pair] = {"total": 0, "successful": 0}
            framework_pairs[pair]["total"] += 1
            if migration["success"]:
                framework_pairs[pair]["successful"] += 1

        return {
            "total_migrations": total_migrations,
            "successful_migrations": successful_migrations,
            "overall_success_rate": successful_migrations / total_migrations,
            "framework_pair_success_rates": {
                pair: data["successful"] / data["total"] for pair, data in framework_pairs.items()
            },
            "most_common_migrations": sorted(framework_pairs.items(), key=lambda x: x[1]["total"], reverse=True)[:5],
        }


class HybridOrchestrator:
    """Orchestrates hybrid agent architectures using multiple frameworks."""

    def __init__(self):
        self.framework_agents: dict[str, Any] = {}  # framework -> agent instances
        self.architectures: dict[str, HybridArchitecture] = {}
        self.performance_monitor = PerformanceMonitor()

    def register_framework_agent(self, framework: str, agent: Any):
        """Register an agent for a specific framework."""
        self.framework_agents[framework] = agent
        logger.info(f"Registered {framework} agent")

    def create_hybrid_architecture(self, name: str, architecture: HybridArchitecture) -> bool:
        """Create a hybrid architecture configuration."""
        # Verify all participating frameworks are available
        for framework in architecture.participating_frameworks:
            if framework not in self.framework_agents:
                logger.error(f"Framework {framework} not available for hybrid architecture")
                return False

        self.architectures[name] = architecture
        logger.info(f"Created hybrid architecture: {name} ({architecture.architecture_type.value})")
        return True

    async def execute_with_architecture(self, architecture_name: str, task: dict[str, Any]) -> dict[str, Any]:
        """Execute task using specified hybrid architecture."""
        if architecture_name not in self.architectures:
            return {"error": f"Architecture {architecture_name} not found"}

        architecture = self.architectures[architecture_name]

        start_time = time.time()
        result = None

        try:
            if architecture.architecture_type == ArchitectureType.ENSEMBLE:
                result = await self._execute_ensemble(architecture, task)
            elif architecture.architecture_type == ArchitectureType.PIPELINE:
                result = await self._execute_pipeline(architecture, task)
            elif architecture.architecture_type == ArchitectureType.HIERARCHICAL:
                result = await self._execute_hierarchical(architecture, task)
            elif architecture.architecture_type == ArchitectureType.SPECIALIZED:
                result = await self._execute_specialized(architecture, task)
            elif architecture.architecture_type == ArchitectureType.FALLBACK:
                result = await self._execute_fallback(architecture, task)
            else:
                result = await self._execute_single_framework(architecture, task)

            execution_time = time.time() - start_time
            result["execution_time"] = execution_time
            result["architecture"] = architecture_name

            # Record performance
            self.performance_monitor.record_execution(architecture_name, execution_time, result.get("success", False))

            return result

        except Exception as e:
            logger.error(f"Hybrid execution failed: {e}")
            return {
                "error": str(e),
                "execution_time": time.time() - start_time,
                "architecture": architecture_name,
                "success": False,
            }

    async def _execute_ensemble(self, architecture: HybridArchitecture, task: dict[str, Any]) -> dict[str, Any]:
        """Execute using ensemble voting across frameworks."""
        results = {}
        votes = []

        # Execute with all frameworks in parallel
        tasks = []
        for framework in architecture.participating_frameworks:
            agent = self.framework_agents[framework]
            # Mock execution - replace with actual agent execution
            task_coroutine = self._mock_agent_execution(agent, task, framework)
            tasks.append(task_coroutine)

        framework_results = await asyncio.gather(*tasks, return_exceptions=True)

        for framework, result in zip(architecture.participating_frameworks, framework_results, strict=False):
            if isinstance(result, Exception):
                results[framework] = {"error": str(result), "success": False}
            else:
                results[framework] = result
                # Vote based on success and confidence
                weight = architecture.voting_weights.get(framework, 1.0)
                confidence = result.get("confidence", 0.5)
                votes.append((framework, confidence * weight, result))

        # Select best result based on weighted voting
        if votes:
            best_vote = max(votes, key=lambda x: x[1])
            best_framework, best_score, best_result = best_vote

            return {
                "success": True,
                "result": best_result.get("output"),
                "selected_framework": best_framework,
                "confidence": best_score,
                "all_results": results,
                "voting_summary": [(f, s) for f, s, _ in votes],
            }

        return {"success": False, "error": "No successful executions", "all_results": results}

    async def _execute_pipeline(self, architecture: HybridArchitecture, task: dict[str, Any]) -> dict[str, Any]:
        """Execute using sequential pipeline of frameworks."""
        current_task = task
        pipeline_results = []

        # Define pipeline order (could be configurable)
        pipeline_order = architecture.participating_frameworks

        for i, framework in enumerate(pipeline_order):
            agent = self.framework_agents[framework]

            # Execute with current framework
            try:
                result = await self._mock_agent_execution(agent, current_task, framework)
                pipeline_results.append({"framework": framework, "result": result, "stage": i + 1})

                # Use output as input for next stage
                if result.get("output"):
                    current_task["input"] = result["output"]
                    current_task["previous_stages"] = pipeline_results

            except Exception as e:
                pipeline_results.append({"framework": framework, "error": str(e), "stage": i + 1})
                break  # Stop pipeline on failure

        return {
            "success": len(pipeline_results) > 0 and "error" not in pipeline_results[-1],
            "result": current_task.get("input"),
            "pipeline_results": pipeline_results,
            "stages_completed": len(pipeline_results),
        }

    async def _execute_hierarchical(self, architecture: HybridArchitecture, task: dict[str, Any]) -> dict[str, Any]:
        """Execute using hierarchical coordination."""
        # Simulate hierarchical execution
        coordinator = architecture.participating_frameworks[0]
        workers = architecture.participating_frameworks[1:]

        # Coordinator analyzes task and delegates
        coordinator_agent = self.framework_agents[coordinator]
        coordinator_result = await self._mock_agent_execution(coordinator_agent, task, coordinator)

        # Workers execute subtasks
        worker_results = {}
        if coordinator_result.get("output"):
            for worker in workers:
                worker_agent = self.framework_agents[worker]
                subtask = {"input": coordinator_result["output"], "role": worker, "coordinator": coordinator}
                worker_result = await self._mock_agent_execution(worker_agent, subtask, worker)
                worker_results[worker] = worker_result

        # Coordinator synthesizes results
        if worker_results:
            synthesis_task = {"input": task["input"], "worker_results": worker_results, "synthesis_request": True}
            final_result = await self._mock_agent_execution(coordinator_agent, synthesis_task, coordinator)
        else:
            final_result = coordinator_result

        return {
            "success": final_result.get("success", False),
            "result": final_result.get("output"),
            "coordinator_result": coordinator_result,
            "worker_results": worker_results,
            "final_result": final_result,
        }

    async def _execute_specialized(self, architecture: HybridArchitecture, task: dict[str, Any]) -> dict[str, Any]:
        """Execute using specialized frameworks for different task types."""
        task_type = task.get("type", "general")

        # Find specialized framework for this task type
        specialized_framework = None
        for framework, task_types in architecture.task_distribution.items():
            if task_type in task_types:
                specialized_framework = framework
                break

        if not specialized_framework:
            # Use first framework as default
            specialized_framework = architecture.participating_frameworks[0]

        agent = self.framework_agents[specialized_framework]
        result = await self._mock_agent_execution(agent, task, specialized_framework)

        return {
            "success": result.get("success", False),
            "result": result.get("output"),
            "selected_framework": specialized_framework,
            "specialization": task_type,
            "task_distribution": architecture.task_distribution,
        }

    async def _execute_fallback(self, architecture: HybridArchitecture, task: dict[str, Any]) -> dict[str, Any]:
        """Execute with fallback mechanisms."""
        last_error = None

        for framework in architecture.fallback_order:
            if framework not in self.framework_agents:
                continue

            agent = self.framework_agents[framework]
            try:
                result = await self._mock_agent_execution(agent, task, framework)

                if result.get("success", False):
                    return {
                        "success": True,
                        "result": result.get("output"),
                        "used_framework": framework,
                        "fallback_attempts": architecture.fallback_order.index(framework),
                    }
                last_error = result.get("error", "Execution failed")

            except Exception as e:
                last_error = str(e)
                continue

        return {
            "success": False,
            "error": last_error or "All fallback frameworks failed",
            "attempted_frameworks": architecture.fallback_order,
        }

    async def _execute_single_framework(self, architecture: HybridArchitecture, task: dict[str, Any]) -> dict[str, Any]:
        """Execute using single framework (baseline)."""
        framework = architecture.participating_frameworks[0]
        agent = self.framework_agents[framework]
        result = await self._mock_agent_execution(agent, task, framework)

        return {"success": result.get("success", False), "result": result.get("output"), "framework": framework}

    async def _mock_agent_execution(self, agent: Any, task: dict[str, Any], framework: str) -> dict[str, Any]:
        """Mock agent execution for testing."""
        # Simulate processing time
        await asyncio.sleep(0.1 + (0.05 * len(framework)))

        # Simulate framework-specific behavior
        success_rates = {"langchain": 0.85, "openai_sdk": 0.90, "autogen": 0.82, "crewai": 0.88}

        success = time.random() < success_rates.get(framework, 0.8)

        if success:
            return {
                "success": True,
                "output": f"Processed by {framework}: {task.get('input', 'No input')[:50]}...",
                "confidence": 0.7 + (0.2 * time.random()),
                "framework": framework,
                "metadata": {"processing_time": 0.1},
            }
        return {"success": False, "error": f"Mock error from {framework}", "framework": framework}

    def get_architecture_performance(self, architecture_name: str) -> dict[str, Any]:
        """Get performance statistics for an architecture."""
        return self.performance_monitor.get_architecture_stats(architecture_name)


class PerformanceMonitor:
    """Monitors performance across frameworks and architectures."""

    def __init__(self):
        self.execution_history: list[dict[str, Any]] = []
        self.framework_stats: dict[str, list[float]] = {}
        self.architecture_stats: dict[str, list[float]] = {}

    def record_execution(self, architecture_or_framework: str, execution_time: float, success: bool):
        """Record execution performance."""
        record = {
            "name": architecture_or_framework,
            "execution_time": execution_time,
            "success": success,
            "timestamp": datetime.now().isoformat(),
        }
        self.execution_history.append(record)

        # Update statistics
        if architecture_or_framework not in self.framework_stats:
            self.framework_stats[architecture_or_framework] = []
        self.framework_stats[architecture_or_framework].append(execution_time)

    def get_framework_stats(self, framework: str) -> dict[str, float]:
        """Get performance statistics for a framework."""
        if framework not in self.framework_stats or not self.framework_stats[framework]:
            return {"error": "No data available"}

        times = self.framework_stats[framework]
        successful_executions = [r for r in self.execution_history if r["name"] == framework and r["success"]]

        return {
            "total_executions": len(times),
            "successful_executions": len(successful_executions),
            "success_rate": len(successful_executions) / len(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
            "median_time": sorted(times)[len(times) // 2],
        }

    def get_architecture_stats(self, architecture: str) -> dict[str, float]:
        """Get performance statistics for an architecture."""
        architecture_executions = [r for r in self.execution_history if r.get("architecture") == architecture]

        if not architecture_executions:
            return {"error": "No data available"}

        times = [e["execution_time"] for e in architecture_executions]
        successful = [e for e in architecture_executions if e["success"]]

        return {
            "total_executions": len(times),
            "successful_executions": len(successful),
            "success_rate": len(successful) / len(times),
            "average_time": sum(times) / len(times),
            "min_time": min(times),
            "max_time": max(times),
        }

    def compare_frameworks(self) -> dict[str, Any]:
        """Compare performance across all frameworks."""
        comparison = {}
        for framework in self.framework_stats:
            comparison[framework] = self.get_framework_stats(framework)

        # Find best performing framework
        if comparison:
            best_framework = max(comparison.items(), key=lambda x: x[1].get("success_rate", 0))
            comparison["best_framework"] = {
                "name": best_framework[0],
                "success_rate": best_framework[1]["success_rate"],
                "average_time": best_framework[1]["average_time"],
            }

        return comparison


# Factory functions for easy usage


def create_mechanical_engineering_hybrid_architecture() -> HybridArchitecture:
    """Create hybrid architecture optimized for mechanical engineering."""
    return HybridArchitecture(
        architecture_type=ArchitectureType.SPECIALIZED,
        participating_frameworks=["langchain", "autogen", "crewai"],
        coordination_strategy="domain_specialized",
        task_distribution={
            "langchain": ["design_analysis", "technical_documentation"],
            "autogen": ["safety_review", "multi_agent_coordination"],
            "crewai": ["manufacturing_planning", "quality_assurance"],
        },
        fallback_order=["langchain", "crewai", "autogen"],
        voting_weights={"langchain": 0.3, "autogen": 0.4, "crewai": 0.3},
        performance_thresholds={"min_success_rate": 0.8, "max_execution_time": 5.0, "min_confidence": 0.7},
    )


async def demonstrate_framework_migration():
    """Demonstrate framework migration capabilities."""
    # Create analyzer and migrator
    analyzer = MigrationAnalyzer()
    migrator = FrameworkMigrator(analyzer)

    # Create sample agent profile
    profile = AgentProfile(
        agent_id="mech_engineer_001",
        name="Mechanical Design Engineer",
        description="Specialized agent for mechanical design analysis",
        capabilities=["design_analysis", "cad_review", "material_selection"],
        current_framework="langchain",
        performance_metrics={"accuracy": 0.85, "latency": 1.2},
        configuration={"model": "gpt-3.5-turbo", "temperature": 0.1, "max_tokens": 1000, "complex_tool_chains": True},
    )

    # Analyze migration to different frameworks
    for target_framework in ["openai_sdk", "autogen", "crewai"]:
        plan = analyzer.analyze_migration_feasibility(profile, target_framework)
        logger.info(f"Migration to {target_framework}: {plan.estimated_success_rate:.2f} success rate")

        # Perform migration
        success, migrated_profile = await migrator.migrate_agent(profile, target_framework)
        logger.info(f"Migration {success}: {migrated_profile.current_framework}")

    # Get migration statistics
    stats = migrator.get_migration_statistics()
    logger.info(f"Migration statistics: {stats}")


async def demonstrate_hybrid_architecture():
    """Demonstrate hybrid architecture execution."""
    # Create hybrid orchestrator
    orchestrator = HybridOrchestrator()

    # Register mock agents (in real implementation, these would be actual framework agents)
    for framework in ["langchain", "openai_sdk", "autogen", "crewai"]:
        orchestrator.register_framework_agent(framework, f"mock_{framework}_agent")

    # Create hybrid architecture
    architecture = create_mechanical_engineering_hybrid_architecture()
    orchestrator.create_hybrid_architecture("mech_engineering_hybrid", architecture)

    # Execute test task
    task = {
        "type": "design_analysis",
        "input": "Analyze this mechanical design for manufacturing feasibility",
        "priority": "high",
    }

    result = await orchestrator.execute_with_architecture("mech_engineering_hybrid", task)
    logger.info(f"Hybrid execution result: {result}")

    # Get performance statistics
    performance = orchestrator.get_architecture_performance("mech_engineering_hybrid")
    logger.info(f"Architecture performance: {performance}")
