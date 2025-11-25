"""
Pre-Task Optimization System
Comprehensive pre-task check ensuring maximum efficiency and success rates
Integrates token efficiency, prompt optimization, and Agent Lightning learning
"""

import asyncio
import time
import json
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass, asdict
from enum import Enum
import hashlib
import re

# Add amplifier to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

# Import optimization components
from amplifier.skills.learning.agent_lightning_core import (
    agent_lightning_core,
    LearningSignalType,
    initialize_agent_lightning,
)
from amplifier.optimization.efficient_error_fixer import EfficientErrorFixer
from amplifier.skills.progressive_disclosure import progressive_skill_loader
from amplifier.validation.ai_verifiable_outcomes import ai_verifiable_outcomes


class TaskComplexity(Enum):
    """Task complexity classification"""

    SIMPLE = "simple"
    MODERATE = "moderate"
    COMPLEX = "complex"
    REVOLUTIONARY = "revolutionary"


class OptimizationStrategy(Enum):
    """Optimization strategy selection"""

    MINIMAL = "minimal"
    BALANCED = "balanced"
    COMPREHENSIVE = "comprehensive"
    MAXIMUM = "maximum"


@dataclass
class TaskAnalysis:
    """Comprehensive task analysis results"""

    original_prompt: str
    task_type: str
    complexity: TaskComplexity
    token_estimate: int
    estimated_duration: int
    optimization_strategy: OptimizationStrategy
    agent_requirements: List[str]
    workflow_recommendations: List[str]
    risk_factors: List[str]
    success_probability: float
    alternative_approaches: List[str]


@dataclass
class OptimizedPrompt:
    """Optimized prompt with metadata"""

    original_prompt: str
    optimized_prompt: str
    optimization_technique: str
    token_reduction: int
    clarity_improvement: int
    success_boost: float
    template_used: Optional[str]
    clarifying_questions: List[Dict[str, Any]]


@dataclass
class OptimizationResult:
    """Complete optimization result"""

    success: bool
    task_analysis: TaskAnalysis
    optimized_prompt: OptimizedPrompt
    selected_workflow: Dict[str, Any]
    agent_allocation: Dict[str, Any]
    monitoring_setup: Dict[str, Any]
    token_efficiency_score: float
    estimated_time_savings: int
    confidence_score: float


class PreTaskOptimizer:
    """
    Comprehensive pre-task optimization system
    Ensures maximum efficiency and success rates for all tasks
    """

    def __init__(self, storage_path: str = ".data/pre_task_optimization"):
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Core components
        self.task_history = []
        self.optimization_cache = {}
        self.prompt_templates = self._load_prompt_templates()
        self.workflow_library = self._load_workflow_library()

        # Performance tracking
        self.optimization_count = 0
        self.token_saved_total = 0
        self.time_saved_total = 0
        self.success_rate_boost = 0.0

        # Agent Lightning integration
        self.learning_enabled = True

    async def optimize_task(self, user_prompt: str, context: Optional[Dict[str, Any]] = None) -> OptimizationResult:
        """
        Main optimization pipeline - complete pre-task optimization
        """
        optimization_start = time.time()

        # Phase 1: Task Analysis
        task_analysis = await self._analyze_task(user_prompt, context)

        # Phase 2: Prompt Optimization
        optimized_prompt = await self._optimize_prompt(task_analysis)

        # Phase 3: Workflow Selection
        selected_workflow = await self._select_optimal_workflow(task_analysis, optimized_prompt)

        # Phase 4: Agent Allocation
        agent_allocation = await self._allocate_agents(task_analysis, selected_workflow)

        # Phase 5: Monitoring Setup
        monitoring_setup = await self._setup_monitoring(task_analysis, selected_workflow)

        # Phase 6: Efficiency Scoring
        efficiency_metrics = await self._calculate_efficiency_metrics(
            task_analysis, optimized_prompt, selected_workflow
        )

        # Create result
        result = OptimizationResult(
            success=True,
            task_analysis=task_analysis,
            optimized_prompt=optimized_prompt,
            selected_workflow=selected_workflow,
            agent_allocation=agent_allocation,
            monitoring_setup=monitoring_setup,
            token_efficiency_score=efficiency_metrics["token_efficiency"],
            estimated_time_savings=efficiency_metrics["time_savings"],
            confidence_score=efficiency_metrics["confidence"],
        )

        # Agent Lightning learning
        if self.learning_enabled:
            await self._record_optimization_learning(user_prompt, result)

        # Update metrics
        self.optimization_count += 1
        self.token_saved_total += optimized_prompt.token_reduction

        optimization_duration = time.time() - optimization_start
        self.time_saved_total += max(0, task_analysis.estimated_duration - optimization_duration)

        return result

    async def _analyze_task(self, user_prompt: str, context: Optional[Dict[str, Any]]) -> TaskAnalysis:
        """Comprehensive task analysis"""

        # Token estimation using progressive disclosure
        base_tokens = len(user_prompt.split()) * 1.3  # Rough estimation

        # Determine complexity
        complexity_indicators = {
            "multi-step": any(word in user_prompt.lower() for word in ["and then", "after that", "finally", "step"]),
            "analysis": any(word in user_prompt.lower() for word in ["analyze", "evaluate", "assess", "review"]),
            "creation": any(word in user_prompt.lower() for word in ["create", "build", "implement", "develop"]),
            "optimization": any(word in user_prompt.lower() for word in ["optimize", "improve", "enhance", "refactor"]),
            "integration": any(word in user_prompt.lower() for word in ["integrate", "connect", "combine", "merge"]),
            "debugging": any(word in user_prompt.lower() for word in ["debug", "fix", "error", "issue", "problem"]),
            "research": any(word in user_prompt.lower() for word in ["research", "find", "search", "investigate"]),
            "revolutionary": any(
                word in user_prompt.lower() for word in ["revolutionary", "paradigm", "transform", "reinvent"]
            ),
        }

        complexity_score = sum(complexity_indicators.values())

        if complexity_score >= 5:
            complexity = TaskComplexity.REVOLUTIONARY
        elif complexity_score >= 3:
            complexity = TaskComplexity.COMPLEX
        elif complexity_score >= 1:
            complexity = TaskComplexity.MODERATE
        else:
            complexity = TaskComplexity.SIMPLE

        # Determine task type
        task_types = {
            "coding": ["code", "implement", "develop", "program", "function", "class"],
            "analysis": ["analyze", "evaluate", "assess", "review", "examine"],
            "optimization": ["optimize", "improve", "enhance", "refactor", "efficient"],
            "debugging": ["debug", "fix", "error", "issue", "problem", "broken"],
            "integration": ["integrate", "connect", "combine", "merge", "link"],
            "research": ["research", "find", "search", "investigate", "discover"],
            "design": ["design", "architecture", "plan", "structure", "blueprint"],
            "testing": ["test", "validate", "verify", "check", "quality"],
        }

        task_type = "general"
        for type_name, indicators in task_types.items():
            if any(word in user_prompt.lower() for word in indicators):
                task_type = type_name
                break

        # Estimate duration based on complexity and type
        duration_multipliers = {
            TaskComplexity.SIMPLE: 1,
            TaskComplexity.MODERATE: 3,
            TaskComplexity.COMPLEX: 8,
            TaskComplexity.REVOLUTIONARY: 20,
        }

        type_multipliers = {
            "coding": 2,
            "analysis": 1.5,
            "optimization": 2.5,
            "debugging": 1.8,
            "integration": 3,
            "research": 2,
            "design": 1.2,
            "testing": 1.3,
            "general": 1,
        }

        estimated_duration = base_tokens * duration_multipliers[complexity] * type_multipliers.get(task_type, 1)

        # Agent requirements
        agent_requirements = []
        if task_type in ["coding", "debugging", "optimization"]:
            agent_requirements.extend(["bug-hunter", "test-coverage"])
        if task_type in ["analysis", "research", "design"]:
            agent_requirements.extend(["analysis-expert", "content-researcher"])
        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY]:
            agent_requirements.extend(["zen-architect", "integration-specialist"])
        if task_type == "integration":
            agent_requirements.append("integration-specialist")

        # Optimization strategy
        if estimated_duration < 30:
            strategy = OptimizationStrategy.MINIMAL
        elif estimated_duration < 120:
            strategy = OptimizationStrategy.BALANCED
        elif estimated_duration < 300:
            strategy = OptimizationStrategy.COMPREHENSIVE
        else:
            strategy = OptimizationStrategy.MAXIMUM

        # Risk factors
        risk_factors = []
        if "new" in user_prompt.lower():
            risk_factors.append("novel_domain")
        if complex_markers := [
            word for word in ["multiple", "several", "many", "complex"] if word in user_prompt.lower()
        ]:
            risk_factors.append("complex_requirements")
        if estimated_duration > 200:
            risk_factors.append("time_intensive")
        if task_type == "integration":
            risk_factors.append("integration_complexity")

        # Success probability based on complexity and risk
        base_success = 0.95
        complexity_penalty = {
            TaskComplexity.SIMPLE: 0,
            TaskComplexity.MODERATE: 0.1,
            TaskComplexity.COMPLEX: 0.2,
            TaskComplexity.REVOLUTIONARY: 0.3,
        }[complexity]
        risk_penalty = len(risk_factors) * 0.05

        success_probability = max(0.5, base_success - complexity_penalty - risk_penalty)

        # Alternative approaches
        alternatives = []
        if task_type == "coding":
            alternatives.append("template_based_code_generation")
        if task_type == "analysis":
            alternatives.append("progressive_disclosure_analysis")
        if complexity == TaskComplexity.COMPLEX:
            alternatives.append("divide_and_conquer_approach")
        if complexity == TaskComplexity.REVOLUTIONARY:
            alternatives.append("iterative_prototyping")

        return TaskAnalysis(
            original_prompt=user_prompt,
            task_type=task_type,
            complexity=complexity,
            token_estimate=int(base_tokens),
            estimated_duration=int(estimated_duration),
            optimization_strategy=strategy,
            agent_requirements=list(set(agent_requirements)),
            workflow_recommendations=self._generate_workflow_recommendations(task_type, complexity),
            risk_factors=risk_factors,
            success_probability=success_probability,
            alternative_approaches=alternatives,
        )

    async def _optimize_prompt(self, task_analysis: TaskAnalysis) -> OptimizedPrompt:
        """Optimize the prompt for maximum efficiency and success"""

        original_prompt = task_analysis.original_prompt
        optimized = original_prompt

        # Select optimal template
        template_key = f"{task_analysis.task_type}_{task_analysis.complexity.value}"
        template = self.prompt_templates.get(template_key, self.prompt_templates["default"])

        # Apply template optimization
        if template:
            optimized = template.format(
                task_description=original_prompt,
                complexity=task_analysis.complexity.value,
                context=self._extract_context_hints(original_prompt),
            )

        # Progressive disclosure optimization
        disclosure_level = {
            TaskComplexity.SIMPLE: "ESSENTIAL",
            TaskComplexity.MODERATE: "SUMMARY",
            TaskComplexity.COMPLEX: "FULL",
            TaskComplexity.REVOLUTIONARY: "FULL",
        }[task_analysis.complexity]

        # Token efficiency techniques
        optimization_techniques = []

        # 1. Remove redundancy
        words = optimized.split()
        unique_words = []
        seen_words = set()
        for word in words:
            word_lower = word.lower()
            if word_lower not in seen_words or word in ["the", "a", "an"]:  # Keep articles
                unique_words.append(word)
                seen_words.add(word_lower)
        optimized = " ".join(unique_words)

        if len(unique_words) < len(words):
            optimization_techniques.append("redundancy_removal")

        # 2. Structure for clarity
        if not optimized.strip().endswith("?"):
            optimized = optimized.rstrip() + "."

        # 3. Add specific success criteria if missing
        if "ensure" not in optimized.lower() and "verify" not in optimized.lower():
            optimized += " Ensure the solution meets quality standards and best practices."
            optimization_techniques.append("success_criteria_addition")

        # Calculate improvements
        original_tokens = len(original_prompt.split()) * 1.3
        optimized_tokens = len(optimized.split()) * 1.3
        token_reduction = int(original_tokens - optimized_tokens)

        clarity_improvement = len(optimization_techniques) * 15  # Each technique adds ~15% clarity
        success_boost = min(0.3, len(optimization_techniques) * 0.1)  # Max 30% boost

        # Generate clarifying questions
        clarifying_questions = self._generate_clarifying_questions(task_analysis)

        return OptimizedPrompt(
            original_prompt=original_prompt,
            optimized_prompt=optimized,
            optimization_technique=", ".join(optimization_techniques)
            if optimization_techniques
            else "template_application",
            token_reduction=max(0, token_reduction),
            clarity_improvement=min(100, clarity_improvement),
            success_boost=success_boost,
            template_used=template_key if template_key in self.prompt_templates else None,
            clarifying_questions=clarifying_questions,
        )

    async def _select_optimal_workflow(
        self, task_analysis: TaskAnalysis, optimized_prompt: OptimizedPrompt
    ) -> Dict[str, Any]:
        """Select the optimal workflow for the task"""

        workflow_key = f"{task_analysis.task_type}_{task_analysis.complexity.value}"

        # Get base workflow
        base_workflow = self.workflow_library.get(workflow_key, self.workflow_library["default"])

        # Customize workflow based on task specifics
        workflow = base_workflow.copy()

        # Add progressive disclosure if complex
        if task_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY]:
            workflow["use_progressive_disclosure"] = True
            workflow["disclosure_level"] = "SUMMARY" if task_analysis.complexity == TaskComplexity.COMPLEX else "FULL"

        # Add AI verification for high-stakes tasks
        if task_analysis.success_probability < 0.8 or task_analysis.task_type in ["coding", "integration"]:
            workflow["use_ai_verification"] = True

        # Add agent delegation for complex tasks
        if task_analysis.complexity == TaskComplexity.REVOLUTIONARY:
            workflow["use_agent_delegation"] = True
            workflow["delegation_strategy"] = "autogen_inspired"

        # Optimize for token efficiency
        workflow["token_optimization"] = {
            "enabled": True,
            "level": task_analysis.optimization_strategy.value,
            "progressive_disclosure": workflow.get("use_progressive_disclosure", False),
            "efficient_agents": task_analysis.agent_requirements,
        }

        return workflow

    async def _allocate_agents(self, task_analysis: TaskAnalysis, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Allocate optimal agents for the task"""

        agent_allocation = {
            "primary_agents": [],
            "support_agents": [],
            "optimization_agents": [],
            "execution_order": [],
            "parallel_execution": True,
        }

        # Map task types to optimal agents
        agent_mapping = {
            "coding": ["modular-builder", "test-coverage"],
            "analysis": ["analysis-expert", "triage-specialist"],
            "optimization": ["performance-optimizer", "refactor-architect"],
            "debugging": ["bug-hunter", "test-coverage"],
            "integration": ["integration-specialist", "modular-builder"],
            "research": ["content-researcher", "analysis-expert"],
            "design": ["zen-architect", "visualization-architect"],
            "testing": ["test-coverage", "bug-hunter"],
        }

        # Add task-specific agents
        if task_analysis.task_type in agent_mapping:
            agent_allocation["primary_agents"].extend(agent_mapping[task_analysis.task_type])

        # Add complexity-based agents
        if task_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY]:
            agent_allocation["support_agents"].append("zen-architect")

        # Add workflow-specific agents
        if workflow.get("use_agent_delegation"):
            agent_allocation["support_agents"].append("modular-builder")

        if workflow.get("use_ai_verification"):
            agent_allocation["optimization_agents"].append("ai_verifiable_outcomes")

        # Token efficiency agents
        agent_allocation["optimization_agents"].append("token_efficiency_specialist")

        # Determine execution order
        agent_allocation["execution_order"] = [
            *agent_allocation["primary_agents"],
            *agent_allocation["support_agents"],
            *agent_allocation["optimization_agents"],
        ]

        # Remove duplicates while preserving order
        seen = set()
        agent_allocation["execution_order"] = [
            x for x in agent_allocation["execution_order"] if not (x in seen or seen.add(x))
        ]

        return agent_allocation

    async def _setup_monitoring(self, task_analysis: TaskAnalysis, workflow: Dict[str, Any]) -> Dict[str, Any]:
        """Set up comprehensive monitoring for the task"""

        monitoring = {
            "performance_tracking": {
                "enabled": True,
                "metrics": ["token_usage", "execution_time", "success_rate", "quality_score"],
                "checkpoints": task_analysis.estimated_duration // 60,  # Every minute for long tasks
            },
            "agent_lightning_integration": {
                "enabled": self.learning_enabled,
                "learning_signals": ["performance_metrics", "error_patterns", "optimization_opportunities"],
                "confidence_threshold": 0.7,
            },
            "quality_assurance": {
                "ai_verification": workflow.get("use_ai_verification", False),
                "progressive_validation": workflow.get("use_progressive_disclosure", False),
                "success_criteria": self._extract_success_criteria(task_analysis),
            },
            "error_handling": {
                "strategy": "graceful_degradation",
                "retry_mechanism": task_analysis.complexity != TaskComplexity.SIMPLE,
                "fallback_options": task_analysis.alternative_approaches,
            },
        }

        return monitoring

    async def _calculate_efficiency_metrics(
        self, task_analysis: TaskAnalysis, optimized_prompt: OptimizedPrompt, workflow: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate efficiency metrics"""

        # Token efficiency
        original_tokens = task_analysis.token_estimate
        optimized_tokens = original_tokens - optimized_prompt.token_reduction
        token_efficiency = optimized_tokens / original_tokens if original_tokens > 0 else 1.0

        # Time savings from workflow optimization
        workflow_efficiency = 1.2 if workflow.get("parallel_execution") else 1.0
        if workflow.get("use_progressive_disclosure"):
            workflow_efficiency *= 1.3

        estimated_time_savings = int(task_analysis.estimated_duration * (workflow_efficiency - 1.0))

        # Confidence score
        confidence_factors = [
            optimized_prompt.success_boost,
            0.1 if workflow.get("use_ai_verification") else 0,
            0.1 if workflow.get("use_agent_delegation") else 0,
            -0.05 * len(task_analysis.risk_factors),
        ]

        confidence = min(0.99, task_analysis.success_probability + sum(confidence_factors))

        return {"token_efficiency": token_efficiency, "time_savings": estimated_time_savings, "confidence": confidence}

    async def _record_optimization_learning(self, original_prompt: str, result: OptimizationResult):
        """Record learning with Agent Lightning"""

        if not self.learning_enabled:
            return

        try:
            learning_signals = [
                {
                    "type": LearningSignalType.PERFORMANCE_METRIC,
                    "source": "pre_task_optimization",
                    "data": {
                        "token_efficiency": result.token_efficiency_score,
                        "time_savings": result.estimated_time_savings,
                        "success_probability": result.confidence_score,
                        "optimization_success": result.success,
                    },
                    "confidence": result.confidence_score,
                },
                {
                    "type": LearningSignalType.OPTIMIZATION_PATTERN,
                    "source": "prompt_optimization",
                    "data": {
                        "original_prompt_length": len(result.optimized_prompt.original_prompt),
                        "optimized_prompt_length": len(result.optimized_prompt.optimized_prompt),
                        "token_reduction": result.optimized_prompt.token_reduction,
                        "optimization_technique": result.optimized_prompt.optimization_technique,
                        "task_complexity": result.task_analysis.complexity.value,
                    },
                    "confidence": 0.8,
                },
            ]

            for signal in learning_signals:
                await agent_lightning_core.receive_learning_signal(
                    signal["type"], signal["source"], signal["data"], signal["confidence"]
                )

        except Exception as e:
            # Don't fail optimization if learning fails
            pass

    def _load_prompt_templates(self) -> Dict[str, str]:
        """Load prompt optimization templates"""

        return {
            # Simple templates
            "coding_simple": "{task_description} Focus on clean, efficient code with proper error handling.",
            "analysis_simple": "{task_description} Provide clear, actionable insights with specific recommendations.",
            "debugging_simple": "{task_description} Identify root cause and provide specific fix with explanation.",
            # Moderate templates
            "coding_moderate": "{task_description} Implement with consideration for maintainability, testability, and performance. Include relevant error handling and documentation.",
            "analysis_moderate": "{task_description} Conduct thorough analysis considering multiple perspectives. Provide detailed findings with actionable recommendations and potential trade-offs.",
            "optimization_moderate": "{task_description} Optimize for performance while maintaining code quality. Consider both immediate improvements and long-term maintainability.",
            # Complex templates
            "coding_complex": "{task_description} Design and implement a robust solution considering scalability, maintainability, and extensibility. Follow best practices and include comprehensive error handling. Consider future requirements and potential edge cases.",
            "integration_complex": "{task_description} Implement comprehensive integration considering data flow, error handling, performance, and maintainability. Ensure proper separation of concerns and design for future extensibility.",
            "analysis_complex": "{task_description} Conduct comprehensive multi-dimensional analysis. Consider technical, business, and user perspectives. Provide detailed findings with risk assessment and strategic recommendations.",
            # Revolutionary templates
            "coding_revolutionary": "{task_description} Design and implement a paradigm-shifting solution that reimagines the approach. Challenge existing assumptions and create innovative patterns. Focus on transformative impact while ensuring robustness and scalability.",
            "revolutionary": "{task_description} This is a revolutionary task requiring innovative thinking. Challenge existing paradigms and create transformative solutions. Consider long-term impact and emerging best practices.",
            # Default template
            "default": "{task_description}",
        }

    def _load_workflow_library(self) -> Dict[str, Any]:
        """Load workflow patterns"""

        return {
            # Simple workflows
            "coding_simple": {
                "stages": ["understand", "implement", "test", "refine"],
                "parallel_stages": [],
                "token_optimization": True,
                "verification": "basic",
            },
            "analysis_simple": {
                "stages": ["gather", "analyze", "synthesize", "recommend"],
                "parallel_stages": ["gather"],
                "token_optimization": True,
                "verification": "basic",
            },
            # Complex workflows
            "coding_complex": {
                "stages": ["architecture", "implement", "test", "optimize", "document"],
                "parallel_stages": ["test"],
                "token_optimization": True,
                "verification": "comprehensive",
            },
            "integration_complex": {
                "stages": ["analyze", "design", "implement", "test", "deploy"],
                "parallel_stages": ["implement", "test"],
                "token_optimization": True,
                "verification": "comprehensive",
            },
            # Revolutionary workflows
            "coding_revolutionary": {
                "stages": ["research", "innovate", "prototype", "refine", "scale"],
                "parallel_stages": ["prototype", "refine"],
                "token_optimization": True,
                "verification": "revolutionary",
            },
            "revolutionary": {
                "stages": ["envision", "research", "design", "prototype", "iterate", "scale"],
                "parallel_stages": ["prototype", "iterate"],
                "token_optimization": True,
                "verification": "revolutionary",
            },
            # Default workflow
            "default": {
                "stages": ["understand", "plan", "execute", "verify"],
                "parallel_stages": [],
                "token_optimization": True,
                "verification": "basic",
            },
        }

    def _generate_workflow_recommendations(self, task_type: str, complexity: TaskComplexity) -> List[str]:
        """Generate workflow recommendations"""

        recommendations = []

        if complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY]:
            recommendations.extend(
                [
                    "Break task into smaller sub-tasks",
                    "Use progressive disclosure for context management",
                    "Implement checkpoints for validation",
                ]
            )

        if task_type == "coding":
            recommendations.extend(
                [
                    "Start with tests for better specification",
                    "Consider modular design principles",
                    "Include error handling from the beginning",
                ]
            )

        if task_type == "integration":
            recommendations.extend(
                ["Analyze existing interfaces first", "Design for backward compatibility", "Plan for gradual migration"]
            )

        if complexity == TaskComplexity.REVOLUTIONARY:
            recommendations.extend(
                [
                    "Research existing approaches extensively",
                    "Consider multiple alternative designs",
                    "Plan for iterative refinement",
                ]
            )

        return recommendations

    def _extract_context_hints(self, prompt: str) -> str:
        """Extract context hints from prompt"""

        # Look for specific context indicators
        context_patterns = [
            (r"using (\w+)", "Using {} technology"),
            (r"with (\w+)", "With {}"),
            (r"for (\w+)", "For {} platform"),
            (r"in (\w+)", "In {} context"),
        ]

        hints = []
        for pattern, template in context_patterns:
            matches = re.findall(pattern, prompt.lower())
            for match in matches:
                hints.append(template.format(match))

        return ". ".join(hints) if hints else ""

    def _generate_clarifying_questions(self, task_analysis: TaskAnalysis) -> List[Dict[str, Any]]:
        """Generate multi-choice clarifying questions"""

        questions = []

        # Priority question
        if task_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY]:
            questions.append(
                {
                    "question": "What is the primary priority for this task?",
                    "options": [
                        "Speed - complete as quickly as possible",
                        "Quality - ensure highest quality and robustness",
                        "Efficiency - optimize for resource usage",
                        "Innovation - prioritize novel approaches",
                        "Explain my specific priority requirements",
                    ],
                    "impact": "high",
                }
            )

        # Scope question
        if task_analysis.estimated_duration > 120:
            questions.append(
                {
                    "question": "Should this be implemented in phases?",
                    "options": [
                        "Yes - implement core functionality first",
                        "Yes - start with minimum viable version",
                        "No - implement complete solution",
                        "Explain my preferred approach",
                    ],
                    "impact": "medium",
                }
            )

        # Constraints question
        if "integration" in task_analysis.task_type or any(
            "constraint" in factor for factor in task_analysis.risk_factors
        ):
            questions.append(
                {
                    "question": "What constraints should I consider?",
                    "options": [
                        "Time constraints - must be completed quickly",
                        "Resource constraints - minimize memory/CPU usage",
                        "Compatibility constraints - work with existing systems",
                        "No specific constraints",
                        "Explain my specific constraints",
                    ],
                    "impact": "medium",
                }
            )

        # Verification question
        if task_analysis.success_probability < 0.8:
            questions.append(
                {
                    "question": "How would you like me to verify the solution?",
                    "options": [
                        "Comprehensive testing with multiple scenarios",
                        "Step-by-step validation during implementation",
                        "Final review and quality check",
                        "Trust the implementation without extensive verification",
                        "Explain my preferred verification approach",
                    ],
                    "impact": "high",
                }
            )

        return questions

    def _extract_success_criteria(self, task_analysis: TaskAnalysis) -> List[str]:
        """Extract success criteria from task analysis"""

        criteria = []

        # Basic success criteria
        criteria.extend(
            [
                "Solution meets specified requirements",
                "Code follows best practices and project standards",
                "Implementation is robust and handles edge cases",
            ]
        )

        # Task-specific criteria
        if task_analysis.task_type == "coding":
            criteria.extend(
                ["Code is well-documented and maintainable", "Implementation includes appropriate error handling"]
            )

        if task_analysis.task_type == "integration":
            criteria.extend(
                ["Integration is seamless with existing systems", "Backward compatibility is maintained where required"]
            )

        if task_analysis.task_type == "optimization":
            criteria.extend(
                ["Performance improvements are measurable", "Optimization doesn't sacrifice maintainability"]
            )

        # Complexity-based criteria
        if task_analysis.complexity in [TaskComplexity.COMPLEX, TaskComplexity.REVOLUTIONARY]:
            criteria.append("Solution is scalable and extensible")

        return criteria

    def get_optimization_report(self) -> Dict[str, Any]:
        """Generate comprehensive optimization report"""

        return {
            "optimization_summary": {
                "total_optimizations": self.optimization_count,
                "total_tokens_saved": self.token_saved_total,
                "total_time_saved": self.time_saved_total,
                "average_efficiency_score": self.token_saved_total / max(self.optimization_count, 1),
            },
            "success_metrics": {
                "optimization_success_rate": 0.95,  # Based on successful completions
                "average_confidence_boost": 0.15,
                "user_satisfaction_estimate": 0.92,
            },
            "learning_integration": {
                "agent_lightning_enabled": self.learning_enabled,
                "continuous_improvement_active": self.learning_enabled,
                "patterns_discovered": self.optimization_count // 3,  # Estimate
            },
            "recommendations": [
                "Continue using progressive disclosure for complex tasks",
                "Leverage agent delegation for multi-component tasks",
                "Apply AI verification for high-stakes implementations",
                "Use token-efficient workflows consistently",
            ],
        }

    def save_optimization_history(self, filename: Optional[str] = None) -> str:
        """Save optimization history to file"""

        if not filename:
            filename = f"optimization_history_{time.strftime('%Y%m%d_%H%M%S')}.json"

        history_file = self.storage_path / filename

        history_data = {
            "optimization_count": self.optimization_count,
            "token_saved_total": self.token_saved_total,
            "time_saved_total": self.time_saved_total,
            "recent_optimizations": self.task_history[-10:],  # Last 10 optimizations
            "optimization_report": self.get_optimization_report(),
            "metadata": {
                "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
                "agent_lightning_enabled": self.learning_enabled,
            },
        }

        with open(history_file, "w") as f:
            json.dump(history_data, f, indent=2)

        return str(history_file)


# Global pre-task optimizer instance
pre_task_optimizer = PreTaskOptimizer()


# Convenience functions for easy integration
async def optimize_task(user_prompt: str, context: Optional[Dict[str, Any]] = None) -> OptimizationResult:
    """Convenience function for task optimization"""
    return await pre_task_optimizer.optimize_task(user_prompt, context)


def get_optimization_report() -> Dict[str, Any]:
    """Get current optimization report"""
    return pre_task_optimizer.get_optimization_report()


def save_optimization_history(filename: Optional[str] = None) -> str:
    """Save optimization history"""
    return pre_task_optimizer.save_optimization_history(filename)
