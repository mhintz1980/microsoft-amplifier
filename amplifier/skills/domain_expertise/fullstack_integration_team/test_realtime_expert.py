"""
Test suite for Real-time Application Expert Skill

Comprehensive testing including:
- Unit tests for all major functions
- Integration tests for skill workflows
- Performance validation
- Zero hallucination validation
- Agent Lightning integration testing
"""

import pytest
import asyncio
import time
from typing import Dict, Any

# Import the skill to test
from real_time_application_expert import RealTimeApplicationExpert, RealtimeTechnology
from ...skills_framework.base_skill import SkillContext


class TestRealTimeApplicationExpert:
    """Comprehensive test suite for Real-time Application Expert"""

    @pytest.fixture
    def skill(self):
        """Create skill instance for testing"""
        return RealTimeApplicationExpert()

    @pytest.fixture
    def skill_context(self):
        """Create skill context for testing"""
        return SkillContext(user_id="test_user", session_id="test_session", metadata={"test": True})

    # Basic Skill Functionality Tests
    @pytest.mark.asyncio
    async def test_skill_initialization(self, skill):
        """Test skill initialization and configuration"""
        assert skill.skill_id == "realtime_application_expert"
        assert skill.name == "Real-time Application Expert"
        assert skill.description is not None
        assert len(skill.get_capabilities()) > 0

    @pytest.mark.asyncio
    async def test_skill_capabilities(self, skill):
        """Test skill capabilities list"""
        capabilities = skill.get_capabilities()

        # Verify key capabilities are present
        expected_capabilities = [
            "WebSocket integration patterns",
            "Server-Sent Events implementation",
            "Real-time architecture design",
            "Connection management strategies",
            "Data synchronization patterns",
            "Performance optimization",
        ]

        for cap in expected_capabilities:
            assert cap in capabilities

    @pytest.mark.asyncio
    async def test_input_validation(self, skill):
        """Test input validation"""
        # Valid input
        valid_input = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "medium"}}
        assert await skill.validate_input(valid_input) == True

        # Invalid input - missing request_type
        invalid_input = {"parameters": {"use_case": "chat"}}
        assert await skill.validate_input(invalid_input) == False

        # Invalid input - not a dictionary
        assert await skill.validate_input("invalid") == False

    # WebSocket Analysis Tests
    @pytest.mark.asyncio
    async def test_websocket_analysis_chat_use_case(self, skill, skill_context):
        """Test WebSocket analysis for chat application"""
        input_data = {
            "request_type": "websocket_analysis",
            "parameters": {
                "use_case": "chat",
                "scale": "medium",
                "features": ["chat", "presence", "typing_indicators"],
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "websockets"
        assert result.data["complexity"] == "advanced"
        assert "patterns" in result.data
        assert "connection_management" in result.data["patterns"]
        assert "message_handling" in result.data["patterns"]
        assert "scalability" in result.data["patterns"]
        assert len(result.data["recommendations"]) > 0
        assert result.execution_time > 0

    @pytest.mark.asyncio
    async def test_websocket_analysis_large_scale(self, skill, skill_context):
        """Test WebSocket analysis for large-scale application"""
        input_data = {
            "request_type": "websocket_analysis",
            "parameters": {
                "use_case": "collaboration",
                "scale": "enterprise",
                "features": ["collaboration", "real_time_sync", "multi_region"],
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert "Redis Pub/Sub" in str(result.data)
        assert "multi-server" in str(result.data).lower()
        assert len(result.data["recommendations"]) > 5  # Enterprise should have more recommendations

    # Server-Sent Events Tests
    @pytest.mark.asyncio
    async def test_sse_analysis_dashboard(self, skill, skill_context):
        """Test SSE analysis for dashboard application"""
        input_data = {
            "request_type": "sse_analysis",
            "parameters": {"data_source": "database", "update_frequency": "high", "client_count": "large"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "server_sent_events"
        assert result.data["complexity"] == "intermediate"
        assert "stream_management" in result.data["patterns"]
        assert "event_formatting" in result.data["patterns"]
        assert "data_sync" in result.data["patterns"]
        assert len(result.data["use_cases"]) > 0

    @pytest.mark.asyncio
    async def test_sse_code_examples(self, skill, skill_context):
        """Test SSE code examples are valid Python"""
        input_data = {"request_type": "sse_analysis", "parameters": {"data_source": "database"}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Extract code example and verify it's syntactically valid
        stream_code = result.data["patterns"]["stream_management"]["code_example"]
        assert "class SSEStreamManager" in stream_code
        assert "async def create_stream" in stream_code

        # Test that the code would compile (basic syntax check)
        try:
            compile(stream_code, "<string>", "exec")
        except SyntaxError:
            pytest.fail("SSE code example has syntax errors")

    # Architecture Design Tests
    @pytest.mark.asyncio
    async def test_architecture_design_small_scale(self, skill, skill_context):
        """Test architecture design for small-scale application"""
        input_data = {
            "request_type": "architecture_design",
            "parameters": {
                "scale": "small",
                "requirements": {"features": ["chat", "presence"], "performance": {"latency": "low"}},
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "architecture"
        assert result.data["complexity"] == "expert"
        assert "architecture" in result.data
        assert "high_level_design" in result.data["architecture"]
        assert "components" in result.data["architecture"]
        assert "data_flow" in result.data["architecture"]
        assert len(result.data["architecture"]["components"]) > 0

    @pytest.mark.asyncio
    async def test_architecture_design_enterprise(self, skill, skill_context):
        """Test architecture design for enterprise application"""
        input_data = {
            "request_type": "architecture_design",
            "parameters": {
                "scale": "enterprise",
                "requirements": {
                    "features": ["multi_region", "high_availability"],
                    "performance": {"latency": "ultra_low"},
                },
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert "Microservices Real-time Platform" in str(result.data)
        assert "multi-region" in str(result.data).lower()
        assert len(result.data["architecture"]["components"]) > 4  # Enterprise should have more components

    # Connection Management Tests
    @pytest.mark.asyncio
    async def test_connection_strategy_websocket(self, skill, skill_context):
        """Test connection management strategy for WebSocket"""
        input_data = {
            "request_type": "connection_strategy",
            "parameters": {"connection_type": "websocket", "scale": "large"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "connection_management"
        assert result.data["complexity"] == "advanced"
        assert "strategy" in result.data
        assert "connection_lifecycle" in result.data["strategy"]
        assert "pool_management" in result.data["strategy"]
        assert "load_balancing" in result.data["strategy"]

    # Data Synchronization Tests
    @pytest.mark.asyncio
    async def test_sync_pattern_operational_transformation(self, skill, skill_context):
        """Test operational transformation sync pattern"""
        input_data = {
            "request_type": "sync_pattern",
            "parameters": {
                "sync_type": "realtime",
                "data_size": "medium",
                "conflict_resolution": "operational_transformation",
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "data_synchronization"
        assert result.data["complexity"] == "expert"
        assert "Operational Transformation" in str(result.data)
        assert "implementation_examples" in result.data

    @pytest.mark.asyncio
    async def test_sync_pattern_crdt(self, skill, skill_context):
        """Test CRDT sync pattern"""
        input_data = {
            "request_type": "sync_pattern",
            "parameters": {"sync_type": "eventual", "data_size": "large", "conflict_resolution": "crdt"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert "CRDT" in str(result.data)
        assert "Conflict-free Replicated Data Types" in str(result.data)

    # Performance Optimization Tests
    @pytest.mark.asyncio
    async def test_performance_optimization(self, skill, skill_context):
        """Test performance optimization recommendations"""
        input_data = {
            "request_type": "performance_optimization",
            "parameters": {
                "bottleneck_type": "connection",
                "current_metrics": {"latency": "200ms", "throughput": "1000 msg/s"},
                "target_metrics": {"latency": "50ms", "throughput": "5000 msg/s"},
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "performance_optimization"
        assert result.data["complexity"] == "expert"
        assert "optimizations" in result.data
        assert "connection_optimization" in result.data["optimizations"]
        assert "message_optimization" in result.data["optimizations"]
        assert len(result.data["optimizations"]["connection_optimization"]) > 0

    # Database Integration Tests
    @pytest.mark.asyncio
    async def test_database_integration_postgresql(self, skill, skill_context):
        """Test PostgreSQL database integration"""
        input_data = {
            "request_type": "database_integration",
            "parameters": {"database_type": "postgresql", "sync_method": "change_data_capture", "scale": "medium"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "database_integration"
        assert result.data["complexity"] == "expert"
        assert "Logical Replication" in str(result.data)
        assert "change_detection" in result.data["integration"]
        assert len(result.data["implementation_examples"]) > 0

    @pytest.mark.asyncio
    async def test_database_integration_mongodb(self, skill, skill_context):
        """Test MongoDB database integration"""
        input_data = {
            "request_type": "database_integration",
            "parameters": {"database_type": "mongodb", "sync_method": "change_streams", "scale": "large"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert "Change Streams" in str(result.data)
        assert "MongoDB" in str(result.data)

    # Collaboration Features Tests
    @pytest.mark.asyncio
    async def test_collaboration_document_editing(self, skill, skill_context):
        """Test collaboration features for document editing"""
        input_data = {
            "request_type": "collaboration_features",
            "parameters": {
                "feature_type": "document_editing",
                "user_count": "large",
                "requirements": ["cursor_tracking", "presence", "conflict_resolution"],
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "collaboration_features"
        assert result.data["complexity"] == "expert"
        assert "real_time_cursor" in result.data["features"]
        assert "presence_awareness" in result.data["features"]
        assert "conflict_resolution" in result.data["features"]
        assert len(result.data["implementation_examples"]) > 0

    # Technology Selection Tests
    @pytest.mark.asyncio
    async def test_technology_selection_recommendations(self, skill, skill_context):
        """Test technology selection recommendations"""
        input_data = {
            "request_type": "technology_selection",
            "parameters": {
                "requirements": {"bidirectional": True, "latency": "low", "scale": "medium", "reliability": "high"},
                "constraints": {"team_expertise": {"javascript": 4, "python": 2}, "budget": "medium"},
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "technology_selection"
        assert result.data["complexity"] == "advanced"
        assert "recommendations" in result.data
        assert "communication_protocols" in result.data["recommendations"]
        assert "backend_technologies" in result.data["recommendations"]
        assert "database_solutions" in result.data["recommendations"]

    @pytest.mark.asyncio
    async def test_technology_scoring(self, skill, skill_context):
        """Test technology recommendation scoring"""
        input_data = {
            "request_type": "technology_selection",
            "parameters": {
                "requirements": {"bidirectional": True, "latency": "ultra_low"},
                "constraints": {"team_expertise": {"go": 4}, "budget": "large"},
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Check that scoring is applied
        backend_techs = result.data["recommendations"]["backend_technologies"]
        for tech, info in backend_techs.items():
            assert "score" in info
            assert isinstance(info["score"], int)
            assert 0 <= info["score"] <= 10  # Reasonable score range

    # Implementation Patterns Tests
    @pytest.mark.asyncio
    async def test_implementation_patterns(self, skill, skill_context):
        """Test implementation patterns and templates"""
        input_data = {
            "request_type": "implementation_patterns",
            "parameters": {"pattern_type": "general", "technology": "websocket"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "implementation_patterns"
        assert result.data["complexity"] == "expert"
        assert "patterns" in result.data
        assert "error_handling" in result.data["patterns"]
        assert "testing" in result.data["patterns"]
        assert "monitoring" in result.data["patterns"]
        assert "code_templates" in result.data
        assert len(result.data["code_templates"]) > 0

    @pytest.mark.asyncio
    async def test_code_templates_validity(self, skill, skill_context):
        """Test that code templates are syntactically valid"""
        input_data = {"request_type": "implementation_patterns", "parameters": {"technology": "websocket"}}

        result = await skill.run_with_monitoring(input_data, skill_context)
        templates = result.data["code_templates"]

        # Test WebSocket server template
        if "websocket_server" in templates:
            ws_code = templates["websocket_server"]
            try:
                compile(ws_code, "<string>", "exec")
            except SyntaxError as e:
                pytest.fail(f"WebSocket server template has syntax errors: {e}")

        # Test SSE server template
        if "sse_server" in templates:
            sse_code = templates["sse_server"]
            try:
                compile(sse_code, "<string>", "exec")
            except SyntaxError as e:
                pytest.fail(f"SSE server template has syntax errors: {e}")

    # General Expertise Tests
    @pytest.mark.asyncio
    async def test_general_expertise(self, skill, skill_context):
        """Test general real-time expertise"""
        input_data = {"request_type": "general_analysis", "parameters": {"project_type": "chat_application"}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert result.data["technology"] == "general_expertise"
        assert result.data["complexity"] == "expert"
        assert "overview" in result.data
        assert "getting_started" in result.data
        assert "resources" in result.data

    # Performance Tests
    @pytest.mark.asyncio
    async def test_performance_websocket_analysis(self, skill, skill_context):
        """Test performance of WebSocket analysis"""
        input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "large"}}

        start_time = time.time()
        result = await skill.run_with_monitoring(input_data, skill_context)
        execution_time = time.time() - start_time

        assert result.success == True
        assert execution_time < 5.0  # Should complete within 5 seconds
        assert result.execution_time < 5.0

    @pytest.mark.asyncio
    async def test_performance_concurrent_requests(self, skill):
        """Test performance under concurrent requests"""
        tasks = []
        for i in range(5):
            input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "medium"}}
            task = skill.run_with_monitoring(input_data, SkillContext())
            tasks.append(task)

        # Run tasks concurrently
        results = await asyncio.gather(*tasks)

        # All should succeed
        assert all(result.success for result in results)
        # Total time should be reasonable
        total_time = sum(result.execution_time for result in results)
        assert total_time < 10.0  # Should complete within 10 seconds total

    # Zero Hallucination Tests
    @pytest.mark.asyncio
    async def test_technical_accuracy_websocket(self, skill, skill_context):
        """Test technical accuracy of WebSocket recommendations"""
        input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "medium"}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Verify technical accuracy
        assert "WebSocket" in str(result.data)
        assert "bi-directional" in str(result.data).lower() or "bidirectional" in str(result.data).lower()
        assert "full-duplex" in str(result.data).lower()

    @pytest.mark.asyncio
    async def test_technical_accuracy_sse(self, skill, skill_context):
        """Test technical accuracy of SSE recommendations"""
        input_data = {"request_type": "sse_analysis", "parameters": {"data_source": "database"}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Verify technical accuracy
        assert "Server-Sent Events" in str(result.data) or "SSE" in str(result.data)
        assert "one-way" in str(result.data).lower() or "unidirectional" in str(result.data).lower()
        assert "HTTP" in str(result.data)

    @pytest.mark.asyncio
    async def test_technical_accuracy_database_cdc(self, skill, skill_context):
        """Test technical accuracy of database CDC recommendations"""
        input_data = {
            "request_type": "database_integration",
            "parameters": {"database_type": "postgresql", "sync_method": "change_data_capture"},
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Verify technical accuracy
        assert "PostgreSQL" in str(result.data)
        assert "Logical Replication" in str(result.data)
        assert "Change Data Capture" in str(result.data) or "CDC" in str(result.data)

    # Agent Lightning Integration Tests
    @pytest.mark.asyncio
    async def test_agent_lightning_optimization_enabled(self, skill):
        """Test that Agent Lightning optimization is enabled"""
        assert hasattr(skill, "_optimization_enabled")
        assert skill._optimization_enabled == True
        assert hasattr(skill, "_zero_hallucination_enforced")
        assert skill._zero_hallucination_enforced == True
        assert hasattr(skill, "_performance_monitoring")
        assert skill._performance_monitoring == True

    @pytest.mark.asyncio
    async def test_zero_hallucination_validation(self, skill, skill_context):
        """Test zero hallucination validation in execution"""
        input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "medium"}}

        # This should pass zero-hallucination checks
        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        # Verify no uncertain language in responses
        result_str = str(result.data)
        uncertain_phrases = ["perhaps", "maybe", "probably", "might", "could"]
        for phrase in uncertain_phrases:
            if phrase in result_str.lower():
                # Allow uncertain phrases in recommendations section only
                assert "recommendations" not in result_str.lower() or result_str.lower().count(phrase) <= 1

    # Error Handling Tests
    @pytest.mark.asyncio
    async def test_invalid_request_type(self, skill, skill_context):
        """Test handling of invalid request types"""
        input_data = {"request_type": "invalid_type", "parameters": {}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Should fall back to general expertise
        assert result.success == True
        assert result.data["technology"] == "general_expertise"

    @pytest.mark.asyncio
    async def test_missing_parameters(self, skill, skill_context):
        """Test handling of missing parameters"""
        input_data = {
            "request_type": "websocket_analysis",
            "parameters": {},  # Missing expected parameters
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Should still succeed with defaults
        assert result.success == True
        assert result.data["technology"] == "websockets"

    # Memory and Resource Tests
    @pytest.mark.asyncio
    async def test_memory_usage_multiple_calls(self, skill):
        """Test memory usage across multiple calls"""
        import psutil
        import os

        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss

        # Make multiple calls
        for i in range(10):
            input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "medium"}}
            await skill.run_with_monitoring(input_data, SkillContext())

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory

        # Memory increase should be reasonable (less than 50MB)
        assert memory_increase < 50 * 1024 * 1024  # 50MB in bytes

    # Integration Tests
    @pytest.mark.asyncio
    async def test_end_to_end_chat_application_workflow(self, skill, skill_context):
        """Test end-to-end workflow for chat application design"""
        # Step 1: Analyze WebSocket requirements
        ws_result = await skill.run_with_monitoring(
            {
                "request_type": "websocket_analysis",
                "parameters": {"use_case": "chat", "scale": "medium", "features": ["chat", "presence", "typing"]},
            },
            skill_context,
        )

        assert ws_result.success == True

        # Step 2: Design architecture
        arch_result = await skill.run_with_monitoring(
            {
                "request_type": "architecture_design",
                "parameters": {"scale": "medium", "requirements": {"features": ["chat", "real_time"]}},
            },
            skill_context,
        )

        assert arch_result.success == True

        # Step 3: Get database integration
        db_result = await skill.run_with_monitoring(
            {"request_type": "database_integration", "parameters": {"database_type": "postgresql", "scale": "medium"}},
            skill_context,
        )

        assert db_result.success == True

        # Step 4: Get implementation patterns
        impl_result = await skill.run_with_monitoring(
            {"request_type": "implementation_patterns", "parameters": {"technology": "websocket"}}, skill_context
        )

        assert impl_result.success == True

        # Verify all results are consistent and complementary
        assert all(result.success for result in [ws_result, arch_result, db_result, impl_result])

    # Configuration Tests
    @pytest.mark.asyncio
    async def test_skill_configuration(self, skill):
        """Test skill configuration"""
        config = {"optimization_enabled": True, "zero_hallucination_enforced": True, "performance_monitoring": True}

        skill.configure(config)

        assert skill._optimization_enabled == True
        assert skill._zero_hallucination_enforced == True
        assert skill._performance_monitoring == True

    @pytest.mark.asyncio
    async def test_skill_metrics_tracking(self, skill, skill_context):
        """Test skill metrics tracking"""
        input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat"}}

        # Execute multiple times to generate metrics
        for i in range(3):
            await skill.run_with_monitoring(input_data, skill_context)

        metrics = skill.get_metrics()
        assert metrics.total_executions >= 3
        assert metrics.successful_executions >= 3
        assert metrics.success_rate > 0.9
        assert metrics.average_execution_time > 0

    # Quality Assurance Tests
    @pytest.mark.asyncio
    async def test_code_quality_examples(self, skill, skill_context):
        """Test that code examples follow quality standards"""
        input_data = {"request_type": "implementation_patterns", "parameters": {"technology": "websocket"}}

        result = await skill.run_with_monitoring(input_data, skill_context)
        templates = result.data["code_templates"]

        quality_indicators = [
            "async def",  # Asynchronous functions
            "try:",  # Error handling
            "except",  # Error handling
            "class ",  # Class definitions
            "def ",  # Function definitions
            "return ",  # Return statements
        ]

        for template_name, template_code in templates.items():
            # Check for quality indicators
            for indicator in quality_indicators:
                assert indicator in template_code, f"Template {template_name} missing quality indicator: {indicator}"

            # Check that it's not trivially short
            assert len(template_code) > 500, f"Template {template_name} seems too short"

    @pytest.mark.asyncio
    async def test_documentation_completeness(self, skill, skill_context):
        """Test that results include comprehensive documentation"""
        input_data = {"request_type": "websocket_analysis", "parameters": {"use_case": "chat", "scale": "medium"}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        # Check for comprehensive documentation elements
        documentation_elements = [
            "patterns",
            "recommendations",
            "benefits",
            "implementation",
            "security",
            "performance",
        ]

        result_str = str(result.data).lower()
        for element in documentation_elements:
            # At least some documentation should be present
            assert element in result_str or len([d for d in result_str.split() if element in d]) > 0

    # Edge Case Tests
    @pytest.mark.asyncio
    async def test_empty_parameters(self, skill, skill_context):
        """Test handling of empty parameters"""
        input_data = {"request_type": "general_analysis", "parameters": {}}

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        assert len(result.data) > 0  # Should still provide meaningful results

    @pytest.mark.asyncio
    async def test_extreme_scale_parameters(self, skill, skill_context):
        """Test handling of extreme scale parameters"""
        input_data = {
            "request_type": "websocket_analysis",
            "parameters": {
                "use_case": "global_platform",
                "scale": "enterprise",
                "features": ["multi_region", "high_availability", "millions_users"],
            },
        }

        result = await skill.run_with_monitoring(input_data, skill_context)

        assert result.success == True
        # Should provide enterprise-level recommendations
        result_str = str(result.data).lower()
        enterprise_indicators = ["multi-region", "enterprise", "large", "scalable"]
        assert any(indicator in result_str for indicator in enterprise_indicators)


# Performance benchmark tests
class TestPerformanceBenchmarks:
    """Performance benchmark tests for the skill"""

    @pytest.mark.asyncio
    async def test_response_time_benchmarks(self):
        """Benchmark response times for different request types"""
        skill = RealTimeApplicationExpert()
        context = SkillContext()

        request_types = [
            ("websocket_analysis", {"use_case": "chat"}),
            ("sse_analysis", {"data_source": "database"}),
            ("architecture_design", {"scale": "medium"}),
            ("technology_selection", {"requirements": {"bidirectional": True}}),
        ]

        response_times = []

        for request_type, params in request_types:
            input_data = {"request_type": request_type, "parameters": params}

            start_time = time.time()
            result = await skill.run_with_monitoring(input_data, context)
            response_time = time.time() - start_time

            assert result.success == True
            response_times.append(response_time)

        # Average response time should be reasonable
        avg_response_time = sum(response_times) / len(response_times)
        assert avg_response_time < 3.0  # Average should be under 3 seconds

        # No single request should take too long
        assert max(response_times) < 5.0  # Max should be under 5 seconds


# Integration test with the broader amplifier framework
class TestAmplifierFrameworkIntegration:
    """Test integration with amplifier framework"""

    @pytest.mark.asyncio
    async def test_skill_registry_integration(self):
        """Test that skill is properly registered in the amplifier framework"""
        from ...skills_framework.base_skill import skill_registry

        # Check if skill is registered
        registered_skills = skill_registry.list_skills("domain_expertise")
        domain_skills = [skill for skill in registered_skills if skill.skill_id == "realtime_application_expert"]

        assert len(domain_skills) > 0, "Real-time expert skill should be registered in domain_expertise category"

        realtime_skill = domain_skills[0]
        assert realtime_skill.name == "Real-time Application Expert"
        assert len(realtime_skill.get_capabilities()) > 0

    @pytest.mark.asyncio
    async def test_skill_metrics_persistence(self):
        """Test that skill metrics are properly tracked"""
        skill = RealTimeApplicationExpert()
        context = SkillContext()

        # Execute skill multiple times
        for i in range(5):
            await skill.run_with_monitoring(
                {"request_type": "websocket_analysis", "parameters": {"use_case": "chat"}}, context
            )

        # Check metrics
        metrics = skill.get_metrics()
        assert metrics.total_executions == 5
        assert metrics.successful_executions == 5
        assert metrics.success_rate == 1.0
        assert metrics.average_execution_time > 0
        assert metrics.error_rate == 0.0


if __name__ == "__main__":
    # Run tests directly
    pytest.main([__file__, "-v", "--tb=short"])
