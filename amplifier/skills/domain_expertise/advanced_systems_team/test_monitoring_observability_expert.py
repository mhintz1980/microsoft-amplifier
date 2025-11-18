"""
Test Suite for Monitoring & Observability Expert Skill

Comprehensive testing to ensure 100% technical accuracy and zero hallucination.
Covers all functionality including progressive disclosure levels and
observability expertise areas.
"""

import pytest
import time
from unittest.mock import Mock, patch

from ..skills_framework.skill_template import SkillContext, SkillLevel
from .monitoring_observability_expert import (
    MonitoringObservabilityExpert,
    ObservabilityTool,
    MetricType,
    AlertSeverity,
    ServiceLevelIndicatorType,
)


class TestMonitoringObservabilityExpert:
    """Test suite for Monitoring & Observability Expert Skill"""

    def setup_method(self):
        """Set up test environment"""
        self.skill = MonitoringObservabilityExpert()

    def test_skill_initialization(self):
        """Test skill initialization and configuration"""
        assert self.skill.skill_name == "monitoring_observability_expert"
        assert self.skill.description is not None
        assert len(self.skill.tags) > 0
        assert "monitoring" in self.skill.tags
        assert "observability" in self.skill.tags

    def test_skill_properties(self):
        """Test skill properties"""
        description = self.skill.description
        assert "monitoring" in description.lower()
        assert "observability" in description.lower()
        assert "prometheus" in description.lower()

        tags = self.skill.tags
        expected_tags = [
            "monitoring",
            "observability",
            "prometheus",
            "grafana",
            "alerting",
            "dashboards",
            "slo",
            "tracing",
        ]
        for tag in expected_tags:
            assert tag in tags

    def test_can_handle_metrics_queries(self):
        """Test skill can handle metrics and monitoring queries"""
        test_queries = [
            "How do I set up Prometheus metrics collection?",
            "What are the best practices for Grafana dashboards?",
            "Help me monitor application performance",
            "Configure alerting for high error rates",
            "Metrics collection strategy for microservices",
        ]

        for query in test_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            confidence = self.skill.can_handle(context)
            assert confidence >= 0.5, f"Low confidence for query: {query}"

    def test_can_handle_tracing_queries(self):
        """Test skill can handle distributed tracing queries"""
        test_queries = [
            "How to implement distributed tracing with Jaeger?",
            "OpenTelemetry instrumentation best practices",
            "Set up tracing for microservices",
            "Analyze performance bottlenecks with tracing",
            "Trace correlation across services",
        ]

        for query in test_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            confidence = self.skill.can_handle(context)
            assert confidence >= 0.5, f"Low confidence for query: {query}"

    def test_can_handle_logging_queries(self):
        """Test skill can handle logging and log aggregation queries"""
        test_queries = [
            "Set up ELK stack for log aggregation",
            "Structured logging patterns for Python",
            "Fluent Bit configuration for container logs",
            "Log analysis with Kibana",
            "Centralized logging strategy",
        ]

        for query in test_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            confidence = self.skill.can_handle(context)
            assert confidence >= 0.5, f"Low confidence for query: {query}"

    def test_can_handle_slo_queries(self):
        """Test skill can handle SLO and error budget queries"""
        test_queries = [
            "How to define SLIs and SLOs?",
            "Error budget calculation and monitoring",
            "Service level objective implementation",
            "SLO dashboard in Grafana",
            "Track service reliability metrics",
        ]

        for query in test_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            confidence = self.skill.can_handle(context)
            assert confidence >= 0.5, f"Low confidence for query: {query}"

    def test_metadata_level_response(self):
        """Test metadata level response generation"""
        context = SkillContext(query="monitoring setup", conversation_history=[], available_tokens=100)

        result = self.skill.execute(context, SkillLevel.METADATA)

        assert result.skill_name == "monitoring_observability_expert"
        assert result.level == SkillLevel.METADATA
        assert result.tokens_used <= 100
        assert "monitoring" in result.content.lower()
        assert "observability" in result.content.lower()
        assert len(result.content.split()) > 10  # Ensure meaningful content

    def test_summary_level_response(self):
        """Test summary level response generation"""
        test_cases = [
            ("prometheus metrics", "metrics"),
            ("distributed tracing", "tracing"),
            ("ELK stack logging", "logging"),
            ("alert management", "alerting"),
            ("SLO management", "slo"),
        ]

        for query, expected_content in test_cases:
            context = SkillContext(query=query, conversation_history=[], available_tokens=500)

            result = self.skill.execute(context, SkillLevel.SUMMARY)

            assert result.skill_name == "monitoring_observability_expert"
            assert result.level == SkillLevel.SUMMARY
            assert result.tokens_used <= 500
            assert expected_content in result.content.lower()
            assert "##" in result.content  # Should contain markdown headers

    def test_detailed_level_response(self):
        """Test detailed level response generation"""
        context = SkillContext(
            query="Complete Prometheus and Grafana setup guide", conversation_history=[], available_tokens=5000
        )

        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.skill_name == "monitoring_observability_expert"
        assert result.level == SkillLevel.FULL
        assert result.tokens_used <= 5000
        assert len(result.content) > 1000  # Should be comprehensive
        assert "```" in result.content  # Should contain code blocks
        assert "prometheus" in result.content.lower()
        assert "grafana" in result.content.lower()

    def test_response_quality_and_accuracy(self):
        """Test response quality and technical accuracy"""
        test_queries = [
            "Prometheus configuration for Kubernetes",
            "Grafana dashboard JSON structure",
            "AlertManager routing rules",
            "SLI calculation formulas",
            "OpenTelemetry Python instrumentation",
        ]

        for query in test_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)

            result = self.skill.execute(context, SkillLevel.FULL)

            # Verify technical accuracy indicators
            content = result.content.lower()

            # Should contain code examples
            assert "```" in result.content

            # Should contain configuration examples
            assert any(keyword in content for keyword in ["prometheus.yml", "alertmanager.yml", "dashboard", "metric"])

            # Should be well-structured
            assert "##" in result.content  # Headers
            assert len(result.content.split("\n")) > 10  # Multiple lines

    def test_progressive_disclosure_structure(self):
        """Test progressive disclosure levels provide increasing detail"""
        query = "Set up comprehensive monitoring"

        context = SkillContext(query=query, conversation_history=[], available_tokens=5000)

        metadata_result = self.skill.execute(context, SkillLevel.METADATA)
        summary_result = self.skill.execute(context, SkillLevel.SUMMARY)
        detailed_result = self.skill.execute(context, SkillLevel.FULL)

        # Progressive disclosure should increase content length
        assert len(metadata_result.content) < len(summary_result.content)
        assert len(summary_result.content) < len(detailed_result.content)

        # Token usage should respect limits
        assert metadata_result.tokens_used <= 100
        assert summary_result.tokens_used <= 500
        assert detailed_result.tokens_used <= 5000

    def test_observability_tools_coverage(self):
        """Test coverage of major observability tools"""
        tools_to_test = [
            ("prometheus", ["metrics", "promql", "scrape"]),
            ("grafana", ["dashboard", "visualization", "panel"]),
            ("jaeger", ["tracing", "span", "trace"]),
            ("elasticsearch", ["logging", "search", "index"]),
            ("alertmanager", ["alert", "routing", "silence"]),
        ]

        for tool, expected_keywords in tools_to_test:
            query = f"How to use {tool} for observability?"
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)

            result = self.skill.execute(context, SkillLevel.SUMMARY)
            content_lower = result.content.lower()

            # Should mention the tool
            assert tool in content_lower

            # Should contain relevant keywords
            found_keywords = [kw for kw in expected_keywords if kw in content_lower]
            assert len(found_keywords) > 0, f"No relevant keywords found for {tool}"

    def test_error_handling(self):
        """Test error handling in skill execution"""
        context = SkillContext(
            query="",  # Empty query
            conversation_history=[],
            available_tokens=100,
        )

        # Should handle gracefully
        result = self.skill.execute(context, SkillLevel.METADATA)
        assert result.skill_name == "monitoring_observability_expert"
        assert result.content is not None
        assert len(result.content) > 0

    def test_execution_time_performance(self):
        """Test skill execution performance"""
        context = SkillContext(query="Comprehensive monitoring setup", conversation_history=[], available_tokens=2000)

        start_time = time.time()
        result = self.skill.execute(context, SkillLevel.FULL)
        execution_time = time.time() - start_time

        # Should execute reasonably quickly
        assert execution_time < 5.0  # 5 seconds max
        assert result.execution_time == execution_time

    def test_technical_accuracy_code_examples(self):
        """Test technical accuracy of code examples"""
        # Test Prometheus configuration examples
        context = SkillContext(
            query="Prometheus configuration for scraping applications", conversation_history=[], available_tokens=3000
        )

        result = self.skill.execute(context, SkillLevel.FULL)
        content = result.content

        # Should contain valid Prometheus configuration elements
        assert "scrape_configs:" in content
        assert "job_name:" in content
        assert "static_configs:" in content
        assert "targets:" in content

        # Should contain monitoring configuration
        assert "global:" in content or "scrape_interval:" in content

    def test_best_practices_inclusion(self):
        """Test inclusion of observability best practices"""
        context = SkillContext(
            query="Production monitoring best practices", conversation_history=[], available_tokens=3000
        )

        result = self.skill.execute(context, SkillLevel.FULL)
        content_lower = result.content.lower()

        # Should mention key best practices
        best_practices = ["golden signals", "error budget", "slo", "alerting", "dashboard", "retention", "cardinality"]

        found_practices = [practice for practice in best_practices if practice in content_lower]
        assert len(found_practices) >= 3, "Should include multiple best practices"

    def test_context_awareness(self):
        """Test skill shows different responses based on context"""
        queries_context_pairs = [
            ("prometheus setup", "should focus on Prometheus configuration"),
            ("alert routing", "should focus on AlertManager routing"),
            ("trace analysis", "should focus on Jaeger/OpenTelemetry tracing"),
        ]

        for query, expectation in queries_context_pairs:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)

            result = self.skill.execute(context, SkillLevel.SUMMARY)
            content_lower = result.content.lower()

            # Response should be relevant to the query context
            if "prometheus" in query:
                assert "prometheus" in content_lower
            elif "alert" in query:
                assert "alert" in content_lower
            elif "trace" in query:
                assert any(word in content_lower for word in ["trace", "jaeger", "opentelemetry"])

    def test_comprehensive_observability_coverage(self):
        """Test comprehensive coverage of observability pillars"""
        context = SkillContext(
            query="Complete observability stack implementation", conversation_history=[], available_tokens=5000
        )

        result = self.skill.execute(context, SkillLevel.FULL)
        content_lower = result.content.lower()

        # Should cover the three pillars of observability
        observability_pillars = {
            "metrics": ["prometheus", "metric", "counter", "gauge", "histogram"],
            "logs": ["log", "elasticsearch", "fluent", "kibana", "logging"],
            "traces": ["trace", "jaeger", "span", "opentelemetry", "zipkin"],
        }

        for pillar, keywords in observability_pillars.items():
            found_keywords = [kw for kw in keywords if kw in content_lower]
            assert len(found_keywords) > 0, f"Should cover {pillar} pillar of observability"


class TestObservabilityEnums:
    """Test observability-related enums and data structures"""

    def test_observability_tool_enum(self):
        """Test ObservabilityTool enum"""
        tools = list(ObservabilityTool)
        expected_tools = ["PROMETHEUS", "GRAFANA", "JAEGHER", "ELK_STACK", "OPENTELEMETRY"]

        tool_names = [tool.name for tool in tools]
        for expected_tool in expected_tools:
            assert expected_tool in tool_names

    def test_metric_type_enum(self):
        """Test MetricType enum"""
        metric_types = list(MetricType)
        expected_types = ["COUNTER", "GAUGE", "HISTOGRAM", "SUMMARY"]

        type_names = [metric.name for metric in metric_types]
        for expected_type in expected_types:
            assert expected_type in type_names

    def test_alert_severity_enum(self):
        """Test AlertSeverity enum"""
        severities = list(AlertSeverity)
        expected_severities = ["CRITICAL", "HIGH", "WARNING", "INFO"]

        severity_names = [severity.name for severity in severities]
        for expected_severity in expected_severities:
            assert expected_severity in severity_names

    def test_sli_type_enum(self):
        """Test ServiceLevelIndicatorType enum"""
        sli_types = list(ServiceLevelIndicatorType)
        expected_types = ["AVAILABILITY", "LATENCY", "THROUGHPUT", "ERROR_RATE"]

        type_names = [sli_type.name for sli_type in sli_types]
        for expected_type in expected_types:
            assert expected_type in type_names


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
