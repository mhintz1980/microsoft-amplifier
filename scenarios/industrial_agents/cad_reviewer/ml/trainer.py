"""
Machine learning training pipeline using Agent Lightning.
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

try:
    from agent_lightning import LightningAgent, TrainingConfig

    AGENT_LIGHTNING_AVAILABLE = True
except ImportError:
    AGENT_LIGHTNING_AVAILABLE = False
    print("Warning: Agent Lightning not available. Using mock ML implementation.")

from ..core.models import TrainingData
from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelTrainer:
    """Machine learning model trainer for CAD analysis."""

    def __init__(self):
        self.agent = None
        if AGENT_LIGHTNING_AVAILABLE:
            self.agent = LightningAgent()
        else:
            logger.warning("Using mock ML implementation - Agent Lightning not installed")

    async def train(
        self, data_dir: Path, model_dir: Path, epochs: int = 100, validation_split: float = 0.2
    ) -> dict[str, Any]:
        """Train ML models on CAD design data."""
        logger.info(f"Starting training with data from {data_dir}")

        # Load training data
        training_data = await self._load_training_data(data_dir)
        if not training_data:
            raise ValueError("No training data found")

        # Prepare data for training
        X_train, y_train, X_val, y_val = await self._prepare_training_data(training_data, validation_split)

        if AGENT_LIGHTNING_AVAILABLE and self.agent:
            # Use Agent Lightning for training
            metrics = await self._train_with_lightning(X_train, y_train, X_val, y_val, model_dir, epochs)
        else:
            # Mock training for development
            metrics = await self._mock_train(X_train, y_train, X_val, y_val, model_dir, epochs)

        # Save model metadata
        await self._save_model_metadata(model_dir, metrics, training_data)

        logger.info(f"Training completed. Model saved to {model_dir}")
        return metrics

    async def validate(self, model_dir: Path, test_dir: Path) -> dict[str, Any]:
        """Validate trained model on test data."""
        logger.info(f"Validating model {model_dir} on test data from {test_dir}")

        # Load test data
        test_data = await self._load_training_data(test_dir)
        if not test_data:
            raise ValueError("No test data found")

        # Prepare test data
        X_test, y_test = await self._prepare_test_data(test_data)

        if AGENT_LIGHTNING_AVAILABLE and self.agent:
            # Use Agent Lightning for validation
            metrics = await self._validate_with_lightning(model_dir, X_test, y_test)
        else:
            # Mock validation
            metrics = await self._mock_validate(X_test, y_test)

        logger.info(f"Validation completed. Test accuracy: {metrics['test_accuracy']:.4f}")
        return metrics

    async def _load_training_data(self, data_dir: Path) -> list[TrainingData]:
        """Load training data from directory."""
        training_data = []

        # Look for JSON files with training data
        for json_file in data_dir.glob("**/*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)

                # Convert to TrainingData objects
                if "expert_rating" in data and "expert_recommendations" in data:
                    training_data.append(TrainingData(**data))

            except Exception as e:
                logger.warning(f"Failed to load training data from {json_file}: {e}")

        logger.info(f"Loaded {len(training_data)} training samples")
        return training_data

    async def _prepare_training_data(
        self, training_data: list[TrainingData], validation_split: float
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Prepare data for ML training."""
        X = []
        y = []

        for data in training_data:
            # Extract features from CAD data
            features = await self._extract_features(data)
            X.append(features)

            # Target is the expert rating
            y.append(data.expert_rating)

        X = np.array(X)
        y = np.array(y)

        # Split into train/validation
        split_idx = int(len(X) * (1 - validation_split))
        X_train, X_val = X[:split_idx], X[split_idx:]
        y_train, y_val = y[:split_idx], y[split_idx:]

        return X_train, y_train, X_val, y_val

    async def _prepare_test_data(self, test_data: list[TrainingData]) -> tuple[np.ndarray, np.ndarray]:
        """Prepare test data for validation."""
        X = []
        y = []

        for data in test_data:
            features = await self._extract_features(data)
            X.append(features)
            y.append(data.expert_rating)

        return np.array(X), np.array(y)

    async def _extract_features(self, data: TrainingData) -> list[float]:
        """Extract features from training data."""
        features = []

        # Basic features
        features.append(data.expert_rating)
        features.append(len(data.expert_recommendations))

        # Extract features from recommendations
        critical_count = sum(1 for r in data.expert_recommendations if r.severity.value == "critical")
        high_count = sum(1 for r in data.expert_recommendations if r.severity.value == "high")
        features.append(critical_count)
        features.append(high_count)

        # Acoustic features
        if data.acoustic_data:
            features.append(data.acoustic_data.predicted_stc or 0)
            features.append(len(data.acoustic_data.weak_points))
            features.append(data.acoustic_data.overall_rating or 0)
        else:
            features.extend([0, 0, 0])

        # Structural features
        if data.structural_data:
            features.append(len(data.structural_data.stress_concentrations))
            features.append(data.structural_data.overall_rating or 0)
            safety_factors = list(data.structural_data.safety_factors.values())
            features.append(np.mean(safety_factors) if safety_factors else 0)
        else:
            features.extend([0, 0, 0])

        # Manufacturing features
        if data.manufacturing_data:
            features.append(data.manufacturing_data.cnc_feasibility)
            features.append(len(data.manufacturing_data.tool_access_issues))
            features.append(data.manufacturing_data.overall_rating or 0)
        else:
            features.extend([0, 0, 0])

        return features

    async def _train_with_lightning(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        model_dir: Path,
        epochs: int,
    ) -> dict[str, Any]:
        """Train using Agent Lightning."""
        config = TrainingConfig(epochs=epochs, batch_size=32, learning_rate=0.001, validation_split=0.2)

        # Prepare data for Lightning
        train_data = {"X": X_train.tolist(), "y": y_train.tolist()}
        val_data = {"X": X_val.tolist(), "y": y_val.tolist()}

        # Train model
        result = await self.agent.train(
            train_data=train_data, val_data=val_data, config=config, model_path=str(model_dir / "cad_model")
        )

        return {
            "final_loss": result.get("final_loss", 0.0),
            "final_accuracy": result.get("final_accuracy", 0.0),
            "best_model_path": str(model_dir / "cad_model_best"),
            "training_time": result.get("training_time", 0.0),
            "epochs_trained": epochs,
        }

    async def _mock_train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray,
        y_val: np.ndarray,
        model_dir: Path,
        epochs: int,
    ) -> dict[str, Any]:
        """Mock training for development without Agent Lightning."""
        logger.info("Using mock training implementation")

        # Simulate training progress
        import time

        start_time = time.time()

        best_accuracy = 0.0
        final_loss = 1.0

        for epoch in range(epochs):
            # Simulate training loss decreasing
            final_loss = final_loss * 0.95 + 0.1

            # Simulate accuracy improving
            current_accuracy = min(0.95, best_accuracy + 0.01)
            best_accuracy = max(best_accuracy, current_accuracy)

            if epoch % 10 == 0:
                logger.info(f"Epoch {epoch}: Loss={final_loss:.4f}, Accuracy={current_accuracy:.4f}")

            await asyncio.sleep(0.01)  # Simulate training time

        training_time = time.time() - start_time

        # Save mock model
        model_dir.mkdir(parents=True, exist_ok=True)
        with open(model_dir / "mock_model.json", "w") as f:
            json.dump(
                {
                    "model_type": "mock_cad_analyzer",
                    "features": X_train.shape[1],
                    "training_date": datetime.now().isoformat(),
                    "final_accuracy": best_accuracy,
                    "final_loss": final_loss,
                },
                f,
            )

        return {
            "final_loss": final_loss,
            "final_accuracy": best_accuracy,
            "best_model_path": str(model_dir / "mock_model.json"),
            "training_time": training_time,
            "epochs_trained": epochs,
        }

    async def _validate_with_lightning(self, model_dir: Path, X_test: np.ndarray, y_test: np.ndarray) -> dict[str, Any]:
        """Validate using Agent Lightning."""
        test_data = {"X": X_test.tolist(), "y": y_test.tolist()}

        result = await self.agent.evaluate(model_path=str(model_dir / "cad_model_best"), test_data=test_data)

        return {
            "test_accuracy": result.get("accuracy", 0.0),
            "test_loss": result.get("loss", 0.0),
            "precision": result.get("precision", 0.0),
            "recall": result.get("recall", 0.0),
            "f1_score": result.get("f1_score", 0.0),
        }

    async def _mock_validate(self, X_test: np.ndarray, y_test: np.ndarray) -> dict[str, Any]:
        """Mock validation for development."""
        logger.info("Using mock validation implementation")

        # Simulate validation metrics
        accuracy = 0.85 + np.random.normal(0, 0.05)
        loss = 0.3 + np.random.normal(0, 0.05)
        precision = 0.82 + np.random.normal(0, 0.03)
        recall = 0.88 + np.random.normal(0, 0.03)
        f1_score = 2 * (precision * recall) / (precision + recall)

        return {
            "test_accuracy": max(0, min(1, accuracy)),
            "test_loss": max(0, loss),
            "precision": max(0, min(1, precision)),
            "recall": max(0, min(1, recall)),
            "f1_score": max(0, min(1, f1_score)),
        }

    async def _save_model_metadata(
        self, model_dir: Path, metrics: dict[str, Any], training_data: list[TrainingData]
    ) -> None:
        """Save model metadata."""
        metadata = {
            "training_date": datetime.now().isoformat(),
            "num_training_samples": len(training_data),
            "metrics": metrics,
            "data_sources": [data.cad_file_path for data in training_data],
            "model_version": "1.0.0",
        }

        with open(model_dir / "metadata.json", "w") as f:
            json.dump(metadata, f, indent=2)

        logger.info(f"Model metadata saved to {model_dir / 'metadata.json'}")
