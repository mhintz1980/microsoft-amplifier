"""
Test Suite for Security Integration Expert Skill

Comprehensive testing of Security Integration Expert with zero hallucination validation,
performance testing, and security accuracy verification.

Tests cover:
- All 8 security domains
- Progressive disclosure levels
- Agent Lightning optimization
- Code example validation
- Performance metrics
- Edge cases and error handling
"""

import pytest
import asyncio
import time
from unittest.mock import Mock, patch
from typing import Dict, List, Any

# Import the security expert skill
from .security_integration_expert import SecurityIntegrationExpertSkill
from .security_integration_expert_agent_lightning_integration import (
    SecurityIntegrationExpertAgentLightning,
    OptimizationLevel,
    create_optimized_security_expert,
    benchmark_security_expert_performance,
)
from ..skills_framework.skill_template import SkillContext, SkillResult, SkillLevel


class TestSecurityIntegrationExpertBase:
    """Base test class for Security Integration Expert"""

    @pytest.fixture
    def security_expert(self):
        """Create security expert instance for testing"""
        return SecurityIntegrationExpertSkill()

    @pytest.fixture
    def sample_context(self):
        """Create sample skill context for testing"""
        return SkillContext(
            query="How do I implement secure authentication for web applications?",
            conversation_history=[],
            available_tokens=2000,
        )

    @pytest.fixture
    def security_test_queries(self):
        """Sample queries covering all security domains"""
        return {
            "application_security": [
                "How do I prevent SQL injection attacks?",
                "What are the OWASP Top 10 vulnerabilities?",
                "How to implement secure coding practices?",
                "How to conduct penetration testing?",
                "What is the best way to handle user input validation?",
            ],
            "identity_access": [
                "How do I implement single sign-on (SSO)?",
                "What are RBAC best practices?",
                "How to implement multi-factor authentication?",
                "OAuth 2.0 vs OpenID Connect?",
                "How to manage user access lifecycle?",
            ],
            "api_security": [
                "How do I secure REST APIs?",
                "What is API rate limiting?",
                "How to implement API key authentication?",
                "GraphQL security best practices?",
                "How to prevent API abuse?",
            ],
            "data_protection": [
                "How to implement encryption at rest?",
                "GDPR compliance requirements?",
                "Data masking strategies?",
                "How to protect sensitive data?",
                "Cloud data security best practices?",
            ],
            "compliance": [
                "SOC 2 compliance requirements?",
                "How to achieve ISO 27001 certification?",
                "HIPAA security requirements?",
                "PCI DSS compliance checklist?",
                "Audit trail requirements?",
            ],
            "security_monitoring": [
                "How to implement SIEM?",
                "Security monitoring best practices?",
                "How to detect security threats?",
                "Incident response planning?",
                "Security analytics implementation?",
            ],
            "cloud_security": [
                "AWS security best practices?",
                "How to secure cloud infrastructure?",
                "Multi-cloud security strategy?",
                "Cloud compliance automation?",
                "Container security implementation?",
            ],
            "devsecops": [
                "How to integrate security in CI/CD?",
                "DevSecOps pipeline security?",
                "Infrastructure as Code security?",
                "Supply chain security best practices?",
                "Automated security testing?",
            ],
        }


class TestSecurityIntegrationExpertFunctionality(TestSecurityIntegrationExpertBase):
    """Test core functionality of Security Integration Expert"""

    def test_skill_initialization(self, security_expert):
        """Test proper skill initialization"""
        assert security_expert.skill_name == "security_integration_expert"
        assert len(security_expert.tags) > 0
        assert "security" in security_expert.tags
        assert "owasp" in security_expert.tags
        assert "compliance" in security_expert.tags

    def test_skill_description(self, security_expert):
        """Test skill description is comprehensive"""
        description = security_expert.description
        assert len(description) > 50
        assert "security" in description.lower()
        assert "application" in description.lower()
        assert "compliance" in description.lower()

    def test_tags_completeness(self, security_expert):
        """Test tags cover all security domains"""
        tags = security_expert.tags

        required_tags = [
            "security",
            "application-security",
            "owasp",
            "compliance",
            "identity-management",
            "api-security",
            "data-protection",
            "cloud-security",
            "devsecops",
            "threat-modeling",
        ]

        for required_tag in required_tags:
            assert required_tag in tags, f"Missing required tag: {required_tag}"

    def test_can_handle_security_queries(self, security_expert, security_test_queries):
        """Test confidence scoring for security queries"""
        for domain, queries in security_test_queries.items():
            for query in queries:
                context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
                confidence = security_expert.can_handle(context)
                assert confidence >= 0.7, f"Low confidence ({confidence}) for security query: {query}"

    def test_can_handle_non_security_queries(self, security_expert):
        """Test low confidence for non-security queries"""
        non_security_queries = [
            "How to implement machine learning algorithms?",
            "What is the best database design?",
            "How to optimize JavaScript performance?",
            "React component best practices?",
            "Python data structures tutorial?",
        ]

        for query in non_security_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            confidence = security_expert.can_handle(context)
            assert confidence <= 0.5, f"High confidence ({confidence}) for non-security query: {query}"

    def test_metadata_level_content(self, security_expert, sample_context):
        """Test metadata level content generation"""
        result = security_expert.execute(sample_context, SkillLevel.METADATA)

        assert isinstance(result, SkillResult)
        assert result.level == SkillLevel.METADATA
        assert len(result.content) > 0
        assert result.tokens_used < 100  # Should be very concise
        assert "8" in result.content  # Should mention 8 domains
        assert "zero hallucination" in result.content.lower()

    def test_summary_level_content(self, security_expert, sample_context):
        """Test summary level content generation"""
        result = security_expert.execute(sample_context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert result.level == SkillLevel.SUMMARY
        assert len(result.content) > 100
        assert "authentication" in result.content.lower()
        assert "authorization" in result.content.lower()
        assert result.tokens_used < 1000

    def test_full_level_content(self, security_expert, sample_context):
        """Test full level content generation"""
        result = security_expert.execute(sample_context, SkillLevel.FULL)

        assert isinstance(result, SkillResult)
        assert result.level == SkillLevel.FULL
        assert len(result.content) > 1000
        assert "authentication" in result.content.lower()
        assert "implementation" in result.content.lower()
        assert result.tokens_used > 500

    def test_domain_specific_routing(self, security_expert, security_test_queries):
        """Test proper routing to specific security domains"""
        domain_routing = {
            "application_security": ["owasp", "vulnerability", "injection"],
            "identity_access": ["authentication", "authorization", "rbac"],
            "api_security": ["api", "rate limiting", "rest"],
            "data_protection": ["encryption", "gdpr", "privacy"],
            "compliance": ["soc2", "iso", "audit"],
            "security_monitoring": ["siem", "monitoring", "threat"],
            "cloud_security": ["aws", "azure", "cloud"],
            "devsecops": ["ci/cd", "pipeline", "devsecops"],
        }

        for domain, queries in security_test_queries.items():
            for query in queries[:1]:  # Test first query from each domain
                context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
                result = security_expert.execute(context, SkillLevel.SUMMARY)

                # Check domain-specific keywords are in response
                domain_keywords = domain_routing.get(domain, [])
                content_lower = result.content.lower()

                # At least one domain keyword should be present
                assert any(keyword in content_lower for keyword in domain_keywords), (
                    f"Domain {domain} keywords not found in response for: {query}"
                )

    def test_error_handling(self, security_expert):
        """Test error handling for invalid inputs"""
        # Test with None query
        with pytest.raises(Exception):
            context = SkillContext(query=None, conversation_history=[], available_tokens=2000)
            security_expert.execute(context, SkillLevel.SUMMARY)

        # Test with empty query
        context = SkillContext(query="", conversation_history=[], available_tokens=2000)
        result = security_expert.execute(context, SkillLevel.SUMMARY)
        assert result.tokens_used < 100  # Should be minimal response

    def test_execution_time_reasonable(self, security_expert, sample_context):
        """Test execution time is reasonable"""
        start_time = time.time()
        result = security_expert.execute(sample_context, SkillLevel.SUMMARY)
        execution_time = time.time() - start_time

        assert result.execution_time <= execution_time + 0.1  # Allow small discrepancy
        assert execution_time < 5.0  # Should complete within 5 seconds

    def test_token_limit_respect(self, security_expert, sample_context):
        """Test respect for token limits"""
        # Test with very limited tokens
        limited_context = SkillContext(query=sample_context.query, conversation_history=[], available_tokens=100)

        result = security_expert.execute(limited_context, SkillLevel.SUMMARY)
        assert result.tokens_used <= limited_context.available_tokens

    def test_security_accuracy_validation(self, security_expert, security_test_queries):
        """Test security accuracy and zero hallucination"""
        critical_security_concepts = {
            "owasp": ["injection", "broken access control", "cryptographic failures"],
            "authentication": ["password", "mfa", "single sign-on", "oauth"],
            "encryption": ["aes", "tls", "key management", "encryption at rest"],
            "compliance": ["audit", "controls", "risk assessment", "documentation"],
        }

        for domain, queries in security_test_queries.items():
            for query in queries[:2]:  # Test first 2 queries from each domain
                context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
                result = security_expert.execute(context, SkillLevel.SUMMARY)

                content_lower = result.content.lower()

                # Check for accuracy - no dangerous or incorrect advice
                dangerous_patterns = [
                    "disable security",
                    "bypass authentication",
                    "ignore vulnerabilities",
                    "use weak encryption",
                    "skip validation",
                ]

                for pattern in dangerous_patterns:
                    assert pattern not in content_lower, f"Dangerous pattern found in security advice: {pattern}"

                # Verify key security concepts are present when relevant
                for concept, keywords in critical_security_concepts.items():
                    if concept in query.lower():
                        found_keywords = [kw for kw in keywords if kw in content_lower]
                        assert len(found_keywords) > 0, (
                            f"Critical security concept '{concept}' missing from response for: {query}"
                        )


class TestSecurityIntegrationExpertAgentLightning(TestSecurityIntegrationExpertBase):
    """Test Agent Lightning optimized Security Integration Expert"""

    @pytest.fixture
    def optimized_expert(self):
        """Create optimized security expert instance"""
        return SecurityIntegrationExpertAgentLightning(OptimizationLevel.OPTIMIZED)

    def test_optimized_expert_initialization(self, optimized_expert):
        """Test optimized expert initialization"""
        assert optimized_expert.skill_name == "security_integration_expert"
        assert optimized_expert.optimization_level == OptimizationLevel.OPTIMIZED
        assert hasattr(optimized_expert, "cache")
        assert hasattr(optimized_expert, "optimizer")
        assert hasattr(optimized_expert, "parallel_processor")

    def test_optimization_levels(self):
        """Test different optimization levels"""
        levels = [
            OptimizationLevel.TURBO,
            OptimizationLevel.OPTIMIZED,
            OptimizationLevel.BALANCED,
            OptimizationLevel.CONSERVATIVE,
        ]

        for level in levels:
            expert = SecurityIntegrationExpertAgentLightning(level)
            assert expert.optimization_level == level

    def test_factory_function(self):
        """Test factory function for creating optimized expert"""
        expert = create_optimized_security_expert(OptimizationLevel.TURBO)
        assert isinstance(expert, SecurityIntegrationExpertAgentLightning)
        assert expert.optimization_level == OptimizationLevel.TURBO

    @pytest.mark.asyncio
    async def test_async_execution(self, optimized_expert, sample_context):
        """Test async execution functionality"""
        result = await optimized_expert.execute_async(sample_context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert result.level == SkillLevel.SUMMARY
        assert len(result.content) > 0
        assert "optimization_level" in result.metadata

    def test_cache_functionality(self, optimized_expert, sample_context):
        """Test caching functionality"""
        # First execution - should be cache miss
        result1 = optimized_expert.execute(sample_context, SkillLevel.SUMMARY)
        cache_stats_1 = optimized_expert.cache.get_cache_stats()

        # Second execution - should be cache hit (depending on optimization level)
        result2 = optimized_expert.execute(sample_context, SkillLevel.SUMMARY)
        cache_stats_2 = optimized_expert.cache.get_cache_stats()

        # Cache statistics should be updated
        assert cache_stats_2["hits"] >= cache_stats_1["hits"]
        assert cache_stats_2["misses"] >= cache_stats_1["misses"]

    def test_performance_improvement(self, security_expert, optimized_expert, sample_context):
        """Test performance improvement with optimization"""
        # Test base expert
        start_time = time.time()
        base_result = security_expert.execute(sample_context, SkillLevel.SUMMARY)
        base_time = time.time() - start_time

        # Test optimized expert
        start_time = time.time()
        optimized_result = optimized_expert.execute(sample_context, SkillLevel.SUMMARY)
        optimized_time = time.time() - start_time

        # Optimized version should be faster or at least not significantly slower
        # (Allow some variance due to cache warmup)
        assert optimized_time <= base_time * 1.5  # Allow 50% variance

        # Both should provide relevant content
        assert len(base_result.content) > 0
        assert len(optimized_result.content) > 0

    @pytest.mark.asyncio
    async def test_parallel_processing(self, optimized_expert):
        """Test parallel processing of multiple domains"""
        multi_domain_query = "How to implement comprehensive security including authentication, API security, encryption, and compliance?"
        context = SkillContext(query=multi_domain_query, conversation_history=[], available_tokens=3000)

        result = await optimized_expert.execute_async(context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert "parallel_tasks" in result.metadata.get("performance", {})
        assert len(result.content) > 0

    def test_content_optimization(self, optimized_expert):
        """Test content optimization reduces token usage"""
        test_query = "Implement comprehensive security measures for enterprise web application"
        context = SkillContext(query=test_query, conversation_history=[], available_tokens=5000)

        # Test different optimization levels
        results = {}
        for level in [OptimizationLevel.CONSERVATIVE, OptimizationLevel.BALANCED, OptimizationLevel.TURBO]:
            optimized_expert.set_optimization_level(level)
            optimized_expert.clear_caches()  # Clear cache for fair comparison

            result = optimized_expert.execute(context, SkillLevel.FULL)
            results[level] = result

        # Turbo level should use fewer tokens than conservative
        assert results[OptimizationLevel.TURBO].tokens_used <= results[OptimizationLevel.CONSERVATIVE].tokens_used

    def test_optimization_report(self, optimized_expert):
        """Test optimization report generation"""
        report = optimized_expert.get_optimization_report()

        assert "skill_name" in report
        assert "optimization_level" in report
        assert "performance_metrics" in report
        assert "optimization_features" in report

        performance_metrics = report["performance_metrics"]
        assert "cache_efficiency" in performance_metrics
        assert "parallel_processing" in performance_metrics
        assert "execution_history" in performance_metrics

    def test_cache_management(self, optimized_expert):
        """Test cache management functions"""
        # Add some items to cache through execution
        context = SkillContext(query="Test query for cache", conversation_history=[], available_tokens=1000)
        optimized_expert.execute(context, SkillLevel.METADATA)

        # Check cache has items
        cache_stats_before = optimized_expert.cache.get_cache_stats()
        total_cache_items = (
            cache_stats_before["metadata_cache_size"]
            + cache_stats_before["summary_cache_size"]
            + cache_stats_before["content_cache_size"]
        )

        # Clear caches
        optimized_expert.clear_caches()

        # Verify caches are cleared
        cache_stats_after = optimized_expert.cache.get_cache_stats()
        total_cache_items_after = (
            cache_stats_after["metadata_cache_size"]
            + cache_stats_after["summary_cache_size"]
            + cache_stats_after["content_cache_size"]
        )

        assert total_cache_items_after < total_cache_items

    @pytest.mark.asyncio
    async def test_performance_benchmarking(self, optimized_expert):
        """Test performance benchmarking functionality"""
        test_queries = [
            "How to implement OWASP security controls?",
            "What are API security best practices?",
            "How to achieve SOC 2 compliance?",
        ]

        # Run benchmark
        benchmark_results = await benchmark_security_expert_performance(optimized_expert, test_queries)

        assert isinstance(benchmark_results, dict)
        assert len(benchmark_results) == len(OptimizationLevel)

        # Check that each optimization level has results
        for level_name, results in benchmark_results.items():
            assert "total_time" in results
            assert "average_time" in results
            assert "average_tokens" in results
            assert "cache_hit_rate" in results
            assert "queries_processed" in results
            assert results["queries_processed"] == len(test_queries)


class TestSecurityIntegrationExpertCodeExamples(TestSecurityIntegrationExpertBase):
    """Test code examples and security patterns"""

    def test_database_security_examples(self, security_expert):
        """Test database security code examples"""
        query = "How to implement secure database queries with parameterized statements?"
        context = SkillContext(query=query, conversation_history=[], available_tokens=3000)
        result = security_expert.execute(context, SkillLevel.FULL)

        content = result.content.lower()

        # Should contain secure database patterns
        secure_patterns = ["parameterized", "prepared statements", "execute", "cursor", "sql injection"]

        found_patterns = [pattern for pattern in secure_patterns if pattern in content]
        assert len(found_patterns) >= 3, f"Database security patterns not found: {found_patterns}"

    def test_authentication_code_examples(self, security_expert):
        """Test authentication code examples"""
        query = "Show me secure authentication implementation with password hashing"
        context = SkillContext(query=query, conversation_history=[], available_tokens=3000)
        result = security_expert.execute(context, SkillLevel.FULL)

        content = result.content.lower()

        # Should contain authentication security patterns
        auth_patterns = ["password hashing", "bcrypt", "salt", "hash", "authentication"]

        found_patterns = [pattern for pattern in auth_patterns if pattern in content]
        assert len(found_patterns) >= 3, f"Authentication security patterns not found: {found_patterns}"

    def test_encryption_code_examples(self, security_expert):
        """Test encryption code examples"""
        query = "Implement data encryption with proper key management"
        context = SkillContext(query=query, conversation_history=[], available_tokens=3000)
        result = security_expert.execute(context, SkillLevel.FULL)

        content = result.content.lower()

        # Should contain encryption patterns
        encryption_patterns = ["encryption", "key", "aes", "cryptography", "decrypt"]

        found_patterns = [pattern for pattern in encryption_patterns if pattern in content]
        assert len(found_patterns) >= 3, f"Encryption patterns not found: {found_patterns}"

    def test_api_security_examples(self, security_expert):
        """Test API security code examples"""
        query = "Implement secure REST API with authentication and rate limiting"
        context = SkillContext(query=query, conversation_history=[], available_tokens=3000)
        result = security_expert.execute(context, SkillLevel.FULL)

        content = result.content.lower()

        # Should contain API security patterns
        api_patterns = ["api", "authentication", "rate limiting", "token", "authorization"]

        found_patterns = [pattern for pattern in api_patterns if pattern in content]
        assert len(found_patterns) >= 3, f"API security patterns not found: {found_patterns}"

    def test_code_example_safety(self, security_expert, security_test_queries):
        """Test that code examples don't contain security vulnerabilities"""
        dangerous_code_patterns = [
            "eval(",
            "exec(",
            "shell=True",
            "subprocess.call",
            "os.system",
            "pickle.loads",
            "input() without validation",
            "SELECT * FROM",
            "password = '",
            "secret_key = '",
            "disable_ssl_verification",
            "skip_verification",
        ]

        for domain, queries in security_test_queries.items():
            for query in queries[:1]:  # Test one query per domain
                context = SkillContext(query=query, conversation_history=[], available_tokens=3000)
                result = security_expert.execute(context, SkillLevel.FULL)

                content_lower = result.content.lower()

                for dangerous_pattern in dangerous_code_patterns:
                    assert dangerous_pattern not in content_lower, (
                        f"Dangerous code pattern found in {domain} response: {dangerous_pattern}"
                    )


class TestSecurityIntegrationExpertEdgeCases(TestSecurityIntegrationExpertBase):
    """Test edge cases and boundary conditions"""

    def test_very_long_query(self, security_expert):
        """Test handling of very long queries"""
        long_query = "security " * 500  # Very long repetitive query
        context = SkillContext(query=long_query, conversation_history=[], available_tokens=2000)

        result = security_expert.execute(context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert len(result.content) > 0
        assert result.execution_time < 10.0  # Should complete reasonably

    def test_unicode_security_query(self, security_expert):
        """Test handling of unicode characters in security queries"""
        unicode_query = "Implementación de seguridad con 🔐 y caracteres especiales: ñáéíóú"
        context = SkillContext(query=unicode_query, conversation_history=[], available_tokens=2000)

        result = security_expert.execute(context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert len(result.content) > 0
        # Should handle unicode without errors

    def test_mixed_language_query(self, security_expert):
        """Test handling of mixed language security queries"""
        mixed_query = "How to implement sécurité authentication with OAuth 2.0 protección de datos?"
        context = SkillContext(query=mixed_query, conversation_history=[], available_tokens=2000)

        result = security_expert.execute(context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert len(result.content) > 0

    def test_minimal_token_context(self, security_expert):
        """Test handling of very minimal token limits"""
        minimal_context = SkillContext(
            query="security basics",
            conversation_history=[],
            available_tokens=10,  # Very minimal
        )

        result = security_expert.execute(minimal_context, SkillLevel.METADATA)

        assert isinstance(result, SkillResult)
        assert result.tokens_used <= minimal_context.available_tokens

    def test_empty_conversation_history(self, security_expert):
        """Test handling of empty conversation history"""
        context = SkillContext(query="security question", conversation_history=[], available_tokens=2000)

        result = security_expert.execute(context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert len(result.content) > 0

    def test_large_conversation_history(self, security_expert):
        """Test handling of large conversation history"""
        large_history = [{"role": "user", "content": f"Previous conversation item {i}"} for i in range(1000)]

        context = SkillContext(
            query="current security question", conversation_history=large_history, available_tokens=2000
        )

        result = security_expert.execute(context, SkillLevel.SUMMARY)

        assert isinstance(result, SkillResult)
        assert len(result.content) > 0

    def test_repeated_similar_queries(self, security_expert):
        """Test handling of repeated similar queries"""
        query = "How to implement secure authentication?"
        context = SkillContext(query=query, conversation_history=[], available_tokens=2000)

        results = []
        for i in range(5):
            result = security_expert.execute(context, SkillLevel.SUMMARY)
            results.append(result)

        # All results should be consistent
        for result in results[1:]:
            assert result.content == results[0].content

    def test_vague_security_query(self, security_expert):
        """Test handling of vague security queries"""
        vague_queries = ["security", "help with security", "make it secure", "security stuff", "protect things"]

        for query in vague_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            result = security_expert.execute(context, SkillLevel.SUMMARY)

            assert isinstance(result, SkillResult)
            assert len(result.content) > 0
            # Should provide helpful guidance even for vague queries


# Integration tests
class TestSecurityIntegrationExpertIntegration:
    """Integration tests for Security Integration Expert"""

    def test_end_to_end_security_workflow(self):
        """Test complete security workflow from query to solution"""
        expert = SecurityIntegrationExpertSkill()

        # Simulate security consultation workflow
        security_queries = [
            "What security vulnerabilities should I worry about?",
            "How do I implement secure authentication?",
            "How to secure my API endpoints?",
            "What encryption should I use?",
            "How to ensure compliance?",
        ]

        results = []
        for query in security_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=3000)
            result = expert.execute(context, SkillLevel.SUMMARY)
            results.append(result)

            assert isinstance(result, SkillResult)
            assert len(result.content) > 0
            assert result.execution_time < 5.0

        # Verify comprehensive coverage
        all_content = " ".join(result.content for result in results).lower()
        security_domains_mentioned = ["authentication", "api", "encryption", "compliance", "vulnerability"]

        for domain in security_domains_mentioned:
            assert domain in all_content, f"Security domain {domain} not covered in workflow"

    def test_cross_domain_security_consistency(self):
        """Test consistency across security domains"""
        expert = SecurityIntegrationExpertSkill()

        cross_domain_query = "How does authentication relate to API security and compliance requirements?"
        context = SkillContext(query=cross_domain_query, conversation_history=[], available_tokens=4000)

        result = expert.execute(context, SkillLevel.FULL)

        content = result.content.lower()

        # Should mention relationships between domains
        cross_domain_keywords = ["authentication", "api", "compliance", "security", "requirements"]

        found_keywords = [kw for kw in cross_domain_keywords if kw in content]
        assert len(found_keywords) >= 4, "Cross-domain relationships not adequately covered"

    @pytest.mark.asyncio
    async def test_concurrent_security_consultations(self):
        """Test handling multiple concurrent security consultations"""
        expert = SecurityIntegrationExpertAgentLightning(OptimizationLevel.OPTIMIZED)

        concurrent_queries = [
            "OWASP security implementation",
            "OAuth 2.0 best practices",
            "Data encryption strategies",
            "SOC 2 compliance roadmap",
            "Cloud security architecture",
        ]

        # Execute queries concurrently
        tasks = []
        for query in concurrent_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)
            task = expert.execute_async(context, SkillLevel.SUMMARY)
            tasks.append(task)

        results = await asyncio.gather(*tasks)

        # Verify all queries were handled successfully
        assert len(results) == len(concurrent_queries)

        for result in results:
            assert isinstance(result, SkillResult)
            assert len(result.content) > 0
            assert result.execution_time < 5.0


# Performance and load tests
class TestSecurityIntegrationExpertPerformance:
    """Performance testing for Security Integration Expert"""

    def test_response_time_performance(self):
        """Test response time meets performance requirements"""
        expert = SecurityIntegrationExpertSkill()

        test_queries = [
            "SQL injection prevention",
            "Multi-factor authentication",
            "API rate limiting",
            "Data encryption standards",
            "Security monitoring implementation",
        ]

        response_times = []
        for query in test_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=2000)

            start_time = time.time()
            result = expert.execute(context, SkillLevel.SUMMARY)
            response_time = time.time() - start_time

            response_times.append(response_time)

        # Performance assertions
        average_time = sum(response_times) / len(response_times)
        max_time = max(response_times)

        assert average_time < 2.0, f"Average response time too high: {average_time:.2f}s"
        assert max_time < 5.0, f"Maximum response time too high: {max_time:.2f}s"

    def test_memory_usage_stability(self):
        """Test memory usage remains stable during extended use"""
        expert = SecurityIntegrationExpertAgentLightning(OptimizationLevel.BALANCED)

        # Simulate extended usage
        for i in range(100):
            query = f"Security question {i}: How to implement secure coding practices?"
            context = SkillContext(query=query, conversation_history=[], available_tokens=1000)
            result = expert.execute(context, SkillLevel.SUMMARY)

            assert isinstance(result, SkillResult)

            # Every 10 executions, check cache sizes are reasonable
            if i % 10 == 0:
                cache_stats = expert.cache.get_cache_stats()
                total_cached_items = (
                    cache_stats["metadata_cache_size"]
                    + cache_stats["summary_cache_size"]
                    + cache_stats["content_cache_size"]
                )

                # Cache should not grow unboundedly
                assert total_cached_items < 350, f"Cache size too large: {total_cached_items}"

    def test_scalability_with_query_complexity(self):
        """Test scalability with increasing query complexity"""
        expert = SecurityIntegrationExpertSkill()

        # Queries of increasing complexity
        complexity_queries = [
            "security",
            "web application security",
            "secure web application development with OWASP compliance",
            "comprehensive enterprise security architecture including application security, identity management, API security, data protection, compliance frameworks, security monitoring, cloud security, and DevSecOps practices",
            "implement a zero-trust security architecture with multi-layered defense-in-depth approach, covering all OWASP Top 10 vulnerabilities, implementing robust authentication and authorization with OAuth 2.0 and OpenID Connect, securing all APIs with proper rate limiting and input validation, encrypting data at rest and in transit using AES-256 and TLS 1.3, ensuring compliance with SOC 2, ISO 27001, GDPR, HIPAA, and PCI DSS, implementing comprehensive SIEM with real-time threat detection and automated incident response, securing multi-cloud infrastructure across AWS, Azure, and GCP with proper IAM and network security, and integrating security throughout the CI/CD pipeline with automated testing, vulnerability scanning, and supply chain security",
        ]

        response_times = []
        token_usage = []

        for query in complexity_queries:
            context = SkillContext(query=query, conversation_history=[], available_tokens=5000)

            start_time = time.time()
            result = expert.execute(context, SkillLevel.SUMMARY)
            response_time = time.time() - start_time

            response_times.append(response_time)
            token_usage.append(result.tokens_used)

        # Response time should scale reasonably with complexity
        time_growth_rate = response_times[-1] / response_times[0]
        token_growth_rate = token_usage[-1] / token_usage[0]

        # Should not be exponential growth
        assert time_growth_rate < 10, f"Response time scaling poor: {time_growth_rate}x growth"
        assert token_growth_rate < 8, f"Token usage scaling poor: {token_growth_rate}x growth"


if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
