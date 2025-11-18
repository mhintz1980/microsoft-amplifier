"""
Test suite for Cloud Integration Expert skill

Comprehensive testing including unit tests, integration tests,
and real-world scenario validation.
"""

import pytest
import json
import time
from unittest.mock import Mock, patch, MagicMock

# Import the skill under test
from cloud_integration_expert import (
    CloudIntegrationExpert,
    CloudProvider,
    IntegrationType,
    DeploymentPattern,
    CloudConfiguration,
)
from amplifier.skills.skills_framework.skill_template import SkillContext, SkillLevel


class TestCloudIntegrationExpert:
    """Test suite for CloudIntegrationExpert skill."""

    def setup_method(self):
        """Set up test fixtures before each test method."""
        self.skill = CloudIntegrationExpert()

    def test_skill_initialization(self):
        """Test skill initializes correctly."""
        assert self.skill.skill_name == "cloud_integration_expert"
        assert len(self.skill.tags) > 0
        assert "cloud" in self.skill.tags
        assert "aws" in self.skill.tags
        assert "azure" in self.skill.tags
        assert "gcp" in self.skill.tags

    def test_skill_description(self):
        """Test skill description is comprehensive."""
        description = self.skill.description
        assert "cloud" in description.lower()
        assert "aws" in description.lower() or "azure" in description.lower() or "gcp" in description.lower()
        assert "integration" in description.lower()
        assert len(description) > 100  # Ensure substantive description

    def test_tags_completeness(self):
        """Test skill tags cover key areas."""
        required_tags = ["cloud", "serverless", "integration", "cost-optimization"]

        for tag in required_tags:
            assert tag in self.skill.tags

    def test_can_handle_aws_queries(self):
        """Test confidence scoring for AWS-related queries."""
        aws_queries = [
            "How do I integrate with AWS S3?",
            "Set up Lambda functions for my application",
            "AWS RDS database integration patterns",
            "Cost optimization for AWS services",
        ]

        for query in aws_queries:
            context = SkillContext(query=query, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence > 0.5, f"Low confidence for AWS query: {query}"

    def test_can_handle_azure_queries(self):
        """Test confidence scoring for Azure-related queries."""
        azure_queries = [
            "Integrate with Azure Blob Storage",
            "Azure Functions best practices",
            "Azure Cosmos DB integration",
            "Azure cost management strategies",
        ]

        for query in azure_queries:
            context = SkillContext(query=query, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence > 0.5, f"Low confidence for Azure query: {query}"

    def test_can_handle_gcp_queries(self):
        """Test confidence scoring for GCP-related queries."""
        gcp_queries = [
            "Google Cloud Storage integration",
            "Cloud Functions implementation",
            "BigQuery data pipeline setup",
            "GCP cost optimization techniques",
        ]

        for query in gcp_queries:
            context = SkillContext(query=query, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence > 0.5, f"Low confidence for GCP query: {query}"

    def test_can_handle_multi_cloud_queries(self):
        """Test confidence scoring for multi-cloud queries."""
        multi_cloud_queries = [
            "Multi-cloud strategy for enterprise",
            "Best practices for AWS and Azure integration",
            "Compare GCP vs AWS for my use case",
            "Hybrid cloud architecture patterns",
        ]

        for query in multi_cloud_queries:
            context = SkillContext(query=query, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence > 0.4, f"Low confidence for multi-cloud query: {query}"

    def test_can_handle_serverless_queries(self):
        """Test confidence scoring for serverless queries."""
        serverless_queries = [
            "Serverless architecture design",
            "Event-driven microservices",
            "Functions-as-a-Service patterns",
            "Lambda vs Cloud Functions comparison",
        ]

        for query in serverless_queries:
            context = SkillContext(query=query, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence > 0.5, f"Low confidence for serverless query: {query}"

    def test_can_handle_low_relevance_queries(self):
        """Test confidence scoring for unrelated queries."""
        unrelated_queries = [
            "How to cook pasta",
            "Best programming language for beginners",
            "Local development setup",
            "UI design principles",
        ]

        for query in unrelated_queries:
            context = SkillContext(query=query, available_tokens=1000)
            confidence = self.skill.can_handle(context)
            assert confidence < 0.3, f"High confidence for unrelated query: {query}"

    def test_execute_metadata_level(self):
        """Test metadata level execution."""
        context = SkillContext(query="AWS integration", conversation_history=[], available_tokens=100)

        result = self.skill.execute(context, SkillLevel.METADATA)

        assert result.success is True
        assert result.level == SkillLevel.METADATA
        assert len(result.content) < 200  # Should be very concise
        assert "cloud" in result.content.lower()
        assert result.execution_time > 0
        assert result.tokens_used < 100

    def test_execute_summary_level(self):
        """Test summary level execution."""
        context = SkillContext(query="AWS S3 integration with Lambda", conversation_history=[], available_tokens=500)

        result = self.skill.execute(context, SkillLevel.SUMMARY)

        assert result.success is True
        assert result.level == SkillLevel.SUMMARY
        assert "aws" in result.content.lower()
        assert "integration" in result.content.lower()
        assert result.tokens_used < 500

    def test_execute_full_level(self):
        """Test full level execution."""
        context = SkillContext(
            query="Complete AWS serverless architecture with S3, Lambda, and DynamoDB",
            conversation_history=[],
            available_tokens=5000,
        )

        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True
        assert result.level == SkillLevel.FULL
        assert len(result.content) > 1000  # Should be comprehensive
        assert "aws" in result.content.lower()
        assert "lambda" in result.content.lower()
        assert "s3" in result.content.lower() or "storage" in result.content.lower()
        assert result.execution_time > 0

    def test_provider_analysis_aws(self):
        """Test AWS provider analysis."""
        analysis = self.skill._analyze_provider_context("AWS Lambda and S3 integration")

        assert analysis["recommended_provider"] == "aws"
        assert "serverless" in analysis["integration_types"]
        assert "storage" in analysis["integration_types"]

    def test_provider_analysis_azure(self):
        """Test Azure provider analysis."""
        analysis = self.skill._analyze_provider_context("Azure Functions with Cosmos DB")

        assert analysis["recommended_provider"] == "azure"
        assert "serverless" in analysis["integration_types"]
        assert "database" in analysis["integration_types"]

    def test_provider_analysis_gcp(self):
        """Test GCP provider analysis."""
        analysis = self.skill._analyze_provider_context("Google Cloud Functions and BigQuery")

        assert analysis["recommended_provider"] == "gcp"
        assert "serverless" in analysis["integration_types"]
        assert "database" in analysis["integration_types"]

    def test_provider_analysis_multi_cloud(self):
        """Test multi-cloud scenario analysis."""
        analysis = self.skill._analyze_provider_context("Compare AWS and Azure for enterprise")

        assert analysis["recommended_provider"] in ["aws", "azure"]  # Should pick one as primary

    def test_migration_pattern_analysis(self):
        """Test migration pattern detection."""
        test_cases = [
            ("migrate application to cloud", "lift_and_shift"),
            ("replatform for cloud optimization", "re_platform"),
            ("serverless architecture redesign", "serverless_first"),
            ("convert to microservices", "microservices"),
        ]

        for query, expected_pattern in test_cases:
            analysis = self.skill._analyze_provider_context(query)
            assert analysis["migration_pattern"] == expected_pattern

    def test_storage_guidance_aws(self):
        """Test AWS storage guidance."""
        guidance = self.skill._get_storage_guidance("aws")

        assert "S3" in guidance
        assert "EFS" in guidance
        assert "object storage" in guidance.lower()
        assert len(guidance) > 200

    def test_storage_guidance_azure(self):
        """Test Azure storage guidance."""
        guidance = self.skill._get_storage_guidance("azure")

        assert "Blob Storage" in guidance
        assert "File Storage" in guidance
        assert len(guidance) > 200

    def test_storage_guidance_gcp(self):
        """Test GCP storage guidance."""
        guidance = self.skill._get_storage_guidance("gcp")

        assert "Cloud Storage" in guidance
        assert "Filestore" in guidance
        assert len(guidance) > 200

    def test_database_guidance_contains_key_services(self):
        """Test database guidance covers key services."""
        for provider in ["aws", "azure", "gcp"]:
            guidance = self.skill._get_database_guidance(provider)

            # Should mention database services
            assert any(
                db_service in guidance for db_service in ["RDS", "SQL", "Firestore", "Cosmos", "DynamoDB", "BigQuery"]
            )
            assert len(guidance) > 200

    def test_serverless_guidance_code_examples(self):
        """Test serverless guidance includes code examples."""
        for provider in ["aws", "azure", "gcp"]:
            guidance = self.skill._get_serverless_guidance(provider)

            # Should include code examples
            assert "def " in guidance or "function" in guidance.lower()
            assert "```" in guidance  # Code blocks
            assert len(guidance) > 500

    def test_iam_guidance_security_focus(self):
        """Test IAM guidance focuses on security."""
        for provider in ["aws", "azure", "gcp"]:
            guidance = self.skill._get_iam_guidance(provider)

            # Should mention security concepts
            assert any(
                security_term in guidance.lower()
                for security_term in ["least privilege", "mfa", "authentication", "authorization", "security"]
            )

    def test_cost_optimization_guidance_practical(self):
        """Test cost optimization guidance is practical."""
        for provider in ["aws", "azure", "gcp"]:
            guidance = self.skill._get_cost_optimization_guidance(provider)

            # Should mention specific optimization techniques
            assert any(
                cost_term in guidance.lower()
                for cost_term in ["reserved", "spot", "autoscaling", "savings", "monitoring"]
            )

    def test_security_guidance_comprehensive(self):
        """Test security guidance covers comprehensive security."""
        for provider in ["aws", "azure", "gcp"]:
            guidance = self.skill._get_security_guidance(provider)

            # Should cover multiple security aspects
            assert any(network_term in guidance.lower() for network_term in ["network", "vpc", "firewall"])
            assert any(data_term in guidance.lower() for data_term in ["encryption", "data"])
            assert any(monitoring_term in guidance.lower() for monitoring_term in ["monitoring", "logging"])

    def test_implementation_examples_infrastructure_as_code(self):
        """Test implementation examples include infrastructure as code."""
        for provider in ["aws", "azure", "gcp"]:
            examples = self.skill._get_implementation_examples(provider)

            # Should include infrastructure as code examples
            assert any(
                iac_term in examples.lower() for iac_term in ["cloudformation", "terraform", "arm template", "bicep"]
            )

    def test_monitoring_guidance_observability(self):
        """Test monitoring guidance covers observability."""
        for provider in ["aws", "azure", "gcp"]:
            guidance = self.skill._get_monitoring_guidance(provider)

            # Should mention observability components
            assert any(
                observability_term in guidance.lower()
                for observability_term in ["metrics", "logs", "tracing", "monitoring"]
            )

    def test_integration_patterns_loaded(self):
        """Test integration patterns are loaded correctly."""
        assert len(self.skill._integration_patterns) > 0

        # Check key patterns exist
        assert "aws_serverless_api" in self.skill._integration_patterns
        assert "azure_event_driven" in self.skill._integration_patterns
        assert "gcp_streaming" in self.skill._integration_patterns

    def test_integration_patterns_structure(self):
        """Test integration patterns have required structure."""
        for pattern_name, pattern in self.skill._integration_patterns.items():
            assert pattern.name
            assert pattern.description
            assert pattern.provider
            assert pattern.integration_type
            assert pattern.implementation
            assert pattern.cost_estimate
            assert isinstance(pattern.security_considerations, list)
            assert pattern.example_code

    def test_cost_rules_comprehensive(self):
        """Test cost optimization rules are comprehensive."""
        cost_rules = self.skill._cost_optimization_rules

        assert "compute_optimization" in cost_rules
        assert "storage_optimization" in cost_rules
        assert "network_optimization" in cost_rules
        assert "data_transfer" in cost_rules

        for rule_category, rules in cost_rules.items():
            assert isinstance(rules, dict)
            assert len(rules) > 0

    def test_security_checklists_comprehensive(self):
        """Test security checklists are comprehensive."""
        checklists = self.skill._security_checklists

        required_categories = ["identity_security", "network_security", "data_security", "application_security"]

        for category in required_categories:
            assert category in checklists
            assert isinstance(checklists[category], list)
            assert len(checklists[category]) > 0

    def test_error_handling_in_execute(self):
        """Test error handling in execute method."""
        # Test with malformed context that might cause errors
        try:
            context = SkillContext(
                query="",  # Empty query
                conversation_history=None,  # None instead of list
                available_tokens=-1000,  # Invalid token count
            )

            result = self.skill.execute(context, SkillLevel.SUMMARY)

            # Should still return a result, not raise an exception
            assert result is not None
        except Exception as e:
            # If exception is raised, it should be handled gracefully
            assert False, f"Unhandled exception in execute: {e}"

    def test_token_efficiency_metadata(self):
        """Test metadata level respects token limits."""
        context = SkillContext(query="cloud", available_tokens=50)
        result = self.skill.execute(context, SkillLevel.METADATA)

        assert result.tokens_used <= context.available_tokens

    def test_token_efficiency_summary(self):
        """Test summary level respects token limits."""
        context = SkillContext(query="cloud integration", available_tokens=200)
        result = self.skill.execute(context, SkillLevel.SUMMARY)

        assert result.tokens_used <= context.available_tokens

    def test_progressive_disclosure_levels(self):
        """Test progressive disclosure provides increasing detail."""
        context = SkillContext(query="AWS serverless architecture", available_tokens=5000)

        metadata_result = self.skill.execute(context, SkillLevel.METADATA)
        summary_result = self.skill.execute(context, SkillLevel.SUMMARY)
        full_result = self.skill.execute(context, SkillLevel.FULL)

        # Content should increase with each level
        assert len(full_result.content) > len(summary_result.content)
        assert len(summary_result.content) > len(metadata_result.content)

    def test_real_world_scenario_ecommerce(self):
        """Test real-world e-commerce scenario."""
        query = """
        Design a cloud architecture for an e-commerce platform that needs:
        - Product catalog with search capabilities
        - Shopping cart and checkout process
        - Order processing and fulfillment
        - User authentication and profiles
        - Payment processing
        - Analytics and reporting
        - Cost optimization for variable traffic
        """

        context = SkillContext(query=query, available_tokens=5000)
        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True
        assert "storage" in result.content.lower()
        assert "database" in result.content.lower()
        assert "serverless" in result.content.lower()
        assert "cost" in result.content.lower()

    def test_real_world_scenario_iot(self):
        """Test real-world IoT scenario."""
        query = """
        Design a cloud architecture for IoT data processing:
        - Handle millions of device messages per hour
        - Real-time data processing and alerting
        - Historical data storage and analysis
        - Device management and provisioning
        - Security and compliance requirements
        """

        context = SkillContext(query=query, available_tokens=5000)
        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True
        assert "messaging" in result.content.lower() or "queue" in result.content.lower()
        assert "processing" in result.content.lower()
        assert "storage" in result.content.lower()

    def test_real_world_scenario_fintech(self):
        """Test real-world fintech scenario."""
        query = """
        Cloud architecture for financial technology application:
        - High security and compliance (PCI DSS)
        - Transaction processing with ACID guarantees
        - Real-time fraud detection
        - Audit logging and regulatory compliance
        - High availability and disaster recovery
        """

        context = SkillContext(query=query, available_tokens=5000)
        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True
        assert "security" in result.content.lower()
        assert "database" in result.content.lower()
        assert "compliance" in result.content.lower()

    def test_performance_under_load(self):
        """Test skill performance under multiple requests."""
        queries = [
            "AWS S3 integration",
            "Azure Functions setup",
            "GCP BigQuery pipeline",
            "Multi-cloud strategy",
            "Serverless cost optimization",
        ]

        start_time = time.time()
        results = []

        for query in queries:
            context = SkillContext(query=query, available_tokens=1000)
            result = self.skill.execute(context, SkillLevel.SUMMARY)
            results.append(result)

        total_time = time.time() - start_time

        # Should complete all queries efficiently
        assert total_time < 10.0  # Less than 10 seconds for 5 queries
        assert all(result.success for result in results)
        assert all(result.execution_time < 2.0 for result in results)  # Each under 2 seconds

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        edge_cases = [
            "",  # Empty query
            "a" * 1000,  # Very long query
            "🚀☁️📦",  # Unicode emojis
            "   " * 10,  # Only whitespace
            "Special chars: !@#$%^&*()",  # Special characters
        ]

        for query in edge_cases:
            context = SkillContext(query=query, available_tokens=1000)
            result = self.skill.execute(context, SkillLevel.METADATA)

            # Should handle gracefully without crashing
            assert result is not None
            assert isinstance(result.content, str)

    def test_concurrent_execution(self):
        """Test concurrent execution of the skill."""
        import threading

        results = []

        def execute_skill():
            context = SkillContext(query="AWS integration", available_tokens=1000)
            result = self.skill.execute(context, SkillLevel.SUMMARY)
            results.append(result)

        # Create multiple threads
        threads = [threading.Thread(target=execute_skill) for _ in range(5)]

        # Start all threads
        for thread in threads:
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # All should complete successfully
        assert len(results) == 5
        assert all(result.success for result in results)


class TestCloudIntegrationExpertIntegration:
    """Integration tests for Cloud Integration Expert."""

    def setup_method(self):
        """Set up integration test fixtures."""
        self.skill = CloudIntegrationExpert()

    def test_end_to_end_aws_scenario(self):
        """Test end-to-end AWS scenario."""
        # Simulate a conversation about AWS migration
        conversation_history = [
            {"role": "user", "content": "I want to migrate my web application to AWS"},
            {"role": "assistant", "content": "I can help you design an AWS migration strategy"},
            {"role": "user", "content": "The app has user data, product catalog, and orders"},
        ]

        context = SkillContext(
            query="Design complete AWS architecture with database, storage, and serverless components",
            conversation_history=conversation_history,
            available_tokens=5000,
        )

        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True
        assert "aws" in result.content.lower()
        assert "architecture" in result.content.lower()
        # Should be comprehensive with multiple sections
        assert len(result.content) > 2000

    def test_end_to_end_multi_cloud_comparison(self):
        """Test end-to-end multi-cloud comparison."""
        context = SkillContext(
            query="Compare AWS, Azure, and GCP for machine learning workloads including cost, performance, and ease of use",
            available_tokens=5000,
        )

        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True
        # Should mention multiple providers
        providers_mentioned = []
        for provider in ["aws", "azure", "gcp"]:
            if provider in result.content.lower():
                providers_mentioned.append(provider)

        assert len(providers_mentioned) >= 2  # Should mention at least 2 providers

    def test_technical_accuracy_validation(self):
        """Test technical accuracy of provided information."""
        # Query for specific technical details
        context = SkillContext(
            query="What are the exact pricing models and service limits for AWS Lambda, Azure Functions, and Google Cloud Functions?",
            available_tokens=3000,
        )

        result = self.skill.execute(context, SkillLevel.FULL)

        assert result.success is True

        # Should contain accurate technical information
        # (This is a simplified validation - in practice, you'd want more specific checks)
        assert "lambda" in result.content.lower() or "functions" in result.content.lower()
        assert "pricing" in result.content.lower() or "cost" in result.content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
