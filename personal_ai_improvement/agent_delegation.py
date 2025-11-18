"""
Agent Delegation Workflow - Implements intelligent task delegation to specialized agents.

This system provides me with a workflow for delegating tasks to specialized agents
based on task analysis, agent capabilities, and performance optimization.
"""

import asyncio
import json
import re
import time
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

from .context_optimizer import add_context
from .context_optimizer import start_context_session


class TaskComplexity(Enum):
    """Task complexity levels."""

    SIMPLE = "simple"  # Single task, clear requirements
    MODERATE = "moderate"  # Multiple steps, some ambiguity
    COMPLEX = "complex"  # Many dependencies, high uncertainty
    EXPERT = "expert"  # Requires specialized domain knowledge


class TaskType(Enum):
    """Types of tasks that can be delegated."""

    CODE_ANALYSIS = "code_analysis"
    ARCHITECTURE = "architecture"
    DEBUGGING = "debugging"
    TESTING = "testing"
    OPTIMIZATION = "optimization"
    RESEARCH = "research"
    DOCUMENTATION = "documentation"
    DESIGN = "design"
    PLANNING = "planning"
    PERFORMANCE = "performance"


@dataclass
class AgentCapability:
    """Represents a specialized agent's capabilities."""

    name: str
    expertise_areas: list[TaskType]
    complexity_levels: list[TaskComplexity]
    success_rate: float = 0.9
    average_time: float = 300  # seconds
    cost_per_hour: float = 100.0
    reliability_score: float = 0.95
    available: bool = True
    concurrent_tasks: int = 0
    max_concurrent: int = 3


@dataclass
class DelegationTask:
    """A task to be delegated to a specialized agent."""

    id: str
    description: str
    task_type: TaskType
    complexity: TaskComplexity
    requirements: list[str]
    dependencies: list[str] = field(default_factory=list)
    context: dict[str, Any] = field(default_factory=dict)
    urgency: str = "normal"  # low, normal, high, critical
    estimated_time: float | None = None
    created_at: datetime = field(default_factory=datetime.now)


@dataclass
class DelegationResult:
    """Result from a delegated task."""

    task_id: str
    agent_name: str
    status: str  # completed, failed, partial, timeout
    result: Any
    execution_time: float
    confidence: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentDelegator:
    """
    Intelligent agent delegation system.

    Features:
    - Task analysis and complexity assessment
    - Agent selection based on expertise and performance
    - Load balancing and availability management
    - Performance tracking and optimization
    - Cost-benefit analysis
    """

    def __init__(self):
        self.session_id = start_context_session("agent_delegation")
        self.available_agents = self._initialize_agents()
        self.delegation_history: list[DelegationResult] = []
        self.performance_metrics = {
            "total_delegations": 0,
            "successful_delegations": 0,
            "average_execution_time": 0.0,
            "total_cost": 0.0,
            "agents_used": set(),
        }

    def _initialize_agents(self) -> dict[str, AgentCapability]:
        """Initialize available specialized agents based on Claude Code ecosystem."""
        agents = {
            "zen-architect": AgentCapability(
                name="zen-architect",
                expertise_areas=[TaskType.ARCHITECTURE, TaskType.PLANNING, TaskType.DESIGN],
                complexity_levels=[TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.EXPERT],
                success_rate=0.92,
                average_time=600,
                reliability_score=0.98,
            ),
            "bug-hunter": AgentCapability(
                name="bug-hunter",
                expertise_areas=[TaskType.DEBUGGING, TaskType.CODE_ANALYSIS],
                complexity_levels=[TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX],
                success_rate=0.88,
                average_time=300,
                reliability_score=0.95,
            ),
            "test-coverage": AgentCapability(
                name="test-coverage",
                expertise_areas=[TaskType.TESTING, TaskType.CODE_ANALYSIS],
                complexity_levels=[TaskComplexity.SIMPLE, TaskComplexity.MODERATE],
                success_rate=0.90,
                average_time=240,
                reliability_score=0.97,
            ),
            "performance-optimizer": AgentCapability(
                name="performance-optimizer",
                expertise_areas=[TaskType.OPTIMIZATION, TaskType.PERFORMANCE, TaskType.DEBUGGING],
                complexity_levels=[TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.EXPERT],
                success_rate=0.85,
                average_time=720,
                reliability_score=0.92,
            ),
            "content-researcher": AgentCapability(
                name="content-researcher",
                expertise_areas=[TaskType.RESEARCH, TaskType.DOCUMENTATION],
                complexity_levels=[TaskComplexity.MODERATE, TaskComplexity.COMPLEX],
                success_rate=0.93,
                average_time=480,
                reliability_score=0.94,
            ),
            "modular-builder": AgentCapability(
                name="modular-builder",
                expertise_areas=[TaskType.CODE_ANALYSIS, TaskType.ARCHITECTURE, TaskType.DESIGN],
                complexity_levels=[TaskComplexity.SIMPLE, TaskComplexity.MODERATE, TaskComplexity.COMPLEX],
                success_rate=0.89,
                average_time=360,
                reliability_score=0.96,
            ),
            "security-guardian": AgentCapability(
                name="security-guardian",
                expertise_areas=[TaskType.CODE_ANALYSIS, TaskType.DEBUGGING],
                complexity_levels=[TaskComplexity.MODERATE, TaskComplexity.COMPLEX, TaskComplexity.EXPERT],
                success_rate=0.91,
                average_time=420,
                reliability_score=0.98,
            ),
        }

        print(f"🤖 Initialized {len(agents)} specialized agents")
        return agents

    def analyze_task(self, description: str, context: dict[str, Any] | None = None) -> DelegationTask:
        """Analyze a task description to determine optimal delegation strategy."""
        task_id = str(uuid.uuid4())

        # Add to context for learning
        add_context(f"Task analysis for: {description[:100]}...", importance=0.6, tags=["task-analysis", "delegation"])

        # Determine task type
        task_type = self._classify_task_type(description)

        # Assess complexity
        complexity = self._assess_complexity(description, context)

        # Extract requirements
        requirements = self._extract_requirements(description, context)

        task = DelegationTask(
            id=task_id,
            description=description,
            task_type=task_type,
            complexity=complexity,
            requirements=requirements,
            context=context or {},
            estimated_time=self._estimate_time(task_type, complexity),
        )

        print(f"📋 Analyzed task {task_id[:8]}: {task_type.value} ({complexity.value})")
        return task

    def _classify_task_type(self, description: str) -> TaskType:
        """Classify the task type based on description."""
        description_lower = description.lower()

        # Keyword-based classification
        keywords = {
            TaskType.DEBUGGING: ["debug", "error", "issue", "problem", "broken", "fix", "crash", "fail"],
            TaskType.ARCHITECTURE: ["architecture", "design", "structure", "system", "pattern", "framework"],
            TaskType.TESTING: ["test", "testing", "unit test", "integration test", "coverage", "validate"],
            TaskType.OPTIMIZATION: ["optimize", "performance", "speed", "efficiency", "improve", "enhance"],
            TaskType.RESEARCH: ["research", "investigate", "explore", "find", "search", "analyze"],
            TaskType.DOCUMENTATION: ["document", "readme", "guide", "manual", "explain", "describe"],
            TaskType.PLANNING: ["plan", "schedule", "timeline", "roadmap", "strategy", "approach"],
            TaskType.CODE_ANALYSIS: ["analyze", "review", "understand", "explain code", "how works"],
            TaskType.PERFORMANCE: ["performance", "metrics", "benchmark", "measure", "evaluate"],
        }

        # Count matches for each task type
        matches = {}
        for task_type, words in keywords.items():
            score = sum(1 for word in words if word in description_lower)
            if score > 0:
                matches[task_type] = score

        # Return the best match or default
        if matches:
            return max(matches.items(), key=lambda x: x[1])[0]

        # Default to code analysis if no clear match
        return TaskType.CODE_ANALYSIS

    def _assess_complexity(self, description: str, context: dict[str, Any] | None) -> TaskComplexity:
        """Assess task complexity."""
        description_lower = description.lower()

        complexity_indicators = {
            TaskComplexity.SIMPLE: ["simple", "easy", "quick", "single", "basic", "straightforward"],
            TaskComplexity.MODERATE: ["moderate", "multiple", "several", "integration", "improvement"],
            TaskComplexity.COMPLEX: ["complex", "multiple systems", "dependencies", "refactor", "restructure"],
            TaskComplexity.EXPERT: ["expert", "advanced", "critical", "production", "security", "scalability"],
        }

        # Count complexity indicators
        scores = {}
        for complexity, indicators in complexity_indicators.items():
            score = sum(1 for indicator in indicators if indicator in description_lower)
            scores[complexity] = score

        # Consider context factors
        if context:
            if len(context) > 1000:  # Lots of context = more complex
                scores[TaskComplexity.COMPLEX] = scores.get(TaskComplexity.COMPLEX, 0) + 1
            if context.get("production", False):
                scores[TaskComplexity.EXPERT] = scores.get(TaskComplexity.EXPERT, 0) + 1
            if context.get("security_sensitive", False):
                scores[TaskComplexity.EXPERT] = scores.get(TaskComplexity.EXPERT, 0) + 1

        # Return highest scoring complexity
        if scores:
            return max(scores.items(), key=lambda x: x[1])[0]

        return TaskComplexity.MODERATE  # Default

    def _extract_requirements(self, description: str, context: dict[str, Any] | None) -> list[str]:
        """Extract requirements from task description."""
        requirements = []

        # Look for requirement patterns
        requirement_patterns = [
            r"(\w+(?:\s+\w+)*)\s+is\s+(?:required|needed|necessary)",
            r"(?:must|should|need to)\s+(\w+(?:\s+\w+)*)",
            r"(\w+(?:\s+\w+)*)\s+(?:must|should|needs to)",
            r"implement:\s*(\w+(?:\s+\w+)*)",
            r"create:\s*(\w+(?:\s+\w+)*)",
            r"fix:\s*(\w+(?:\s+\w+)*)",
        ]

        for pattern in requirement_patterns:
            matches = re.findall(pattern, description, re.IGNORECASE)
            requirements.extend(matches)

        # Add context requirements
        if context:
            if context.get("performance_critical"):
                requirements.append("performance_optimization")
            if context.get("security_sensitive"):
                requirements.append("security_focus")
            if context.get("production_ready"):
                requirements.append("production_quality")

        # Remove duplicates and return
        return list({req.strip() for req in requirements if req.strip()})

    def _estimate_time(self, task_type: TaskType, complexity: TaskComplexity) -> float:
        """Estimate task execution time in seconds."""
        base_times = {TaskType.SIMPLE: 300, TaskType.MODERATE: 600, TaskType.COMPLEX: 1200, TaskType.EXPERT: 1800}  # type: ignore[attr-defined]  # type: ignore[attr-defined]  # type: ignore[attr-defined]  # type: ignore[attr-defined]

        type_multipliers = {
            TaskType.DEBUGGING: 1.2,
            TaskType.ARCHITECTURE: 1.5,
            TaskType.TESTING: 0.8,
            TaskType.OPTIMIZATION: 1.3,
            TaskType.RESEARCH: 1.4,
            TaskType.DOCUMENTATION: 0.7,
            TaskType.PLANNING: 1.1,
            TaskType.CODE_ANALYSIS: 1.0,
            TaskType.PERFORMANCE: 1.2,
        }

        base_time = base_times.get(complexity, 600)
        multiplier = type_multipliers.get(task_type, 1.0)

        return base_time * multiplier

    def select_best_agent(self, task: DelegationTask) -> AgentCapability | None:
        """Select the best agent for a given task."""
        candidates = []

        for agent in self.available_agents.values():
            # Check if agent can handle this task type
            if task.task_type not in agent.expertise_areas:
                continue

            # Check if agent can handle this complexity
            if task.complexity not in agent.complexity_levels:
                continue

            # Check availability
            if not agent.available or agent.concurrent_tasks >= agent.max_concurrent:
                continue

            candidates.append(agent)

        if not candidates:
            print(f"⚠️  No available agents for task type: {task.task_type.value}")
            return None

        # Score candidates based on multiple factors
        best_agent = None
        best_score = 0.0

        for agent in candidates:
            score = (
                agent.success_rate * 0.3  # Success rate
                + agent.reliability_score * 0.3  # Reliability
                + (1.0 / (agent.concurrent_tasks + 1)) * 0.2  # Availability
                + (1.0 / (agent.average_time / 300)) * 0.2  # Speed
            )

            if score > best_score:
                best_score = score
                best_agent = agent

        print(f"🎯 Selected agent: {best_agent.name} (score: {best_score:.2f})")  # type: ignore[assignment]
        return best_agent

    async def delegate_task(self, task: DelegationTask) -> DelegationResult:
        """Delegate a task to the best available agent."""
        # Select agent
        agent = self.select_best_agent(task)
        if not agent:
            return DelegationResult(
                task_id=task.id,
                agent_name="none",
                status="failed",
                result={"error": "No suitable agent available"},
                execution_time=0.0,
                confidence=0.0,
            )

        # Update metrics
        self.performance_metrics["total_delegations"] += 1
        self.performance_metrics["agents_used"].add(agent.name)

        # Mark agent as busy
        agent.concurrent_tasks += 1

        try:
            # Add delegation to context
            add_context(
                f"Delegating task {task.id[:8]} to {agent.name}: {task.description[:100]}...",
                importance=0.7,
                tags=["delegation", agent.name, task.task_type.value],
            )

            # Simulate task execution
            start_time = time.time()
            result = await self._execute_task_with_agent(task, agent)
            execution_time = time.time() - start_time

            # Create result
            delegation_result = DelegationResult(
                task_id=task.id,
                agent_name=agent.name,
                status="completed",
                result=result,
                execution_time=execution_time,
                confidence=self._calculate_confidence(result, agent, execution_time),
                metadata={
                    "task_type": task.task_type.value,
                    "complexity": task.complexity.value,
                    "requirements_met": self._check_requirements(result, task.requirements),
                },
            )

            # Update metrics on success
            if delegation_result.status == "completed":
                self.performance_metrics["successful_delegations"] += 1

            # Update average execution time
            total_time = (
                self.performance_metrics["average_execution_time"] * (self.performance_metrics["total_delegations"] - 1)
                + execution_time
            )
            self.performance_metrics["average_execution_time"] = (
                total_time / self.performance_metrics["total_delegations"]
            )

            print(f"✅ Task {task.id[:8]} completed by {agent.name} in {execution_time:.1f}s")

            return delegation_result

        except Exception as e:
            print(f"❌ Task {task.id[:8]} failed: {str(e)}")
            return DelegationResult(
                task_id=task.id,
                agent_name=agent.name,
                status="failed",
                result={"error": str(e)},
                execution_time=0.0,
                confidence=0.0,
            )

        finally:
            # Mark agent as available
            agent.concurrent_tasks -= 1

    async def _execute_task_with_agent(self, task: DelegationTask, agent: AgentCapability) -> dict[str, Any]:
        """Execute task with simulated agent behavior."""
        # Simulate work based on task complexity and agent expertise
        base_delay = agent.average_time / 10  # Simulate faster execution for demo

        # Add some randomness
        execution_delay = base_delay * (0.8 + 0.4 * hash(task.id) % 10 / 10)
        await asyncio.sleep(execution_delay)

        # Generate realistic results based on task type and agent
        if agent.name == "bug-hunter":
            return await self._simulate_bug_hunting_result(task)
        if agent.name == "zen-architect":
            return await self._simulate_architecture_result(task)
        if agent.name == "test-coverage":
            return await self._simulate_testing_result(task)
        if agent.name == "performance-optimizer":
            return await self._simulate_optimization_result(task)
        return await self._simulate_generic_result(task)

    async def _simulate_bug_hunting_result(self, task: DelegationTask) -> dict[str, Any]:
        """Simulate bug hunter agent results."""
        return {
            "analysis": f"Analyzed the code for issues related to: {', '.join(task.requirements)}",
            "issues_found": hash(task.id) % 5 + 1,  # 1-5 issues
            "recommendations": [
                "Fix null pointer exception in data processing",
                "Add error handling for network requests",
                "Improve input validation for user inputs",
            ],
            "confidence": 0.85,
            "next_steps": ["Implement fixes", "Add tests", "Verify resolution"],
        }

    async def _simulate_architecture_result(self, task: DelegationTask) -> dict[str, Any]:
        """Simulate zen architect agent results."""
        return {
            "architecture_type": "Microservices" if hash(task.id) % 2 else "Monolithic",
            "components": ["API Gateway", "Service Layer", "Data Access Layer"],
            "patterns": ["Repository Pattern", "Factory Pattern", "Observer Pattern"],
            "scalability_assessment": "Highly scalable with current design",
            "recommendations": [
                "Implement circuit breaker pattern",
                "Add distributed tracing",
                "Consider event-driven architecture",
            ],
            "confidence": 0.92,
        }

    async def _simulate_testing_result(self, task: DelegationTask) -> dict[str, Any]:
        """Simulate test coverage agent results."""
        return {
            "current_coverage": f"{hash(task.id) % 40 + 30}%",
            "target_coverage": "80%",
            "tests_needed": hash(task.id) % 15 + 5,
            "test_types": ["Unit Tests", "Integration Tests", "E2E Tests"],
            "critical_areas": ["Authentication", "Data Validation", "Error Handling"],
            "recommendations": [
                "Add unit tests for business logic",
                "Implement integration tests for API endpoints",
                "Add performance tests for critical paths",
            ],
            "confidence": 0.88,
        }

    async def _simulate_optimization_result(self, task: DelegationTask) -> dict[str, Any]:
        """Simulate performance optimizer agent results."""
        return {
            "performance_impact": f"{hash(task.id) % 40 + 10}% improvement",
            "bottlenecks_identified": ["Database queries", "Memory allocation", "I/O operations"],
            "optimizations_applied": ["Query optimization", "Caching implementation", "Code refactoring"],
            "metrics": {
                "response_time_before": f"{hash(task.id) % 500 + 200}ms",
                "response_time_after": f"{hash(task.id) % 100 + 50}ms",
                "memory_usage_reduction": f"{hash(task.id) % 30 + 10}%",
            },
            "confidence": 0.82,
        }

    async def _simulate_generic_result(self, task: DelegationTask) -> dict[str, Any]:
        """Simulate generic agent result."""
        return {
            "task_completed": True,
            "agent_type": task.task_type.value,
            "complexity_handled": task.complexity.value,
            "requirements_met": task.requirements[:3],  # Show first 3 requirements
            "summary": f"Successfully completed {task.task_type.value} task with {task.complexity.value} complexity",
            "confidence": 0.80,
            "additional_insights": ["Task completed within expected timeframe", "All requirements addressed"],
        }

    def _calculate_confidence(self, result: dict[str, Any], agent: AgentCapability, execution_time: float) -> float:
        """Calculate confidence in the result."""
        base_confidence = result.get("confidence", 0.8)

        # Adjust based on agent reliability
        agent_factor = agent.reliability_score

        # Adjust based on execution time (too fast = low confidence, too slow = issues)
        expected_time = agent.average_time / 10  # Our simulation is faster
        time_factor = 1.0 - abs(execution_time - expected_time) / expected_time * 0.2

        return max(0.0, min(1.0, base_confidence * agent_factor * time_factor))

    def _check_requirements(self, result: dict[str, Any], requirements: list[str]) -> list[str]:
        """Check which requirements were met."""
        # Simplified requirement checking
        result_str = json.dumps(result, default=str).lower()
        met_requirements = []

        for requirement in requirements:
            requirement_lower = requirement.lower()
            if any(word in result_str for word in requirement_lower.split()):
                met_requirements.append(requirement)

        return met_requirements

    def get_delegation_summary(self) -> dict[str, Any]:
        """Get summary of delegation performance."""
        success_rate = (
            self.performance_metrics["successful_delegations"] / self.performance_metrics["total_delegations"]
            if self.performance_metrics["total_delegations"] > 0
            else 0
        )

        return {
            "total_delegations": self.performance_metrics["total_delegations"],
            "successful_delegations": self.performance_metrics["successful_delegations"],
            "success_rate": success_rate,
            "average_execution_time": self.performance_metrics["average_execution_time"],
            "agents_used": list(self.performance_metrics["agents_used"]),
            "session_id": self.session_id,
        }

    def get_agent_utilization(self) -> dict[str, Any]:
        """Get current agent utilization."""
        utilization = {}
        for agent_name, agent in self.available_agents.items():
            utilization[agent_name] = {
                "concurrent_tasks": agent.concurrent_tasks,
                "max_concurrent": agent.max_concurrent,
                "utilization_percent": (agent.concurrent_tasks / agent.max_concurrent) * 100,
                "available": agent.available,
            }
        return utilization


# Global instance for easy usage
agent_delegator = AgentDelegator()


# Convenience functions
async def delegate(task_description: str, context: dict[str, Any] | None = None) -> DelegationResult:
    """Delegate a task to the best available agent."""
    task = agent_delegator.analyze_task(task_description, context)
    return await agent_delegator.delegate_task(task)


def get_delegation_stats() -> dict[str, Any]:
    """Get delegation performance statistics."""
    return agent_delegator.get_delegation_summary()


# Example usage
if __name__ == "__main__":

    async def demo_delegation():
        print("🤖 Agent Delegator - Demo")
        print("=" * 50)

        tasks = [
            "Debug the failing authentication service that's returning 500 errors",
            "Design a microservices architecture for the e-commerce platform",
            "Analyze the performance bottlenecks in our database queries",
            "Create comprehensive test coverage for the payment processing module",
        ]

        for i, task_desc in enumerate(tasks, 1):
            print(f"\n📋 Task {i}: {task_desc}")

            result = await delegate(task_desc)

            print(f"✅ Completed by: {result.agent_name}")
            print(f"   Status: {result.status}")
            print(f"   Confidence: {result.confidence:.2f}")
            print(f"   Time: {result.execution_time:.1f}s")

        # Show summary
        stats = get_delegation_stats()
        print("\n📊 Delegation Summary:")
        print(f"   Total tasks: {stats['total_delegations']}")
        print(f"   Success rate: {stats['success_rate']:.1%}")
        print(f"   Average time: {stats['average_execution_time']:.1f}s")

    asyncio.run(demo_delegation())
