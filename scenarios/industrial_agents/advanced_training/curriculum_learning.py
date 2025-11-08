"""
Advanced Curriculum Learning System for Engineering Agents

Implements sophisticated curriculum learning strategies for progressive skill development:
- Adaptive curriculum that adjusts to agent performance
- Self-paced learning with automatic difficulty progression
- Domain-specific curricula for mechanical engineering disciplines
- Just-in-time training for specific engineering tasks
- Multi-skill progression with prerequisite tracking
"""

import asyncio
import json
import logging
import uuid
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any

import networkx as nx
import numpy as np

logger = logging.getLogger(__name__)


class SkillLevel(Enum):
    """Proficiency levels for engineering skills."""

    NOVICE = "novice"
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"
    MASTER = "master"


class LearningObjective(Enum):
    """Learning objectives for engineering agents."""

    CONCEPT_UNDERSTANDING = "concept_understanding"
    PROCEDURAL_SKILL = "procedural_skill"
    PROBLEM_SOLVING = "problem_solving"
    DESIGN_OPTIMIZATION = "design_optimization"
    INNOVATION = "innovation"
    SAFETY_COMPLIANCE = "safety_compliance"
    QUALITY_ASSURANCE = "quality_assurance"
    COLLABORATION = "collaboration"


class EngineeringDomain(Enum):
    """Engineering domains for curriculum specialization."""

    MECHANICAL_DESIGN = "mechanical_design"
    THERMAL_ANALYSIS = "thermal_analysis"
    STRUCTURAL_ANALYSIS = "structural_analysis"
    FLUID_DYNAMICS = "fluid_dynamics"
    MANUFACTURING = "manufacturing"
    MATERIALS_SCIENCE = "materials_science"
    CONTROL_SYSTEMS = "control_systems"
    ACOUSTICS = "acoustics"
    VIBRATION_ANALYSIS = "vibration_analysis"


@dataclass
class Skill:
    """Represents an engineering skill."""

    skill_id: str
    name: str
    domain: EngineeringDomain
    description: str
    level: SkillLevel
    prerequisites: list[str] = field(default_factory=list)
    learning_objectives: list[LearningObjective] = field(default_factory=list)
    difficulty_score: float = 0.5
    estimated_time: float = 1.0  # hours
    assessment_criteria: dict[str, float] = field(default_factory=dict)
    resources: list[str] = field(default_factory=list)

    def is_prerequisite_satisfied(self, completed_skills: set[str]) -> bool:
        """Check if all prerequisites are satisfied."""
        return all(prereq in completed_skills for prereq in self.prerequisites)

    def get_complexity_score(self) -> float:
        """Calculate overall complexity score."""
        level_weights = {
            SkillLevel.NOVICE: 0.1,
            SkillLevel.BEGINNER: 0.25,
            SkillLevel.INTERMEDIATE: 0.5,
            SkillLevel.ADVANCED: 0.75,
            SkillLevel.EXPERT: 0.9,
            SkillLevel.MASTER: 1.0,
        }

        base_complexity = level_weights[self.level]
        prerequisite_factor = 1.0 + len(self.prerequisites) * 0.1
        objective_factor = 1.0 + len(self.learning_objectives) * 0.05

        return base_complexity * prerequisite_factor * objective_factor


@dataclass
class LearningTask:
    """Individual learning task within a curriculum."""

    task_id: str
    skill_id: str
    name: str
    description: str
    task_type: str  # "theory", "practice", "assessment", "project"
    difficulty: float
    content: dict[str, Any] = field(default_factory=dict)
    evaluation_criteria: dict[str, float] = field(default_factory=dict)
    time_limit: float | None = None
    resources: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class Curriculum:
    """Structured learning curriculum."""

    curriculum_id: str
    name: str
    domain: EngineeringDomain
    description: str
    target_level: SkillLevel
    skills: list[Skill] = field(default_factory=list)
    tasks: list[LearningTask] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    estimated_duration: float = 0.0
    success_criteria: dict[str, float] = field(default_factory=dict)

    def get_skill_graph(self) -> nx.DiGraph:
        """Build prerequisite graph for skills."""
        graph = nx.DiGraph()

        # Add nodes
        for skill in self.skills:
            graph.add_node(skill.skill_id, skill=skill)

        # Add edges for prerequisites
        for skill in self.skills:
            for prereq_id in skill.prerequisites:
                if graph.has_node(prereq_id):
                    graph.add_edge(prereq_id, skill.skill_id)

        return graph

    def get_learning_path(self, current_skills: set[str]) -> list[Skill]:
        """Get optimal learning path based on current skills."""
        self.get_skill_graph()
        available_skills = []

        for skill in self.skills:
            if skill.skill_id not in current_skills and skill.is_prerequisite_satisfied(current_skills):
                available_skills.append(skill)

        # Sort by difficulty and prerequisites
        available_skills.sort(key=lambda s: (s.get_complexity_score(), len(s.prerequisites)))

        return available_skills


@dataclass
class LearningProgress:
    """Track learning progress for an agent."""

    agent_id: str
    curriculum_id: str
    completed_skills: set[str] = field(default_factory=set)
    completed_tasks: set[str] = field(default_factory=set)
    skill_mastery: dict[str, float] = field(default_factory=dict)
    task_performance: dict[str, float] = field(default_factory=dict)
    learning_history: list[dict[str, Any]] = field(default_factory=list)
    current_focus: str | None = None
    start_time: datetime = field(default_factory=datetime.now)
    last_update: datetime = field(default_factory=datetime.now)

    def update_progress(self, task_id: str, performance: float, skill_id: str):
        """Update learning progress."""
        self.task_performance[task_id] = performance
        self.completed_tasks.add(task_id)

        # Update skill mastery
        if skill_id not in self.skill_mastery:
            self.skill_mastery[skill_id] = 0.0

        # Exponential moving average for skill mastery
        alpha = 0.3  # Learning rate
        self.skill_mastery[skill_id] = (1 - alpha) * self.skill_mastery[skill_id] + alpha * performance

        # Mark skill as completed if mastery threshold reached
        if self.skill_mastery[skill_id] >= 0.8:
            self.completed_skills.add(skill_id)

        # Record learning event
        self.learning_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "task_id": task_id,
                "skill_id": skill_id,
                "performance": performance,
                "mastery_after": self.skill_mastery[skill_id],
            }
        )

        self.last_update = datetime.now()


class AdaptiveCurriculumManager:
    """Manages adaptive curriculum based on agent performance."""

    def __init__(self):
        self.curricula: dict[str, Curriculum] = {}
        self.learning_progress: dict[str, LearningProgress] = {}
        self.performance_history: dict[str, list[float]] = defaultdict(list)
        self.difficulty_adjustments: dict[str, float] = defaultdict(float)

    def register_curriculum(self, curriculum: Curriculum):
        """Register a new curriculum."""
        self.curricula[curriculum.curriculum_id] = curriculum
        logger.info(f"Registered curriculum: {curriculum.name}")

    def enroll_agent(self, agent_id: str, curriculum_id: str) -> LearningProgress:
        """Enroll an agent in a curriculum."""
        if curriculum_id not in self.curricula:
            raise ValueError(f"Curriculum {curriculum_id} not found")

        progress = LearningProgress(agent_id=agent_id, curriculum_id=curriculum_id)

        self.learning_progress[agent_id] = progress
        logger.info(f"Agent {agent_id} enrolled in curriculum {curriculum_id}")

        return progress

    def get_next_task(self, agent_id: str) -> LearningTask | None:
        """Get next appropriate task for an agent."""
        if agent_id not in self.learning_progress:
            return None

        progress = self.learning_progress[agent_id]
        curriculum = self.curricula[progress.curriculum_id]

        # Get available skills based on current progress
        available_skills = curriculum.get_learning_path(progress.completed_skills)

        if not available_skills:
            # Check if there are incomplete tasks for current skills
            for skill_id in progress.skill_mastery:
                if progress.skill_mastery[skill_id] < 0.8:
                    # Find remaining tasks for this skill
                    remaining_tasks = [
                        task
                        for task in curriculum.tasks
                        if (task.skill_id == skill_id and task.task_id not in progress.completed_tasks)
                    ]

                    if remaining_tasks:
                        # Select most appropriate task
                        return self._select_best_task(remaining_tasks, progress)

            return None  # Curriculum completed

        # Get tasks for next available skill
        next_skill = available_skills[0]
        available_tasks = [
            task
            for task in curriculum.tasks
            if task.skill_id == next_skill.skill_id and task.task_id not in progress.completed_tasks
        ]

        if not available_tasks:
            return None

        return self._select_best_task(available_tasks, progress)

    def _select_best_task(self, tasks: list[LearningTask], progress: LearningProgress) -> LearningTask:
        """Select the best task from available options."""
        # Calculate task scores based on multiple factors
        task_scores = []

        for task in tasks:
            score = 0.0

            # Difficulty appropriateness
            if progress.agent_id in self.difficulty_adjustments:
                adjusted_difficulty = task.difficulty + self.difficulty_adjustments[progress.agent_id]
            else:
                adjusted_difficulty = task.difficulty

            # Optimal difficulty range (Vygotsky's zone of proximal development)
            if 0.4 <= adjusted_difficulty <= 0.7:
                score += 0.4
            elif 0.3 <= adjusted_difficulty <= 0.8:
                score += 0.2

            # Task type variety
            recent_task_types = [event.get("task_type") for event in progress.learning_history[-5:]]
            if task.task_type not in recent_task_types:
                score += 0.2

            # Time efficiency
            if task.time_limit:
                score += 0.1 * (1.0 - task.time_limit / 2.0)  # Prefer shorter tasks

            # Resource availability
            if task.resources:
                score += 0.1 * min(1.0, len(task.resources) / 3.0)

            task_scores.append((score, task))

        # Select highest scoring task
        task_scores.sort(key=lambda x: x[0], reverse=True)
        return task_scores[0][1]

    def update_difficulty(self, agent_id: str, task_performance: float, task_difficulty: float):
        """Update difficulty adjustment based on performance."""
        if agent_id not in self.performance_history:
            self.performance_history[agent_id] = []

        self.performance_history[agent_id].append(task_performance)

        # Maintain window of recent performance
        if len(self.performance_history[agent_id]) > 10:
            self.performance_history[agent_id].pop(0)

        # Calculate average recent performance
        recent_performance = np.mean(self.performance_history[agent_id])

        # Adjust difficulty based on performance
        if recent_performance > 0.85:  # Too easy
            adjustment = 0.1
        elif recent_performance > 0.75:  # Slightly easy
            adjustment = 0.05
        elif recent_performance < 0.4:  # Too hard
            adjustment = -0.1
        elif recent_performance < 0.5:  # Slightly hard
            adjustment = -0.05
        else:
            adjustment = 0.0  # Just right

        # Apply adjustment with smoothing
        self.difficulty_adjustments[agent_id] = 0.7 * self.difficulty_adjustments[agent_id] + 0.3 * adjustment

        # Clamp adjustment range
        self.difficulty_adjustments[agent_id] = np.clip(self.difficulty_adjustments[agent_id], -0.3, 0.3)

    def generate_progress_report(self, agent_id: str) -> dict[str, Any]:
        """Generate detailed progress report for an agent."""
        if agent_id not in self.learning_progress:
            return {"error": "Agent not enrolled in any curriculum"}

        progress = self.learning_progress[agent_id]
        curriculum = self.curricula[progress.curriculum_id]

        # Calculate overall progress
        total_skills = len(curriculum.skills)
        completed_skills = len(progress.completed_skills)
        overall_progress = completed_skills / total_skills if total_skills > 0 else 0.0

        # Skill-specific progress
        skill_progress = {}
        for skill in curriculum.skills:
            mastery = progress.skill_mastery.get(skill.skill_id, 0.0)
            completed = skill.skill_id in progress.completed_skills

            skill_progress[skill.skill_id] = {
                "name": skill.name,
                "level": skill.level.value,
                "mastery": mastery,
                "completed": completed,
                "difficulty": skill.get_complexity_score(),
            }

        # Performance trends
        if len(progress.learning_history) >= 5:
            recent_performances = [event["performance"] for event in progress.learning_history[-5:]]
            performance_trend = "improving" if recent_performances[-1] > recent_performances[0] else "declining"
            avg_performance = np.mean(recent_performances)
        else:
            performance_trend = "insufficient_data"
            avg_performance = 0.0

        # Learning efficiency
        total_time = (progress.last_update - progress.start_time).total_seconds() / 3600  # hours
        tasks_per_hour = len(progress.completed_tasks) / total_time if total_time > 0 else 0.0

        return {
            "agent_id": agent_id,
            "curriculum": curriculum.name,
            "domain": curriculum.domain.value,
            "overall_progress": overall_progress,
            "skills_completed": completed_skills,
            "total_skills": total_skills,
            "skill_progress": skill_progress,
            "average_performance": avg_performance,
            "performance_trend": performance_trend,
            "learning_efficiency": tasks_per_hour,
            "difficulty_adjustment": self.difficulty_adjustments.get(agent_id, 0.0),
            "last_update": progress.last_update.isoformat(),
        }


class JustInTimeTrainer:
    """Just-in-time training for specific engineering tasks."""

    def __init__(self, curriculum_manager: AdaptiveCurriculumManager):
        self.curriculum_manager = curriculum_manager
        self.task_templates: dict[str, dict[str, Any]] = {}
        self.training_queue: list[dict[str, Any]] = []
        self.critical_skills: dict[str, list[str]] = defaultdict(list)

    def register_critical_skills(self, domain: str, skills: list[str]):
        """Register critical skills for a domain."""
        self.critical_skills[domain] = skills

    def create_just_in_time_task(self, engineering_context: dict[str, Any]) -> LearningTask:
        """Create a targeted training task based on engineering context."""
        task_type = engineering_context.get("task_type", "assessment")
        engineering_context.get("domain", "mechanical_design")
        required_skills = engineering_context.get("required_skills", [])
        urgency = engineering_context.get("urgency", "normal")

        # Generate task ID
        task_id = f"jit_{uuid.uuid4().hex[:8]}"

        # Determine task difficulty based on context complexity
        complexity_factors = [
            len(required_skills) * 0.1,
            len(engineering_context.get("constraints", [])) * 0.05,
            engineering_context.get("safety_critical", False) * 0.2,
            urgency == "high" * 0.1,
        ]
        difficulty = min(1.0, sum(complexity_factors))

        # Create task content
        content = self._generate_task_content(engineering_context, required_skills)

        # Set evaluation criteria
        evaluation_criteria = {
            "accuracy": 0.8,
            "efficiency": 0.7,
            "safety_compliance": 0.9 if engineering_context.get("safety_critical", False) else 0.7,
        }

        task = LearningTask(
            task_id=task_id,
            skill_id=required_skills[0] if required_skills else "general_engineering",
            name=f"Just-in-time: {engineering_context.get('task_name', 'Engineering Task')}",
            description=f"Targeted training for: {engineering_context.get('description', 'Engineering task')}",
            task_type=task_type,
            difficulty=difficulty,
            content=content,
            evaluation_criteria=evaluation_criteria,
            time_limit=0.5 if urgency == "high" else 2.0,
            metadata={"context": engineering_context, "urgency": urgency, "created_at": datetime.now().isoformat()},
        )

        return task

    def _generate_task_content(self, context: dict[str, Any], required_skills: list[str]) -> dict[str, Any]:
        """Generate task content based on context."""
        content = {
            "scenario": context.get("scenario", "Generic engineering scenario"),
            "objectives": context.get("objectives", ["Complete engineering task"]),
            "constraints": context.get("constraints", []),
            "resources": context.get("resources", []),
            "success_criteria": context.get("success_criteria", {}),
            "skill_focus": required_skills,
        }

        # Add domain-specific content
        domain = context.get("domain", "mechanical_design")
        if domain == "mechanical_design":
            content.update(
                {
                    "design_parameters": context.get("design_parameters", {}),
                    "material_requirements": context.get("material_requirements", []),
                    "manufacturing_constraints": context.get("manufacturing_constraints", []),
                }
            )
        elif domain == "thermal_analysis":
            content.update(
                {
                    "thermal_conditions": context.get("thermal_conditions", {}),
                    "heat_sources": context.get("heat_sources", []),
                    "cooling_requirements": context.get("cooling_requirements", []),
                }
            )

        return content

    async def train_on_demand(self, agent_id: str, engineering_context: dict[str, Any]) -> dict[str, Any]:
        """Train agent on-demand for specific engineering task."""
        logger.info(f"Starting just-in-time training for agent {agent_id}")

        # Create targeted task
        task = self.create_just_in_time_task(engineering_context)

        # Simulate training execution
        training_result = await self._execute_training(agent_id, task)

        # Update curriculum progress if applicable
        if agent_id in self.curriculum_manager.learning_progress:
            progress = self.curriculum_manager.learning_progress[agent_id]
            progress.update_progress(
                task_id=task.task_id, performance=training_result["performance"], skill_id=task.skill_id
            )

        return {
            "task_id": task.task_id,
            "training_result": training_result,
            "task_difficulty": task.difficulty,
            "training_time": training_result["training_time"],
            "skill_improvement": training_result.get("skill_improvement", 0.0),
        }

    async def _execute_training(self, agent_id: str, task: LearningTask) -> dict[str, Any]:
        """Execute training task (simulation)."""
        start_time = datetime.now()

        # Simulate training based on task difficulty
        base_performance = 0.7
        difficulty_factor = 1.0 - task.difficulty * 0.3

        # Add some randomness to simulate real training variability
        performance_variation = np.random.normal(0, 0.1)
        final_performance = np.clip(base_performance * difficulty_factor + performance_variation, 0.0, 1.0)

        # Calculate training time
        training_time = (datetime.now() - start_time).total_seconds()
        training_time += task.difficulty * 300  # Base time + difficulty factor

        # Simulate skill improvement
        skill_improvement = final_performance * 0.2  # 20% of performance translates to skill improvement

        await asyncio.sleep(min(training_time, 5.0))  # Simulate training time (max 5s for demo)

        return {
            "performance": final_performance,
            "training_time": training_time,
            "skill_improvement": skill_improvement,
            "success": final_performance >= 0.6,
            "completed_at": datetime.now().isoformat(),
        }


class CurriculumLearningSystem:
    """Main curriculum learning system integrating all components."""

    def __init__(self):
        self.curriculum_manager = AdaptiveCurriculumManager()
        self.jit_trainer = JustInTimeTrainer(self.curriculum_manager)
        self.domain_curricula: dict[EngineeringDomain, str] = {}

        # Initialize with standard engineering curricula
        self._initialize_standard_curricula()

    def _initialize_standard_curricula(self):
        """Initialize standard engineering curricula."""
        # Mechanical Design Curriculum
        mechanical_curriculum = self._create_mechanical_design_curriculum()
        self.curriculum_manager.register_curriculum(mechanical_curriculum)
        self.domain_curricula[EngineeringDomain.MECHANICAL_DESIGN] = mechanical_curriculum.curriculum_id

        # Thermal Analysis Curriculum
        thermal_curriculum = self._create_thermal_analysis_curriculum()
        self.curriculum_manager.register_curriculum(thermal_curriculum)
        self.domain_curricula[EngineeringDomain.THERMAL_ANALYSIS] = thermal_curriculum.curriculum_id

        # Structural Analysis Curriculum
        structural_curriculum = self._create_structural_analysis_curriculum()
        self.curriculum_manager.register_curriculum(structural_curriculum)
        self.domain_curricula[EngineeringDomain.STRUCTURAL_ANALYSIS] = structural_curriculum.curriculum_id

    def _create_mechanical_design_curriculum(self) -> Curriculum:
        """Create mechanical design curriculum."""
        curriculum = Curriculum(
            curriculum_id="mechanical_design_v1",
            name="Mechanical Design Engineering",
            domain=EngineeringDomain.MECHANICAL_DESIGN,
            description="Comprehensive curriculum for mechanical design engineering",
            target_level=SkillLevel.ADVANCED,
        )

        # Define skills
        skills = [
            Skill(
                skill_id="cad_basics",
                name="CAD Fundamentals",
                domain=EngineeringDomain.MECHANICAL_DESIGN,
                description="Basic CAD modeling and design principles",
                level=SkillLevel.BEGINNER,
                learning_objectives=[LearningObjective.CONCEPT_UNDERSTANDING, LearningObjective.PROCEDURAL_SKILL],
                difficulty_score=0.3,
                estimated_time=8.0,
            ),
            Skill(
                skill_id="material_selection",
                name="Material Selection",
                domain=EngineeringDomain.MECHANICAL_DESIGN,
                description="Select appropriate materials for engineering applications",
                level=SkillLevel.INTERMEDIATE,
                prerequisites=["cad_basics"],
                learning_objectives=[LearningObjective.PROBLEM_SOLVING, LearningObjective.DESIGN_OPTIMIZATION],
                difficulty_score=0.5,
                estimated_time=12.0,
            ),
            Skill(
                skill_id="structural_analysis",
                name="Structural Analysis",
                domain=EngineeringDomain.MECHANICAL_DESIGN,
                description="Analyze structural integrity and performance",
                level=SkillLevel.INTERMEDIATE,
                prerequisites=["cad_basics", "material_selection"],
                learning_objectives=[LearningObjective.PROBLEM_SOLVING, LearningObjective.QUALITY_ASSURANCE],
                difficulty_score=0.6,
                estimated_time=16.0,
            ),
            Skill(
                skill_id="advanced_design",
                name="Advanced Design Optimization",
                domain=EngineeringDomain.MECHANICAL_DESIGN,
                description="Advanced design techniques and optimization",
                level=SkillLevel.ADVANCED,
                prerequisites=["structural_analysis"],
                learning_objectives=[LearningObjective.DESIGN_OPTIMIZATION, LearningObjective.INNOVATION],
                difficulty_score=0.8,
                estimated_time=20.0,
            ),
        ]

        curriculum.skills = skills
        curriculum.estimated_duration = sum(skill.estimated_time for skill in skills)

        # Generate tasks for each skill
        tasks = []
        for skill in skills:
            skill_tasks = self._generate_tasks_for_skill(skill)
            tasks.extend(skill_tasks)

        curriculum.tasks = tasks

        return curriculum

    def _create_thermal_analysis_curriculum(self) -> Curriculum:
        """Create thermal analysis curriculum."""
        curriculum = Curriculum(
            curriculum_id="thermal_analysis_v1",
            name="Thermal Analysis Engineering",
            domain=EngineeringDomain.THERMAL_ANALYSIS,
            description="Thermal analysis and heat transfer engineering",
            target_level=SkillLevel.ADVANCED,
        )

        skills = [
            Skill(
                skill_id="heat_transfer_basics",
                name="Heat Transfer Fundamentals",
                domain=EngineeringDomain.THERMAL_ANALYSIS,
                description="Basic heat transfer principles and calculations",
                level=SkillLevel.BEGINNER,
                learning_objectives=[LearningObjective.CONCEPT_UNDERSTANDING],
                difficulty_score=0.3,
                estimated_time=10.0,
            ),
            Skill(
                skill_id="thermal_simulation",
                name="Thermal Simulation",
                domain=EngineeringDomain.THERMAL_ANALYSIS,
                description="Computer-aided thermal analysis and simulation",
                level=SkillLevel.INTERMEDIATE,
                prerequisites=["heat_transfer_basics"],
                learning_objectives=[LearningObjective.PROCEDURAL_SKILL, LearningObjective.PROBLEM_SOLVING],
                difficulty_score=0.6,
                estimated_time=15.0,
            ),
            Skill(
                skill_id="cooling_systems",
                name="Cooling System Design",
                domain=EngineeringDomain.THERMAL_ANALYSIS,
                description="Design and optimize cooling systems",
                level=SkillLevel.ADVANCED,
                prerequisites=["thermal_simulation"],
                learning_objectives=[LearningObjective.DESIGN_OPTIMIZATION, LearningObjective.SAFETY_COMPLIANCE],
                difficulty_score=0.8,
                estimated_time=18.0,
            ),
        ]

        curriculum.skills = skills
        curriculum.estimated_duration = sum(skill.estimated_time for skill in skills)

        # Generate tasks
        tasks = []
        for skill in skills:
            skill_tasks = self._generate_tasks_for_skill(skill)
            tasks.extend(skill_tasks)

        curriculum.tasks = tasks

        return curriculum

    def _create_structural_analysis_curriculum(self) -> Curriculum:
        """Create structural analysis curriculum."""
        curriculum = Curriculum(
            curriculum_id="structural_analysis_v1",
            name="Structural Analysis Engineering",
            domain=EngineeringDomain.STRUCTURAL_ANALYSIS,
            description="Structural analysis and finite element methods",
            target_level=SkillLevel.ADVANCED,
        )

        skills = [
            Skill(
                skill_id="mechanics_of_materials",
                name="Mechanics of Materials",
                domain=EngineeringDomain.STRUCTURAL_ANALYSIS,
                description="Stress, strain, and material behavior",
                level=SkillLevel.BEGINNER,
                learning_objectives=[LearningObjective.CONCEPT_UNDERSTANDING],
                difficulty_score=0.4,
                estimated_time=12.0,
            ),
            Skill(
                skill_id="finite_element_analysis",
                name="Finite Element Analysis",
                domain=EngineeringDomain.STRUCTURAL_ANALYSIS,
                description="FEA methods and applications",
                level=SkillLevel.INTERMEDIATE,
                prerequisites=["mechanics_of_materials"],
                learning_objectives=[LearningObjective.PROCEDURAL_SKILL, LearningObjective.PROBLEM_SOLVING],
                difficulty_score=0.7,
                estimated_time=20.0,
            ),
            Skill(
                skill_id="advanced_structural",
                name="Advanced Structural Design",
                domain=EngineeringDomain.STRUCTURAL_ANALYSIS,
                description="Complex structural analysis and optimization",
                level=SkillLevel.ADVANCED,
                prerequisites=["finite_element_analysis"],
                learning_objectives=[LearningObjective.DESIGN_OPTIMIZATION, LearningObjective.INNOVATION],
                difficulty_score=0.9,
                estimated_time=25.0,
            ),
        ]

        curriculum.skills = skills
        curriculum.estimated_duration = sum(skill.estimated_time for skill in skills)

        # Generate tasks
        tasks = []
        for skill in skills:
            skill_tasks = self._generate_tasks_for_skill(skill)
            tasks.extend(skill_tasks)

        curriculum.tasks = tasks

        return curriculum

    def _generate_tasks_for_skill(self, skill: Skill) -> list[LearningTask]:
        """Generate learning tasks for a skill."""
        tasks = []

        # Theory task
        tasks.append(
            LearningTask(
                task_id=f"{skill.skill_id}_theory",
                skill_id=skill.skill_id,
                name=f"Theory: {skill.name}",
                description=f"Theoretical understanding of {skill.name}",
                task_type="theory",
                difficulty=skill.difficulty_score * 0.8,
                content={"theory_content": f"Learning materials for {skill.name}"},
                evaluation_criteria={"understanding": 0.8},
                time_limit=skill.estimated_time * 0.3,
            )
        )

        # Practice task
        tasks.append(
            LearningTask(
                task_id=f"{skill.skill_id}_practice",
                skill_id=skill.skill_id,
                name=f"Practice: {skill.name}",
                description=f"Practical application of {skill.name}",
                task_type="practice",
                difficulty=skill.difficulty_score,
                content={"practice_exercises": f"Hands-on exercises for {skill.name}"},
                evaluation_criteria={"proficiency": 0.75},
                time_limit=skill.estimated_time * 0.5,
            )
        )

        # Assessment task
        tasks.append(
            LearningTask(
                task_id=f"{skill.skill_id}_assessment",
                skill_id=skill.skill_id,
                name=f"Assessment: {skill.name}",
                description=f"Assessment of {skill.name} mastery",
                task_type="assessment",
                difficulty=skill.difficulty_score * 1.1,
                content={"assessment_criteria": f"Evaluation criteria for {skill.name}"},
                evaluation_criteria={"accuracy": 0.85, "efficiency": 0.7},
                time_limit=skill.estimated_time * 0.2,
            )
        )

        return tasks

    async def start_learning_path(self, agent_id: str, domain: EngineeringDomain) -> dict[str, Any]:
        """Start agent on learning path for specific domain."""
        if domain not in self.domain_curricula:
            raise ValueError(f"No curriculum available for domain: {domain.value}")

        curriculum_id = self.domain_curricula[domain]
        self.curriculum_manager.enroll_agent(agent_id, curriculum_id)

        # Get first task
        first_task = self.curriculum_manager.get_next_task(agent_id)

        return {
            "agent_id": agent_id,
            "domain": domain.value,
            "curriculum_id": curriculum_id,
            "first_task": first_task.task_id if first_task else None,
            "estimated_duration": self.curriculum_manager.curricula[curriculum_id].estimated_duration,
            "total_skills": len(self.curriculum_manager.curricula[curriculum_id].skills),
        }

    async def continue_learning(self, agent_id: str, task_performance: float) -> dict[str, Any]:
        """Continue learning path with performance feedback."""
        if agent_id not in self.curriculum_manager.learning_progress:
            raise ValueError(f"Agent {agent_id} not enrolled in any curriculum")

        progress = self.curriculum_manager.learning_progress[agent_id]
        current_task_id = progress.current_focus

        if not current_task_id:
            return {"error": "No current task in progress"}

        # Update progress
        curriculum = self.curriculum_manager.curricula[progress.curriculum_id]
        current_task = next((t for t in curriculum.tasks if t.task_id == current_task_id), None)

        if current_task:
            # Update curriculum progress
            self.curriculum_manager.update_progress(
                agent_id=agent_id, task_id=current_task_id, performance=task_performance, skill_id=current_task.skill_id
            )

            # Update difficulty adjustment
            self.curriculum_manager.update_difficulty(
                agent_id=agent_id, task_performance=task_performance, task_difficulty=current_task.difficulty
            )

        # Get next task
        next_task = self.curriculum_manager.get_next_task(agent_id)

        if next_task:
            progress.current_focus = next_task.task_id
        else:
            progress.current_focus = None  # Curriculum completed

        return {
            "agent_id": agent_id,
            "task_completed": current_task_id,
            "performance": task_performance,
            "next_task": next_task.task_id if next_task else None,
            "curriculum_completed": next_task is None,
            "current_mastery": progress.skill_mastery.copy(),
        }

    async def request_just_in_time_training(self, agent_id: str, engineering_context: dict[str, Any]) -> dict[str, Any]:
        """Request just-in-time training for specific engineering context."""
        return await self.jit_trainer.train_on_demand(agent_id, engineering_context)

    def get_learning_analytics(self, agent_id: str = None) -> dict[str, Any]:
        """Get comprehensive learning analytics."""
        if agent_id:
            # Analytics for specific agent
            if agent_id not in self.curriculum_manager.learning_progress:
                return {"error": "Agent not found"}

            return self.curriculum_manager.generate_progress_report(agent_id)
        # System-wide analytics
        total_agents = len(self.curriculum_manager.learning_progress)
        completed_curricula = sum(
            1
            for progress in self.curriculum_manager.learning_progress.values()
            if len(progress.completed_skills) == len(self.curriculum_manager.curricula[progress.curriculum_id].skills)
        )

        avg_progress = 0.0
        if total_agents > 0:
            total_progress = sum(
                len(progress.completed_skills) / len(self.curriculum_manager.curricula[progress.curriculum_id].skills)
                for progress in self.curriculum_manager.learning_progress.values()
            )
            avg_progress = total_progress / total_agents

        return {
            "total_agents": total_agents,
            "completed_curricula": completed_curricula,
            "average_progress": avg_progress,
            "available_curricula": len(self.curriculum_manager.curricula),
            "difficulty_adjustments": dict(self.curriculum_manager.difficulty_adjustments),
        }


# CLI interface
async def main():
    """CLI interface for curriculum learning system."""
    import argparse

    parser = argparse.ArgumentParser(description="Advanced Curriculum Learning System")
    parser.add_argument(
        "--action", choices=["start", "continue", "jit", "analytics"], required=True, help="Action to perform"
    )
    parser.add_argument("--agent-id", help="Agent ID")
    parser.add_argument(
        "--domain", choices=[d.value for d in EngineeringDomain], default="mechanical_design", help="Engineering domain"
    )
    parser.add_argument("--performance", type=float, help="Task performance (0-1)")
    parser.add_argument("--context-file", help="JSON file with engineering context for JIT training")

    args = parser.parse_args()

    # Initialize curriculum learning system
    cls = CurriculumLearningSystem()

    if args.action == "start":
        if not args.agent_id:
            print("Error: --agent-id required for start action")
            return

        domain = EngineeringDomain(args.domain)
        result = await cls.start_learning_path(args.agent_id, domain)

        print(f"Started learning path for agent {args.agent_id}:")
        print(f"  Domain: {result['domain']}")
        print(f"  Curriculum: {result['curriculum_id']}")
        print(f"  Total skills: {result['total_skills']}")
        print(f"  Estimated duration: {result['estimated_duration']:.1f} hours")
        print(f"  First task: {result['first_task']}")

    elif args.action == "continue":
        if not args.agent_id or args.performance is None:
            print("Error: --agent-id and --performance required for continue action")
            return

        result = await cls.continue_learning(args.agent_id, args.performance)

        print(f"Learning progress for agent {args.agent_id}:")
        print(f"  Task completed: {result['task_completed']}")
        print(f"  Performance: {result['performance']:.3f}")
        print(f"  Next task: {result['next_task']}")
        print(f"  Curriculum completed: {result['curriculum_completed']}")

    elif args.action == "jit":
        if not args.agent_id or not args.context_file:
            print("Error: --agent-id and --context-file required for JIT action")
            return

        # Load engineering context
        try:
            with open(args.context_file) as f:
                context = json.load(f)
        except Exception as e:
            print(f"Error loading context file: {e}")
            return

        result = await cls.request_just_in_time_training(args.agent_id, context)

        print(f"Just-in-time training for agent {args.agent_id}:")
        print(f"  Task ID: {result['task_id']}")
        print(f"  Performance: {result['training_result']['performance']:.3f}")
        print(f"  Training time: {result['training_time']:.1f} seconds")
        print(f"  Skill improvement: {result['skill_improvement']:.3f}")

    elif args.action == "analytics":
        if args.agent_id:
            result = cls.get_learning_analytics(args.agent_id)
            print(f"Learning analytics for agent {args.agent_id}:")
        else:
            result = cls.get_learning_analytics()
            print("System-wide learning analytics:")

        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
