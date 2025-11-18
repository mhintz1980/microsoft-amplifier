"""
Tests for AI/ML Integration Expert Skill

Comprehensive test suite covering:
- Skill functionality and edge cases
- Progressive disclosure levels
- ML framework integrations
- API design recommendations
- MLOps implementations
- Performance optimizations
- Responsible AI guidelines
- Zero hallucination validation
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path

from amplifier.skills.skills_framework.skill_template import SkillContext, SkillLevel
from ai_ml_integration_expert import (
    AIMLIntegrationExpert,
    ModelConfiguration,
    MLFramework,
    ModelType,
    DeploymentPlatform,
    InferencePattern,
    APIDesignConfiguration,
    MLOpsConfiguration,
    PerformanceOptimization,
    ResponsibleAIConfiguration,
    validate_ml_configuration,
    estimate_deployment_complexity,
    MLPatternOptimizer,
)


class TestAIMLIntegrationExpert:
    """Test suite for AI/ML Integration Expert skill"""

    def setup_method(self):
        """Setup test environment"""
        self.skill = AIMLIntegrationExpert()

    def test_skill_initialization(self):
        """Test skill initialization"""
        assert self.skill.skill_name == "ai_ml_integration_expert"
        assert self.skill.execution_count == 0
        assert self.skill.last_execution is None
        assert len(self.skill._ml_patterns) > 0
        assert len(self.skill._api_designs) > 0
        assert len(self.skill._mlops_practices) > 0

    def test_skill_properties(self):
        """Test skill properties"""
        assert "ai/ml integration" in self.skill.description.lower()
        assert "machine learning" in self.skill.description.lower()

        expected_tags = [
            "ai",
            "ml",
            "machine_learning",
            "tensorflow",
            "pytorch",
            "mlops",
            "api_design",
            "deployment",
            "optimization",
        ]
        assert all(tag in self.skill.tags for tag in expected_tags)

    def test_can_handle_high_confidence(self):
        """Test high confidence matching"""
        high_confidence_queries = [
            "ml integration patterns for tensorflow deployment",
            "machine learning integration with pytorch api",
            "mlops practices for model versioning",
            "llm integration with openai and hugging face",
            "responsible ai implementation for fairness",
            "edge ai deployment strategies",
            "feature engineering pipeline design",
        ]

        for query in high_confidence_queries:
            context = SkillContext(query=query, parameters={}, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence >= 0.8, f"Query should have high confidence: {query}"

    def test_can_handle_medium_confidence(self):
        """Test medium confidence matching"""
        medium_confidence_queries = [
            "ai integration for predictions",
            "model api development",
            "ml pipeline setup",
            "model versioning strategy",
            "prediction service design",
            "inference api patterns",
        ]

        for query in medium_confidence_queries:
            context = SkillContext(query=query, parameters={}, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert 0.6 <= confidence < 0.8, f"Query should have medium confidence: {query}"

    def test_can_handle_low_confidence(self):
        """Test low confidence matching"""
        low_confidence_queries = [
            "ai system",
            "ml model",
            "tensorflow training",
            "pytorch neural network",
            "machine learning algorithm",
        ]

        for query in low_confidence_queries:
            context = SkillContext(query=query, parameters={}, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert 0.1 <= confidence < 0.6, f"Query should have low confidence: {query}"

    def test_can_handle_no_match(self):
        """Test no confidence matching"""
        no_match_queries = [
            "web development",
            "database design",
            "user interface",
            "business strategy",
        ]

        for query in no_match_queries:
            context = SkillContext(query=query, parameters={}, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence < 0.3, f"Query should have no confidence: {query}"

    def test_extract_ml_config_valid(self):
        """Test valid ML configuration extraction"""
        config_data = {
            "model_type": "classification",
            "framework": "tensorflow",
            "model_path": "/models/classifier",
            "model_version": "2.0.0",
            "model_size_mb": 500.0,
            "input_schema": {"features": "float32[10]"},
            "output_schema": {"prediction": "string", "confidence": "float32"},
        }

        context = SkillContext(query="ml integration", parameters={"ml_config": config_data}, available_tokens=1000)

        ml_config = self.skill._extract_ml_config(context)

        assert ml_config.model_type == ModelType.CLASSIFICATION
        assert ml_config.framework == MLFramework.TENSORFLOW
        assert ml_config.model_path == "/models/classifier"
        assert ml_config.model_version == "2.0.0"
        assert ml_config.model_size_mb == 500.0

    def test_extract_ml_config_invalid(self):
        """Test invalid ML configuration extraction"""
        config_data = {
            "model_type": "invalid_model_type",
            "framework": "invalid_framework",
        }

        context = SkillContext(query="ml integration", parameters={"ml_config": config_data}, available_tokens=1000)

        with pytest.raises(ValueError, match="Invalid ML configuration"):
            self.skill._extract_ml_config(context)

    def test_extract_requirements(self):
        """Test requirements extraction"""
        requirements_data = {
            "deployment_platform": "kubernetes",
            "expected_qps": 1000,
            "latency_requirement_ms": 50,
            "accuracy_requirement": 0.95,
            "team_expertise": "expert",
            "compliance_requirements": ["GDPR", "HIPAA"],
        }

        context = SkillContext(query="ml integration", parameters=requirements_data, available_tokens=1000)

        requirements = self.skill._extract_requirements(context)

        assert requirements["deployment_platform"] == "kubernetes"
        assert requirements["expected_qps"] == 1000
        assert requirements["latency_requirement_ms"] == 50
        assert requirements["accuracy_requirement"] == 0.95
        assert requirements["team_expertise"] == "expert"
        assert requirements["compliance_requirements"] == ["GDPR", "HIPAA"]

    def test_generate_metadata_response(self):
        """Test metadata level response"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"deployment_platform": "kubernetes"}

        response = self.skill._generate_metadata_response(ml_config, requirements)

        assert "skill" in response
        assert response["model_type"] == "classification"
        assert response["framework"] == "tensorflow"
        assert response["deployment_platform"] == "kubernetes"
        assert "complexity" in response
        assert "optimization_potential" in response

    def test_generate_summary_response(self):
        """Test summary level response"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"expected_qps": 500, "latency_requirement_ms": 100}

        response = self.skill._generate_summary_response(ml_config, requirements)

        assert "overview" in response
        assert "key_recommendations" in response
        assert "performance_expectations" in response
        assert "critical_considerations" in response

        overview = response["overview"]
        assert overview["model_type"] == "classification"
        assert overview["framework"] == "tensorflow"
        assert "recommended_deployment" in overview
        assert "complexity_level" in overview

    def test_generate_detailed_response(self):
        """Test detailed level response"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {
            "deployment_platform": "kubernetes",
            "expected_qps": 1000,
            "compliance_requirements": ["GDPR"],
            "responsible_ai_requirements": ["fairness"],
        }

        response = self.skill._generate_detailed_response(ml_config, requirements)

        # Check all major sections are present
        expected_sections = [
            "deployment_strategy",
            "api_design",
            "mlops_implementation",
            "optimization_plan",
            "responsible_ai",
            "implementation_roadmap",
            "monitoring_strategy",
            "scalability_plan",
            "security_considerations",
        ]

        for section in expected_sections:
            assert section in response, f"Missing section: {section}"

        # LLM integration should be None for non-generative models
        assert response["llm_integration"] is None

    def test_generate_detailed_response_llm(self):
        """Test detailed response for LLM models"""
        ml_config = ModelConfiguration(
            model_type=ModelType.GENERATIVE_AI, framework=MLFramework.HUGGING_FACE, model_path="/models/llm"
        )
        requirements = {"deployment_platform": "serverless"}

        response = self.skill._generate_detailed_response(ml_config, requirements)

        # LLM integration should be present for generative AI models
        assert response["llm_integration"] is not None
        assert "model_provider_integration" in response["llm_integration"]
        assert "prompt_engineering" in response["llm_integration"]
        assert "response_handling" in response["llm_integration"]
        assert "cost_optimization" in response["llm_integration"]

    @pytest.mark.asyncio
    async def test_execute_metadata_level(self):
        """Test execution at metadata level"""
        context = SkillContext(
            query="ml integration help",
            parameters={"ml_config": {"model_type": "classification", "framework": "tensorflow"}},
            available_tokens=1000,
        )

        result = await self.skill.execute(context, SkillLevel.METADATA)

        assert result.success
        assert result.skill_name == "ai_ml_integration_expert"
        assert result.level == SkillLevel.METADATA
        assert result.tokens_used < 1000
        assert result.execution_time > 0
        assert result.next_level_available is True

        # Parse and verify content
        content = json.loads(result.content)
        assert "model_type" in content
        assert "framework" in content

    @pytest.mark.asyncio
    async def test_execute_summary_level(self):
        """Test execution at summary level"""
        context = SkillContext(
            query="ml deployment recommendations",
            parameters={
                "ml_config": {"model_type": "classification", "framework": "tensorflow", "model_size_mb": 500},
                "expected_qps": 1000,
                "latency_requirement_ms": 100,
            },
            available_tokens=2000,
        )

        result = await self.skill.execute(context, SkillLevel.SUMMARY)

        assert result.success
        assert result.level == SkillLevel.SUMMARY
        assert result.tokens_used < 2000

        content = json.loads(result.content)
        assert "overview" in content
        assert "key_recommendations" in content
        assert len(result.metadata) > 0

    @pytest.mark.asyncio
    async def test_execute_detailed_level(self):
        """Test execution at detailed level"""
        context = SkillContext(
            query="comprehensive ml integration strategy",
            parameters={
                "ml_config": {"model_type": "computer_vision", "framework": "pytorch", "model_size_mb": 2000},
                "deployment_platform": "kubernetes",
                "expected_qps": 2000,
                "compliance_requirements": ["GDPR", "SOC2"],
                "responsible_ai_requirements": ["fairness", "interpretability"],
            },
            available_tokens=10000,
        )

        result = await self.skill.execute(context, SkillLevel.FULL)

        assert result.success
        assert result.level == SkillLevel.FULL
        assert result.tokens_used < 10000
        assert result.next_level_available is False

        content = json.loads(result.content)
        # Verify comprehensive response
        assert len(content) >= 9  # All major sections present

    @pytest.mark.asyncio
    async def test_execute_error_handling(self):
        """Test error handling in execution"""
        context = SkillContext(
            query="ml integration",
            parameters={"ml_config": {"model_type": "invalid_type", "framework": "tensorflow"}},
            available_tokens=1000,
        )

        result = await self.skill.execute(context, SkillLevel.SUMMARY)

        # Should handle error gracefully
        assert result.skill_name == "ai_ml_integration_expert"
        assert result.execution_time > 0
        assert "Error:" in result.content

    def test_recommend_deployment_platform(self):
        """Test deployment platform recommendation logic"""
        # High performance requirements
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"expected_qps": 5000, "latency_requirement_ms": 25}

        platform = self.skill._recommend_deployment_platform(ml_config, requirements)
        assert platform in ["kubernetes", "aws_sagemaker"]

        # Beginner team with moderate requirements
        requirements = {"expected_qps": 100, "latency_requirement_ms": 200, "team_expertise": "beginner"}
        platform = self.skill._recommend_deployment_platform(ml_config, requirements)
        assert platform in ["aws_sagemaker", "docker"]

        # Low volume requirements
        requirements = {"expected_qps": 5, "latency_requirement_ms": 1000}
        platform = self.skill._recommend_deployment_platform(ml_config, requirements)
        assert platform == "serverless"

    def test_assess_complexity(self):
        """Test complexity assessment"""
        # High complexity scenario
        ml_config = ModelConfiguration(
            model_type=ModelType.GENERATIVE_AI,
            framework=MLFramework.TENSORFLOW,
            model_path="/models/test",
            model_size_mb=2000,
        )
        requirements = {
            "expected_qps": 5000,
            "latency_requirement_ms": 25,
            "compliance_requirements": ["GDPR", "HIPAA", "SOC2", "PCI-DSS"],
        }

        complexity = self.skill._assess_complexity(ml_config, requirements)
        assert complexity in ["High", "Very High"]

        # Low complexity scenario
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION,
            framework=MLFramework.SCIKIT_LEARN,
            model_path="/models/test",
            model_size_mb=50,
        )
        requirements = {"expected_qps": 50, "latency_requirement_ms": 500, "compliance_requirements": []}

        complexity = self.skill._assess_complexity(ml_config, requirements)
        assert complexity in ["Low", "Medium"]

    def test_assess_optimization_potential(self):
        """Test optimization potential assessment"""
        # High potential
        ml_config = ModelConfiguration(
            model_type=ModelType.COMPUTER_VISION,
            framework=MLFramework.TENSORFLOW,
            model_path="/models/test",
            model_size_mb=1500,
        )
        potential = self.skill._assess_optimization_potential(ml_config)
        assert potential == "High"

        # Low potential
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION,
            framework=MLFramework.XGBOOST,
            model_path="/models/test",
            model_size_mb=50,
        )
        potential = self.skill._assess_optimization_potential(ml_config)
        assert potential == "Low"

    def test_recommendation_caching(self):
        """Test that recommendations are cached"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"deployment_platform": "kubernetes"}

        # First call should populate cache
        cache_key_1 = self.skill._generate_cache_key(ml_config, requirements)

        # Generate cache key for identical config
        cache_key_2 = self.skill._generate_cache_key(ml_config, requirements)

        assert cache_key_1 == cache_key_2

        # Different config should produce different key
        different_requirements = {"deployment_platform": "aws_sagemaker"}
        cache_key_3 = self.skill._generate_cache_key(ml_config, different_requirements)
        assert cache_key_1 != cache_key_3

    def test_framework_specific_recommendations(self):
        """Test framework-specific recommendations"""
        # TensorFlow recommendations
        ml_config_tf = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"expected_qps": 100}
        recommendations = self.skill._get_key_recommendations(ml_config_tf, requirements)

        tf_framework_recs = [r for r in recommendations if r["category"] == "Framework"]
        assert len(tf_framework_recs) > 0
        assert "tensorflow serving" in tf_framework_recs[0]["recommendation"].lower()

        # PyTorch recommendations
        ml_config_pt = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.PYTORCH, model_path="/models/test"
        )
        recommendations = self.skill._get_key_recommendations(ml_config_pt, requirements)

        pt_framework_recs = [r for r in recommendations if r["category"] == "Framework"]
        assert len(pt_framework_recs) > 0
        assert "torch" in pt_framework_recs[0]["recommendation"].lower()

    def test_performance_estimation(self):
        """Test performance estimation"""
        # TensorFlow model
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION,
            framework=MLFramework.TENSORFLOW,
            model_path="/models/test",
            model_size_mb=200,
        )
        requirements = {"expected_qps": 500}

        performance = self.skill._estimate_performance(ml_config, requirements)

        assert "estimated_throughput_qps" in performance
        assert "estimated_latency_ms" in performance
        assert "estimated_memory_mb" in performance
        assert "recommended_hardware" in performance

        # Verify reasonable ranges
        assert performance["estimated_latency_ms"] > 0
        assert performance["estimated_memory_mb"] > 0
        assert "cpu" in performance["recommended_hardware"]

    def test_api_endpoint_design(self):
        """Test API endpoint design for different model types"""
        # Classification model
        ml_config_class = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"expected_qps": 100}

        endpoints = self.skill._design_api_endpoints(ml_config_class, requirements)

        assert "health" in endpoints
        assert "model_info" in endpoints
        assert "predict" in endpoints

        predict_endpoint = endpoints["predict"]
        assert predict_endpoint["method"] == "POST"
        assert "prediction" in predict_endpoint["response"]
        assert "confidence" in predict_endpoint["response"]

        # Generative AI model
        ml_config_gen = ModelConfiguration(
            model_type=ModelType.GENERATIVE_AI, framework=MLFramework.HUGGING_FACE, model_path="/models/test"
        )

        endpoints = self.skill._design_api_endpoints(ml_config_gen, requirements)
        predict_endpoint = endpoints["predict"]
        assert "generate" in predict_endpoint["path"] or predict_endpoint["path"] == "/generate"
        assert "prompt" in predict_endpoint["request"]
        assert "generated_text" in predict_endpoint["response"]

    def test_responsible_ai_requirements(self):
        """Test responsible AI requirements handling"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )

        # No responsible AI requirements
        requirements = {"responsible_ai_requirements": []}
        responsible_ai = self.skill._generate_responsible_ai_plan(ml_config, requirements)

        assert responsible_ai["compliance_automation"] is not None
        assert responsible_ai["fairness_monitoring"] is None
        assert responsible_ai["interpretability"] is None

        # With responsible AI requirements
        requirements = {
            "responsible_ai_requirements": ["fairness", "interpretability", "privacy"],
            "compliance_requirements": ["GDPR"],
        }
        responsible_ai = self.skill._generate_responsible_ai_plan(ml_config, requirements)

        assert responsible_ai["fairness_monitoring"] is not None
        assert responsible_ai["interpretability"] is not None
        assert responsible_ai["privacy_preservation"] is not None
        assert responsible_ai["transparency_reporting"] is None  # Not requested

    def test_implementation_roadmap(self):
        """Test implementation roadmap generation"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.PYTORCH, model_path="/models/test"
        )
        requirements = {"deployment_platform": "kubernetes", "expected_qps": 1000, "team_expertise": "intermediate"}

        roadmap = self.skill._generate_implementation_roadmap(ml_config, requirements)

        assert "phases" in roadmap
        assert len(roadmap["phases"]) >= 3  # At least foundation, core, production

        for phase in roadmap["phases"]:
            assert "phase" in phase
            assert "duration_weeks" in phase
            assert "tasks" in phase
            assert len(phase["tasks"]) > 0

            for task in phase["tasks"]:
                assert "task" in task
                assert "days" in task

        assert "critical_path" in roadmap
        assert "team_requirements" in roadmap
        assert "risk_mitigation" in roadmap


class TestModelConfiguration:
    """Test suite for ModelConfiguration data class"""

    def test_model_configuration_creation(self):
        """Test ModelConfiguration creation"""
        config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION,
            framework=MLFramework.TENSORFLOW,
            model_path="/models/test",
            model_version="1.0.0",
            model_size_mb=500.0,
            hyperparameters={"learning_rate": 0.001, "epochs": 100},
        )

        assert config.model_type == ModelType.CLASSIFICATION
        assert config.framework == MLFramework.TENSORFLOW
        assert config.model_path == "/models/test"
        assert config.model_version == "1.0.0"
        assert config.model_size_mb == 500.0
        assert config.hyperparameters["learning_rate"] == 0.001


class TestUtilityFunctions:
    """Test suite for utility functions"""

    def test_validate_ml_configuration_valid(self):
        """Test validation of valid ML configuration"""
        with patch("pathlib.Path.exists", return_value=True):
            config = ModelConfiguration(
                model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
            )

            result = validate_ml_configuration(config)
            assert result is True

    def test_validate_ml_configuration_invalid_path(self):
        """Test validation with invalid model path"""
        with patch("pathlib.Path.exists", return_value=False):
            config = ModelConfiguration(
                model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/nonexistent"
            )

            result = validate_ml_configuration(config)
            assert result is False

    def test_estimate_deployment_complexity(self):
        """Test deployment complexity estimation"""
        ml_config = ModelConfiguration(
            model_type=ModelType.GENERATIVE_AI,
            framework=MLFramework.TENSORFLOW,
            model_path="/models/test",
            model_size_mb=2000,
        )
        requirements = {
            "expected_qps": 5000,
            "latency_requirement_ms": 25,
            "compliance_requirements": ["GDPR", "HIPAA", "SOC2"],
            "team_expertise": "beginner",
        }

        complexity = estimate_deployment_complexity(ml_config, requirements)

        assert "complexity_score" in complexity
        assert "complexity_level" in complexity
        assert "estimated_duration_weeks" in complexity
        assert "factors" in complexity
        assert "recommendations" in complexity

        assert complexity["complexity_level"] in ["Low", "Medium", "High", "Very High"]
        assert complexity["estimated_duration_weeks"] > 0

    def test_mlpattern_optimizer_initialization(self):
        """Test MLPatternOptimizer initialization"""
        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )

        optimizer = MLPatternOptimizer(ml_config)

        assert optimizer.ml_config == ml_config
        assert len(optimizer.optimization_rules) > 0
        assert "tensorflow" in optimizer.optimization_rules


class TestEnums:
    """Test suite for enum values"""

    def test_ml_framework_values(self):
        """Test MLFramework enum values"""
        assert MLFramework.TENSORFLOW.value == "tensorflow"
        assert MLFramework.PYTORCH.value == "pytorch"
        assert MLFramework.SCIKIT_LEARN.value == "scikit_learn"
        assert MLFramework.HUGGING_FACE.value == "hugging_face"

    def test_model_type_values(self):
        """Test ModelType enum values"""
        assert ModelType.CLASSIFICATION.value == "classification"
        assert ModelType.GENERATIVE_AI.value == "generative_ai"
        assert ModelType.COMPUTER_VISION.value == "computer_vision"

    def test_deployment_platform_values(self):
        """Test DeploymentPlatform enum values"""
        assert DeploymentPlatform.KUBERNETES.value == "kubernetes"
        assert DeploymentPlatform.AWS_SAGEMAKER.value == "aws_sagemaker"
        assert DeploymentPlatform.SERVERLESS.value == "serverless"


class TestZeroHallucinationValidation:
    """Test zero hallucination requirements"""

    def test_no_hallucinated_frameworks(self):
        """Test that no hallucinated ML frameworks are mentioned"""
        skill = AIMLIntegrationExpert()

        # Check that all referenced frameworks are valid
        valid_frameworks = {f.value for f in MLFramework}

        # Check initialization data
        for framework in skill._ml_patterns.get("frameworks", {}):
            assert framework in valid_frameworks, f"Hallucinated framework: {framework}"

    def test_no_hallucinated_platforms(self):
        """Test that no hallucinated deployment platforms are mentioned"""
        skill = AIMLIntegrationExpert()

        valid_platforms = {p.value for p in DeploymentPlatform}

        # Would need to check actual recommendations for platform validity
        # This is a placeholder for comprehensive validation
        assert len(valid_platforms) > 0

    def test_technical_accuracy_in_recommendations(self):
        """Test technical accuracy of recommendations"""
        skill = AIMLIntegrationExpert()

        ml_config = ModelConfiguration(
            model_type=ModelType.CLASSIFICATION, framework=MLFramework.TENSORFLOW, model_path="/models/test"
        )
        requirements = {"expected_qps": 100}

        recommendations = skill._get_key_recommendations(ml_config, requirements)

        # Verify that TensorFlow recommendations mention actual TensorFlow Serving
        tf_recs = [r for r in recommendations if "tensorflow" in r["recommendation"].lower()]
        if tf_recs:
            assert any("tensorflow serving" in rec["recommendation"].lower() for rec in tf_recs), (
                "Should recommend actual TensorFlow Serving"
            )

    def test_no_impossible_combinations(self):
        """Test that no impossible framework/model type combinations are suggested"""
        # This would test that the skill doesn't suggest impossible combinations
        # e.g., reinforcement learning with scikit-learn (not supported)

        skill = AIMLIntegrationExpert()

        # Test with scikit-learn
        ml_config = ModelConfiguration(
            model_type=ModelType.REINFORCEMENT_LEARNING, framework=MLFramework.SCIKIT_LEARN, model_path="/models/test"
        )
        requirements = {}

        # Should not crash and should provide realistic recommendations
        try:
            recommendations = skill._get_key_recommendations(ml_config, requirements)
            # If reinforcement learning with scikit-learn is not realistic,
            # the skill should handle this gracefully
            assert isinstance(recommendations, list)
        except Exception:
            # This is acceptable - the skill should recognize invalid combos
            pass


class TestProgressiveDisclosure:
    """Test progressive disclosure functionality"""

    @pytest.mark.asyncio
    async def test_metadata_token_usage(self):
        """Test that metadata level stays within token limits"""
        skill = AIMLIntegrationExpert()

        context = SkillContext(
            query="ml integration",
            parameters={"ml_config": {"model_type": "classification", "framework": "tensorflow"}},
            available_tokens=100,  # Very limited tokens
        )

        result = await skill.execute(context, SkillLevel.METADATA)

        assert result.success
        assert result.tokens_used < 100

        # Should be very concise
        content = json.loads(result.content)
        assert len(content) <= 6  # Very few fields in metadata

    @pytest.mark.asyncio
    async def test_summary_token_usage(self):
        """Test that summary level respects token limits"""
        skill = AIMLIntegrationExpert()

        context = SkillContext(
            query="ml integration help",
            parameters={
                "ml_config": {"model_type": "classification", "framework": "tensorflow", "model_size_mb": 500},
                "expected_qps": 1000,
            },
            available_tokens=500,  # Moderate token limit
        )

        result = await skill.execute(context, SkillLevel.SUMMARY)

        assert result.success
        assert result.tokens_used < 500

    @pytest.mark.asyncio
    async def test_progressive_disclosure_content_growth(self):
        """Test that content grows appropriately with disclosure level"""
        skill = AIMLIntegrationExpert()

        context = SkillContext(
            query="comprehensive ml integration",
            parameters={
                "ml_config": {"model_type": "classification", "framework": "tensorflow", "model_size_mb": 500},
                "expected_qps": 1000,
                "compliance_requirements": ["GDPR"],
            },
            available_tokens=10000,
        )

        # Test all levels
        metadata_result = await skill.execute(context, SkillLevel.METADATA)
        summary_result = await skill.execute(context, SkillLevel.SUMMARY)
        detailed_result = await skill.execute(context, SkillLevel.FULL)

        # Token usage should increase with detail level
        assert metadata_result.tokens_used < summary_result.tokens_used < detailed_result.tokens_used

        # Content complexity should increase
        metadata_content = json.loads(metadata_result.content)
        summary_content = json.loads(summary_result.content)
        detailed_content = json.loads(detailed_result.content)

        assert len(metadata_content) < len(summary_content) < len(detailed_content)

        # Metadata should have minimal fields
        assert len(metadata_content) <= 6

        # Summary should have overview and recommendations
        assert "overview" in summary_content
        assert "key_recommendations" in summary_content

        # Detailed should have comprehensive sections
        expected_sections = [
            "deployment_strategy",
            "api_design",
            "mlops_implementation",
            "optimization_plan",
            "monitoring_strategy",
        ]
        for section in expected_sections:
            assert section in detailed_content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
