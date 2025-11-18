#!/usr/bin/env python3
"""
API Gateway Expert Skill Demonstration

This script demonstrates the comprehensive capabilities of the API Gateway Expert skill,
showcasing progressive disclosure, architecture design, and optimization features.

Usage:
    python demo_api_gateway_expert.py

Requirements:
    - Python 3.8+
    - Required dependencies installed in the environment
"""

import asyncio
import json
import sys
import time
from pathlib import Path

# Add the skill directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from api_gateway_expert import APIGatewayExpert, SkillContext, SkillResult
from typing import Dict, Any


class GatewayExpertDemo:
    """Demonstration class for API Gateway Expert skill"""

    def __init__(self):
        """Initialize demonstration"""
        self.skill = APIGatewayExpert()
        self.demo_results = []

    def create_context(self, action: str, parameters: Dict[str, Any] = None) -> SkillContext:
        """Create skill context for demonstration"""
        context = SkillContext()
        context.parameters = parameters or {}
        context.parameters["action"] = action
        return context

    async def run_demonstration(self):
        """Run complete demonstration of skill capabilities"""
        print("🚀 API Gateway Expert Skill Demonstration")
        print("=" * 60)

        # Test progressive disclosure levels
        await self.demo_progressive_disclosure()

        # Test requirement analysis
        await self.demo_requirement_analysis()

        # Test architecture design
        await self.demo_architecture_design()

        # Test performance optimization
        await self.demo_performance_optimization()

        # Test security implementation
        await self.demo_security_implementation()

        # Test monitoring setup
        await self.demo_monitoring_setup()

        # Generate summary report
        self.generate_summary_report()

    async def demo_progressive_disclosure(self):
        """Demonstrate progressive disclosure functionality"""
        print("\n📊 Progressive Disclosure Demo")
        print("-" * 40)

        levels = ["METADATA", "SUMMARY", "DETAILED", "FULL"]

        for level in levels:
            print(f"\n🔍 {level} Level:")

            start_time = time.time()
            content = (
                self.skill._get_metadata_content()
                if level == "METADATA"
                else self.skill._get_summary_content()
                if level == "SUMMARY"
                else self.skill._get_detailed_content()
                if level == "DETAILED"
                else self.skill._get_full_content()
            )
            execution_time = time.time() - start_time

            # Calculate content size
            content_size = len(json.dumps(content, default=str))

            print(f"  ⏱️  Execution time: {execution_time:.3f}s")
            print(f"  📏 Content size: {content_size:,} characters")
            print(f"  📋 Key sections: {list(content.keys())[:5]}...")

            self.demo_results.append(
                {
                    "test": f"Progressive Disclosure - {level}",
                    "execution_time": execution_time,
                    "content_size": content_size,
                    "success": True,
                }
            )

    async def demo_requirement_analysis(self):
        """Demonstrate requirement analysis functionality"""
        print("\n🔍 Requirement Analysis Demo")
        print("-" * 40)

        # Test different scenarios
        scenarios = [
            {
                "name": "Startup API Gateway",
                "requirements": {
                    "traffic_rps": 100,
                    "security_level": "standard",
                    "service_count": 5,
                    "deployment_type": "startup",
                },
            },
            {
                "name": "Enterprise API Gateway",
                "requirements": {
                    "traffic_rps": 5000,
                    "security_level": "high",
                    "service_count": 50,
                    "deployment_type": "enterprise",
                },
            },
            {
                "name": "High-Performance Gateway",
                "requirements": {
                    "traffic_rps": 20000,
                    "security_level": "high",
                    "service_count": 100,
                    "deployment_type": "cloud_native",
                },
            },
        ]

        for scenario in scenarios:
            print(f"\n📋 Analyzing: {scenario['name']}")

            context = self.create_context("analyze", scenario)
            start_time = time.time()

            try:
                result = await skill.execute(context)
                execution_time = time.time() - start_time

                if result.success:
                    analysis = result.data
                    print(f"  ✅ Analysis completed in {execution_time:.3f}s")
                    print(
                        f"  🏗️  Recommended Gateway: {analysis.get('recommended_gateway', {}).get('recommended_gateway', 'N/A')}"
                    )
                    print(
                        f"  📈 Traffic Level: {analysis.get('requirements_assessment', {}).get('traffic_volume', {}).get('level', 'N/A')}"
                    )
                    print(f"  🔐 Security Level: {scenario['requirements']['security_level']}")

                    self.demo_results.append(
                        {
                            "test": f"Requirement Analysis - {scenario['name']}",
                            "execution_time": execution_time,
                            "success": True,
                        }
                    )
                else:
                    print(f"  ❌ Analysis failed: {result.data.get('error', 'Unknown error')}")
                    self.demo_results.append(
                        {
                            "test": f"Requirement Analysis - {scenario['name']}",
                            "execution_time": execution_time,
                            "success": False,
                        }
                    )

            except Exception as e:
                print(f"  ❌ Exception occurred: {str(e)}")
                self.demo_results.append(
                    {
                        "test": f"Requirement Analysis - {scenario['name']}",
                        "execution_time": time.time() - start_time,
                        "success": False,
                    }
                )

    async def demo_architecture_design(self):
        """Demonstrate architecture design functionality"""
        print("\n🏗️ Architecture Design Demo")
        print("-" * 40)

        design_configs = [
            {
                "name": "Microservices Architecture",
                "config": {
                    "pattern": "api_gateway_pattern",
                    "services": [
                        {"name": "user-service", "port": 8080},
                        {"name": "order-service", "port": 8081},
                        {"name": "payment-service", "port": 8082},
                    ],
                    "routes": [
                        {"path": "/api/users", "service": "user-service"},
                        {"path": "/api/orders", "service": "order-service"},
                        {"path": "/api/payments", "service": "payment-service"},
                    ],
                },
            },
            {
                "name": "Backend-for-Frontend Pattern",
                "config": {
                    "pattern": "backend_for_frontend",
                    "client_types": ["web", "mobile", "iot"],
                    "services": [
                        {"name": "web-bff", "port": 8080},
                        {"name": "mobile-bff", "port": 8081},
                        {"name": "iot-bff", "port": 8082},
                    ],
                },
            },
        ]

        for design_config in design_configs:
            print(f"\n🏛️ Designing: {design_config['name']}")

            context = self.create_context("design", design_config)
            start_time = time.time()

            try:
                result = await skill.execute(context)
                execution_time = time.time() - start_time

                if result.success:
                    architecture = result.data
                    high_level = architecture.get("high_level_design", {})
                    components = high_level.get("components", [])

                    print(f"  ✅ Design completed in {execution_time:.3f}s")
                    print(f"  🧩 Architecture Components: {len(components)}")
                    print(f"  🏗️ Pattern: {high_level.get('pattern', 'N/A')}")

                    # Show component types
                    component_types = [comp.get("type", "unknown") for comp in components]
                    print(f"  ⚙️  Component Types: {', '.join(set(component_types))}")

                    self.demo_results.append(
                        {
                            "test": f"Architecture Design - {design_config['name']}",
                            "execution_time": execution_time,
                            "components_count": len(components),
                            "success": True,
                        }
                    )
                else:
                    print(f"  ❌ Design failed: {result.data.get('error', 'Unknown error')}")
                    self.demo_results.append(
                        {
                            "test": f"Architecture Design - {design_config['name']}",
                            "execution_time": execution_time,
                            "success": False,
                        }
                    )

            except Exception as e:
                print(f"  ❌ Exception occurred: {str(e)}")
                self.demo_results.append(
                    {
                        "test": f"Architecture Design - {design_config['name']}",
                        "execution_time": time.time() - start_time,
                        "success": False,
                    }
                )

    async def demo_performance_optimization(self):
        """Demonstrate performance optimization functionality"""
        print("\n⚡ Performance Optimization Demo")
        print("-" * 40)

        optimization_scenarios = [
            {
                "name": "High Latency Issues",
                "config": {
                    "current_config": {"timeout": 30, "connections": 100, "caching": "disabled"},
                    "performance_issues": [
                        {"type": "high_latency", "value": "2000ms"},
                        {"type": "slow_upstream", "value": "1500ms"},
                    ],
                },
            },
            {
                "name": "Connection Exhaustion",
                "config": {
                    "current_config": {"timeout": 60, "connections": 1000, "keepalive": False},
                    "performance_issues": [
                        {"type": "connection_exhaustion", "value": "95% usage"},
                        {"type": "high_memory", "value": "90% usage"},
                    ],
                },
            },
        ]

        for scenario in optimization_scenarios:
            print(f"\n🔧 Optimizing: {scenario['name']}")

            context = self.create_context("optimize", scenario)
            start_time = time.time()

            try:
                result = await skill.execute(context)
                execution_time = time.time() - start_time

                if result.success:
                    optimization = result.data
                    strategies = optimization.get("optimization_strategies", {})

                    print(f"  ✅ Optimization analysis completed in {execution_time:.3f}s")
                    print(
                        f"  🎯 Identified Bottlenecks: {len(optimization.get('performance_analysis', {}).get('bottlenecks', []))}"
                    )
                    print(f"  📋 Optimization Strategies: {len(strategies)}")

                    # Show strategy categories
                    strategy_categories = list(strategies.keys())
                    print(f"  🛠️  Strategy Types: {', '.join(strategy_categories)}")

                    self.demo_results.append(
                        {
                            "test": f"Performance Optimization - {scenario['name']}",
                            "execution_time": execution_time,
                            "strategies_count": len(strategies),
                            "success": True,
                        }
                    )
                else:
                    print(f"  ❌ Optimization failed: {result.data.get('error', 'Unknown error')}")
                    self.demo_results.append(
                        {
                            "test": f"Performance Optimization - {scenario['name']}",
                            "execution_time": execution_time,
                            "success": False,
                        }
                    )

            except Exception as e:
                print(f"  ❌ Exception occurred: {str(e)}")
                self.demo_results.append(
                    {
                        "test": f"Performance Optimization - {scenario['name']}",
                        "execution_time": time.time() - start_time,
                        "success": False,
                    }
                )

    async def demo_security_implementation(self):
        """Demonstrate security implementation functionality"""
        print("\n🔒 Security Implementation Demo")
        print("-" * 40)

        security_scenarios = [
            {
                "name": "JWT Authentication",
                "security_requirements": {
                    "authentication_type": "jwt",
                    "authorization_type": "rbac",
                    "compliance": ["oauth2"],
                },
            },
            {
                "name": "Enterprise Security",
                "security_requirements": {
                    "authentication_type": "oauth2_mfa",
                    "authorization_type": "abac",
                    "compliance": ["gdpr", "soc2", "pci_dss"],
                    "encryption": "tls_13",
                },
            },
        ]

        for scenario in security_scenarios:
            print(f"\n🛡️  Securing: {scenario['name']}")

            context = self.create_context("secure", scenario)
            start_time = time.time()

            try:
                result = await skill.execute(context)
                execution_time = time.time() - start_time

                if result.success:
                    security = result.data
                    controls = security.get("security_controls", {})
                    threats = security.get("threat_model", {})

                    print(f"  ✅ Security analysis completed in {execution_time:.3f}s")
                    print(f"  🚨 Attack Vectors Identified: {len(threats.get('attack_vectors', []))}")
                    print(f"  🔐 Security Controls: {len(controls)}")

                    # Show control categories
                    control_categories = list(controls.keys())
                    print(f"  🛠️  Control Types: {', '.join(control_categories)}")

                    self.demo_results.append(
                        {
                            "test": f"Security Implementation - {scenario['name']}",
                            "execution_time": execution_time,
                            "controls_count": len(controls),
                            "success": True,
                        }
                    )
                else:
                    print(f"  ❌ Security analysis failed: {result.data.get('error', 'Unknown error')}")
                    self.demo_results.append(
                        {
                            "test": f"Security Implementation - {scenario['name']}",
                            "execution_time": execution_time,
                            "success": False,
                        }
                    )

            except Exception as e:
                print(f"  ❌ Exception occurred: {str(e)}")
                self.demo_results.append(
                    {
                        "test": f"Security Implementation - {scenario['name']}",
                        "execution_time": time.time() - start_time,
                        "success": False,
                    }
                )

    async def demo_monitoring_setup(self):
        """Demonstrate monitoring setup functionality"""
        print("\n📊 Monitoring Setup Demo")
        print("-" * 40)

        monitoring_scenarios = [
            {
                "name": "Basic Monitoring Stack",
                "monitoring_config": {
                    "metrics_backend": "prometheus",
                    "logging_backend": "elasticsearch",
                    "alerting_enabled": True,
                },
            },
            {
                "name": "Advanced Observability",
                "monitoring_config": {
                    "metrics_backend": "prometheus",
                    "logging_backend": "elasticsearch",
                    "tracing_backend": "jaeger",
                    "apm_integration": True,
                    "sla_monitoring": True,
                },
            },
        ]

        for scenario in monitoring_scenarios:
            print(f"\n📈 Setting up: {scenario['name']}")

            context = self.create_context("monitor", scenario)
            start_time = time.time()

            try:
                result = await skill.execute(context)
                execution_time = time.time() - start_time

                if result.success:
                    monitoring = result.data
                    stack = monitoring.get("monitoring_stack", {})
                    dashboards = monitoring.get("dashboards", {})

                    print(f"  ✅ Monitoring setup completed in {execution_time:.3f}s")
                    print(f"  📊 Monitoring Components: {len(stack)}")
                    print(f"  📋 Dashboards: {len(dashboards)}")

                    # Show monitoring stack components
                    stack_components = list(stack.keys())
                    print(f"  🔧 Stack Components: {', '.join(stack_components)}")

                    self.demo_results.append(
                        {
                            "test": f"Monitoring Setup - {scenario['name']}",
                            "execution_time": execution_time,
                            "components_count": len(stack),
                            "success": True,
                        }
                    )
                else:
                    print(f"  ❌ Monitoring setup failed: {result.data.get('error', 'Unknown error')}")
                    self.demo_results.append(
                        {
                            "test": f"Monitoring Setup - {scenario['name']}",
                            "execution_time": execution_time,
                            "success": False,
                        }
                    )

            except Exception as e:
                print(f"  ❌ Exception occurred: {str(e)}")
                self.demo_results.append(
                    {
                        "test": f"Monitoring Setup - {scenario['name']}",
                        "execution_time": time.time() - start_time,
                        "success": False,
                    }
                )

    def generate_summary_report(self):
        """Generate comprehensive summary report"""
        print("\n📋 Demonstration Summary Report")
        print("=" * 60)

        total_tests = len(self.demo_results)
        successful_tests = sum(1 for result in self.demo_results if result["success"])
        success_rate = (successful_tests / total_tests * 100) if total_tests > 0 else 0

        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Successful Tests: {successful_tests}")
        print(f"❌ Failed Tests: {total_tests - successful_tests}")
        print(f"📈 Success Rate: {success_rate:.1f}%")

        # Performance metrics
        execution_times = [result.get("execution_time", 0) for result in self.demo_results]
        avg_execution_time = sum(execution_times) / len(execution_times) if execution_times else 0
        max_execution_time = max(execution_times) if execution_times else 0
        min_execution_time = min(execution_times) if execution_times else 0

        print(f"\n⏱️  Performance Metrics:")
        print(f"  📊 Average Execution Time: {avg_execution_time:.3f}s")
        print(f"  ⬆️  Maximum Execution Time: {max_execution_time:.3f}s")
        print(f"  ⬇️  Minimum Execution Time: {min_execution_time:.3f}s")

        # Test category breakdown
        categories = {}
        for result in self.demo_results:
            test_name = result["test"]
            category = test_name.split(" - ")[0]
            if category not in categories:
                categories[category] = {"total": 0, "successful": 0}
            categories[category]["total"] += 1
            if result["success"]:
                categories[category]["successful"] += 1

        print(f"\n📋 Test Categories:")
        for category, stats in categories.items():
            category_success_rate = stats["successful"] / stats["total"] * 100
            print(f"  🏷️  {category}: {stats['successful']}/{stats['total']} ({category_success_rate:.1f}%)")

        # Failed tests details
        failed_tests = [result for result in self.demo_results if not result["success"]]
        if failed_tests:
            print(f"\n❌ Failed Tests:")
            for failed_test in failed_tests:
                print(f"  🚫 {failed_test['test']}")

        # Skill capabilities demonstrated
        capabilities_demonstrated = set()
        for result in self.demo_results:
            test_name = result["test"]
            if "Progressive Disclosure" in test_name:
                capabilities_demonstrated.add("Progressive Disclosure")
            elif "Requirement Analysis" in test_name:
                capabilities_demonstrated.add("Requirements Analysis")
            elif "Architecture Design" in test_name:
                capabilities_demonstrated.add("Architecture Design")
            elif "Performance Optimization" in test_name:
                capabilities_demonstrated.add("Performance Optimization")
            elif "Security Implementation" in test_name:
                capabilities_demonstrated.add("Security Implementation")
            elif "Monitoring Setup" in test_name:
                capabilities_demonstrated.add("Monitoring Setup")

        print(f"\n🎯 Capabilities Demonstrated:")
        for capability in sorted(capabilities_demonstrated):
            print(f"  ✅ {capability}")

        print(f"\n🚀 API Gateway Expert Skill: {'PASSED' if success_rate >= 90 else 'NEEDS ATTENTION'}")
        print("=" * 60)


async def main():
    """Main demonstration function"""
    try:
        demo = GatewayExpertDemo()
        await demo.run_demonstration()
    except KeyboardInterrupt:
        print("\n\n⏹️  Demonstration interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Demonstration failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    # Run the demonstration
    print("Starting API Gateway Expert Skill Demonstration...")
    print("This will showcase the skill's comprehensive capabilities.\n")

    asyncio.run(main())
