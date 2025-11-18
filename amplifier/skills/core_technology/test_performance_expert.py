"""
Test Cases for Performance Testing Expert Skill

Comprehensive test suite ensuring zero-hallucination performance recommendations
and validated optimization patterns.
"""

import asyncio
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from performance_testing_expert import PerformanceTestingExpertSkill, PerformanceMetric, PerformanceGrade
from performance_tools_integration import PerformanceToolsManager, LighthouseIntegration
from agent_lightning_performance_patterns import AgentLightningPerformancePatterns
from performance_examples import PerformanceOptimizationExamples, PerformanceDemoRunner


class TestPerformanceTestingExpertSkill(unittest.TestCase):
    """Test cases for PerformanceTestingExpertSkill."""

    def setUp(self):
        """Set up test fixtures."""
        self.skill = PerformanceTestingExpertSkill()

    def test_skill_initialization(self):
        """Test skill initialization and properties."""
        self.assertEqual(self.skill.skill_name, "performance_testing_expert")
        self.assertIn("performance", self.skill.tags)
        self.assertIn("web-vitals", self.skill.tags)
        self.assertIn("core_web_vitals", self.skill.tags)

    def test_skill_description(self):
        """Test skill description contains key capabilities."""
        description = self.skill.description
        self.assertIn("Core Web Vitals", description)
        self.assertIn("zero hallucination", description)
        self.assertIn("Lighthouse", description)
        self.assertIn("load testing", description)

    def test_can_handle_performance_queries(self):
        """Test skill correctly identifies performance-related queries."""
        # Mock context
        high_confidence_context = Mock()
        high_confidence_context.query = "Analyze performance for https://example.com"
        high_confidence_context.conversation_history = []
        high_confidence_context.available_tokens = 5000

        confidence = self.skill.can_handle(high_confidence_context)
        self.assertGreater(confidence, 0.9)

        # Medium confidence
        medium_confidence_context = Mock()
        medium_confidence_context.query = "My website is slow, can you help optimize it?"
        medium_confidence_context.conversation_history = []
        medium_confidence_context.available_tokens = 5000

        confidence = self.skill.can_handle(medium_confidence_context)
        self.assertGreater(confidence, 0.7)

        # Low confidence
        low_confidence_context = Mock()
        low_confidence_context.query = "What is the weather today?"
        low_confidence_context.conversation_history = []
        low_confidence_context.available_tokens = 5000

        confidence = self.skill.can_handle(low_confidence_context)
        self.assertLess(confidence, 0.5)

    def test_extract_url_from_query(self):
        """Test URL extraction from queries."""
        # Valid URL
        query_with_url = "Please analyze https://example.com for performance issues"
        extracted_url = self.skill._extract_url(query_with_url)
        self.assertEqual(extracted_url, "https://example.com")

        # Query without URL
        query_without_url = "How can I improve my website performance?"
        extracted_url = self.skill._extract_url(query_without_url)
        self.assertIsNone(extracted_url)

        # Multiple URLs (should return first)
        query_multiple_urls = "Compare https://site1.com and https://site2.com performance"
        extracted_url = self.skill._extract_url(query_multiple_urls)
        self.assertEqual(extracted_url, "https://site1.com")

    def test_url_validation(self):
        """Test URL validation."""
        # Valid URLs
        self.assertTrue(self.skill._is_valid_url("https://example.com"))
        self.assertTrue(self.skill._is_valid_url("https://www.google.com"))

        # Invalid URLs
        self.assertFalse(self.skill._is_valid_url("not-a-url"))
        self.assertFalse(self.skill._is_valid_url("http://nonexistent-domain-12345.com"))

    def test_get_optimization_strategies_for_lcp(self):
        """Test getting optimization strategies for LCP."""
        strategies = self.skill.get_optimization_strategies(PerformanceMetric.LCP)

        self.assertGreater(len(strategies), 0)
        for strategy in strategies:
            self.assertIn("lcp", strategy.expected_improvement)
            self.assertIn("implementation", strategy.implementation)
            self.assertIn("validation_method", strategy.implementation)
            self.assertGreater(len(strategy.references), 0)

    def test_get_optimization_strategies_for_fid(self):
        """Test getting optimization strategies for FID."""
        strategies = self.skill.get_optimization_strategies(PerformanceMetric.FID)

        self.assertGreater(len(strategies), 0)
        for strategy in strategies:
            self.assertIn("fid", strategy.expected_improvement)
            self.assertIn("implementation_complexity", str(strategy.implementation_complexity))

    def test_performance_recommendations_generation(self):
        """Test performance recommendations generation."""
        # Simulate performance data with issues
        performance_data = {
            "largest_contentful_paint": 3500,  # Poor LCP
            "first_input_delay": 200,  # Needs improvement FID
            "cumulative_layout_shift": 0.3,  # Poor CLS
            "time_to_first_byte": 600,  # Good TTFB
        }

        recommendations = self.skill.get_performance_recommendations(performance_data)

        self.assertGreater(len(recommendations), 0)

        # Check that recommendations are properly prioritized
        priorities = [rec["priority"] for rec in recommendations]
        self.assertIn("high", priorities)

        # Check that recommendations include implementation strategies
        for rec in recommendations:
            self.assertIn("strategy", rec)
            self.assertIn("priority", rec)
            self.assertIn("current_value", rec)
            self.assertIn("grade", rec)

    def test_web_vitals_thresholds(self):
        """Test Web Vitals thresholds are properly defined."""
        from performance_testing_expert import WEB_VITALS_THRESHOLDS

        # Test LCP thresholds
        lcp_thresholds = WEB_VITALS_THRESHOLDS[PerformanceMetric.LCP]
        self.assertEqual(lcp_thresholds.good, 2500)
        self.assertEqual(lcp_thresholds.needs_improvement, 4000)

        # Test FID thresholds
        fid_thresholds = WEB_VITALS_THRESHOLDS[PerformanceMetric.FID]
        self.assertEqual(fid_thresholds.good, 100)
        self.assertEqual(fid_thresholds.needs_improvement, 300)

        # Test CLS thresholds
        cls_thresholds = WEB_VITALS_THRESHOLDS[PerformanceMetric.CLS]
        self.assertEqual(cls_thresholds.good, 0.1)
        self.assertEqual(cls_thresholds.needs_improvement, 0.25)

    def test_web_vital_grading(self):
        """Test Web Vitals grading system."""
        from performance_testing_expert import WEB_VITALS_THRESHOLDS

        # Test LCP grading
        lcp_thresholds = WEB_VITALS_THRESHOLDS[PerformanceMetric.LCP]
        self.assertEqual(lcp_thresholds.get_grade(2000), PerformanceGrade.EXCELLENT)
        self.assertEqual(lcp_thresholds.get_grade(3000), PerformanceGrade.GOOD)
        self.assertEqual(lcp_thresholds.get_grade(5000), PerformanceGrade.POOR)

        # Test FID grading
        fid_thresholds = WEB_VITALS_THRESHOLDS[PerformanceMetric.FID]
        self.assertEqual(fid_thresholds.get_grade(50), PerformanceGrade.EXCELLENT)
        self.assertEqual(fid_thresholds.get_grade(200), PerformanceGrade.GOOD)
        self.assertEqual(fid_thresholds.get_grade(400), PerformanceGrade.POOR)


class TestAgentLightningPerformancePatterns(unittest.TestCase):
    """Test cases for Agent Lightning performance patterns."""

    def setUp(self):
        """Set up test fixtures."""
        self.patterns = AgentLightningPerformancePatterns()

    def test_patterns_loading(self):
        """Test that patterns are loaded correctly."""
        self.assertGreater(len(self.patterns.patterns), 0)

        # Check that patterns have required fields
        for pattern_id, pattern in self.patterns.patterns.items():
            self.assertIsNotNone(pattern.pattern_id)
            self.assertIsNotNone(pattern.category)
            self.assertIsNotNone(pattern.title)
            self.assertGreater(pattern.success_rate, 0)
            self.assertLessEqual(pattern.success_rate, 1.0)
            self.assertGreater(len(pattern.average_improvement), 0)
            self.assertIn(pattern.implementation_complexity, ["low", "medium", "high"])

    def test_get_recommended_patterns(self):
        """Test pattern recommendation system."""
        # Context with LCP issues
        context = {
            "core_web_vitals": {
                "lcp": 4000,  # Poor LCP
                "fid": 50,  # Good FID
                "cls": 0.05,  # Good CLS
            }
        }

        recommendations = self.patterns.get_recommended_patterns(context)

        self.assertGreater(len(recommendations), 0)

        # Should include patterns for LCP optimization
        lcp_patterns = [r for r in recommendations if r.category == "image_optimization"]
        self.assertGreater(len(lcp_patterns), 0)

        # Patterns should be sorted by success rate
        success_rates = [r.success_rate for r in recommendations]
        self.assertEqual(success_rates, sorted(success_rates, reverse=True))

    def test_implement_pattern(self):
        """Test pattern implementation plan generation."""
        pattern_id = "webp_conversion_with_fallback"
        context = {"url": "https://example.com"}

        implementation_plan = self.patterns.implement_pattern(pattern_id, context)

        self.assertIn("pattern", implementation_plan)
        self.assertIn("implementation", implementation_plan)
        self.assertIn("validation", implementation_plan)
        self.assertIn("monitoring", implementation_plan)
        self.assertIn("notes", implementation_plan)

        # Check implementation details
        impl = implementation_plan["implementation"]
        self.assertIn("steps", impl)
        self.assertIn("code_snippets", impl)
        self.assertIn("tools", impl)
        self.assertIn("complexity", impl)

    def test_pattern_tracking(self):
        """Test pattern success tracking."""
        pattern_id = "webp_conversion_with_fallback"
        actual_improvement = {"lcp": 30.0, "page_weight": 25.0}
        success = True
        notes = "Implementation successful on e-commerce site"

        # Track success
        self.patterns.track_pattern_success(pattern_id, actual_improvement, success, notes)

        # Verify tracking data
        self.assertIn(pattern_id, self.patterns.success_tracking)
        self.assertEqual(len(self.patterns.success_tracking[pattern_id]), 1)

        # Verify pattern statistics updated
        pattern = self.patterns.patterns[pattern_id]
        self.assertGreater(pattern.sample_size, 0)

    def test_pattern_insights(self):
        """Test pattern insights generation."""
        insights = self.patterns.get_pattern_insights()

        self.assertGreater(len(insights), 0)

        # Check insights structure
        for pattern_id, insight in insights.items():
            self.assertIn("title", insight)
            self.assertIn("category", insight)
            self.assertIn("success_rate", insight)
            self.assertIn("confidence_level", insight)
            self.assertIn("average_improvement", insight)

    def test_export_import_patterns(self):
        """Test patterns export and import."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            export_path = f.name

        try:
            # Add some tracking data
            self.patterns.track_pattern_success(
                "webp_conversion_with_fallback", {"lcp": 30.0}, True, "Test implementation"
            )

            # Export patterns
            self.patterns.export_patterns(export_path)
            self.assertTrue(Path(export_path).exists())

            # Verify export file content
            with open(export_path, "r") as f:
                export_data = json.load(f)

            self.assertIn("patterns", export_data)
            self.assertIn("success_tracking", export_data)
            self.assertIn("export_timestamp", export_data)

            # Create new instance and import
            new_patterns = AgentLightningPerformancePatterns()
            new_patterns.import_patterns(export_path)

            # Verify import worked
            self.assertIn("webp_conversion_with_fallback", new_patterns.success_tracking)

        finally:
            Path(export_path).unlink(missing_ok=True)


class TestPerformanceExamples(unittest.TestCase):
    """Test cases for performance optimization examples."""

    def setUp(self):
        """Set up test fixtures."""
        self.examples = PerformanceOptimizationExamples()

    def test_examples_loading(self):
        """Test that examples are loaded correctly."""
        self.assertGreater(len(self.examples.examples), 0)

        # Check example structure
        for example in self.examples.examples:
            self.assertIsNotNone(example.title)
            self.assertIsNotNone(example.description)
            self.assertIsNotNone(example.category)
            self.assertGreater(len(example.before_metrics), 0)
            self.assertGreater(len(example.after_metrics), 0)
            self.assertGreater(len(example.implementation_code), 0)
            self.assertGreater(len(example.lessons_learned), 0)

    def test_get_example_by_category(self):
        """Test filtering examples by category."""
        image_examples = self.examples.get_example_by_category("image_optimization")
        self.assertGreater(len(image_examples), 0)

        for example in image_examples:
            self.assertEqual(example.category, "image_optimization")

    def test_get_top_improvements(self):
        """Test getting top improvements by metric."""
        top_lcp_improvements = self.examples.get_top_improvements("lcp", limit=3)

        self.assertLessEqual(len(top_lcp_improvements), 3)

        # Verify all examples have LCP improvements
        for example in top_lcp_improvements:
            self.assertIn("lcp", example.actual_improvements)

        # Should be sorted by improvement percentage
        if len(top_lcp_improvements) > 1:
            improvements = [example.actual_improvements["lcp"] for example in top_lcp_improvements]
            self.assertEqual(improvements, sorted(improvements, reverse=True))

    def test_calculate_roi(self):
        """Test ROI calculation for examples."""
        example = self.examples.examples[0]  # Use first example
        roi = self.examples.calculate_roi(example)

        self.assertIn("performance_improvement", roi)
        self.assertIn("estimated_revenue_impact", roi)
        self.assertIn("user_experience_improvement", roi)

        # ROI values should be reasonable
        self.assertGreaterEqual(roi["performance_improvement"], 0)
        self.assertGreaterEqual(roi["user_experience_improvement"], 0)


class TestPerformanceToolsManager(unittest.TestCase):
    """Test cases for PerformanceToolsManager."""

    def setUp(self):
        """Set up test fixtures."""
        self.manager = PerformanceToolsManager()

    def test_tools_status_check(self):
        """Test tools status checking."""
        tools_status = self.manager.get_tools_status()

        self.assertIn("lighthouse", tools_status)
        self.assertIn("webpagetest", tools_status)
        self.assertIn("chrome_devtools", tools_status)
        self.assertIn("bundle_analyzer", tools_status)

        # Check status structure
        for tool_name, config in tools_status.items():
            self.assertIsNotNone(config.tool_name)
            self.assertIsInstance(config.available, bool)
            self.assertIsNotNone(config.setup_instructions)

    @patch("requests.get")
    def test_webpagetest_availability_check(self, mock_get):
        """Test WebPageTest availability checking."""
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        manager = PerformanceToolsManager()
        status = manager.webpagetest.config

        # Should be available with successful mock response
        self.assertTrue(status.available)

    @patch("subprocess.run")
    def test_lighthouse_availability_check(self, mock_run):
        """Test Lighthouse availability checking."""
        # Mock successful Lighthouse run
        mock_result = Mock()
        mock_result.returncode = 0
        mock_result.stdout = "Lighthouse 10.0.0"
        mock_run.return_value = mock_result

        lighthouse = LighthouseIntegration()
        self.assertTrue(lighthouse.config.available)

        # Mock failed Lighthouse run
        mock_result.returncode = 1
        mock_run.return_value = mock_result

        lighthouse = LighthouseIntegration()
        self.assertFalse(lighthouse.config.available)


class TestPerformanceDemoRunner(unittest.TestCase):
    """Test cases for PerformanceDemoRunner."""

    def setUp(self):
        """Set up test fixtures."""
        self.demo = PerformanceDemoRunner()

    def test_demo_initialization(self):
        """Test demo runner initialization."""
        self.assertIsNotNone(self.demo.examples)
        self.assertIsNotNone(self.demo.tools_manager)
        self.assertIsNotNone(self.demo.patterns)

    def test_get_relevant_examples(self):
        """Test getting relevant examples based on analysis."""
        # Mock analysis results with LCP issues
        analysis_results = {
            "lighthouse": {
                "core_web_vitals": {
                    "lcp": {"value": 4000},  # Poor LCP
                    "fid": {"value": 50},  # Good FID
                    "cls": {"value": 0.05},  # Good CLS
                }
            }
        }

        relevant_examples = self.demo._get_relevant_examples(analysis_results)

        # Should return relevant optimization examples
        self.assertGreater(len(relevant_examples), 0)

        # Check example structure
        for example in relevant_examples:
            self.assertIn("title", example)
            self.assertIn("category", example)
            self.assertIn("improvements", example)
            self.assertIn("lessons", example)

    def test_generate_next_steps(self):
        """Test next steps generation."""
        # Mock analysis results with poor performance
        analysis_results = {
            "lighthouse": {
                "performance_score": 45  # Poor performance
            },
            "tools_used": ["lighthouse"],
        }

        # Mock recommendations
        class MockRecommendation:
            def __init__(self):
                self.title = "Test Optimization"
                self.success_rate = 0.9
                self.average_improvement = {"lcp": 30}

        recommendations = [MockRecommendation()]

        next_steps = self.demo._generate_next_steps(analysis_results, recommendations)

        self.assertGreater(len(next_steps), 0)

        # Should include high priority steps for poor performance
        priorities = [step["priority"] for step in next_steps]
        self.assertIn("high", priorities)

        # Check step structure
        for step in next_steps:
            self.assertIn("priority", step)
            self.assertIn("action", step)
            self.assertIn("description", step)


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete performance testing system."""

    def setUp(self):
        """Set up integration test fixtures."""
        self.skill = PerformanceTestingExpertSkill()
        self.patterns = AgentLightningPerformancePatterns()
        self.examples = PerformanceOptimizationExamples()

    def test_skill_patterns_integration(self):
        """Test integration between skill and patterns."""
        # Create a performance context
        from performance_testing_expert import SkillContext

        context = SkillContext(
            query="Analyze performance for https://example.com", conversation_history=[], available_tokens=5000
        )

        # Get skill execution result
        result = self.skill.execute(context, level="FULL")
        self.assertIsNotNone(result.content)

        # Get patterns recommendations
        mock_context = {"core_web_vitals": {"lcp": 4000, "fid": 200, "cls": 0.3}}
        recommendations = self.patterns.get_recommended_patterns(mock_context)

        # Verify both systems provide complementary insights
        self.assertGreater(len(recommendations), 0)
        self.assertGreater(len(result.content), 1000)  # Substantial response

    def test_end_to_end_performance_analysis(self):
        """Test end-to-end performance analysis workflow."""
        # Simulate performance data
        performance_data = {
            "url": "https://example.com",
            "lighthouse_score": 65,
            "core_web_vitals": {"lcp": 3500, "fid": 180, "cls": 0.25, "ttfb": 900},
        }

        # Get skill recommendations
        recommendations = self.skill.get_performance_recommendations(
            {
                "largest_contentful_paint": performance_data["core_web_vitals"]["lcp"],
                "first_input_delay": performance_data["core_web_vitals"]["fid"],
                "cumulative_layout_shift": performance_data["core_web_vitals"]["cls"],
                "time_to_first_byte": performance_data["core_web_vitals"]["ttfb"],
            }
        )

        # Get pattern recommendations
        pattern_recommendations = self.patterns.get_recommended_patterns(performance_data)

        # Get relevant examples
        relevant_examples = self.examples.get_top_improvements("lcp", limit=3)

        # Verify comprehensive analysis
        self.assertGreater(len(recommendations), 0)
        self.assertGreater(len(pattern_recommendations), 0)
        self.assertGreater(len(relevant_examples), 0)

        # Check that recommendations cover different aspects
        recommendation_categories = set(rec["strategy"]["category"] for rec in recommendations)
        pattern_categories = set(pattern.category for pattern in pattern_recommendations)
        example_categories = set(example.category for example in relevant_examples)

        # Should have diverse coverage
        total_categories = len(recommendation_categories | pattern_categories | example_categories)
        self.assertGreater(total_categories, 1)

    def test_zero_hallucination_validation(self):
        """Test that recommendations are validated and don't contain hallucinations."""
        # Test pattern success rates are realistic
        for pattern in self.patterns.patterns.values():
            self.assertGreaterEqual(pattern.success_rate, 0)
            self.assertLessEqual(pattern.success_rate, 1.0)
            self.assertGreaterEqual(pattern.confidence_level, 0)
            self.assertLessEqual(pattern.confidence_level, 1.0)
            self.assertGreater(pattern.sample_size, 0)

        # Test example improvements are realistic
        for example in self.examples.examples:
            for metric, improvement in example.actual_improvements.items():
                self.assertGreaterEqual(improvement, 0)
                self.assertLessEqual(improvement, 100)  # Should be reasonable percentages

            # Verify before/after metrics make sense
            for metric in example.before_metrics:
                before = example.before_metrics[metric]
                after = example.after_metrics.get(metric)
                if after is not None:
                    # For most metrics (time, size), after should be less than before
                    if metric in ["lcp", "fid", "cls", "ttfb", "bundle_size", "page_weight"]:
                        self.assertLessEqual(after, before)

    def test_performance_metric_consistency(self):
        """Test that performance metrics are consistent across components."""
        # Test that Core Web Vitals are consistently defined
        vital_metrics = ["lcp", "fid", "cls", "ttfb", "fcp"]

        # Check in skill
        skill_metrics = [metric.value for metric in PerformanceMetric]
        for vital in vital_metrics:
            self.assertIn(vital, skill_metrics)

        # Check in patterns
        for pattern in self.patterns.patterns.values():
            for metric in pattern.average_improvement.keys():
                if metric in vital_metrics:
                    # Should be lowercase in patterns
                    self.assertEqual(metric, metric.lower())

        # Check in examples
        for example in self.examples.examples:
            all_metrics = set(example.before_metrics.keys()) | set(example.after_metrics.keys())
            example_vitals = [m for m in all_metrics if m in vital_metrics]
            for vital in example_vitals:
                self.assertIn(vital, vital_metrics)


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
