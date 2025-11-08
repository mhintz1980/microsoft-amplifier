"""
Machine learning predictor for CAD analysis.
"""

import json
from pathlib import Path
from typing import Any

import numpy as np

try:
    from agent_lightning import LightningAgent

    AGENT_LIGHTNING_AVAILABLE = True
except ImportError:
    AGENT_LIGHTNING_AVAILABLE = False

from ..utils.logger import get_logger

logger = get_logger(__name__)


class MLPredictor:
    """Machine learning predictor for CAD analysis."""

    def __init__(self):
        self.agent = None
        self.models_loaded = False
        self.model_dir = None

        if AGENT_LIGHTNING_AVAILABLE:
            self.agent = LightningAgent()

    async def load_models(self, model_dir: Path) -> bool:
        """Load trained ML models."""
        try:
            self.model_dir = model_dir

            if AGENT_LIGHTNING_AVAILABLE and self.agent:
                # Load models with Agent Lightning
                await self.agent.load_model(str(model_dir / "cad_model_best"))
                self.models_loaded = True
                logger.info("ML models loaded successfully")
            else:
                # Load mock model
                mock_model_path = model_dir / "mock_model.json"
                if mock_model_path.exists():
                    with open(mock_model_path) as f:
                        self.mock_model = json.load(f)
                    self.models_loaded = True
                    logger.info("Mock ML model loaded successfully")
                else:
                    logger.warning("No model found, using rule-based predictions")
                    self.models_loaded = False

            return self.models_loaded

        except Exception as e:
            logger.error(f"Failed to load ML models: {e}")
            self.models_loaded = False
            return False

    async def predict_acoustic_performance(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Predict acoustic performance using ML models."""
        features = await self._extract_acoustic_features(cad_data)

        if self.models_loaded:
            if AGENT_LIGHTNING_AVAILABLE and self.agent:
                prediction = await self.agent.predict(features)
                return await self._interpret_acoustic_prediction(prediction)
            else:
                return await self._mock_acoustic_prediction(features)
        else:
            return await self._rule_based_acoustic_prediction(cad_data)

    async def predict_structural_performance(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Predict structural performance using ML models."""
        features = await self._extract_structural_features(cad_data)

        if self.models_loaded:
            if AGENT_LIGHTNING_AVAILABLE and self.agent:
                prediction = await self.agent.predict(features)
                return await self._interpret_structural_prediction(prediction)
            else:
                return await self._mock_structural_prediction(features)
        else:
            return await self._rule_based_structural_prediction(cad_data)

    async def predict_manufacturability(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Predict manufacturability using ML models."""
        features = await self._extract_manufacturing_features(cad_data)

        if self.models_loaded:
            if AGENT_LIGHTNING_AVAILABLE and self.agent:
                prediction = await self.agent.predict(features)
                return await self._interpret_manufacturing_prediction(prediction)
            else:
                return await self._mock_manufacturing_prediction(features)
        else:
            return await self._rule_based_manufacturing_prediction(cad_data)

    async def _extract_acoustic_features(self, cad_data: dict[str, Any]) -> list[float]:
        """Extract features for acoustic prediction."""
        features = []

        # Visual features
        if "image_data" in cad_data:
            image = cad_data["image_data"]
            # Basic image statistics
            features.extend(
                [
                    np.mean(image),
                    np.std(image),
                    image.shape[0],  # height
                    image.shape[1],  # width
                ]
            )

        # Geometric features
        if "geometry" in cad_data:
            geometry = cad_data["geometry"]
            features.extend(
                [
                    geometry.get("surface_area", 0),
                    geometry.get("volume", 0),
                    geometry.get("surface_area_to_volume_ratio", 0),
                ]
            )

        # Material properties if available
        if "material_properties" in cad_data:
            material = cad_data["material_properties"]
            features.extend(
                [material.get("density", 0), material.get("youngs_modulus", 0), material.get("poisson_ratio", 0)]
            )

        # Ensure consistent feature length
        while len(features) < 20:
            features.append(0.0)

        return features[:20]

    async def _extract_structural_features(self, cad_data: dict[str, Any]) -> list[float]:
        """Extract features for structural prediction."""
        features = []

        # Geometric features
        if "geometry" in cad_data:
            geometry = cad_data["geometry"]
            features.extend(
                [
                    geometry.get("volume", 0),
                    geometry.get("bounding_box_volume", 0),
                    geometry.get("aspect_ratios", [1.0])[0] if geometry.get("aspect_ratios") else 1.0,
                ]
            )

        # Load and stress information if available
        if "load_conditions" in cad_data:
            loads = cad_data["load_conditions"]
            features.extend(
                [
                    loads.get("max_expected_load", 0),
                    loads.get("safety_factor_required", 2.0),
                    loads.get("operating_temperature", 20),
                ]
            )

        # Material properties
        if "material_properties" in cad_data:
            material = cad_data["material_properties"]
            features.extend(
                [
                    material.get("yield_strength", 0),
                    material.get("ultimate_strength", 0),
                    material.get("youngs_modulus", 0),
                    material.get("fatigue_limit", 0),
                ]
            )

        # Ensure consistent feature length
        while len(features) < 20:
            features.append(0.0)

        return features[:20]

    async def _extract_manufacturing_features(self, cad_data: dict[str, Any]) -> list[float]:
        """Extract features for manufacturability prediction."""
        features = []

        # Geometric complexity
        if "geometry" in cad_data:
            geometry = cad_data["geometry"]
            features.extend(
                [
                    geometry.get("surface_area", 0),
                    geometry.get("volume", 0),
                    geometry.get("surface_area_to_volume_ratio", 0),
                    len(geometry.get("undercuts", [])),
                    len(geometry.get("draft_angles", [])),
                ]
            )

        # Manufacturing constraints
        if "manufacturing_constraints" in cad_data:
            constraints = cad_data["manufacturing_constraints"]
            features.extend(
                [
                    constraints.get("max_tool_diameter", 10),
                    constraints.get("min_feature_size", 0.1),
                    constraints.get("tolerance_requirement", 0.1),
                ]
            )

        # Material properties affecting manufacturability
        if "material_properties" in cad_data:
            material = cad_data["material_properties"]
            features.extend(
                [
                    material.get("hardness", 0),
                    material.get("machinability_rating", 0.5),
                    material.get("tool_wear_factor", 1.0),
                ]
            )

        # Ensure consistent feature length
        while len(features) < 20:
            features.append(0.0)

        return features[:20]

    async def _interpret_acoustic_prediction(self, prediction: Any) -> dict[str, Any]:
        """Interpret ML prediction for acoustic analysis."""
        # This would interpret the actual ML model output
        return {
            "predicted_stc": prediction.get("stc", 40.0),
            "resonance_frequencies": prediction.get("resonances", [125, 250, 500, 1000]),
            "transmission_loss_spectrum": {
                "125Hz": prediction.get("tl_125", 20),
                "250Hz": prediction.get("tl_250", 25),
                "500Hz": prediction.get("tl_500", 30),
                "1000Hz": prediction.get("tl_1000", 35),
                "2000Hz": prediction.get("tl_2000", 40),
            },
        }

    async def _interpret_structural_prediction(self, prediction: Any) -> dict[str, Any]:
        """Interpret ML prediction for structural analysis."""
        return {
            "safety_factors": {
                "overall": prediction.get("safety_factor", 2.5),
                "critical_section": prediction.get("critical_sf", 2.0),
            },
            "critical_loads": [
                {
                    "location": "main_support",
                    "critical_load": prediction.get("critical_load", 1000),
                    "safety_factor": prediction.get("safety_factor", 2.5),
                }
            ],
            "deformation_analysis": {
                "max_deformation": prediction.get("max_deflection", 0.1),
                "location": "center_span",
            },
        }

    async def _interpret_manufacturing_prediction(self, prediction: Any) -> dict[str, Any]:
        """Interpret ML prediction for manufacturing analysis."""
        return {
            "cnc_feasibility": prediction.get("feasibility", 0.8),
            "estimated_cost": prediction.get("cost", 100.0),
            "machining_time": prediction.get("time", 2.5),
            "material_waste": prediction.get("waste", 15.0),
        }

    async def _mock_acoustic_prediction(self, features: list[float]) -> dict[str, Any]:
        """Mock acoustic prediction for development."""
        # Simulate prediction based on features
        base_stc = 35.0
        complexity_factor = np.std(features) if features else 1.0

        predicted_stc = base_stc + complexity_factor * 5.0 + np.random.normal(0, 2)
        predicted_stc = max(20, min(60, predicted_stc))  # Clamp to reasonable range

        # Generate resonance frequencies
        base_frequencies = [125, 250, 500, 1000, 2000]
        resonances = [f * (1 + np.random.normal(0, 0.1)) for f in base_frequencies]

        return {
            "predicted_stc": predicted_stc,
            "resonance_frequencies": resonances,
            "transmission_loss_spectrum": {
                "125Hz": predicted_stc * 0.6,
                "250Hz": predicted_stc * 0.7,
                "500Hz": predicted_stc * 0.8,
                "1000Hz": predicted_stc * 0.9,
                "2000Hz": predicted_stc,
            },
        }

    async def _mock_structural_prediction(self, features: list[float]) -> dict[str, Any]:
        """Mock structural prediction for development."""
        # Simulate safety factors based on features
        base_safety = 2.5
        volume_factor = features[2] / 1000 if len(features) > 2 else 1.0

        overall_sf = base_safety * (1 + volume_factor * 0.1) + np.random.normal(0, 0.2)
        critical_sf = overall_sf * 0.8

        return {
            "safety_factors": {"overall": max(1.0, overall_sf), "critical_section": max(1.0, critical_sf)},
            "critical_loads": [
                {"location": "main_support", "critical_load": 1000 * overall_sf, "safety_factor": overall_sf}
            ],
            "deformation_analysis": {"max_deformation": 0.1 / overall_sf, "location": "center_span"},
        }

    async def _mock_manufacturing_prediction(self, features: list[float]) -> dict[str, Any]:
        """Mock manufacturing prediction for development."""
        # Simulate manufacturability based on complexity
        complexity = np.std(features[:10]) if len(features) >= 10 else 1.0

        cnc_feasibility = max(0.1, 1.0 - complexity * 0.1)
        estimated_cost = 50 + complexity * 100 + np.random.normal(0, 10)
        machining_time = 1.0 + complexity * 3.0 + np.random.normal(0, 0.5)
        material_waste = 10 + complexity * 20 + np.random.normal(0, 5)

        return {
            "cnc_feasibility": max(0.0, min(1.0, cnc_feasibility)),
            "estimated_cost": max(0, estimated_cost),
            "machining_time": max(0.1, machining_time),
            "material_waste": max(0, min(100, material_waste)),
        }

    async def _rule_based_acoustic_prediction(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Rule-based acoustic prediction when ML models are not available."""
        # Simple rule-based predictions
        predicted_stc = 40.0  # Default STC rating

        # Adjust based on visual analysis
        if "acoustic_features" in cad_data:
            features = cad_data["acoustic_features"]
            openings = len(features.get("openings", []))
            thin_sections = len(features.get("thin_sections", []))

            # Reduce STC for each acoustic issue
            predicted_stc -= openings * 2.0
            predicted_stc -= thin_sections * 1.5

        predicted_stc = max(20, min(60, predicted_stc))

        return {
            "predicted_stc": predicted_stc,
            "resonance_frequencies": [125, 250, 500, 1000, 2000],
            "transmission_loss_spectrum": {
                "125Hz": predicted_stc * 0.6,
                "250Hz": predicted_stc * 0.7,
                "500Hz": predicted_stc * 0.8,
                "1000Hz": predicted_stc * 0.9,
                "2000Hz": predicted_stc,
            },
        }

    async def _rule_based_structural_prediction(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Rule-based structural prediction when ML models are not available."""
        # Default safety factors
        overall_sf = 2.5
        critical_sf = 2.0

        # Adjust based on structural features
        if "structural_features" in cad_data:
            features = cad_data["structural_features"]
            stress_points = len(features.get("stress_concentrations", []))
            len(features.get("connections", []))

            # Reduce safety factors for structural issues
            overall_sf -= stress_points * 0.1
            critical_sf -= stress_points * 0.15

        overall_sf = max(1.0, overall_sf)
        critical_sf = max(1.0, critical_sf)

        return {
            "safety_factors": {"overall": overall_sf, "critical_section": critical_sf},
            "critical_loads": [
                {"location": "main_support", "critical_load": 1000 * overall_sf, "safety_factor": overall_sf}
            ],
            "deformation_analysis": {"max_deformation": 0.1 / overall_sf, "location": "center_span"},
        }

    async def _rule_based_manufacturing_prediction(self, cad_data: dict[str, Any]) -> dict[str, Any]:
        """Rule-based manufacturing prediction when ML models are not available."""
        # Default manufacturability
        cnc_feasibility = 0.8
        estimated_cost = 100.0
        machining_time = 2.5
        material_waste = 15.0

        # Adjust based on manufacturing features
        if "manufacturing_features" in cad_data:
            features = cad_data["manufacturing_features"]
            tool_issues = len(features.get("tool_access_issues", []))
            complex_features = len(features.get("complex_features", []))

            # Reduce feasibility and increase cost for manufacturing issues
            cnc_feasibility -= tool_issues * 0.1
            cnc_feasibility -= complex_features * 0.05
            estimated_cost += tool_issues * 20
            estimated_cost += complex_features * 10

        cnc_feasibility = max(0.0, min(1.0, cnc_feasibility))

        return {
            "cnc_feasibility": cnc_feasibility,
            "estimated_cost": estimated_cost,
            "machining_time": machining_time,
            "material_waste": material_waste,
        }
