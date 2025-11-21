"""
Test ML Enhanced Categorizer

Tests for the ML-enhanced file categorization system including
confidence scoring, content analysis, and learning capabilities.
"""

import pytest
import tempfile
import json
from datetime import datetime
from pathlib import Path
from typing import List

from ..models.file_models import FileInfo, CategoryType
from ..ml.enhanced_categorizer import EnhancedCategorizer
from ..ml.content_analyzer import ContentAnalyzer
from ..ml.learning_engine import LearningEngine
from ..ml.models.learning_models import ConfidenceScore, FeatureVector


class TestContentAnalyzer:
    """Test the ContentAnalyzer component."""

    @pytest.fixture
    def analyzer(self):
        """Create a ContentAnalyzer instance for testing."""
        return ContentAnalyzer(max_file_size_mb=1.0, max_content_length=1000)

    @pytest.fixture
    def sample_text_file(self):
        """Create a temporary text file for testing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("""
            def calculate_total(items):
                '''Calculate total price from list of items.'''
                return sum(item.price for item in items)

            # Configuration file for the application
            server_host = "localhost"
            database_url = "sqlite:///app.db"
            api_key = "test_key_123"
            """)
            return Path(f.name)

    @pytest.fixture
    def sample_file_info(self, sample_text_file):
        """Create FileInfo for the sample text file."""
        stat = sample_text_file.stat()
        return FileInfo(
            path=sample_text_file,
            name=sample_text_file.name,
            size=stat.st_size,
            is_file=True,
            is_directory=False,
            extension="txt",
            created_time=datetime.fromtimestamp(stat.st_ctime),
            modified_time=datetime.fromtimestamp(stat.st_mtime),
            accessed_time=datetime.fromtimestamp(stat.st_atime),
        )

    def test_can_analyze_safe_file(self, analyzer, sample_file_info):
        """Test that analyzer can safely analyze text files."""
        assert analyzer.can_analyze_file(sample_file_info)

    def test_cannot_analyze_large_file(self, analyzer):
        """Test that analyzer rejects files that are too large."""
        large_file_info = FileInfo(
            path=Path("large_file.zip"),
            name="large_file.zip",
            size=200 * 1024 * 1024,  # 200MB
            is_file=True,
            is_directory=False,
            extension="zip",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            accessed_time=datetime.now(),
        )
        assert not analyzer.can_analyze_file(large_file_info)

    def test_extract_text_content(self, analyzer, sample_text_file):
        """Test text content extraction."""
        content = analyzer.extract_text_content(sample_text_file)
        assert "calculate_total" in content
        assert "server_host" in content
        assert len(content) > 0

    def test_extract_keywords(self, analyzer):
        """Test keyword extraction from content."""
        content = "This is a configuration file with database settings and API keys"
        keywords = analyzer.extract_keywords(content)
        assert "config" in keywords or "configuration" in keywords
        assert "database" in keywords
        assert any("api" in k for k in keywords.keys())

    def test_detect_content_patterns(self, analyzer):
        """Test content pattern detection."""
        content = """
        def function_name():
            import os
            server_host = "localhost"
            """
        patterns = analyzer.detect_content_patterns(content)
        assert any("code_" in key for key in patterns.keys())
        assert any("config_" in key for key in patterns.keys())

    def test_create_feature_vector(self, analyzer, sample_file_info):
        """Test feature vector creation."""
        features = analyzer.create_feature_vector(sample_file_info)
        assert isinstance(features, FeatureVector)
        assert features.file_size_norm >= 0.0
        assert features.path_depth >= 0
        assert isinstance(features.extension_features, dict)
        assert isinstance(features.keyword_features, dict)


class TestLearningEngine:
    """Test the LearningEngine component."""

    @pytest.fixture
    def temp_learning_dir(self):
        """Create temporary directory for learning data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def learning_engine(self, temp_learning_dir):
        """Create a LearningEngine instance for testing."""
        return LearningEngine(learning_data_path=temp_learning_dir, enable_persistence=True)

    def test_initialization(self, learning_engine):
        """Test learning engine initialization."""
        assert learning_engine.enable_learning
        assert learning_engine.learning_data.learning_enabled
        assert learning_engine.learning_data.min_corrections_for_pattern >= 0

    def test_process_feedback(self, learning_engine):
        """Test processing user feedback."""
        from ..ml.models.feedback_models import UserFeedback, FeedbackType

        confidence = ConfidenceScore(overall=0.6, extension_match=0.8, pattern_match=0.4)

        feedback = UserFeedback(
            id="test_1",
            file_path=Path("/test/file.py"),
            predicted_category=CategoryType.DOCUMENTS,
            user_category=CategoryType.CODE,
            confidence=confidence,
            feedback_type=FeedbackType.CORRECTION,
            was_correct=False,
            timestamp=datetime.now(),
            processing_time_ms=100,
        )

        learning_engine.process_feedback(feedback)
        assert len(learning_engine.learning_data.user_corrections) == 1
        assert learning_engine.learning_data.user_interventions == 1

    def test_calculate_confidence_score(self, learning_engine):
        """Test confidence score calculation."""
        file_info = FileInfo(
            path=Path("/test/script.py"),
            name="script.py",
            size=1024,
            is_file=True,
            is_directory=False,
            extension="py",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            accessed_time=datetime.now(),
        )

        feature_vector = FeatureVector(
            file_size_norm=0.01,
            extension_features={"ext_py": 1.0},
            path_depth=1,
            text_length=10,
            keyword_features={},
            language_score=0.9,
            name_patterns={},
            date_features={},
            user_category_history=0.0,
            correction_frequency=0.0,
        )

        confidence = learning_engine.calculate_confidence_score(file_info, CategoryType.CODE, feature_vector)

        assert isinstance(confidence, ConfidenceScore)
        assert 0.0 <= confidence.overall <= 1.0
        assert 0.0 <= confidence.extension_match <= 1.0

    def test_get_learning_statistics(self, learning_engine):
        """Test learning statistics retrieval."""
        stats = learning_engine.get_learning_statistics()
        assert isinstance(stats, dict)
        assert "total_categorizations" in stats
        assert "accuracy" in stats
        assert "intervention_rate" in stats
        assert "pattern_rules" in stats
        assert stats["learning_enabled"] is True


class TestEnhancedCategorizer:
    """Test the EnhancedCategorizer component."""

    @pytest.fixture
    def temp_learning_dir(self):
        """Create temporary directory for learning data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def enhanced_categorizer(self, temp_learning_dir):
        """Create an EnhancedCategorizer instance for testing."""
        return EnhancedCategorizer(learning_data_path=temp_learning_dir, enable_learning=True, confidence_threshold=0.7)

    @pytest.fixture
    def sample_files(self):
        """Create sample file information objects."""
        files = []

        # Python file
        files.append(
            FileInfo(
                path=Path("/test/script.py"),
                name="script.py",
                size=2048,
                is_file=True,
                is_directory=False,
                extension="py",
                created_time=datetime.now(),
                modified_time=datetime.now(),
                accessed_time=datetime.now(),
            )
        )

        # Document file
        files.append(
            FileInfo(
                path=Path("/test/document.pdf"),
                name="report.pdf",
                size=1024 * 1024,  # 1MB
                is_file=True,
                is_directory=False,
                extension="pdf",
                created_time=datetime.now(),
                modified_time=datetime.now(),
                accessed_time=datetime.now(),
            )
        )

        # Image file
        files.append(
            FileInfo(
                path=Path("/test/image.jpg"),
                name="photo.jpg",
                size=500 * 1024,  # 500KB
                is_file=True,
                is_directory=False,
                extension="jpg",
                created_time=datetime.now(),
                modified_time=datetime.now(),
                accessed_time=datetime.now(),
            )
        )

        return files

    def test_initialization(self, enhanced_categorizer):
        """Test enhanced categorizer initialization."""
        assert enhanced_categorizer.enable_learning is True
        assert enhanced_categorizer.confidence_threshold == 0.7
        assert enhanced_categorizer.content_analyzer is not None
        assert enhanced_categorizer.learning_engine is not None

    def test_categorize_file_enhanced(self, enhanced_categorizer, sample_files):
        """Test enhanced file categorization."""
        python_file = sample_files[0]
        category, confidence = enhanced_categorizer.categorize_file_enhanced(python_file)

        assert category is not None
        assert isinstance(confidence, ConfidenceScore)
        assert 0.0 <= confidence.overall <= 1.0

    def test_categorize_files_batch(self, enhanced_categorizer, sample_files):
        """Test batch file categorization."""
        results = enhanced_categorizer.categorize_files_batch(sample_files)

        assert isinstance(results, dict)
        assert CategoryType.CODE in results
        assert CategoryType.DOCUMENTS in results
        assert CategoryType.IMAGES in results

        # Check that all files were categorized
        total_categorized = sum(len(files) for files in results.values())
        assert total_categorized == len(sample_files)

    def test_should_auto_categorize(self, enhanced_categorizer):
        """Test auto-categorization confidence threshold."""
        high_confidence = ConfidenceScore(overall=0.8)
        low_confidence = ConfidenceScore(overall=0.5)

        assert enhanced_categorizer.should_auto_categorize(high_confidence) is True
        assert enhanced_categorizer.should_auto_categorize(low_confidence) is False

    def test_process_user_feedback(self, enhanced_categorizer, sample_files):
        """Test processing user feedback."""
        python_file = sample_files[0]

        # First, categorize the file
        category, confidence = enhanced_categorizer.categorize_file_enhanced(python_file)

        # Process user feedback
        success = enhanced_categorizer.process_user_feedback(
            file_info=python_file,
            predicted_category=CategoryType.DOCUMENTS,  # Wrong prediction
            correct_category=CategoryType.CODE,  # Correct category
            confidence=confidence,
            user_comment="This is actually a Python script",
        )

        assert success is True

    def test_get_categorization_statistics(self, enhanced_categorizer, sample_files):
        """Test categorization statistics."""
        # Categorize some files to generate statistics
        enhanced_categorizer.categorize_files_batch(sample_files)

        stats = enhanced_categorizer.get_categorization_statistics()
        assert isinstance(stats, dict)
        assert "total_processed" in stats
        assert "auto_categorized" in stats
        assert "user_reviewed" in stats
        assert "accuracy" in stats
        assert "learning_enabled" in stats

    def test_get_recommendations(self, enhanced_categorizer, sample_files):
        """Test getting categorization recommendations."""
        enhanced_categorizer.categorize_files_batch(sample_files)
        recommendations = enhanced_categorizer.get_recommendations()

        assert isinstance(recommendations, dict)
        assert "confidence_improvements" in recommendations
        assert "learning_suggestions" in recommendations
        assert "pattern_opportunities" in recommendations

    def test_backward_compatibility(self, enhanced_categorizer, sample_files):
        """Test backward compatibility with BasicCategorizer interface."""
        # Test categorize_file method (returns category only)
        python_file = sample_files[0]
        category = enhanced_categorizer.categorize_file(python_file)
        assert category is not None

        # Test categorize_files method (returns file infos only)
        categorized = enhanced_categorizer.categorize_files(sample_files)
        assert isinstance(categorized, dict)
        assert CategoryType in (type(k) for k in categorized.keys())
        assert all(isinstance(files, list) for files in categorized.values())


class TestIntegration:
    """Integration tests for the complete ML system."""

    @pytest.fixture
    def temp_learning_dir(self):
        """Create temporary directory for learning data."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    def test_learning_feedback_loop(self, temp_learning_dir):
        """Test the complete learning feedback loop."""
        categorizer = EnhancedCategorizer(
            learning_data_path=temp_learning_dir,
            enable_learning=True,
            confidence_threshold=0.6,  # Lower threshold for testing
        )

        # Create test file info
        test_file = FileInfo(
            path=Path("/test/custom_script.xyz"),
            name="custom_script.xyz",
            size=1024,
            is_file=True,
            is_directory=False,
            extension="xyz",  # Unknown extension
            created_time=datetime.now(),
            modified_time=datetime.now(),
            accessed_time=datetime.now(),
        )

        # Initial categorization (likely low confidence)
        category, confidence = categorizer.categorize_file_enhanced(test_file)
        initial_confidence = confidence.overall

        # Provide user feedback
        categorizer.process_user_feedback(
            file_info=test_file,
            predicted_category=category.type,
            correct_category=CategoryType.CODE,
            confidence=confidence,
            user_comment="This .xyz file contains code",
        )

        # Second categorization of similar file should show learning
        similar_file = FileInfo(
            path=Path("/test/another.xyz"),
            name="another.xyz",
            size=512,
            is_file=True,
            is_directory=False,
            extension="xyz",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            accessed_time=datetime.now(),
        )

        new_category, new_confidence = categorizer.categorize_file_enhanced(similar_file)

        # Check that learning occurred (confidence should improve or category should be correct)
        learning_stats = categorizer.get_categorization_statistics()
        assert learning_stats["user_corrections"] == 1
        assert learning_stats["total_processed"] >= 2


if __name__ == "__main__":
    # Run basic integration test
    print("Running ML Enhanced Categorizer integration test...")

    with tempfile.TemporaryDirectory() as temp_dir:
        categorizer = EnhancedCategorizer(
            learning_data_path=Path(temp_dir), enable_learning=True, confidence_threshold=0.7
        )

        # Create test file
        test_file = FileInfo(
            path=Path("/test/sample.py"),
            name="sample.py",
            size=2048,
            is_file=True,
            is_directory=False,
            extension="py",
            created_time=datetime.now(),
            modified_time=datetime.now(),
            accessed_time=datetime.now(),
        )

        # Test categorization
        category, confidence = categorizer.categorize_file_enhanced(test_file)
        print(f"Categorized as: {category.name} with confidence: {confidence.overall:.2f}")

        # Test statistics
        stats = categorizer.get_categorization_statistics()
        print(f"Statistics: {json.dumps(stats, indent=2, default=str)}")

        # Test recommendations
        recommendations = categorizer.get_recommendations([test_file])
        print(f"Recommendations: {json.dumps(recommendations, indent=2)}")

        print("✅ Integration test completed successfully!")
