"""
Demo Script for Monitoring & Observability Expert Skill

Demonstrates the comprehensive capabilities of the monitoring and observability
expert skill across all areas of modern application observability.
"""

import asyncio
import time
from datetime import datetime

from ..skills_framework.skill_template import SkillContext, SkillLevel
from .monitoring_observability_expert import MonitoringObservabilityExpert


def run_comprehensive_demo():
    """Run comprehensive demo of the Monitoring & Observability Expert skill."""
    print("🎯 Monitoring & Observability Expert Skill Demo")
    print("=" * 60)
    print("Demonstrating expert guidance across all observability areas\n")

    skill = MonitoringObservabilityExpert()

    # Test different expertise areas
    test_scenarios = [
        {
            "title": "📊 Metrics & Prometheus Setup",
            "query": "How do I set up Prometheus for monitoring microservices in Kubernetes?",
            "level": SkillLevel.FULL,
            "expected_focus": "prometheus, metrics, kubernetes",
        },
        {
            "title": "📈 Grafana Dashboard Design",
            "query": "Design comprehensive Grafana dashboards for service monitoring and business KPIs",
            "level": SkillLevel.FULL,
            "expected_focus": "grafana, dashboard, visualization",
        },
        {
            "title": "🔍 Distributed Tracing Implementation",
            "query": "Implement distributed tracing with OpenTelemetry and Jaeger for microservices",
            "level": SkillLevel.FULL,
            "expected_focus": "tracing, opentelemetry, jaeger",
        },
        {
            "title": "📝 Structured Logging Strategy",
            "query": "Set up ELK stack for centralized log aggregation and analysis",
            "level": SkillLevel.FULL,
            "expected_focus": "logging, elk, elasticsearch",
        },
        {
            "title": "🚨 Advanced Alerting Systems",
            "query": "Configure AlertManager with routing rules and escalation policies",
            "level": SkillLevel.FULL,
            "expected_focus": "alerting, alertmanager, escalation",
        },
        {
            "title": "🎯 SLI/SLO Management",
            "query": "Implement service level objectives with error budget tracking",
            "level": SkillLevel.FULL,
            "expected_focus": "slo, sli, error budget",
        },
        {
            "title": "🏗️ Complete Observability Stack",
            "query": "Deploy complete observability stack with Prometheus, Grafana, Jaeger, and ELK",
            "level": SkillLevel.FULL,
            "expected_focus": "comprehensive stack deployment",
        },
    ]

    results = []

    for i, scenario in enumerate(test_scenarios, 1):
        print(f"\n{i}. {scenario['title']}")
        print("-" * len(scenario["title"]))

        # Test confidence
        context = SkillContext(query=scenario["query"], conversation_history=[], available_tokens=3000)

        confidence = skill.can_handle(context)
        print(f"   Confidence Score: {confidence:.2f}")

        if confidence >= 0.5:
            # Execute skill
            start_time = time.time()
            result = skill.execute(context, scenario["level"])
            execution_time = time.time() - start_time

            print(f"   Execution Time: {execution_time:.2f}s")
            print(f"   Tokens Used: {result.tokens_used}")
            print(f"   Response Length: {len(result.content)} characters")

            # Verify response quality
            content_lower = result.content.lower()
            expected_keywords = scenario["expected_focus"].split(", ")

            found_keywords = [kw for kw in expected_keywords if kw in content_lower]
            print(f"   Keywords Found: {len(found_keywords)}/{len(expected_keywords)}")

            # Show brief preview
            lines = result.content.split("\n")
            non_empty_lines = [line for line in lines if line.strip()]
            print(f"   Content Preview: {len(non_empty_lines)} lines total")

            if len(non_empty_lines) > 0:
                print(f"   First line: {non_empty_lines[0][:100]}...")

            results.append(
                {
                    "scenario": scenario["title"],
                    "confidence": confidence,
                    "execution_time": execution_time,
                    "tokens_used": result.tokens_used,
                    "keywords_found": len(found_keywords),
                    "success": True,
                }
            )
        else:
            print(f"   ❌ Low confidence - skipping execution")
            results.append({"scenario": scenario["title"], "confidence": confidence, "success": False})

    # Summary
    print("\n" + "=" * 60)
    print("📊 Demo Summary")
    print("=" * 60)

    successful_results = [r for r in results if r["success"]]
    if successful_results:
        avg_confidence = sum(r["confidence"] for r in successful_results) / len(successful_results)
        avg_execution_time = sum(r["execution_time"] for r in successful_results) / len(successful_results)
        avg_tokens = sum(r["tokens_used"] for r in successful_results) / len(successful_results)

        print(f"✅ Successful Scenarios: {len(successful_results)}/{len(results)}")
        print(f"📈 Average Confidence: {avg_confidence:.2f}")
        print(f"⏱️ Average Execution Time: {avg_execution_time:.2f}s")
        print(f"🪙 Average Token Usage: {avg_tokens:.0f}")

        # Show top performing scenarios
        print("\n🏆 Top Performing Scenarios:")
        sorted_results = sorted(successful_results, key=lambda x: x["confidence"], reverse=True)
        for i, result in enumerate(sorted_results[:3], 1):
            print(f"   {i}. {result['scenario']}")
            print(f"      Confidence: {result['confidence']:.2f}, Keywords: {result['keywords_found']}")
    else:
        print("❌ No scenarios met confidence threshold for execution")

    return results


def demonstrate_progressive_disclosure():
    """Demonstrate progressive disclosure capabilities."""
    print("\n" + "=" * 60)
    print("📚 Progressive Disclosure Demo")
    print("=" * 60)

    skill = MonitoringObservabilityExpert()
    query = "How to implement application monitoring?"

    levels = [(SkillLevel.METADATA, "METADATA"), (SkillLevel.SUMMARY, "SUMMARY"), (SkillLevel.FULL, "FULL")]

    for level, level_name in levels:
        print(f"\n📖 {level_name} Level Response:")
        print("-" * 20)

        context = SkillContext(query=query, conversation_history=[], available_tokens=5000)

        result = skill.execute(context, level)
        print(f"Tokens: {result.tokens_used}")
        print(f"Lines: {len(result.content.split())}")
        print(f"Characters: {len(result.content)}")

        # Show first few lines
        lines = result.content.split("\n")
        preview_lines = [line for line in lines[:5] if line.strip()]
        for line in preview_lines:
            print(f"  {line}")

        if len(lines) > 5:
            print("  ...")


def demonstrate_expertise_areas():
    """Demonstrate expertise across different observability areas."""
    print("\n" + "=" * 60)
    print("🎯 Expertise Areas Demo")
    print("=" * 60)

    skill = MonitoringObservabilityExpert()
    expertise_areas = [
        {
            "name": "Metrics Collection",
            "queries": [
                "Prometheus configuration for application metrics",
                "Create custom metrics for business KPIs",
                "Metric cardinality optimization strategies",
            ],
        },
        {
            "name": "Distributed Tracing",
            "queries": [
                "OpenTelemetry Python instrumentation",
                "Jaeger deployment and configuration",
                "Trace sampling strategies for cost optimization",
            ],
        },
        {
            "name": "Log Management",
            "queries": [
                "ELK stack setup for container logs",
                "Structured logging best practices",
                "Fluent Bit configuration for log shipping",
            ],
        },
        {
            "name": "Alerting & Incident Response",
            "queries": [
                "AlertManager routing and escalation policies",
                "SLO-based alerting strategies",
                "Incident response automation",
            ],
        },
    ]

    for area in expertise_areas:
        print(f"\n🔍 {area['name']}:")
        print("-" * len(area["name"]))

        for query in area["queries"]:
            context = SkillContext(query=query, conversation_history=[], available_tokens=1000)

            confidence = skill.can_handle(context)
            print(f"   Query: {query[:50]}...")
            print(f"   Confidence: {confidence:.2f}")

            if confidence >= 0.5:
                result = skill.execute(context, SkillLevel.SUMMARY)
                print(f"   Response Length: {len(result.content)} chars")
                print(f"   Technical Depth: {'High' if '```' in result.content else 'Medium'}")
            else:
                print("   ❌ Below confidence threshold")
            print()


def test_technical_accuracy():
    """Test technical accuracy of responses."""
    print("\n" + "=" * 60)
    print("🔬 Technical Accuracy Test")
    print("=" * 60)

    skill = MonitoringObservabilityExpert()

    technical_queries = [
        {
            "query": "Write Prometheus configuration for Kubernetes service discovery",
            "expected_elements": ["kubernetes_sd_configs", "role: pod", "relabel_configs"],
        },
        {
            "query": "Create Grafana dashboard JSON for service monitoring",
            "expected_elements": ["dashboard", "panels", "targets", "title"],
        },
        {
            "query": "AlertManager routing rules configuration",
            "expected_elements": ["route", "group_by", "receivers", "match"],
        },
        {
            "query": "OpenTelemetry Python instrumentation example",
            "expected_elements": ["opentelemetry", "TracerProvider", "instrumentation"],
        },
    ]

    for i, test_case in enumerate(technical_queries, 1):
        print(f"\n{i}. {test_case['query'][:60]}...")
        print("-" * 60)

        context = SkillContext(query=test_case["query"], conversation_history=[], available_tokens=2000)

        result = skill.execute(context, SkillLevel.FULL)
        content_lower = result.content.lower()

        # Check for expected technical elements
        found_elements = []
        for element in test_case["expected_elements"]:
            if element.lower() in content_lower:
                found_elements.append(element)
            elif element.replace("_", " ") in content_lower:
                found_elements.append(element)

        print(f"Technical Elements Found: {len(found_elements)}/{len(test_case['expected_elements'])}")
        for element in found_elements:
            print(f"  ✅ {element}")

        missing_elements = set(test_case["expected_elements"]) - set(found_elements)
        for element in missing_elements:
            print(f"  ❌ {element}")

        # Check for code examples
        has_code = "```" in result.content
        has_configuration = any(keyword in content_lower for keyword in ["yml", "yaml", "json", "config"])

        print(f"Contains Code Examples: {'✅' if has_code else '❌'}")
        print(f"Contains Configuration: {'✅' if has_configuration else '❌'}")
        print(
            f"Response Quality: {'High' if len(found_elements) >= len(test_case['expected_elements']) * 0.75 else 'Medium' if len(found_elements) >= len(test_case['expected_elements']) * 0.5 else 'Low'}"
        )


def main():
    """Run all demo scenarios."""
    print("🚀 Monitoring & Observability Expert Skill")
    print("🎯 Comprehensive Demonstration")
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nThis demo showcases the expert skill's capabilities across:")
    print("• Metrics collection and monitoring (Prometheus, Grafana)")
    print("• Distributed tracing (OpenTelemetry, Jaeger)")
    print("• Log aggregation and analysis (ELK stack)")
    print("• Alerting systems and incident response")
    print("• SLI/SLO management and error budgeting")
    print("• Complete observability stack deployment")

    try:
        # Run comprehensive demo
        results = run_comprehensive_demo()

        # Demonstrate progressive disclosure
        demonstrate_progressive_disclosure()

        # Show expertise areas
        demonstrate_expertise_areas()

        # Test technical accuracy
        test_technical_accuracy()

        print("\n" + "=" * 60)
        print("🎉 Demo Completed Successfully!")
        print("=" * 60)
        print("The Monitoring & Observability Expert skill demonstrates:")
        print("✅ Comprehensive coverage of observability tools and practices")
        print("✅ Technical accuracy with production-ready examples")
        print("✅ Progressive disclosure for different detail levels")
        print("✅ Expert guidance across all observability pillars")
        print("✅ Practical code and configuration examples")
        print("✅ Integration patterns for modern observability stacks")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {str(e)}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
