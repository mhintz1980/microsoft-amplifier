"""
Agent Lightning Integration Layer

Integrates advanced training systems with existing Agent Lightning infrastructure:
- Bridge between advanced training components and Agent Lightning
- Unified training orchestration across all systems
- Shared model registry and configuration management
- Seamless transition between training modes
- Compatibility layer for existing agent workflows
"""

import asyncio
import json
import logging
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

import numpy as np
import torch

from .curriculum_learning import CurriculumLearningSystem
from .hierarchical_rl import HierarchicalRLTrainer
from .hierarchical_rl import create_cad_design_hierarchy
from .meta_learning import MetaLearningTrainer
from .meta_learning import create_meta_learner
from .multi_agent_collaborative import MultiAgentTrainer
from .multi_agent_collaborative import create_engineering_team
from .multi_objective_optimizer import MultiObjectiveOptimizer
from .multi_objective_optimizer import create_structural_optimization
from .production_pipeline import TrainingOrchestrator
from .safety_critical_training import SafetyCriticalTrainingSystem

# Import advanced training components
from .verl_framework import VERLTrainer
from .verl_framework import create_verl_setup

# Try to import Agent Lightning
try:
    from agent_lightning import LightningAgent
    from agent_lightning import TrainingConfig

    AGENT_LIGHTNING_AVAILABLE = True
except ImportError:
    AGENT_LIGHTNING_AVAILABLE = False
    print("Warning: Agent Lightning not available. Using mock integration.")

logger = logging.getLogger(__name__)


class TrainingMode(Enum):
    """Available training modes."""

    AGENT_LIGHTNING = "agent_lightning"
    VERL = "verl"
    MULTI_OBJECTIVE = "multi_objective"
    HIERARCHICAL_RL = "hierarchical_rl"
    META_LEARNING = "meta_learning"
    MULTI_AGENT = "multi_agent"
    CURRICULUM = "curriculum"
    SAFETY_CRITICAL = "safety_critical"
    PRODUCTION = "production"
    HYBRID = "hybrid"


class IntegrationLevel(Enum):
    """Integration levels with Agent Lightning."""

    BASIC = "basic"  # Simple model sharing
    STANDARD = "standard"  # Training pipeline integration
    ADVANCED = "advanced"  # Full orchestration
    SEAMLESS = "seamless"  # Unified system


@dataclass
class TrainingConfiguration:
    """Unified training configuration."""

    mode: TrainingMode
    integration_level: IntegrationLevel
    agent_type: str
    domain: str
    objectives: list[str]
    constraints: list[str] = field(default_factory=list)
    hyperparameters: dict[str, Any] = field(default_factory=dict)
    data_config: dict[str, Any] = field(default_factory=dict)
    evaluation_config: dict[str, Any] = field(default_factory=dict)
    deployment_config: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TrainingSession:
    """Training session information."""

    session_id: str
    config: TrainingConfiguration
    started_at: datetime
    status: str
    components: list[str] = field(default_factory=list)
    metrics: dict[str, float] = field(default_factory=dict)
    artifacts: dict[str, str] = field(default_factory=dict)
    completed_at: datetime | None = None
    error_message: str | None = None


class AgentLightningBridge:
    """Bridge between advanced training systems and Agent Lightning."""

    def __init__(self):
        self.agent_lightning_available = AGENT_LIGHTNING_AVAILABLE
        self.agent_models: dict[str, Any] = {}
        self.training_configs: dict[str, dict] = {}

    def create_agent_lightning_model(self, config: dict[str, Any]) -> Any | None:
        """Create Agent Lightning model."""
        if not self.agent_lightning_available:
            logger.warning("Agent Lightning not available, returning mock model")
            return MockAgentLightningModel()

        try:
            # Create Agent Lightning model with config
            model = LightningAgent()
            self.agent_models[config.get("model_id", str(uuid.uuid4()))] = model
            return model
        except Exception as e:
            logger.error(f"Error creating Agent Lightning model: {e}")
            return None

    def get_model_parameters(self, model_id: str) -> dict[str, Any]:
        """Get model parameters for sharing."""
        if model_id not in self.agent_models:
            return {}

        model = self.agent_models[model_id]
        if hasattr(model, "state_dict"):
            return {k: v.tolist() for k, v in model.state_dict().items()}
        return {}

    def load_model_parameters(self, model_id: str, parameters: dict[str, Any]):
        """Load parameters into Agent Lightning model."""
        if model_id not in self.agent_models:
            logger.error(f"Model {model_id} not found")
            return

        model = self.agent_models[model_id]
        if hasattr(model, "load_state_dict"):
            # Convert numpy arrays back to tensors
            tensor_params = {k: torch.tensor(v) for k, v in parameters.items()}
            model.load_state_dict(tensor_params)

    def convert_to_agent_lightning_config(self, config: TrainingConfiguration) -> dict[str, Any]:
        """Convert unified config to Agent Lightning format."""
        return {
            "model_type": config.agent_type,
            "domain": config.domain,
            "training_mode": config.mode.value,
            "hyperparameters": config.hyperparameters,
            "objectives": config.objectives,
            "constraints": config.constraints,
            "data_config": config.data_config,
            "evaluation_config": config.evaluation_config,
        }


class MockAgentLightningModel:
    """Mock Agent Lightning model for testing without actual installation."""

    def __init__(self):
        self.model_id = str(uuid.uuid4())
        self.parameters = {
            "weight1": np.random.randn(64, 32),
            "weight2": np.random.randn(32, 16),
            "bias1": np.random.randn(32),
            "bias2": np.random.randn(16),
        }

    def state_dict(self):
        return self.parameters

    def load_state_dict(self, state_dict):
        self.parameters.update(state_dict)

    def train(self, data, config):
        # Mock training
        return {"loss": 0.123, "accuracy": 0.89}

    def evaluate(self, test_data):
        # Mock evaluation
        return {"test_accuracy": 0.87, "test_loss": 0.145}


class UnifiedTrainingOrchestrator:
    """Unified orchestrator for all training systems."""

    def __init__(self, config_path: str = "./unified_config.yaml"):
        self.config_path = config_path
        self.agent_lightning_bridge = AgentLightningBridge()

        # Initialize training components
        self.verl_trainers: dict[str, VERLTrainer] = {}
        self.multi_objective_optimizers: dict[str, MultiObjectiveOptimizer] = {}
        self.hierarchical_trainers: dict[str, HierarchicalRLTrainer] = {}
        self.meta_learners: dict[str, MetaLearningTrainer] = {}
        self.multi_agent_trainers: dict[str, MultiAgentTrainer] = {}
        self.curriculum_systems: dict[str, CurriculumLearningSystem] = {}
        self.safety_trainers: dict[str, SafetyCriticalTrainingSystem] = {}
        self.production_orchestrator: TrainingOrchestrator | None = None

        # Session management
        self.active_sessions: dict[str, TrainingSession] = {}
        self.session_history: list[TrainingSession] = []

        # Model registry
        self.model_registry: dict[str, dict[str, Any]] = {}

        logger.info("Unified Training Orchestrator initialized")

    async def train_agent(self, config: TrainingConfiguration) -> TrainingSession:
        """Train agent using specified configuration."""
        session_id = str(uuid.uuid4())
        session = TrainingSession(
            session_id=session_id, config=config, started_at=datetime.now(), status="initializing"
        )

        self.active_sessions[session_id] = session
        logger.info(f"Starting training session {session_id} with mode {config.mode.value}")

        try:
            if config.mode == TrainingMode.AGENT_LIGHTNING:
                result = await self._train_with_agent_lightning(session)
            elif config.mode == TrainingMode.VERL:
                result = await self._train_with_verl(session)
            elif config.mode == TrainingMode.MULTI_OBJECTIVE:
                result = await self._train_with_multi_objective(session)
            elif config.mode == TrainingMode.HIERARCHICAL_RL:
                result = await self._train_with_hierarchical_rl(session)
            elif config.mode == TrainingMode.META_LEARNING:
                result = await self._train_with_meta_learning(session)
            elif config.mode == TrainingMode.MULTI_AGENT:
                result = await self._train_with_multi_agent(session)
            elif config.mode == TrainingMode.CURRICULUM:
                result = await self._train_with_curriculum(session)
            elif config.mode == TrainingMode.SAFETY_CRITICAL:
                result = await self._train_with_safety_critical(session)
            elif config.mode == TrainingMode.PRODUCTION:
                result = await self._train_with_production(session)
            elif config.mode == TrainingMode.HYBRID:
                result = await self._train_with_hybrid(session)
            else:
                raise ValueError(f"Unsupported training mode: {config.mode}")

            session.status = "completed"
            session.completed_at = datetime.now()
            session.metrics.update(result.get("metrics", {}))
            session.artifacts.update(result.get("artifacts", {}))

            # Register model in registry
            self._register_model(session)

        except Exception as e:
            session.status = "failed"
            session.error_message = str(e)
            logger.error(f"Training session {session_id} failed: {e}")

        # Move to history
        self.session_history.append(session)
        del self.active_sessions[session_id]

        return session

    async def _train_with_agent_lightning(self, session: TrainingSession) -> dict[str, Any]:
        """Train using Agent Lightning."""
        logger.info(f"Training with Agent Lightning for session {session.session_id}")

        # Create Agent Lightning model
        al_config = self.agent_lightning_bridge.convert_to_agent_lightning_config(session.config)
        model = self.agent_lightning_bridge.create_agent_lightning_model(al_config)

        if not model:
            raise RuntimeError("Failed to create Agent Lightning model")

        session.components.append("agent_lightning")

        # Simulate training (in real implementation, this would use actual Agent Lightning)
        training_data = self._generate_mock_data(session.config)
        training_config = TrainingConfig(**session.config.hyperparameters)

        # Mock training process
        training_result = model.train(training_data, training_config)

        # Get model parameters for sharing
        model_id = f"{session.config.agent_type}_{session.session_id}"
        parameters = self.agent_lightning_bridge.get_model_parameters(model_id)

        return {
            "metrics": {"training_loss": training_result["loss"], "training_accuracy": training_result["accuracy"]},
            "artifacts": {"model_id": model_id, "parameters": parameters, "agent_lightning_config": al_config},
        }

    async def _train_with_verl(self, session: TrainingSession) -> dict[str, Any]:
        """Train using VERL framework."""
        logger.info(f"Training with VERL for session {session.session_id}")

        # Create VERL setup
        environment, agent, trainer = create_verl_setup(
            agent_type=session.config.agent_type, domain=session.config.domain
        )

        self.verl_trainers[session.session_id] = trainer
        session.components.append("verl")

        # Train agent
        self._generate_mock_data(session.config)
        results = await trainer.train(
            num_episodes=session.config.hyperparameters.get("epochs", 100),
            model_save_path=f"./models/{session.session_id}_verl",
        )

        # Extract model parameters
        model_params = {k: v.cpu().numpy() for k, v in agent.state_dict().items()}

        return {
            "metrics": results,
            "artifacts": {
                "model_id": f"verl_{session.session_id}",
                "parameters": model_params,
                "model_path": f"./models/{session.session_id}_verl",
            },
        }

    async def _train_with_multi_objective(self, session: TrainingSession) -> dict[str, Any]:
        """Train using multi-objective optimization."""
        logger.info(f"Training with multi-objective optimization for session {session.session_id}")

        # Create optimizer
        optimizer = create_structural_optimization()
        self.multi_objective_optimizers[session.session_id] = optimizer
        session.components.append("multi_objective")

        # Run optimization
        bounds = {"thickness": (1.0, 20.0), "material_quality": (10.0, 100.0)}

        best_solution, pareto_front = await optimizer.optimize(bounds=bounds)

        return {
            "metrics": {
                "pareto_front_size": len(pareto_front.solutions),
                "best_solution_quality": best_solution.objectives.get("safety", 0.0),
            },
            "artifacts": {
                "optimizer_id": f"mo_{session.session_id}",
                "best_solution": best_solution.__dict__,
                "pareto_front": [s.__dict__ for s in pareto_front.solutions[:10]],
            },
        }

    async def _train_with_hierarchical_rl(self, session: TrainingSession) -> dict[str, Any]:
        """Train using hierarchical RL."""
        logger.info(f"Training with hierarchical RL for session {session.session_id}")

        # Create hierarchy setup
        policy, workflow_manager, trainer = create_cad_design_hierarchy()
        self.hierarchical_trainers[session.session_id] = trainer
        session.components.append("hierarchical_rl")

        # Create root task
        from .hierarchical_rl import EngineeringDomain
        from .hierarchical_rl import create_root_task

        domain = EngineeringDomain(session.config.domain)
        root_task = create_root_task(domain, session.config.agent_type, "Training task")

        # Train workflow
        results = await trainer.train_workflow(root_task, max_steps=500)

        # Extract model parameters
        model_params = {k: v.cpu().numpy() for k, v in policy.state_dict().items()}

        return {
            "metrics": results,
            "artifacts": {
                "model_id": f"hrl_{session.session_id}",
                "parameters": model_params,
                "workflow_completion": results["completion_rate"],
            },
        }

    async def _train_with_meta_learning(self, session: TrainingSession) -> dict[str, Any]:
        """Train using meta-learning."""
        logger.info(f"Training with meta-learning for session {session.session_id}")

        # Create meta-learner
        from .meta_learning import EngineeringDomain

        domain = EngineeringDomain(session.config.domain)
        meta_learner = create_meta_learner(domain)
        self.meta_learners[session.session_id] = meta_learner
        session.components.append("meta_learning")

        # Generate synthetic tasks
        from .meta_learning import generate_synthetic_task

        tasks = [generate_synthetic_task(domain) for _ in range(10)]

        # Train meta-learner
        training_results = meta_learner.meta_train(tasks, num_epochs=50)

        # Save model
        model_path = f"./models/{session.session_id}_meta"
        meta_learner.save_model(model_path)

        return {
            "metrics": training_results,
            "artifacts": {
                "model_id": f"meta_{session.session_id}",
                "model_path": model_path,
                "strategy": training_results["strategy"],
            },
        }

    async def _train_with_multi_agent(self, session: TrainingSession) -> dict[str, Any]:
        """Train using multi-agent collaborative learning."""
        logger.info(f"Training with multi-agent collaboration for session {session.session_id}")

        # Create engineering team
        trainer = create_engineering_team()
        self.multi_agent_trainers[session.session_id] = trainer
        session.components.append("multi_agent")

        # Generate training data
        training_data = self._generate_mock_data(session.config)

        # Train agents
        results = await trainer.train_collaboratively(
            training_data=training_data, num_epochs=50, collaboration_frequency=5
        )

        # Save model
        model_path = f"./models/{session.session_id}_multi_agent"
        trainer.save_training_state(model_path)

        return {
            "metrics": results["final_performances"],
            "artifacts": {
                "model_id": f"ma_{session.session_id}",
                "model_path": model_path,
                "team_size": trainer.num_agents,
            },
        }

    async def _train_with_curriculum(self, session: TrainingSession) -> dict[str, Any]:
        """Train using curriculum learning."""
        logger.info(f"Training with curriculum learning for session {session.session_id}")

        # Create curriculum system
        curriculum_system = CurriculumLearningSystem()
        self.curriculum_systems[session.session_id] = curriculum_system
        session.components.append("curriculum")

        # Start learning path
        from .curriculum_learning import EngineeringDomain

        domain = EngineeringDomain(session.config.domain)
        learning_result = await curriculum_system.start_learning_path("test_agent", domain)

        # Simulate learning progress
        for _i in range(10):
            await curriculum_system.continue_learning("test_agent", 0.8 + np.random.normal(0, 0.1))

        # Get analytics
        analytics = curriculum_system.get_learning_analytics("test_agent")

        return {
            "metrics": analytics,
            "artifacts": {
                "curriculum_id": learning_result["curriculum_id"],
                "total_skills": learning_result["total_skills"],
                "learning_efficiency": analytics.get("learning_efficiency", 0.0),
            },
        }

    async def _train_with_safety_critical(self, session: TrainingSession) -> dict[str, Any]:
        """Train using safety-critical protocols."""
        logger.info(f"Training with safety-critical protocols for session {session.session_id}")

        # Create safety training system
        safety_system = SafetyCriticalTrainingSystem()
        self.safety_trainers[session.session_id] = safety_system
        session.components.append("safety_critical")

        # Train agent
        training_result = await safety_system.train_agent(
            agent_id="test_agent",
            training_scenarios=None,  # Use default scenarios
            num_epochs=50,
        )

        # Save model
        model_path = f"./models/{session.session_id}_safety"
        safety_system.save_training_state(model_path)

        return {
            "metrics": training_result["training_results"],
            "artifacts": {
                "model_id": f"safety_{session.session_id}",
                "model_path": model_path,
                "certification_level": training_result["safety_assessment"]["certification_level"],
            },
        }

    async def _train_with_production(self, session: TrainingSession) -> dict[str, Any]:
        """Train using production pipeline."""
        logger.info(f"Training with production pipeline for session {session.session_id}")

        # Initialize production orchestrator
        if not self.production_orchestrator:
            self.production_orchestrator = TrainingOrchestrator()

        # Submit training job
        job_config = {
            "model_name": session.config.agent_type,
            "trigger": "manual",
            "priority": 5,
            "training_config": session.config.hyperparameters,
            "data_sources": session.config.data_config.get("sources", []),
            "resource_requirements": session.config.deployment_config.get("resources", {}),
        }

        job_id = await self.production_orchestrator.submit_training_job(job_config)

        # Wait for completion (in real implementation, would use proper monitoring)
        await asyncio.sleep(2)  # Simulate waiting

        # Get job status
        job_status = self.production_orchestrator.get_job_status(job_id)

        return {
            "metrics": job_status.get("result", {}).get("performance_metrics", {}),
            "artifacts": {
                "job_id": job_id,
                "job_status": job_status["status"],
                "pipeline_components": ["training", "validation", "deployment"],
            },
        }

    async def _train_with_hybrid(self, session: TrainingSession) -> dict[str, Any]:
        """Train using hybrid approach combining multiple methods."""
        logger.info(f"Training with hybrid approach for session {session.session_id}")

        # Define hybrid strategy based on configuration
        hybrid_strategy = session.config.metadata.get("hybrid_strategy", "sequential")
        components = session.config.metadata.get(
            "components", ["agent_lightning", "safety_critical", "multi_objective"]
        )

        all_results = {}
        all_artifacts = {}

        if hybrid_strategy == "sequential":
            # Run components sequentially
            for component in components:
                # Create temporary config for this component
                temp_config = TrainingConfiguration(
                    mode=TrainingMode(component),
                    integration_level=session.config.integration_level,
                    agent_type=session.config.agent_type,
                    domain=session.config.domain,
                    objectives=session.config.objectives,
                    hyperparameters=session.config.hyperparameters,
                    metadata=session.config.metadata,
                )

                # Train component
                temp_session = TrainingSession(
                    session_id=f"{session.session_id}_{component}",
                    config=temp_config,
                    started_at=datetime.now(),
                    status="running",
                    components=[component],
                )

                try:
                    if component == "agent_lightning":
                        result = await self._train_with_agent_lightning(temp_session)
                    elif component == "safety_critical":
                        result = await self._train_with_safety_critical(temp_session)
                    elif component == "multi_objective":
                        result = await self._train_with_multi_objective(temp_session)
                    else:
                        logger.warning(f"Hybrid component {component} not implemented")
                        continue

                    all_results.update(result["metrics"])
                    all_artifacts.update(result["artifacts"])

                except Exception as e:
                    logger.error(f"Error in hybrid component {component}: {e}")

        elif hybrid_strategy == "parallel":
            # Run components in parallel (simplified for this example)
            tasks = []
            for component in components:
                if component == "agent_lightning":
                    tasks.append(self._train_with_agent_lightning(session))
                elif component == "safety_critical":
                    tasks.append(self._train_with_safety_critical(session))
                elif component == "multi_objective":
                    tasks.append(self._train_with_multi_objective(session))

            # Execute in parallel
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Error in parallel hybrid training: {result}")
                else:
                    all_results.update(result["metrics"])
                    all_artifacts.update(result["artifacts"])

        session.components.extend(components)

        return {"metrics": all_results, "artifacts": all_artifacts, "hybrid_strategy": hybrid_strategy}

    def _generate_mock_data(self, config: TrainingConfiguration) -> dict[str, Any]:
        """Generate mock training data based on configuration."""
        data_size = config.data_config.get("size", 1000)
        feature_dim = config.data_config.get("feature_dim", 64)

        return {
            "features": np.random.randn(data_size, feature_dim).tolist(),
            "labels": np.random.randint(0, 10, data_size).tolist(),
            "metadata": {
                "domain": config.domain,
                "agent_type": config.agent_type,
                "generated_at": datetime.now().isoformat(),
            },
        }

    def _register_model(self, session: TrainingSession):
        """Register trained model in registry."""
        model_info = {
            "session_id": session.session_id,
            "model_name": session.config.agent_type,
            "training_mode": session.config.mode.value,
            "components": session.components,
            "metrics": session.metrics,
            "artifacts": session.artifacts,
            "created_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "status": session.status,
        }

        model_id = session.artifacts.get("model_id", f"{session.config.agent_type}_{session.session_id}")
        self.model_registry[model_id] = model_info

        logger.info(f"Registered model {model_id} in registry")

    def get_session_status(self, session_id: str) -> dict[str, Any] | None:
        """Get status of training session."""
        if session_id in self.active_sessions:
            session = self.active_sessions[session_id]
        elif session_id in [s.session_id for s in self.session_history]:
            session = next(s for s in self.session_history if s.session_id == session_id)
        else:
            return None

        return {
            "session_id": session.session_id,
            "mode": session.config.mode.value,
            "agent_type": session.config.agent_type,
            "status": session.status,
            "components": session.components,
            "metrics": session.metrics,
            "started_at": session.started_at.isoformat(),
            "completed_at": session.completed_at.isoformat() if session.completed_at else None,
            "error_message": session.error_message,
        }

    def get_model_info(self, model_id: str) -> dict[str, Any] | None:
        """Get information about registered model."""
        return self.model_registry.get(model_id)

    def list_models(self, agent_type: str = None, training_mode: str = None) -> dict[str, Any]:
        """List registered models with optional filtering."""
        filtered_models = {}

        for model_id, model_info in self.model_registry.items():
            # Apply filters
            if agent_type and model_info["agent_type"] != agent_type:
                continue
            if training_mode and model_info["training_mode"] != training_mode:
                continue

            filtered_models[model_id] = model_info

        return filtered_models

    def export_model(self, model_id: str, export_format: str = "json") -> str | None:
        """Export model in specified format."""
        model_info = self.model_registry.get(model_id)
        if not model_info:
            return None

        if export_format == "json":
            export_path = f"./exports/{model_id}.json"
            Path("./exports").mkdir(exist_ok=True)

            with open(export_path, "w") as f:
                json.dump(model_info, f, indent=2, default=str)

            return export_path

        return None

    def create_integration_config(self, agent_type: str, domain: str, objectives: list[str]) -> TrainingConfiguration:
        """Create standardized integration configuration."""
        return TrainingConfiguration(
            mode=TrainingMode.HYBRID,
            integration_level=IntegrationLevel.ADVANCED,
            agent_type=agent_type,
            domain=domain,
            objectives=objectives,
            hyperparameters={"epochs": 100, "batch_size": 32, "learning_rate": 0.001},
            data_config={"size": 1000, "feature_dim": 64},
            metadata={
                "hybrid_strategy": "sequential",
                "components": ["agent_lightning", "safety_critical", "multi_objective"],
            },
        )


# CLI interface for unified training
async def main():
    """CLI interface for unified training system."""
    import argparse

    parser = argparse.ArgumentParser(description="Unified Agent Lightning Training Integration")
    parser.add_argument(
        "--action", choices=["train", "status", "list-models", "export"], required=True, help="Action to perform"
    )
    parser.add_argument("--mode", choices=[m.value for m in TrainingMode], default="hybrid", help="Training mode")
    parser.add_argument("--agent-type", default="cad_reviewer", help="Agent type")
    parser.add_argument("--domain", default="mechanical_design", help="Engineering domain")
    parser.add_argument("--objectives", nargs="+", default=["accuracy", "safety"], help="Training objectives")
    parser.add_argument("--session-id", help="Session ID for status check")
    parser.add_argument("--model-id", help="Model ID for export")
    parser.add_argument("--config-file", help="JSON configuration file")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = UnifiedTrainingOrchestrator()

    if args.action == "train":
        # Load config from file if provided
        if args.config_file:
            try:
                with open(args.config_file) as f:
                    config_data = json.load(f)
                # Convert to TrainingConfiguration
                config = TrainingConfiguration(
                    mode=TrainingMode(config_data.get("mode", args.mode)),
                    integration_level=IntegrationLevel(config_data.get("integration_level", "advanced")),
                    agent_type=config_data.get("agent_type", args.agent_type),
                    domain=config_data.get("domain", args.domain),
                    objectives=config_data.get("objectives", args.objectives),
                    hyperparameters=config_data.get("hyperparameters", {}),
                    data_config=config_data.get("data_config", {}),
                    metadata=config_data.get("metadata", {}),
                )
            except Exception as e:
                print(f"Error loading config file: {e}")
                return
        else:
            # Create config from command line arguments
            config = orchestrator.create_integration_config(
                agent_type=args.agent_type, domain=args.domain, objectives=args.objectives
            )
            config.mode = TrainingMode(args.mode)

        # Start training
        print(f"Starting training with mode: {config.mode.value}")
        print(f"Agent type: {config.agent_type}")
        print(f"Domain: {config.domain}")
        print(f"Objectives: {config.objectives}")

        session = await orchestrator.train_agent(config)

        print("\nTraining completed!")
        print(f"Session ID: {session.session_id}")
        print(f"Status: {session.status}")
        print(f"Components: {', '.join(session.components)}")
        print(f"Model ID: {session.artifacts.get('model_id', 'N/A')}")

        if session.metrics:
            print(f"Metrics: {session.metrics}")

    elif args.action == "status":
        if not args.session_id:
            print("Error: --session-id required for status action")
            return

        status = orchestrator.get_session_status(args.session_id)
        if status:
            print("Session Status:")
            print(json.dumps(status, indent=2))
        else:
            print(f"Session {args.session_id} not found")

    elif args.action == "list-models":
        filters = {}
        if args.agent_type:
            filters["agent_type"] = args.agent_type
        if args.mode:
            filters["training_mode"] = args.mode

        models = orchestrator.list_models(**filters)

        print(f"Registered Models ({len(models)} total):")
        for model_id, model_info in models.items():
            print(f"  {model_id}:")
            print(f"    Agent: {model_info['agent_type']}")
            print(f"    Mode: {model_info['training_mode']}")
            print(f"    Status: {model_info['status']}")
            print(f"    Created: {model_info['created_at']}")

    elif args.action == "export":
        if not args.model_id:
            print("Error: --model-id required for export action")
            return

        export_path = orchestrator.export_model(args.model_id)
        if export_path:
            print(f"Model exported to: {export_path}")
        else:
            print(f"Model {args.model_id} not found")


if __name__ == "__main__":
    asyncio.run(main())
