#!/usr/bin/env python3
"""
AI/ML Integration Expert Demonstration

This demo showcases the AI/ML Integration Expert skill with comprehensive examples
covering different frameworks, model types, deployment scenarios, and optimization
techniques.

Usage:
    python demo_ai_ml_integration_expert.py [--level METADATA|SUMMARY|FULL]
"""

import asyncio
import json
import argparse
import sys
from pathlib import Path

# Add the skill path to Python path
sys.path.insert(0, str(Path(__file__).parent))

from ai_ml_integration_expert import (
    AIMLIntegrationExpert,
    ModelConfiguration,
    MLFramework,
    ModelType,
    SkillLevel,
)


class SkillDemonstration:
    """Demonstration class for AI/ML Integration Expert"""

    def __init__(self):
        self.skill = AIMLIntegrationExpert()

    async def demo_tensorflow_classification(self, level: SkillLevel):
        """Demo: TensorFlow Classification Model Integration"""
        print("\n" + "=" * 60)
        print("🔬 DEMO: TensorFlow Classification Model Integration")
        print("=" * 60)

        context = {
            "query": "How do I integrate a TensorFlow classification model into production?",
            "parameters": {
                "ml_config": {
                    "model_type": "classification",
                    "framework": "tensorflow",
                    "model_path": "/models/tensorflow/classifier_v2",
                    "model_version": "2.1.0",
                    "model_size_mb": 450,
                    "input_schema": {"features": "float32[20]", "preprocessing": "standard_scaler"},
                    "output_schema": {"prediction": "string", "confidence": "float32", "probabilities": "object"},
                    "performance_metrics": {"accuracy": 0.94, "precision": 0.92, "recall": 0.93, "f1_score": 0.925},
                },
                "deployment_platform": "kubernetes",
                "expected_qps": 1500,
                "latency_requirement_ms": 75,
                "accuracy_requirement": 0.90,
                "team_expertise": "intermediate",
                "compliance_requirements": ["SOC2"],
                "scaling_requirements": "horizontal",
                "monitoring_requirements": ["performance", "drift"],
            },
            "available_tokens": 5000,
        }

        await self._execute_and_display(context, level)

    async def demo_pytorch_computer_vision(self, level: SkillLevel):
        """Demo: PyTorch Computer Vision Model Integration"""
        print("\n" + "=" * 60)
        print("🖼️  DEMO: PyTorch Computer Vision Model Integration")
        print("=" * 60)

        context = {
            "query": "Integrate PyTorch computer vision model for real-time image processing",
            "parameters": {
                "ml_config": {
                    "model_type": "computer_vision",
                    "framework": "pytorch",
                    "model_path": "/models/pytorch/resnet50_detector",
                    "model_version": "1.3.2",
                    "model_size_mb": 980,
                    "input_schema": {"image": "uint8[224,224,3]", "preprocessing": "normalize_resnet"},
                    "output_schema": {"predictions": "array", "bounding_boxes": "array", "confidence_scores": "array"},
                    "hyperparameters": {"input_size": [224, 224], "num_classes": 1000, "threshold": 0.5},
                    "performance_metrics": {"map_score": 0.87, "inference_time_ms": 45},
                },
                "deployment_platform": "kubernetes",
                "expected_qps": 500,
                "latency_requirement_ms": 100,
                "accuracy_requirement": 0.85,
                "team_expertise": "advanced",
                "compliance_requirements": ["GDPR"],
                "responsible_ai_requirements": ["interpretability", "fairness"],
                "scaling_requirements": "horizontal",
                "monitoring_requirements": ["performance", "data_drift"],
            },
            "available_tokens": 5000,
        }

        await self._execute_and_display(context, level)

    async def demo_huggingface_llm(self, level: SkillLevel):
        """Demo: Hugging Face LLM Integration"""
        print("\n" + "=" * 60)
        print("🤖 DEMO: Hugging Face LLM Integration")
        print("=" * 60)

        context = {
            "query": "Deploy Hugging Face LLM with serverless architecture and cost optimization",
            "parameters": {
                "ml_config": {
                    "model_type": "generative_ai",
                    "framework": "hugging_face",
                    "model_path": "/models/huggingface/llama2-7b-chat",
                    "model_version": "3.0.1",
                    "model_size_mb": 13500,  # 13.5GB
                    "input_schema": {"prompt": "string", "max_tokens": "integer", "temperature": "float32"},
                    "output_schema": {
                        "generated_text": "string",
                        "token_count": "integer",
                        "processing_time_ms": "float32",
                    },
                    "hyperparameters": {
                        "max_length": 2048,
                        "temperature_range": [0.1, 2.0],
                        "top_p": 0.9,
                        "repetition_penalty": 1.1,
                    },
                    "performance_metrics": {"tokens_per_second": 25, "memory_usage_gb": 16},
                },
                "deployment_platform": "serverless",
                "expected_qps": 50,
                "latency_requirement_ms": 5000,
                "team_expertise": "expert",
                "compliance_requirements": ["GDPR", "CCPA"],
                "responsible_ai_requirements": ["privacy", "transparency", "safety"],
                "scaling_requirements": "serverless",
                "monitoring_requirements": ["performance", "cost", "safety"],
                "budget_constraints": {"monthly_limit": 5000, "cost_per_token_threshold": 0.001},
            },
            "available_tokens": 5000,
        }

        await self._execute_and_display(context, level)

    async def demo_xgboost_realtime(self, level: SkillLevel):
        """Demo: XGBoost Real-time Prediction Service"""
        print("\n" + "=" * 60)
        print("⚡ DEMO: XGBoost Real-time Prediction Service")
        print("=" * 60)

        context = {
            "query": "Create real-time prediction API with XGBoost model",
            "parameters": {
                "ml_config": {
                    "model_type": "regression",
                    "framework": "xgboost",
                    "model_path": "/models/xgboost/price_predictor",
                    "model_version": "1.8.5",
                    "model_size_mb": 125,
                    "input_schema": {"features": "float32[50]", "feature_names": "array"},
                    "output_schema": {
                        "prediction": "float64",
                        "prediction_interval": "array",
                        "feature_importance": "object",
                    },
                    "hyperparameters": {"max_depth": 6, "learning_rate": 0.1, "n_estimators": 100},
                    "performance_metrics": {"rmse": 12.5, "mae": 8.3, "r2_score": 0.89},
                },
                "deployment_platform": "docker",
                "expected_qps": 3000,
                "latency_requirement_ms": 25,
                "accuracy_requirement": 0.85,
                "team_expertise": "intermediate",
                "compliance_requirements": [],
                "scaling_requirements": "horizontal",
                "monitoring_requirements": ["performance", "accuracy"],
            },
            "available_tokens": 5000,
        }

        await self._execute_and_display(context, level)

    async def demo_edge_ai_deployment(self, level: SkillLevel):
        """Demo: Edge AI Deployment for IoT"""
        print("\n" + "=" * 60)
        print("📱 DEMO: Edge AI Deployment for IoT")
        print("=" * 60)

        context = {
            "query": "Deploy ML model on edge devices for IoT real-time processing",
            "parameters": {
                "ml_config": {
                    "model_type": "anomaly_detection",
                    "framework": "tensorflow",
                    "model_path": "/models/tensorflow/anomaly_detector_tflite",
                    "model_version": "1.2.0",
                    "model_size_mb": 15,  # Optimized for edge
                    "input_schema": {"sensor_data": "float32[100]", "timestamp": "integer"},
                    "output_schema": {"anomaly_score": "float32", "is_anomaly": "boolean", "confidence": "float32"},
                    "hyperparameters": {"sequence_length": 100, "threshold": 0.8},
                    "performance_metrics": {"precision": 0.91, "recall": 0.88, "inference_time_ms": 5},
                },
                "deployment_platform": "edge_device",
                "expected_qps": 100,
                "latency_requirement_ms": 10,
                "team_expertise": "advanced",
                "compliance_requirements": [],
                "scaling_requirements": "edge_distributed",
                "monitoring_requirements": ["performance", "device_health"],
                "responsible_ai_requirements": ["explainability"],
                "budget_constraints": {"device_cost_limit": 200, "power_consumption_watts": 5},
            },
            "available_tokens": 5000,
        }

        await self._execute_and_display(context, level)

    async def demo_mlops_pipeline(self, level: SkillLevel):
        """Demo: Comprehensive MLOps Pipeline"""
        print("\n" + "=" * 60)
        print("🔄 DEMO: Comprehensive MLOps Pipeline")
        print("=" * 60)

        context = {
            "query": "Design complete MLOps pipeline with automated retraining and A/B testing",
            "parameters": {
                "ml_config": {
                    "model_type": "classification",
                    "framework": "scikit_learn",
                    "model_path": "/models/sklearn/customer_churn",
                    "model_version": "3.1.0",
                    "model_size_mb": 45,
                    "input_schema": {"customer_features": "float32[30]", "categorical_features": "string[10]"},
                    "output_schema": {
                        "churn_probability": "float32",
                        "risk_category": "string",
                        "explanation": "object",
                    },
                    "hyperparameters": {"algorithm": "xgboost", "max_depth": 8, "learning_rate": 0.05},
                    "performance_metrics": {"auc_roc": 0.87, "accuracy": 0.82, "business_impact": "$2.3M_annual"},
                },
                "deployment_platform": "kubernetes",
                "expected_qps": 200,
                "latency_requirement_ms": 200,
                "accuracy_requirement": 0.80,
                "team_expertise": "expert",
                "compliance_requirements": ["SOC2", "GDPR"],
                "responsible_ai_requirements": ["fairness", "interpretability", "transparency"],
                "scaling_requirements": "horizontal",
                "monitoring_requirements": ["performance", "drift", "fairness", "business"],
                "advanced_requirements": {
                    "automated_retraining": True,
                    "a_b_testing": True,
                    "feature_store": True,
                    "data_drift_detection": True,
                    "model_registry": "mlflow",
                },
            },
            "available_tokens": 5000,
        }

        await self._execute_and_display(context, level)

    async def _execute_and_display(self, context: dict, level: SkillLevel):
        """Execute skill and display results"""
        from amplifier.skills.skills_framework.skill_template import SkillContext

        # Convert dict to SkillContext
        skill_context = SkillContext(**context)

        print(f"🎯 Query: {context['query']}")
        print(f"📊 Model Type: {context['parameters']['ml_config']['model_type']}")
        print(f"🔧 Framework: {context['parameters']['ml_config']['framework']}")
        print(f"📱 Expected QPS: {context['parameters'].get('expected_qps', 'N/A')}")
        print(f"⏱️  Latency Requirement: {context['parameters'].get('latency_requirement_ms', 'N/A')}ms")
        print(f"📋 Disclosure Level: {level.value}")
        print("-" * 60)

        # Execute skill
        result = await self.skill.execute(skill_context, level)

        if result.success:
            print(f"✅ Execution successful!")
            print(f"⏱️  Execution time: {result.execution_time:.3f}s")
            print(f"🪙 Tokens used: {result.tokens_used}")
            print(f"📈 Complexity: {result.metadata.get('complexity', 'N/A')}")
            print(f"🎯 Optimization potential: {result.metadata.get('optimization_potential', 'N/A')}")
            print("-" * 60)

            # Parse and display content
            try:
                content = json.loads(result.content)
                self._display_content(content, level)
            except json.JSONDecodeError:
                print("📄 Raw Content:")
                print(result.content)
        else:
            print(f"❌ Execution failed: {result.content}")

    def _display_content(self, content: dict, level: SkillLevel):
        """Display content based on disclosure level"""

        if level == SkillLevel.METADATA:
            self._display_metadata(content)
        elif level == SkillLevel.SUMMARY:
            self._display_summary(content)
        else:
            self._display_detailed(content)

    def _display_metadata(self, content: dict):
        """Display metadata level content"""
        print("📋 METADATA LEVEL:")
        print(f"   Skill: {content.get('skill', 'N/A')}")
        print(f"   Model Type: {content.get('model_type', 'N/A')}")
        print(f"   Framework: {content.get('framework', 'N/A')}")
        print(f"   Platform: {content.get('deployment_platform', 'N/A')}")
        print(f"   Complexity: {content.get('complexity', 'N/A')}")
        print(f"   Optimization Potential: {content.get('optimization_potential', 'N/A')}")

    def _display_summary(self, content: dict):
        """Display summary level content"""
        print("📋 SUMMARY LEVEL:")

        if "overview" in content:
            overview = content["overview"]
            print("\n🎯 OVERVIEW:")
            print(f"   Model Type: {overview.get('model_type', 'N/A')}")
            print(f"   Framework: {overview.get('framework', 'N/A')}")
            print(f"   Recommended Deployment: {overview.get('recommended_deployment', 'N/A')}")
            print(f"   Complexity Level: {overview.get('complexity_level', 'N/A')}")

        if "key_recommendations" in content:
            recommendations = content["key_recommendations"]
            print("\n💡 KEY RECOMMENDATIONS:")
            for i, rec in enumerate(recommendations[:5], 1):  # Show first 5
                print(f"   {i}. [{rec.get('category', 'General')}] {rec.get('recommendation', 'N/A')}")
                print(f"      Reason: {rec.get('reason', 'N/A')}")

        if "performance_expectations" in content:
            perf = content["performance_expectations"]
            print("\n⚡ PERFORMANCE EXPECTATIONS:")
            print(f"   Throughput: {perf.get('estimated_throughput_qps', 'N/A')} QPS")
            print(f"   Latency: {perf.get('estimated_latency_ms', 'N/A')}ms")
            print(f"   Memory: {perf.get('estimated_memory_mb', 'N/A')}MB")

            if "recommended_hardware" in perf:
                hw = perf["recommended_hardware"]
                print(f"   CPU: {hw.get('cpu', 'N/A')}")
                print(f"   Memory: {hw.get('memory', 'N/A')}")
                print(f"   GPU: {hw.get('gpu', 'N/A')}")

        if "critical_considerations" in content:
            considerations = content["critical_considerations"]
            print("\n⚠️  CRITICAL CONSIDERATIONS:")
            for i, consideration in enumerate(considerations, 1):
                print(f"   {i}. {consideration}")

    def _display_detailed(self, content: dict):
        """Display detailed level content"""
        print("📋 DETAILED LEVEL:")

        sections = [
            ("🚀 DEPLOYMENT STRATEGY", "deployment_strategy"),
            ("🔌 API DESIGN", "api_design"),
            ("🔄 MLOPS IMPLEMENTATION", "mlops_implementation"),
            ("⚡ OPTIMIZATION PLAN", "optimization_plan"),
            ("🤖 LLM INTEGRATION", "llm_integration"),
            ("🛡️ RESPONSIBLE AI", "responsible_ai"),
            ("📊 MONITORING STRATEGY", "monitoring_strategy"),
            ("📈 SCALABILITY PLAN", "scalability_plan"),
            ("🔒 SECURITY CONSIDERATIONS", "security_considerations"),
            ("🛣️  IMPLEMENTATION ROADMAP", "implementation_roadmap"),
        ]

        for title, key in sections:
            if key in content and content[key]:
                print(f"\n{title}:")
                self._display_section(content[key], indent="   ")

    def _display_section(self, section: any, indent: str = ""):
        """Recursively display section content"""
        if isinstance(section, dict):
            for key, value in section.items():
                if value is None:
                    continue
                elif isinstance(value, (dict, list)):
                    print(f"{indent}{key.replace('_', ' ').title()}:")
                    self._display_section(value, indent + "   ")
                else:
                    print(f"{indent}{key.replace('_', ' ').title()}: {value}")
        elif isinstance(section, list):
            for i, item in enumerate(section[:3], 1):  # Show first 3 items
                if isinstance(item, dict):
                    print(f"{indent}Item {i}:")
                    self._display_section(item, indent + "   ")
                else:
                    print(f"{indent}- {item}")
            if len(section) > 3:
                print(f"{indent}... and {len(section) - 3} more items")
        else:
            print(f"{indent}{section}")

    async def run_all_demos(self, level: SkillLevel):
        """Run all demonstration scenarios"""
        demos = [
            self.demo_tensorflow_classification,
            self.demo_pytorch_computer_vision,
            self.demo_huggingface_llm,
            self.demo_xgboost_realtime,
            self.demo_edge_ai_deployment,
            self.demo_mlops_pipeline,
        ]

        print("🚀 Starting AI/ML Integration Expert demonstrations...")
        print(f"📊 Disclosure Level: {level.value}")
        print("=" * 80)

        for demo_func in demos:
            try:
                await demo_func(level)
                print("\n" + "=" * 80)
            except Exception as e:
                print(f"❌ Demo failed: {str(e)}")
                print("=" * 80)

        print("✅ All demonstrations completed!")


async def main():
    """Main function to run demonstrations"""
    parser = argparse.ArgumentParser(
        description="AI/ML Integration Expert Demonstration",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python demo_ai_ml_integration_expert.py --level SUMMARY
  python demo_ai_ml_integration_expert.py --level METADATA
  python demo_ai_ml_integration_expert.py --level FULL
        """,
    )

    parser.add_argument(
        "--level",
        choices=["METADATA", "SUMMARY", "FULL"],
        default="SUMMARY",
        help="Disclosure level for demonstrations (default: SUMMARY)",
    )

    parser.add_argument(
        "--demo",
        choices=["tensorflow", "pytorch", "llm", "xgboost", "edge", "mlops", "all"],
        default="all",
        help="Specific demo to run (default: all)",
    )

    args = parser.parse_args()

    # Convert string to SkillLevel
    level_map = {
        "METADATA": SkillLevel.METADATA,
        "SUMMARY": SkillLevel.SUMMARY,
        "FULL": SkillLevel.FULL,
    }
    level = level_map[args.level]

    # Run demonstrations
    demo = SkillDemonstration()

    if args.demo == "all":
        await demo.run_all_demos(level)
    else:
        demo_map = {
            "tensorflow": demo.demo_tensorflow_classification,
            "pytorch": demo.demo_pytorch_computer_vision,
            "llm": demo.demo_huggingface_llm,
            "xgboost": demo.demo_xgboost_realtime,
            "edge": demo.demo_edge_ai_deployment,
            "mlops": demo.demo_mlops_pipeline,
        }

        if args.demo in demo_map:
            await demo_map[args.demo](level)
        else:
            print(f"❌ Unknown demo: {args.demo}")


if __name__ == "__main__":
    asyncio.run(main())
