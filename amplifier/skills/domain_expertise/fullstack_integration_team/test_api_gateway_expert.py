"""
Test suite for API Gateway Expert Skill

Comprehensive tests to validate functionality, accuracy, and reliability
of the API Gateway Expert skill implementation.
"""

import pytest
import asyncio
import json
import time
from unittest.mock import Mock, AsyncMock, patch
from typing import Dict, Any

# Import the skill
from api_gateway_expert import APIGatewayExpert, GatewayConfig, GatewayType, AuthenticationType


class TestAPIGatewayExpert:
    """Test suite for API Gateway Expert skill"""

    @pytest.fixture
    def skill(self):
        """Create skill instance for testing"""
        return APIGatewayExpert()

    @pytest.fixture
    def mock_context(self):
        """Create mock skill context"""
        context = Mock()
        context.parameters = {}
        return context

    @pytest.fixture
    def sample_gateway_config(self):
        """Sample gateway configuration for testing"""
        return GatewayConfig(
            gateway_type=GatewayType.KONG,
            environment="production",
            authentication={"type": "jwt", "issuer": "https://auth.example.com"},
            rate_limiting={"requests_per_minute": 1000},
            load_balancing_strategy="round_robin",
        )

    class TestSkillInitialization:
        """Test skill initialization and basic properties"""

        def test_skill_initialization(self, skill):
            """Test skill initializes correctly"""
            assert skill.name == "api_gateway_expert"
            assert skill.version == "1.0.0"
            assert "gateway architecture" in skill.description.lower()

        def test_disclosure_levels_available(self, skill):
            """Test all disclosure levels are available"""
            expected_levels = ["METADATA", "SUMMARY", "DETAILED", "FULL"]
            assert all(level in skill.disclosure_levels for level in expected_levels)

        def test_gateway_templates_initialized(self, skill):
            """Test gateway templates are initialized"""
            assert hasattr(skill, "gateway_templates")
            assert isinstance(skill.gateway_templates, dict)
            assert "kong" in skill.gateway_templates

        def test_best_practices_initialized(self, skill):
            """Test best practices are initialized"""
            assert hasattr(skill, "best_practices")
            assert isinstance(skill.best_practices, dict)
            assert "security" in skill.best_practices
            assert "performance" in skill.best_practices

    class TestProgressiveDisclosure:
        """Test progressive disclosure functionality"""

        @pytest.mark.asyncio
        async def test_metadata_disclosure(self, skill):
            """Test METADATA level disclosure"""
            content = skill._get_metadata_content()

            assert isinstance(content, dict)
            assert "name" in content
            assert "purpose" in content
            assert "capabilities" in content
            assert "supported_gateways" in content
            assert len(content["capabilities"]) <= 10  # Compressed content

        @pytest.mark.asyncio
        async def test_summary_disclosure(self, skill):
            """Test SUMMARY level disclosure"""
            content = skill._get_summary_content()

            assert isinstance(content, dict)
            assert "overview" in content
            assert "architecture_patterns" in content
            assert "gateway_selection" in content
            assert "key_considerations" in content

        @pytest.mark.asyncio
        async def test_detailed_disclosure(self, skill):
            """Test DETAILED level disclosure"""
            content = skill._get_detailed_content()

            assert isinstance(content, dict)
            assert "gateway_architecture" in content
            assert "load_balancing_strategies" in content
            assert "security_patterns" in content
            assert "patterns" in content["gateway_architecture"]

        @pytest.mark.asyncio
        async def test_full_disclosure(self, skill):
            """Test FULL level disclosure"""
            content = skill._get_full_content()

            assert isinstance(content, dict)
            assert "implementation_guides" in content
            assert "performance_optimization" in content
            assert "monitoring_observability" in content
            assert "deployment_strategies" in content
            assert "troubleshooting_guide" in content
            assert "best_practices" in content
            assert "code_examples" in content
            assert "configuration_templates" in content

    class TestGatewayAnalysis:
        """Test gateway requirement analysis functionality"""

        @pytest.mark.asyncio
        async def test_low_traffic_analysis(self, skill):
            """Test analysis for low traffic requirements"""
            context = Mock()
            context.parameters = {
                "action": "analyze",
                "requirements": {"traffic_rps": 50, "security_level": "basic", "service_count": 3},
            }

            result = await skill._analyze_gateway_requirements(context)

            assert isinstance(result, dict)
            assert "requirements_assessment" in result
            assert "recommended_gateway" in result
            assert "architecture_pattern" in result
            assert "implementation_roadmap" in result

            # Check specific recommendations
            traffic_assessment = result["requirements_assessment"]["traffic_volume"]
            assert traffic_assessment["level"] == "low"
            assert traffic_assessment["instance_count"] == 1

        @pytest.mark.asyncio
        async def test_high_traffic_analysis(self, skill):
            """Test analysis for high traffic requirements"""
            context = Mock()
            context.parameters = {
                "action": "analyze",
                "requirements": {"traffic_rps": 5000, "security_level": "high", "service_count": 20},
            }

            result = await skill._analyze_gateway_requirements(context)

            traffic_assessment = result["requirements_assessment"]["traffic_volume"]
            assert traffic_assessment["level"] == "high"
            assert traffic_assessment["instance_count"] >= 3

        @pytest.mark.asyncio
        async def test_security_requirements_analysis(self, skill):
            """Test security requirements analysis"""
            context = Mock()
            context.parameters = {"action": "analyze", "requirements": {"security_level": "high", "traffic_rps": 100}}

            result = await skill._analyze_gateway_requirements(context)

            security_assessment = result["requirements_assessment"]["security_needs"]
            assert "oauth2_mfa" in str(security_assessment)
            assert "ddos_protection" in str(security_assessment) or "audit_logging" in str(security_assessment)

    class TestArchitectureDesign:
        """Test gateway architecture design functionality"""

        @pytest.mark.asyncio
        async def test_microservices_architecture_design(self, skill):
            """Test design for microservices architecture"""
            context = Mock()
            context.parameters = {
                "action": "design",
                "config": {
                    "pattern": "api_gateway_pattern",
                    "services": [{"name": "user-service", "port": 8080}, {"name": "order-service", "port": 8081}],
                    "routes": [
                        {"path": "/api/users", "service": "user-service"},
                        {"path": "/api/orders", "service": "order-service"},
                    ],
                },
            }

            result = await skill._design_gateway_architecture(context)

            assert isinstance(result, dict)
            assert "high_level_design" in result
            assert "detailed_configuration" in result
            assert "deployment_specification" in result

            design = result["high_level_design"]
            assert "components" in design
            assert "data_flow" in design
            assert len(design["components"]) >= 3  # Should include gateway, load balancer, etc.

        @pytest.mark.asyncio
        async def test_bff_architecture_design(self, skill):
            """Test design for Backend-for-Frontend pattern"""
            context = Mock()
            context.parameters = {
                "action": "design",
                "config": {"pattern": "backend_for_frontend", "client_types": ["web", "mobile", "iot"]},
            }

            result = await skill._design_gateway_architecture(context)

            pattern = result["high_level_design"]["pattern"]
            assert "backend_for_frontend" in pattern or "bff" in pattern.lower()

    class TestPerformanceOptimization:
        """Test performance optimization functionality"""

        @pytest.mark.asyncio
        async def test_performance_bottleneck_identification(self, skill):
            """Test identification of performance bottlenecks"""
            context = Mock()
            context.parameters = {
                "action": "optimize",
                "current_config": {"timeout": 30, "connections": 100},
                "performance_issues": [
                    {"type": "high_latency", "value": "2000ms"},
                    {"type": "connection_exhaustion", "value": "95% usage"},
                ],
            }

            result = await skill._optimize_gateway_performance(context)

            assert isinstance(result, dict)
            assert "performance_analysis" in result
            assert "optimization_strategies" in result
            assert "implementation_plan" in result

            analysis = result["performance_analysis"]
            assert "bottlenecks" in analysis
            assert len(analysis["bottlenecks"]) > 0

        @pytest.mark.asyncio
        async def test_connection_optimization(self, skill):
            """Test connection optimization recommendations"""
            current_config = {"keepalive": False, "connection_timeout": 60}

            optimization = skill._optimize_connections(current_config)

            assert isinstance(optimization, dict)
            # Should recommend enabling keepalive and adjusting timeouts

        @pytest.mark.asyncio
        async def test_caching_optimization(self, skill):
            """Test caching optimization recommendations"""
            current_config = {"caching": "disabled"}

            optimization = skill._optimize_caching(current_config)

            assert isinstance(optimization, dict)
            # Should recommend caching strategies

    class TestSecurityImplementation:
        """Test security implementation functionality"""

        @pytest.mark.asyncio
        async def test_jwt_security_design(self, skill):
            """Test JWT-based security design"""
            context = Mock()
            context.parameters = {
                "action": "secure",
                "security_requirements": {"authentication_type": "jwt", "compliance": ["gdpr", "soc2"]},
            }

            result = await skill._secure_gateway_implementation(context)

            assert isinstance(result, dict)
            assert "threat_model" in result
            assert "security_controls" in result
            assert "implementation_details" in result

            security_controls = result["security_controls"]
            assert "authentication" in security_controls
            assert "authorization" in security_controls

        @pytest.mark.asyncio
        async def test_oauth2_security_design(self, skill):
            """Test OAuth2-based security design"""
            context = Mock()
            context.parameters = {
                "action": "secure",
                "security_requirements": {"authentication_type": "oauth2", "multi_factor": True},
            }

            result = await skill._secure_gateway_implementation(context)

            authentication = result["security_controls"]["authentication"]
            assert "oauth2" in str(authentication).lower()

    class TestMonitoringSetup:
        """Test monitoring setup functionality"""

        @pytest.mark.asyncio
        async def test_comprehensive_monitoring_setup(self, skill):
            """Test comprehensive monitoring setup"""
            context = Mock()
            context.parameters = {
                "action": "monitor",
                "monitoring_config": {
                    "metrics_backend": "prometheus",
                    "logging_backend": "elasticsearch",
                    "tracing_backend": "jaeger",
                },
            }

            result = await skill._setup_monitoring(context)

            assert isinstance(result, dict)
            assert "monitoring_stack" in result
            assert "dashboards" in result
            assert "alerting" in result
            assert "sla_monitoring" in result

            monitoring_stack = result["monitoring_stack"]
            assert "metrics_collection" in monitoring_stack
            assert "log_aggregation" in monitoring_stack
            assert "distributed_tracing" in monitoring_stack

        @pytest.mark.asyncio
        async def test_performance_dashboard_design(self, skill):
            """Test performance dashboard design"""
            dashboard = skill._design_performance_dashboard()

            assert isinstance(dashboard, dict)
            assert "latency_metrics" in str(dashboard)
            assert "throughput_metrics" in str(dashboard)
            assert "error_rate_metrics" in str(dashboard)

    class TestConfigurationExamples:
        """Test configuration examples and templates"""

        def test_kong_configuration_example(self, skill):
            """Test Kong configuration example"""
            config = skill._get_configuration_examples("kong")

            assert isinstance(config, str)
            assert "_format_version" in config
            assert "services:" in config
            assert "plugins:" in config

        def test_nginx_configuration_example(self, skill):
            """Test NGINX configuration example"""
            config = skill._get_configuration_examples("nginx_plus")

            assert isinstance(config, str)
            assert "upstream" in config
            assert "server" in config
            assert "proxy_pass" in config

        def test_custom_plugin_examples(self, skill):
            """Test custom plugin development examples"""
            examples = skill._get_custom_plugin_examples()

            assert isinstance(examples, dict)
            assert "kong_plugin_development" in examples
            assert "envoy_filter_development" in examples

        def test_load_testing_examples(self, skill):
            """Test load testing examples"""
            examples = skill._get_testing_examples()

            assert isinstance(examples, dict)
            assert "load_testing" in examples
            assert "integration_testing" in examples
            assert "k6" in examples["load_testing"]

    class TestSkillExecution:
        """Test complete skill execution"""

        @pytest.mark.asyncio
        async def test_successful_execution_analyze(self, skill, mock_context):
            """Test successful skill execution with analyze action"""
            mock_context.parameters = {
                "action": "analyze",
                "disclosure_level": "SUMMARY",
                "requirements": {"traffic_rps": 100},
            }

            result = await skill.execute(mock_context)

            assert result.success is True
            assert isinstance(result.data, dict)
            assert result.metrics.success is True
            assert result.metrics.execution_time > 0

        @pytest.mark.asyncio
        async def test_successful_execution_design(self, skill, mock_context):
            """Test successful skill execution with design action"""
            mock_context.parameters = {
                "action": "design",
                "disclosure_level": "DETAILED",
                "config": {"pattern": "api_gateway_pattern"},
            }

            result = await skill.execute(mock_context)

            assert result.success is True
            assert isinstance(result.data, dict)

        @pytest.mark.asyncio
        async def test_execution_with_invalid_action(self, skill, mock_context):
            """Test execution with invalid action"""
            mock_context.parameters = {"action": "invalid_action", "disclosure_level": "SUMMARY"}

            result = await skill.execute(mock_context)

            # Should still succeed but return content instead of action result
            assert result.success is True
            assert isinstance(result.data, dict)

        @pytest.mark.asyncio
        async def test_execution_with_invalid_disclosure_level(self, skill, mock_context):
            """Test execution with invalid disclosure level"""
            mock_context.parameters = {"action": "analyze", "disclosure_level": "INVALID_LEVEL"}

            result = await skill.execute(mock_context)

            assert result.success is False
            assert "error" in result.data
            assert "Invalid disclosure level" in result.data["error"]

    class TestErrorHandling:
        """Test error handling and edge cases"""

        @pytest.mark.asyncio
        async def test_missing_required_parameters(self, skill):
            """Test handling of missing required parameters"""
            context = Mock()
            context.parameters = {}  # No action specified

            result = await skill.execute(context)

            # Should handle gracefully with default action
            assert result.success is True

        @pytest.mark.asyncio
        async def test_malformed_configuration(self, skill):
            """Test handling of malformed configuration"""
            # Test with invalid gateway configuration
            try:
                config = GatewayConfig(
                    gateway_type="invalid_gateway",  # Should be enum
                    environment="production",
                )
                # If we get here, the enum validation failed
                assert False, "Should have failed with invalid gateway type"
            except ValueError:
                # Expected to fail with invalid enum value
                pass

    class TestTechnicalAccuracy:
        """Test technical accuracy of content"""

        def test_gateway_types_accuracy(self, skill):
            """Test accuracy of gateway type information"""
            content = skill._get_summary_content(gateway_type="kong")

            assert "kong" in str(content).lower()
            assert "plugin" in str(content).lower()

        def test_load_balancing_strategies_accuracy(self, skill):
            """Test accuracy of load balancing strategies"""
            content = skill._get_detailed_content()

            load_balancing = content.get("load_balancing_strategies", {})
            assert "algorithms" in load_balancing
            assert "health_checks" in load_balancing

            algorithms = load_balancing["algorithms"]
            assert "round_robin" in algorithms
            assert "least_connections" in algorithms

        def test_authentication_patterns_accuracy(self, skill):
            """Test accuracy of authentication patterns"""
            content = skill._get_detailed_content()

            security_patterns = content.get("security_patterns", {})
            assert "authentication" in security_patterns

            authentication = security_patterns["authentication"]
            assert "oauth2_jwt" in authentication or "jwt" in str(authentication)
            assert "api_key" in authentication or "api_key" in str(authentication)

        def test_performance_optimization_accuracy(self, skill):
            """Test accuracy of performance optimization guidance"""
            optimization = skill._get_performance_optimization()

            assert "connection_handling" in optimization
            assert "caching_strategies" in optimization
            assert "request_optimization" in optimization

            connection_handling = optimization["connection_handling"]
            assert "keepalive" in connection_handling
            assert "connection_pooling" in connection_handling

    class TestCodeExamples:
        """Test code examples for syntax and correctness"""

        def test_kong_config_syntax(self, skill):
            """Test Kong configuration syntax"""
            config = skill._get_configuration_examples("kong")

            # Basic YAML syntax validation
            try:
                yaml.safe_load(config)
                # If parsing succeeds, syntax is valid
            except yaml.YAMLError:
                pytest.fail("Kong configuration example has invalid YAML syntax")

        def test_nginx_config_syntax(self, skill):
            """Test NGINX configuration syntax"""
            config = skill._get_configuration_examples("nginx_plus")

            # Basic NGINX config validation
            assert "events" in config
            assert "http" in config
            assert "upstream" in config or "server" in config

        def test_lua_plugin_syntax(self, skill):
            """Test Lua plugin syntax"""
            examples = skill._get_plugin_examples("kong_plugins")

            assert "local" in examples  # Basic Lua keyword
            assert "function" in examples  # Function definition
            assert "return" in examples  # Return statement

    class TestIntegrationExamples:
        """Test integration examples and deployment patterns"""

        def test_kubernetes_deployment_examples(self, skill):
            """Test Kubernetes deployment examples"""
            examples = skill._get_deployment_examples("kubernetes_deployments")

            assert "kong" in examples or "nginx" in examples

            if "kong" in examples:
                kong_example = examples["kubernetes_deployments"]["kong"]
                assert "apiVersion" in kong_example
                assert "Deployment" in kong_example or "Service" in kong_example

        def test_monitoring_integration_examples(self, skill):
            """Test monitoring integration examples"""
            monitoring = skill._get_monitoring_patterns()

            assert "logging" in monitoring
            assert "metrics_collection" in monitoring
            assert "distributed_tracing" in monitoring

            metrics = monitoring["metrics_collection"]
            assert "prometheus" in str(metrics).lower() or "prometheus" in metrics

    class TestPerformanceAndScalability:
        """Test performance and scalability guidance"""

        def test_performance_metrics_accuracy(self, skill):
            """Test accuracy of performance metrics guidance"""
            optimization = skill._get_performance_optimization()

            monitoring_metrics = optimization.get("monitoring_metrics", {})
            assert "key_metrics" in monitoring_metrics

            key_metrics = monitoring_metrics["key_metrics"]
            assert "latency" in key_metrics
            assert "throughput" in key_metrics
            assert "error_rate" in key_metrics

        def test_scaling_strategies_accuracy(self, skill):
            """Test accuracy of scaling strategies"""
            deployment = skill._get_deployment_strategies()

            assert "scaling_strategies" in deployment

            scaling = deployment["scaling_strategies"]
            assert "horizontal_scaling" in scaling
            assert "triggers" in scaling["horizontal_scaling"]

    class TestComplianceAndSecurity:
        """Test compliance and security guidance"""

        def test_security_headers_implementation(self, skill):
            """Test security headers implementation guidance"""
            security_headers = skill._configure_security_headers()

            assert isinstance(security_headers, dict)
            # Should include common security headers

        def test_compliance_requirements(self, skill):
            """Test compliance requirements guidance"""
            context = Mock()
            context.parameters = {
                "action": "secure",
                "security_requirements": {"compliance": ["gdpr", "hipaa", "pci_dss"]},
            }

            # Should handle compliance requirements without errors
            try:
                result = asyncio.run(skill._secure_gateway_implementation(context))
                assert isinstance(result, dict)
            except Exception as e:
                pytest.fail(f"Security implementation failed: {e}")


class TestGatewayConfig:
    """Test Gateway configuration data models"""

    def test_gateway_config_creation(self):
        """Test GatewayConfig creation"""
        config = GatewayConfig(gateway_type=GatewayType.KONG, environment="production")

        assert config.gateway_type == GatewayType.KONG
        assert config.environment == "production"
        assert isinstance(config.listeners, list)
        assert isinstance(config.upstream_services, list)

    def test_gateway_config_with_defaults(self):
        """Test GatewayConfig with default values"""
        config = GatewayConfig(gateway_type=GatewayType.NGINX_PLUS, environment="staging")

        # Should have default values
        assert config.load_balancing is not None  # Should have default value
        assert config.monitoring == {}


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
