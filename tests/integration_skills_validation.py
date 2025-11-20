"""
Integration Skills Validation Tests

Comprehensive validation tests for integration skills to ensure
zero-hallucination enforcement and working patterns.
"""

import pytest

from amplifier.skills.integration import ApiDesignExpertSkill
from amplifier.skills.integration import FullStackIntegrationExpertSkill
from amplifier.skills.integration import GraphQLExpertSkill
from amplifier.skills.skills_framework.skill_template import SkillContext
from amplifier.skills.skills_framework.skill_template import SkillLevel


class TestIntegrationSkillsValidation:
    """Validate that all integration skills provide accurate, working patterns."""

    @pytest.fixture
    def skill_context(self):
        """Create a skill context for testing."""
        return SkillContext(query="test integration patterns", conversation_history=[], available_tokens=4000)

    @pytest.fixture
    def integration_skills(self):
        """All integration skills to test."""
        return [FullStackIntegrationExpertSkill(), ApiDesignExpertSkill(), GraphQLExpertSkill()]

    class TestFullStackIntegrationSkill:
        """Test Full-Stack Integration Expert Skill."""

        def test_skill_metadata(self):
            """Test skill has correct metadata."""
            skill = FullStackIntegrationExpertSkill()

            assert skill.description
            assert "full-stack" in skill.description.lower()
            assert len(skill.tags) > 5
            assert "full-stack" in skill.tags
            assert "integration" in skill.tags
            assert "monorepo" in skill.tags

        def test_skill_handles_relevant_queries(self, skill_context):
            """Test skill correctly identifies relevant queries."""
            skill = FullStackIntegrationExpertSkill()

            # High confidence queries
            high_confidence_queries = [
                "How do I set up a monorepo with frontend and backend?",
                "What are the best practices for full-stack deployment?",
                "Design a complete application architecture",
            ]

            for query in high_confidence_queries:
                context = SkillContext(query=query, conversation_history=[], available_tokens=4000)
                confidence = skill.can_handle(context)
                assert confidence >= 0.7, f"Should handle query: {query}"

        def test_metadata_level_content(self, skill_context):
            """Test metadata level provides minimal info."""
            skill = FullStackIntegrationExpertSkill()
            result = skill.execute(skill_context, SkillLevel.METADATA)

            assert result.skill_name == "fullstack_integration_expert"
            assert result.level == SkillLevel.METADATA
            assert len(result.content) < 500  # Should be concise
            assert "monorepo" in result.content.lower()
            assert "api" in result.content.lower()

        def test_summary_level_contains_key_patterns(self, skill_context):
            """Test summary level contains essential patterns."""
            skill = FullStackIntegrationExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content = result.content.lower()

            # Essential full-stack concepts
            assert "monorepo" in content
            assert "api" in content
            assert "authentication" in content
            assert "deployment" in content

            # Working examples
            assert "dockerfile" in content or "docker" in content
            assert "kubernetes" in content or "k8s" in content

        def test_full_level_has_production_patterns(self, skill_context):
            """Test full level has production-ready patterns."""
            skill = FullStackIntegrationExpertSkill()
            result = skill.execute(skill_context, SkillLevel.FULL)

            content = result.content.lower()

            # Production patterns
            assert "monitoring" in content
            assert "error" in content
            assert "health" in content

            # Security practices
            assert "jwt" in content or "security" in content
            assert "cors" in content

            # Testing patterns
            assert "test" in content

    class TestApiDesignSkill:
        """Test API Design Expert Skill."""

        def test_skill_metadata(self):
            """Test skill has correct metadata."""
            skill = ApiDesignExpertSkill()

            assert skill.description
            assert "api" in skill.description.lower()
            assert "security" in skill.description.lower()
            assert len(skill.tags) > 5
            assert "api-design" in skill.tags
            assert "rest-api" in skill.tags
            assert "owasp" in skill.tags

        def test_security_focus(self, skill_context):
            """Test skill emphasizes security."""
            skill = ApiDesignExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content_lower = result.content.lower()

            # OWASP compliance
            assert "owasp" in content_lower
            assert "security" in content_lower

            # Security practices
            assert "authentication" in content_lower
            assert "authorization" in content_lower
            assert "validation" in content_lower
            assert "rate limiting" in content_lower

        def test_rest_api_patterns(self, skill_context):
            """Test REST API design patterns."""
            skill = ApiDesignExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content = result.content

            # REST patterns
            assert "GET" in content
            assert "POST" in content
            assert "PUT" in content
            assert "DELETE" in content

            # HTTP status codes
            assert "200" in content or "201" in content
            assert "404" in content or "401" in content

        def test_openapi_inclusion(self, skill_context):
            """Test OpenAPI specification is included."""
            skill = ApiDesignExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content = result.content.lower()

            assert "openapi" in content
            assert "documentation" in content

    class TestGraphQLExpertSkill:
        """Test GraphQL Expert Skill."""

        def test_skill_metadata(self):
            """Test skill has correct metadata."""
            skill = GraphQLExpertSkill()

            assert skill.description
            assert "graphql" in skill.description.lower()
            assert "apollo" in skill.description.lower()
            assert len(skill.tags) > 5
            assert "graphql" in skill.tags
            assert "apollo-server" in skill.tags
            assert "federation" in skill.tags

        def test_apollo_server_patterns(self, skill_context):
            """Test Apollo Server setup patterns."""
            skill = GraphQLExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content = result.content.lower()

            assert "apollo" in content
            assert "server" in content
            assert "resolvers" in content

        def test_federation_inclusion(self, skill_context):
            """Test GraphQL Federation is covered."""
            skill = GraphQLExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content = result.content.lower()

            assert "federation" in content

        def test_performance_optimization(self, skill_context):
            """Test performance optimization is emphasized."""
            skill = GraphQLExpertSkill()
            result = skill.execute(skill_context, SkillLevel.SUMMARY)

            content = result.content.lower()

            assert "performance" in content or "optimization" in content
            assert "dataloader" in content

        def test_schema_design_patterns(self, skill_context):
            """Test schema design patterns are included."""
            skill = GraphQLExpertSkill()
            result = skill.execute(skill_context, SkillLevel.FULL)

            content = result.content

            # Schema patterns
            assert "type" in content
            assert "interface" in content or "union" in content
            assert "schema" in content

    class TestZeroHallucinationEnforcement:
        """Test zero-hallucination enforcement across all skills."""

        def test_all_skills_have_working_examples(self, integration_skills, skill_context):
            """Test all skills provide working code examples."""
            for skill in integration_skills:
                result = skill.execute(skill_context, SkillLevel.FULL)
                content = result.content

                # Check for code examples with common patterns
                has_code_examples = (
                    "```javascript" in content
                    or "```typescript" in content
                    or "```yaml" in content
                    or "```json" in content
                )

                assert has_code_examples, f"{skill.skill_name} should have code examples"

        def test_all_skills_emphasize_security(self, integration_skills, skill_context):
            """Test all skills include security considerations."""
            for skill in integration_skills:
                result = skill.execute(skill_context, SkillLevel.SUMMARY)
                content_lower = result.content.lower()

                # Each integration skill should mention security
                has_security_mention = (
                    "security" in content_lower
                    or "auth" in content_lower
                    or "cors" in content_lower
                    or "validation" in content_lower
                    or "jwt" in content_lower
                )

                assert has_security_mention, f"{skill.skill_name} should mention security"

        def test_all_skills_have_production_patterns(self, integration_skills, skill_context):
            """Test all skills include production-ready patterns."""
            for skill in integration_skills:
                result = skill.execute(skill_context, SkillLevel.FULL)
                content_lower = result.content.lower()

                # Production patterns
                has_production_patterns = (
                    "monitoring" in content_lower
                    or "health" in content_lower
                    or "error" in content_lower
                    or "logging" in content_lower
                    or "performance" in content_lower
                )

                assert has_production_patterns, f"{skill.skill_name} should include production patterns"

        def test_progressive_disclosure_works(self, integration_skills, skill_context):
            """Test progressive disclosure provides increasing detail."""
            for skill in integration_skills:
                metadata_result = skill.execute(skill_context, SkillLevel.METADATA)
                summary_result = skill.execute(skill_context, SkillLevel.SUMMARY)
                full_result = skill.execute(skill_context, SkillLevel.FULL)

                # Metadata should be shortest
                assert len(metadata_result.content) < len(summary_result.content)
                assert len(summary_result.content) < len(full_result.content)

                # Content should progressively expand
                assert (
                    summary_result.content.startswith(metadata_result.content)
                    or metadata_result.content in summary_result.content
                )

    class TestAgentLightningOptimizations:
        """Test Agent Lightning optimizations are applied."""

        def test_skills_have_compound_multiplier_effects(self, integration_skills):
            """Test skills are designed to work together."""
            skills_by_name = {skill.skill_name: skill for skill in integration_skills}

            # Skills should have overlapping domains for compound effects
            # Full-Stack covers overall integration
            # API Design covers API specifics
            # GraphQL covers GraphQL specifics

            assert "fullstack_integration_expert" in skills_by_name
            assert "api_design_expert" in skills_by_name
            assert "graphql_expert" in skills_by_name

        def test_skills_have_focus_area_extraction(self, integration_skills, skill_context):
            """Test skills can extract focus areas from queries."""
            for skill in integration_skills:
                # Test with domain-specific queries
                domain_queries = {
                    FullStackIntegrationExpertSkill: "monorepo setup with deployment",
                    ApiDesignExpertSkill: "REST API security and validation",
                    GraphQLExpertSkill: "Apollo Server federation setup",
                }

                if type(skill) in domain_queries:
                    query = domain_queries[type(skill)]
                    context = SkillContext(query=query, conversation_history=[], available_tokens=4000)
                    confidence = skill.can_handle(context)

                    assert confidence >= 0.7, f"{skill.skill_name} should handle domain query: {query}"

        def test_skills_have_optimized_metadata(self, integration_skills):
            """Test skills have optimized metadata for quick matching."""
            for skill in integration_skills:
                # Metadata should be concise and informative
                assert len(skill.description) < 200
                assert len(skill.tags) >= 5
                assert all(len(tag) <= 20 for tag in skill.tags)  # Tags should be reasonable length

        def test_skills_handle_token_limits(self, integration_skills, skill_context):
            """Test skills respect token limits."""
            # Test with very limited tokens
            limited_context = SkillContext(
                query="test query",
                conversation_history=[],
                available_tokens=100,  # Very limited
            )

            for skill in integration_skills:
                result = skill.execute(limited_context, SkillLevel.METADATA)

                # Even with limited tokens, should provide some response
                assert len(result.content) > 0
                assert result.tokens_used <= limited_context.available_tokens * 1.5  # Allow some estimation error


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
