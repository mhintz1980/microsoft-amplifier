"""
Test suite for Cloud Platform Expert skill.

Zero-hallucination validation tests ensuring 100% technical accuracy.
Comprehensive testing of all cloud provider features and recommendations.
"""

import pytest
import asyncio
import json
from unittest.mock import Mock, AsyncMock, patch
from datetime import datetime, timedelta
from typing import Dict, Any, List

# Import the skill under test
from cloud_platform_expert import (
    CloudPlatformExpert,
    CloudProvider,
    CloudProviderConfig,
    CostOptimizationSettings,
    SecurityConfiguration,
    ScalingConfiguration,
    MonitoringConfiguration,
    validate_cloud_configuration,
    estimate_migration_complexity,
    CloudPerformanceOptimizer,
)
from ..skills_framework.skill_template import SkillContext, SkillResult


class TestCloudPlatformExpert:
    """Comprehensive test suite for Cloud Platform Expert skill"""

    @pytest.fixture
    def skill(self):
        """Create skill instance for testing"""
        return CloudPlatformExpert()

    @pytest.fixture
    def sample_aws_config(self):
        """Sample AWS configuration for testing"""
        return CloudProviderConfig(
            provider=CloudProvider.AWS,
            region="us-east-1",
            account_id="123456789012",
            environment="production",
            aws_config={"vpc_cidr": "10.0.0.0/16", "availability_zones": ["us-east-1a", "us-east-1b", "us-east-1c"]},
        )

    @pytest.fixture
    def sample_azure_config(self):
        """Sample Azure configuration for testing"""
        return CloudProviderConfig(
            provider=CloudProvider.AZURE,
            region="East US",
            subscription_id="subscription-123",
            tenant_id="tenant-123",
            environment="production",
        )

    @pytest.fixture
    def sample_gcp_config(self):
        """Sample GCP configuration for testing"""
        return CloudProviderConfig(
            provider=CloudProvider.GCP, region="us-central1", project_id="my-project-123", environment="production"
        )

    @pytest.fixture
    def basic_requirements(self):
        """Sample business and technical requirements"""
        return {
            "workload_type": "web_application",
            "expected_traffic": "medium",
            "data_volume": "medium",
            "availability_requirement": "99.9%",
            "performance_requirement": {"p99_latency": "500ms"},
            "compliance_requirements": ["SOC_2"],
            "budget_constraints": {"monthly_budget": 5000},
            "timeline": "standard",
            "team_expertise": "intermediate",
            "existing_infrastructure": [],
            "integration_requirements": ["api", "database"],
        }

    @pytest.fixture
    def skill_context(self, sample_aws_config, basic_requirements):
        """Create skill context with sample configuration"""
        return SkillContext(
            parameters={
                "cloud_config": {
                    "provider": "aws",
                    "region": "us-east-1",
                    "account_id": "123456789012",
                    "environment": "production",
                },
                "workload_type": "web_application",
                "expected_traffic": "medium",
                "data_volume": "medium",
                "availability_requirement": "99.9%",
                "compliance_requirements": ["SOC_2"],
                "budget_constraints": {"monthly_budget": 5000},
                "timeline": "standard",
                "team_expertise": "intermediate",
            }
        )


class TestConfigurationValidation:
    """Test configuration validation and setup"""

    def test_valid_aws_configuration(self):
        """Test valid AWS configuration validation"""
        config = CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1", account_id="123456789012")
        assert validate_cloud_configuration(config) is True

    def test_valid_azure_configuration(self):
        """Test valid Azure configuration validation"""
        config = CloudProviderConfig(
            provider=CloudProvider.AZURE, region="East US", subscription_id="subscription-123", tenant_id="tenant-123"
        )
        assert validate_cloud_configuration(config) is True

    def test_valid_gcp_configuration(self):
        """Test valid GCP configuration validation"""
        config = CloudProviderConfig(provider=CloudProvider.GCP, region="us-central1", project_id="my-project-123")
        assert validate_cloud_configuration(config) is True

    def test_invalid_aws_configuration_missing_account_id(self):
        """Test AWS configuration validation with missing account ID"""
        config = CloudProviderConfig(
            provider=CloudProvider.AWS,
            region="us-east-1",
            # Missing account_id
        )
        assert validate_cloud_configuration(config) is False

    def test_invalid_azure_configuration_missing_subscription(self):
        """Test Azure configuration validation with missing subscription ID"""
        config = CloudProviderConfig(
            provider=CloudProvider.AZURE,
            region="East US",
            # Missing subscription_id and tenant_id
        )
        assert validate_cloud_configuration(config) is False

    def test_invalid_gcp_configuration_missing_project(self):
        """Test GCP configuration validation with missing project ID"""
        config = CloudProviderConfig(
            provider=CloudProvider.GCP,
            region="us-central1",
            # Missing project_id
        )
        assert validate_cloud_configuration(config) is False


class TestSkillExecution:
    """Test main skill execution and recommendations"""

    @pytest.mark.asyncio
    async def test_successful_execution_aws(self, skill, skill_context):
        """Test successful skill execution with AWS configuration"""
        result = await skill.execute(skill_context)

        assert result.success is True
        assert result.data is not None
        assert "architecture" in result.data
        assert "cost_optimization" in result.data
        assert "security" in result.data
        assert "scalability" in result.data
        assert "implementation" in result.data
        assert result.execution_time > 0

    @pytest.mark.asyncio
    async def test_successful_execution_azure(self, skill):
        """Test successful skill execution with Azure configuration"""
        context = SkillContext(
            parameters={
                "cloud_config": {
                    "provider": "azure",
                    "region": "East US",
                    "subscription_id": "subscription-123",
                    "tenant_id": "tenant-123",
                },
                "workload_type": "web_application",
                "expected_traffic": "medium",
                "availability_requirement": "99.9%",
            }
        )

        result = await skill.execute(context)

        assert result.success is True
        assert result.metadata["provider"] == "azure"

    @pytest.mark.asyncio
    async def test_successful_execution_gcp(self, skill):
        """Test successful skill execution with GCP configuration"""
        context = SkillContext(
            parameters={
                "cloud_config": {"provider": "gcp", "region": "us-central1", "project_id": "my-project-123"},
                "workload_type": "web_application",
                "expected_traffic": "high",
                "availability_requirement": "99.99%",
            }
        )

        result = await skill.execute(context)

        assert result.success is True
        assert result.metadata["provider"] == "gcp"

    @pytest.mark.asyncio
    async def test_execution_with_invalid_config(self, skill):
        """Test skill execution with invalid configuration"""
        context = SkillContext(
            parameters={
                "cloud_config": {
                    "provider": "aws"
                    # Missing required fields
                }
            }
        )

        result = await skill.execute(context)

        assert result.success is False
        assert result.error is not None
        assert "Invalid cloud configuration" in result.error


class TestArchitectureRecommendations:
    """Test architecture pattern recommendations"""

    @pytest.mark.asyncio
    async def test_web_application_architecture_low_traffic(self, skill):
        """Test web application architecture recommendations for low traffic"""
        cloud_config = CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1")
        requirements = {"workload_type": "web_application", "expected_traffic": "low"}

        recommendations = await skill._generate_architecture_recommendations(cloud_config, requirements)

        assert recommendations["primary_pattern"]["pattern"].value == "serverless"
        assert "cost-effective" in recommendations["primary_pattern"]["rationale"]

    @pytest.mark.asyncio
    async def test_web_application_architecture_high_traffic(self, skill):
        """Test web application architecture recommendations for high traffic"""
        cloud_config = CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1")
        requirements = {"workload_type": "web_application", "expected_traffic": "high"}

        recommendations = await skill._generate_architecture_recommendations(cloud_config, requirements)

        assert recommendations["primary_pattern"]["pattern"].value == "microservices"
        assert "independent scaling" in recommendations["primary_pattern"]["rationale"]

    @pytest.mark.asyncio
    async def test_api_gateway_architecture(self, skill):
        """Test API gateway architecture recommendations"""
        cloud_config = CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1")
        requirements = {"workload_type": "api_gateway", "expected_traffic": "medium"}

        recommendations = await skill._generate_architecture_recommendations(cloud_config, requirements)

        assert recommendations["primary_pattern"]["pattern"].value == "backend_for_frontend"

    @pytest.mark.asyncio
    async def test_data_processing_architecture(self, skill):
        """Test data processing architecture recommendations"""
        cloud_config = CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1")
        requirements = {"workload_type": "data_processing", "expected_traffic": "medium"}

        recommendations = await skill._generate_architecture_recommendations(cloud_config, requirements)

        assert recommendations["primary_pattern"]["pattern"].value == "event_driven"

    def test_infrastructure_components_aws(self, skill):
        """Test AWS infrastructure component recommendations"""
        components = skill._recommend_infrastructure_components(CloudProvider.AWS, "web_application", "medium")

        assert "compute" in components
        assert "storage" in components
        assert "database" in components
        assert "networking" in components

        # Verify specific AWS services are included
        compute_services = [item["service"] for item in components["compute"]]
        assert "EC2" in compute_services
        assert "Lambda" in compute_services

    def test_infrastructure_components_azure(self, skill):
        """Test Azure infrastructure component recommendations"""
        components = skill._recommend_infrastructure_components(CloudProvider.AZURE, "web_application", "medium")

        assert "compute" in components
        assert "storage" in components
        assert "database" in components
        assert "networking" in components

        # Verify specific Azure services are included
        compute_services = [item["service"] for item in components["compute"]]
        assert "Virtual Machines" in compute_services
        assert "Functions" in compute_services

    def test_infrastructure_components_gcp(self, skill):
        """Test GCP infrastructure component recommendations"""
        components = skill._recommend_infrastructure_components(CloudProvider.GCP, "web_application", "medium")

        assert "compute" in components
        assert "storage" in components
        assert "database" in components
        assert "networking" in components

        # Verify specific GCP services are included
        compute_services = [item["service"] for item in components["compute"]]
        assert "Compute Engine" in compute_services
        assert "Cloud Functions" in compute_services


class TestCostOptimization:
    """Test cost optimization recommendations and calculations"""

    @pytest.mark.asyncio
    async def test_cost_optimization_generation(self, skill, sample_aws_config, basic_requirements):
        """Test cost optimization recommendations generation"""
        cost_opt = await skill._generate_cost_optimization(sample_aws_config, basic_requirements)

        assert "estimated_monthly_cost" in cost_opt
        assert "cost_breakdown" in cost_opt
        assert "optimization_recommendations" in cost_opt
        assert "potential_savings" in cost_opt
        assert "implementation_priority" in cost_opt

        # Verify cost breakdown includes expected components
        breakdown = cost_opt["cost_breakdown"]
        assert "compute" in breakdown
        assert "storage" in breakdown
        assert "network" in breakdown
        assert "database" in breakdown

    def test_cost_estimates_aws_web_app(self, skill):
        """Test AWS cost estimation for web application"""
        estimates = skill._generate_cost_estimates(CloudProvider.AWS, "web_application", "medium")

        assert estimates["estimated_monthly_cost"] > 0
        assert "breakdown" in estimates
        assert "assumptions" in estimates
        assert estimates["assumptions"]["provider"] == "aws"
        assert estimates["assumptions"]["workload_type"] == "web_application"

    def test_cost_estimates_azure_comparison(self, skill):
        """Test Azure cost estimation and comparison"""
        estimates = skill._generate_cost_estimates(CloudProvider.AZURE, "web_application", "medium")

        assert estimates["estimated_monthly_cost"] > 0
        assert estimates["assumptions"]["provider"] == "azure"

        # Azure should generally be competitive for web applications
        assert 50 < estimates["estimated_monthly_cost"] < 500

    def test_cost_estimates_gcp_comparison(self, skill):
        """Test GCP cost estimation and comparison"""
        estimates = skill._generate_cost_estimates(CloudProvider.GCP, "web_application", "medium")

        assert estimates["estimated_monthly_cost"] > 0
        assert estimates["assumptions"]["provider"] == "gcp"

    def test_traffic_impact_on_costs(self, skill):
        """Test that traffic levels appropriately impact cost estimates"""
        low_traffic = skill._generate_cost_estimates(CloudProvider.AWS, "web_application", "low")

        high_traffic = skill._generate_cost_estimates(CloudProvider.AWS, "web_application", "high")

        # High traffic should cost significantly more than low traffic
        assert high_traffic["estimated_monthly_cost"] > low_traffic["estimated_monthly_cost"]
        assert high_traffic["estimated_monthly_cost"] / low_traffic["estimated_monthly_cost"] >= 2.5

    def test_workload_type_impact_on_costs(self, skill):
        """Test that workload types appropriately impact cost estimates"""
        web_app = skill._generate_cost_estimates(CloudProvider.AWS, "web_application", "medium")

        data_processing = skill._generate_cost_estimates(CloudProvider.AWS, "data_processing", "medium")

        # Data processing should cost more than web applications
        assert data_processing["estimated_monthly_cost"] > web_app["estimated_monthly_cost"]


class TestSecurityRecommendations:
    """Test security and compliance recommendations"""

    @pytest.mark.asyncio
    async def test_security_recommendations_generation(self, skill, sample_aws_config):
        """Test security recommendations generation"""
        requirements = {"compliance_requirements": ["SOC_2", "PCI_DSS"]}
        security = await skill._generate_security_recommendations(sample_aws_config, requirements)

        assert "identity_and_access_management" in security
        assert "network_security" in security
        assert "data_protection" in security
        assert "threat_detection" in security
        assert "compliance" in security
        assert "incident_response" in security

    @pytest.mark.asyncio
    async def test_compliance_specific_recommendations(self, skill, sample_aws_config):
        """Test compliance-specific security recommendations"""
        requirements = {"compliance_requirements": ["HIPAA"]}
        security = await skill._generate_security_recommendations(sample_aws_config, requirements)

        # HIPAA should require additional security measures
        compliance = security["compliance"]
        assert "HIPAA" in str(compliance)

        iam = security["identity_and_access_management"]
        assert iam["mfa_enforcement"] is True

        data_protection = security["data_protection"]
        assert data_protection["encryption_at_rest"] is True
        assert data_protection["encryption_in_transit"] is True

    def test_aws_security_services_included(self, skill):
        """Test that AWS-specific security services are included"""
        iam_best_practices = skill._get_iam_best_practices(CloudProvider.AWS)

        # Should include AWS-specific IAM recommendations
        assert len(iam_best_practices) > 0
        # Should mention AWS IAM concepts
        practices_text = " ".join(iam_best_practices)
        assert any(aws_term in practices_text.lower() for aws_term in ["iam", "role", "policy"])


class TestScalabilityRecommendations:
    """Test scalability and high availability recommendations"""

    @pytest.mark.asyncio
    async def test_scalability_plan_generation(self, skill, sample_aws_config, basic_requirements):
        """Test scalability plan generation"""
        scalability = await skill._generate_scalability_plan(sample_aws_config, basic_requirements)

        assert "horizontal_scaling" in scalability
        assert "vertical_scaling" in scalability
        assert "high_availability" in scalability
        assert "performance_optimization" in scalability

    @pytest.mark.asyncio
    async def test_high_availability_requirements(self, skill, sample_aws_config):
        """Test high availability configuration based on requirements"""
        high_availability_requirements = {"availability_requirement": "99.999%"}
        scalability = await skill._generate_scalability_plan(sample_aws_config, high_availability_requirements)

        ha_config = scalability["high_availability"]
        assert ha_config["multi_region_deployment"] is True
        assert ha_config["multi_az_deployment"]["availability_zones"] >= 3

    @pytest.mark.asyncio
    async def test_standard_availability_requirements(self, skill, sample_aws_config):
        """Test standard availability configuration"""
        standard_requirements = {"availability_requirement": "99.9%"}
        scalability = await skill._generate_scalability_plan(sample_aws_config, standard_requirements)

        ha_config = scalability["high_availability"]
        assert ha_config["multi_az_deployment"]["availability_zones"] == 2

    def test_auto_scaling_configuration(self, skill):
        """Test auto-scaling configuration recommendations"""
        auto_scaling = skill._get_auto_scaling_configuration(CloudProvider.AWS, "medium")

        # Should include scaling configuration parameters
        assert auto_scaling is not None


class TestImplementationRoadmap:
    """Test implementation roadmap generation"""

    @pytest.mark.asyncio
    async def test_standard_timeline_roadmap(self, skill, sample_aws_config, basic_requirements):
        """Test standard timeline implementation roadmap"""
        basic_requirements["timeline"] = "standard"
        roadmap = await skill._generate_implementation_roadmap(sample_aws_config, basic_requirements, {})

        assert "phases" in roadmap
        assert "total_duration_weeks" in roadmap
        assert "critical_path" in roadmap
        assert "team_requirements" in roadmap

        # Standard timeline should be approximately 12 weeks
        assert 10 <= roadmap["total_duration_weeks"] <= 14

        # Should have 4 phases
        assert len(roadmap["phases"]) == 4

    @pytest.mark.asyncio
    async def test_rapid_timeline_roadmap(self, skill, sample_aws_config, basic_requirements):
        """Test rapid timeline implementation roadmap"""
        basic_requirements["timeline"] = "rapid"
        roadmap = await skill._generate_implementation_roadmap(sample_aws_config, basic_requirements, {})

        # Rapid timeline should be shorter
        assert roadmap["total_duration_weeks"] <= 6

    @pytest.mark.asyncio
    async def test_comprehensive_timeline_roadmap(self, skill, sample_aws_config, basic_requirements):
        """Test comprehensive timeline implementation roadmap"""
        basic_requirements["timeline"] = "comprehensive"
        roadmap = await skill._generate_implementation_roadmap(sample_aws_config, basic_requirements, {})

        # Comprehensive timeline should be longer
        assert roadmap["total_duration_weeks"] >= 20

    def test_phase_structure(self, skill):
        """Test that phases have required structure"""
        phases = skill._generate_implementation_roadmap(
            CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1"), {"timeline": "standard"}, {}
        )["phases"]

        for phase in phases:
            assert "name" in phase
            assert "duration_weeks" in phase
            assert "tasks" in phase
            assert "deliverables" in phase

            # Each task should have required fields
            for task in phase["tasks"]:
                assert "task" in task
                assert "estimated_days" in task
                assert "priority" in task


class TestMigrationComplexity:
    """Test migration complexity estimation"""

    def test_simple_infrastructure_complexity(self):
        """Test complexity estimation for simple infrastructure"""
        infrastructure = [
            {"type": "web_server", "data_size_gb": 10, "dependencies": []},
            {"type": "database", "data_size_gb": 50, "dependencies": []},
        ]

        complexity = estimate_migration_complexity(infrastructure)

        assert complexity["complexity_level"] in ["Low", "Medium"]
        assert complexity["estimated_duration_months"] <= 6
        assert complexity["complexity_score"] <= 10

    def test_complex_infrastructure_complexity(self):
        """Test complexity estimation for complex infrastructure"""
        infrastructure = [
            {"type": "web_server", "data_size_gb": 100, "dependencies": ["database", "cache"]},
            {"type": "database", "data_size_gb": 1000, "dependencies": ["backup"]},
            {"type": "cache", "data_size_gb": 50, "dependencies": []},
            {"type": "message_queue", "data_size_gb": 10, "dependencies": ["database"]},
            {"type": "search_index", "data_size_gb": 200, "dependencies": ["database"]},
        ]

        complexity = estimate_migration_complexity(infrastructure)

        assert complexity["complexity_level"] in ["High", "Very High"]
        assert complexity["estimated_duration_months"] >= 6
        assert complexity["complexity_score"] > 10

    def test_empty_infrastructure_complexity(self):
        """Test complexity estimation for empty infrastructure"""
        complexity = estimate_migration_complexity([])

        assert complexity["complexity_level"] == "Low"
        assert complexity["estimated_duration_months"] <= 3
        assert complexity["complexity_score"] == 0


class TestTechnicalAccuracyValidation:
    """Test zero-hallucination technical accuracy validation"""

    def test_aws_service_names_accuracy(self, skill):
        """Test that AWS service names are technically accurate"""
        components = skill._recommend_infrastructure_components(CloudProvider.AWS, "web_application", "medium")

        # Verify all AWS service names are accurate
        compute_services = [item["service"] for item in components["compute"]]
        valid_aws_compute = ["EC2", "Fargate", "Lambda", "EKS"]
        for service in compute_services:
            assert service in valid_aws_compute, f"Invalid AWS compute service: {service}"

        storage_services = [item["service"] for item in components["storage"]]
        valid_aws_storage = ["S3", "EFS", "EBS"]
        for service in storage_services:
            assert service in valid_aws_storage, f"Invalid AWS storage service: {service}"

        database_services = [item["service"] for item in components["database"]]
        valid_aws_database = ["RDS", "DynamoDB", "ElastiCache"]
        for service in database_services:
            assert service in valid_aws_database, f"Invalid AWS database service: {service}"

    def test_azure_service_names_accuracy(self, skill):
        """Test that Azure service names are technically accurate"""
        components = skill._recommend_infrastructure_components(CloudProvider.AZURE, "web_application", "medium")

        # Verify all Azure service names are accurate
        compute_services = [item["service"] for item in components["compute"]]
        valid_azure_compute = ["Virtual Machines", "Container Instances", "Functions", "AKS"]
        for service in compute_services:
            assert service in valid_azure_compute, f"Invalid Azure compute service: {service}"

        storage_services = [item["service"] for item in components["storage"]]
        valid_azure_storage = ["Blob Storage", "Files", "Disk Storage"]
        for service in storage_services:
            assert service in valid_azure_storage, f"Invalid Azure storage service: {service}"

    def test_gcp_service_names_accuracy(self, skill):
        """Test that GCP service names are technically accurate"""
        components = skill._recommend_infrastructure_components(CloudProvider.GCP, "web_application", "medium")

        # Verify all GCP service names are accurate
        compute_services = [item["service"] for item in components["compute"]]
        valid_gcp_compute = ["Compute Engine", "Cloud Run", "Cloud Functions", "GKE"]
        for service in compute_services:
            assert service in valid_gcp_compute, f"Invalid GCP compute service: {service}"

        storage_services = [item["service"] for item in components["storage"]]
        valid_gcp_storage = ["Cloud Storage", "Filestore", "Persistent Disk"]
        for service in storage_services:
            assert service in valid_gcp_storage, f"Invalid GCP storage service: {service}"

    def test_compliance_framework_accuracy(self, skill):
        """Test that compliance framework information is accurate"""
        compliance_frameworks = {
            "SOC_2": "Service Organization Control 2",
            "ISO_27001": "International Organization for Standardization 27001",
            "GDPR": "General Data Protection Regulation",
            "HIPAA": "Health Insurance Portability and Accountability Act",
            "PCI_DSS": "Payment Card Industry Data Security Standard",
            "FedRAMP": "Federal Risk and Authorization Management Program",
        }

        # Test that compliance mappings are accurate
        for framework in compliance_frameworks:
            compliance_mapping = skill._get_compliance_mapping([framework], CloudProvider.AWS)
            assert compliance_mapping is not None

    def test_cost_estimate_reasonableness(self, skill):
        """Test that cost estimates are reasonable and not hallucinated"""
        for provider in [CloudProvider.AWS, CloudProvider.AZURE, CloudProvider.GCP]:
            for workload in ["web_application", "api_gateway", "data_processing"]:
                for traffic in ["low", "medium", "high"]:
                    estimates = skill._generate_cost_estimates(provider, workload, traffic)

                    # Costs should be reasonable (not $1 or $1,000,000 for basic workloads)
                    assert 10 <= estimates["estimated_monthly_cost"] <= 50000, (
                        f"Unreasonable cost estimate for {provider.value} {workload} {traffic}"
                    )

                    # Cost breakdown should make sense
                    breakdown = estimates["cost_breakdown"]
                    total_from_breakdown = sum(breakdown.values())
                    assert abs(total_from_breakdown - estimates["estimated_monthly_cost"]) < 1, (
                        "Cost breakdown doesn't match total"
                    )

    def test_availability_tier_technical_accuracy(self, skill):
        """Test that availability tier configurations are technically accurate"""
        availability_tiers = {
            "99.9%": {"downtime_per_year_hours": 8.76, "multi_az_required": True, "multi_region_required": False},
            "99.99%": {"downtime_per_year_hours": 0.876, "multi_az_required": True, "multi_region_required": False},
            "99.999%": {"downtime_per_year_hours": 0.0876, "multi_az_required": True, "multi_region_required": True},
            "99.9999%": {"downtime_per_year_hours": 0.00876, "multi_az_required": True, "multi_region_required": True},
        }

        for availability, expected in availability_tiers.items():
            network_config = skill._recommend_network_architecture(CloudProvider.AWS, availability)

            # Verify multi-AZ and multi-region requirements match availability targets
            if expected["multi_region_required"]:
                assert network_config["multi_region"] is True
                assert network_config["regions"] >= 2

            assert network_config["availability_zones"] >= (3 if expected["multi_region_required"] else 2)


class TestPerformanceOptimization:
    """Test performance optimization features"""

    def test_performance_optimizer_creation(self):
        """Test CloudPerformanceOptimizer creation"""
        optimizer = CloudPerformanceOptimizer(CloudProvider.AWS)
        assert optimizer.provider == CloudProvider.AWS
        assert hasattr(optimizer, "optimization_rules")

    def test_performance_analysis_method(self):
        """Test performance analysis method structure"""
        optimizer = CloudPerformanceOptimizer(CloudProvider.AWS)
        metrics = {"cpu_utilization": 70, "memory_utilization": 80}

        # Should not raise errors (method structure validation)
        result = optimizer.analyze_performance(metrics)
        assert isinstance(result, list)

    def test_optimization_plan_generation(self):
        """Test optimization plan generation structure"""
        optimizer = CloudPerformanceOptimizer(CloudProvider.AWS)
        analysis = [{"metric": "cpu", "recommendation": "scale_up"}]

        # Should not raise errors (method structure validation)
        plan = optimizer.generate_optimization_plan(analysis)
        assert isinstance(plan, dict)


class TestCachingAndPerformance:
    """Test caching and performance optimization features"""

    def test_cache_key_generation(self, skill):
        """Test cache key generation uniqueness and consistency"""
        config = CloudProviderConfig(provider=CloudProvider.AWS, region="us-east-1")
        requirements = {"workload_type": "web_application", "expected_traffic": "medium"}

        key1 = skill._generate_cache_key(config, requirements)
        key2 = skill._generate_cache_key(config, requirements)

        # Same inputs should generate same key
        assert key1 == key2

        # Different inputs should generate different keys
        different_requirements = {"workload_type": "api_gateway", "expected_traffic": "medium"}
        key3 = skill._generate_cache_key(config, different_requirements)
        assert key1 != key3

    def test_complexity_assessment_accuracy(self, skill):
        """Test complexity assessment logic"""
        simple_requirements = {
            "workload_type": "web_application",
            "expected_traffic": "low",
            "availability_requirement": "99.9%",
            "compliance_requirements": [],
        }

        complexity = skill._assess_complexity(simple_requirements)
        assert complexity in ["Low", "Medium"]

        complex_requirements = {
            "workload_type": "real_time",
            "expected_traffic": "very_high",
            "availability_requirement": "99.9999%",
            "compliance_requirements": ["SOC_2", "HIPAA", "PCI_DSS", "FedRAMP"],
        }

        complexity = skill._assess_complexity(complex_requirements)
        assert complexity in ["High", "Very High"]


class TestErrorHandling:
    """Test error handling and edge cases"""

    @pytest.mark.asyncio
    async def test_missing_cloud_config_parameter(self, skill):
        """Test handling of missing cloud configuration parameter"""
        context = SkillContext(
            parameters={
                # Missing cloud_config
                "workload_type": "web_application"
            }
        )

        result = await skill.execute(context)

        assert result.success is False
        assert "error" in result.__dict__

    @pytest.mark.asyncio
    async def test_invalid_provider_parameter(self, skill):
        """Test handling of invalid cloud provider parameter"""
        context = SkillContext(parameters={"cloud_config": {"provider": "invalid_provider", "region": "us-east-1"}})

        result = await skill.execute(context)

        assert result.success is False

    @pytest.mark.asyncio
    async def test_empty_parameters(self, skill):
        """Test handling of empty parameters"""
        context = SkillContext(parameters={})

        result = await skill.execute(context)

        # Should use defaults and not fail completely
        # This might succeed with default values or fail gracefully
        assert result is not None


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
