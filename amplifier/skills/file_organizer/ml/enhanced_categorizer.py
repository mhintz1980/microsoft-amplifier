"""
Enhanced Categorizer Module

ML-enhanced file categorizer with confidence scoring, content analysis,
and learning from user feedback. Integrates with the basic categorizer
while adding intelligent categorization capabilities.
"""

import logging
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

from ..core.categorizer import BasicCategorizer
from ..models.file_models import FileInfo, Category, CategoryType
from .content_analyzer import ContentAnalyzer
from .learning_engine import LearningEngine
from .models.learning_models import ConfidenceScore, FeatureVector
from .models.feedback_models import UserFeedback, FeedbackType

logger = logging.getLogger(__name__)


class EnhancedCategorizer:
    """
    ML-enhanced file categorizer that combines rule-based categorization
    with machine learning for improved accuracy and confidence scoring.

    Features:
    - Confidence-based categorization with multiple algorithms
    - Content analysis for intelligent categorization
    - Learning from user corrections and feedback
    - Pattern recognition and rule generation
    - Performance monitoring and adaptation
    - Integration with existing BasicCategorizer
    """

    def __init__(
        self,
        learning_data_path: Optional[Path] = None,
        enable_learning: bool = True,
        confidence_threshold: float = 0.7,
        max_file_size_mb: float = 50.0,
    ):
        """
        Initialize the enhanced categorizer.

        Args:
            learning_data_path: Path to store learning data
            enable_learning: Whether to enable ML learning
            confidence_threshold: Minimum confidence for auto-categorization
            max_file_size_mb: Maximum file size for content analysis
        """
        # Initialize basic categorizer for rule-based matching
        self.basic_categorizer = BasicCategorizer()

        # Initialize ML components
        self.content_analyzer = ContentAnalyzer(max_file_size_mb=max_file_size_mb)
        self.learning_engine = (
            LearningEngine(learning_data_path=learning_data_path, enable_persistence=enable_learning)
            if enable_learning
            else None
        )

        # Configuration
        self.enable_learning = enable_learning
        self.confidence_threshold = confidence_threshold

        # Performance tracking
        self._categorization_stats = {
            "total_processed": 0,
            "auto_categorized": 0,
            "user_reviewed": 0,
            "content_analyzed": 0,
            "avg_processing_time_ms": 0,
        }

        logger.info(
            f"Enhanced categorizer initialized (learning: {enable_learning}, confidence_threshold: {confidence_threshold})"
        )

    def categorize_file_enhanced(self, file_info: FileInfo) -> Tuple[Category, ConfidenceScore]:
        """
        Categorize a file with ML enhancement and confidence scoring.

        Args:
            file_info: File information object

        Returns:
            Tuple of (category, confidence_score)
        """
        start_time = time.time()

        try:
            # Get basic rule-based categorization first
            basic_category = self.basic_categorizer.categorize_file(file_info)

            # Extract features for ML analysis
            feature_vector = self.content_analyzer.create_feature_vector(file_info)

            # Use ML to predict category with confidence scoring
            predicted_category, confidence = self._predict_with_ml(file_info, basic_category, feature_vector)

            # If ML is disabled or has low confidence, use basic categorization
            if not self.enable_learning or confidence.overall < self.confidence_threshold:
                confidence = self._calculate_basic_confidence(file_info, basic_category, feature_vector)
                predicted_category = basic_category

            # Update statistics
            processing_time_ms = int((time.time() - start_time) * 1000)
            self._update_statistics(processing_time_ms, confidence.overall >= self.confidence_threshold)

            # Get the actual category object
            category = self.basic_categorizer.get_category(predicted_category) or basic_category

            return category, confidence

        except Exception as e:
            logger.error(f"Enhanced categorization failed for {file_info.path}: {e}")
            # Fallback to basic categorization
            basic_category = self.basic_categorizer.categorize_file(file_info)
            fallback_confidence = ConfidenceScore(overall=0.5, extension_match=0.8)
            return basic_category, fallback_confidence

    def _predict_with_ml(
        self, file_info: FileInfo, basic_category: Category, feature_vector: FeatureVector
    ) -> Tuple[CategoryType, ConfidenceScore]:
        """
        Use ML to predict category and calculate confidence.

        Args:
            file_info: File information
            basic_category: Rule-based categorization result
            feature_vector: Extracted features

        Returns:
            Tuple of (predicted_category, confidence_score)
        """
        if not self.learning_engine:
            # Fallback to basic category with moderate confidence
            return basic_category.type, ConfidenceScore(overall=0.6, extension_match=0.8)

        # Calculate confidence score using learning engine
        confidence = self.learning_engine.calculate_confidence_score(file_info, basic_category.type, feature_vector)

        # If high confidence, use ML prediction
        if confidence.overall >= self.confidence_threshold:
            return basic_category.type, confidence

        # For medium confidence, consider learned patterns
        learned_category = self._apply_learned_patterns(file_info, feature_vector)
        if learned_category:
            # Recalculate confidence for learned category
            learned_confidence = self.learning_engine.calculate_confidence_score(
                file_info, learned_category, feature_vector
            )
            return learned_category, learned_confidence

        # Default to basic categorization
        return basic_category.type, confidence

    def _apply_learned_patterns(self, file_info: FileInfo, feature_vector: FeatureVector) -> Optional[CategoryType]:
        """
        Apply learned patterns to improve categorization.

        Args:
            file_info: File information
            feature_vector: Extracted features

        Returns:
            Category type if patterns match, None otherwise
        """
        if not self.learning_engine:
            return None

        # Check extension-based patterns
        if file_info.extension:
            ext_lower = file_info.extension.lower()
            for category_type in CategoryType:
                if category_type == CategoryType.UNKNOWN:
                    continue

                patterns = self.learning_engine.learning_data.get_reliable_patterns(category_type)
                for pattern in patterns:
                    if (
                        pattern.pattern_type.value == "extension_pattern"
                        and pattern.rule_value == ext_lower
                        and pattern.is_reliable
                    ):
                        return category_type

        # Check name-based patterns
        file_name = file_info.name.lower()
        for category_type in CategoryType:
            if category_type == CategoryType.UNKNOWN:
                continue

            patterns = self.learning_engine.learning_data.get_reliable_patterns(category_type)
            for pattern in patterns:
                if pattern.pattern_type.value == "name_pattern":
                    import fnmatch

                    if fnmatch.fnmatch(file_name, pattern.rule_value):
                        return category_type

        return None

    def _calculate_basic_confidence(
        self, file_info: FileInfo, category: Category, feature_vector: FeatureVector
    ) -> ConfidenceScore:
        """
        Calculate confidence score for basic rule-based categorization.

        Args:
            file_info: File information
            category: Categorization result
            feature_vector: Extracted features

        Returns:
            Confidence score for basic categorization
        """
        # Extension-based confidence
        extension_confidence = 0.0
        if file_info.extension and category.extensions:
            ext_lower = file_info.extension.lower().lstrip(".")
            if ext_lower in [ext.lower().lstrip(".") for ext in category.extensions]:
                extension_confidence = 0.9

        # Pattern-based confidence
        pattern_confidence = 0.0
        if category.patterns:
            import fnmatch

            for pattern in category.patterns:
                if fnmatch.fnmatch(file_info.name.lower(), pattern.lower()):
                    pattern_confidence = 0.8
                    break

        # Content-based confidence
        content_confidence = min(feature_vector.language_score * 1.5, 1.0)

        # Overall confidence
        weights = {"extension": 0.5, "pattern": 0.3, "content": 0.2}
        overall = (
            extension_confidence * weights["extension"]
            + pattern_confidence * weights["pattern"]
            + content_confidence * weights["content"]
        )

        return ConfidenceScore(
            overall=overall,
            extension_match=extension_confidence,
            pattern_match=pattern_confidence,
            content_match=content_confidence,
        )

    def categorize_files_batch(
        self, file_infos: List[FileInfo]
    ) -> Dict[CategoryType, List[Tuple[FileInfo, ConfidenceScore]]]:
        """
        Categorize multiple files with ML enhancement.

        Args:
            file_infos: List of file information objects

        Returns:
            Dictionary mapping category types to lists of (file_info, confidence) tuples
        """
        categorized = {category_type: [] for category_type in CategoryType}

        logger.info(f"Processing batch of {len(file_infos)} files with enhanced categorization")

        for file_info in file_infos:
            try:
                category, confidence = self.categorize_file_enhanced(file_info)
                categorized[category.type].append((file_info, confidence))
            except Exception as e:
                logger.error(f"Failed to categorize {file_info.path}: {e}")
                # Add to unknown category with low confidence
                unknown_confidence = ConfidenceScore(overall=0.1)
                categorized[CategoryType.UNKNOWN].append((file_info, unknown_confidence))

        # Log batch statistics
        total_auto = sum(
            1 for files in categorized.values() for _, conf in files if conf.overall >= self.confidence_threshold
        )
        logger.info(
            f"Batch complete: {total_auto}/{len(file_infos)} files auto-categorized ({total_auto / len(file_infos) * 100:.1f}%)"
        )

        return categorized

    def process_user_feedback(
        self,
        file_info: FileInfo,
        predicted_category: CategoryType,
        correct_category: CategoryType,
        confidence: ConfidenceScore,
        user_comment: Optional[str] = None,
    ) -> bool:
        """
        Process user feedback to improve ML learning.

        Args:
            file_info: File that was categorized
            predicted_category: ML-predicted category
            correct_category: User-corrected category
            confidence: Original confidence score
            user_comment: Optional user comment

        Returns:
            True if feedback processed successfully, False otherwise
        """
        if not self.learning_engine:
            logger.warning("Learning engine disabled - feedback not processed")
            return False

        try:
            # Create feedback object
            feedback = UserFeedback(
                id=str(time.time()),  # Simple timestamp-based ID
                file_path=file_info.path,
                predicted_category=predicted_category,
                user_category=correct_category,
                confidence=confidence,
                feedback_type=FeedbackType.CORRECTION
                if predicted_category != correct_category
                else FeedbackType.CONFIRMATION,
                user_comment=user_comment,
                was_correct=(predicted_category == correct_category),
                timestamp=datetime.now(),
                processing_time_ms=0,  # Not applicable for feedback
            )

            # Process feedback in learning engine
            self.learning_engine.process_feedback(feedback)

            logger.info(f"Processed user feedback for {file_info.path}: {predicted_category} -> {correct_category}")
            return True

        except Exception as e:
            logger.error(f"Failed to process user feedback: {e}")
            return False

    def should_auto_categorize(self, confidence: ConfidenceScore) -> bool:
        """
        Determine if file should be auto-categorized based on confidence.

        Args:
            confidence: Confidence score for categorization

        Returns:
            True if should auto-categorize, False if user review needed
        """
        return confidence.overall >= self.confidence_threshold

    def get_categorization_statistics(self) -> Dict[str, Union[int, float, str]]:
        """
        Get comprehensive categorization statistics.

        Returns:
            Dictionary with categorization statistics
        """
        stats = self._categorization_stats.copy()

        # Add learning engine statistics
        if self.learning_engine:
            learning_stats = self.learning_engine.get_learning_statistics()
            stats.update(learning_stats)

        # Add calculated rates
        if stats["total_processed"] > 0:
            stats["auto_categorization_rate"] = stats["auto_categorized"] / stats["total_processed"]
            stats["user_review_rate"] = stats["user_reviewed"] / stats["total_processed"]
        else:
            stats["auto_categorization_rate"] = 0.0
            stats["user_review_rate"] = 0.0

        stats["confidence_threshold"] = self.confidence_threshold
        stats["learning_enabled"] = self.enable_learning

        return stats

    def _update_statistics(self, processing_time_ms: int, auto_categorized: bool) -> None:
        """Update internal categorization statistics."""
        self._categorization_stats["total_processed"] += 1

        if auto_categorized:
            self._categorization_stats["auto_categorized"] += 1
        else:
            self._categorization_stats["user_reviewed"] += 1

        # Update average processing time
        current_avg = self._categorization_stats["avg_processing_time_ms"]
        total = self._categorization_stats["total_processed"]
        self._categorization_stats["avg_processing_time_ms"] = (current_avg * (total - 1) + processing_time_ms) / total

    def get_recommendations(self, file_infos: List[FileInfo]) -> Dict[str, List[str]]:
        """
        Get categorization recommendations and improvements.

        Args:
            file_infos: Files to analyze

        Returns:
            Dictionary with recommendations
        """
        recommendations = {"confidence_improvements": [], "learning_suggestions": [], "pattern_opportunities": []}

        # Analyze confidence scores
        categorized = self.categorize_files_batch(file_infos)

        low_confidence_files = []
        for category_type, files in categorized.items():
            for file_info, confidence in files:
                if confidence.overall < 0.6:
                    low_confidence_files.append((file_info, confidence))

        if low_confidence_files:
            recommendations["confidence_improvements"].append(
                f"Found {len(low_confidence_files)} files with low confidence (<60%)"
            )

            # Suggest specific improvements
            extension_issues = {}
            for file_info, _ in low_confidence_files:
                if file_info.extension:
                    ext = file_info.extension.lower()
                    extension_issues[ext] = extension_issues.get(ext, 0) + 1

            for ext, count in extension_issues.items():
                if count >= 3:  # Threshold for recommendation
                    recommendations["learning_suggestions"].append(
                        f"Consider providing feedback for {count} '.{ext}' files to improve categorization"
                    )

        # Learning suggestions
        if self.learning_engine and self.enable_learning:
            learning_stats = self.learning_engine.get_learning_statistics()
            if learning_stats["intervention_rate"] > 0.3:
                recommendations["learning_suggestions"].append(
                    f"High intervention rate ({learning_stats['intervention_rate']:.1%}) - more user feedback needed"
                )

            if learning_stats["pattern_rules"] < 10:
                recommendations["pattern_opportunities"].append(
                    "Provide more user corrections to generate learned patterns"
                )

        return recommendations

    def export_learning_data(self, export_path: Path) -> bool:
        """
        Export learning data for backup or analysis.

        Args:
            export_path: Path to export learning data

        Returns:
            True if export successful, False otherwise
        """
        if not self.learning_engine:
            logger.warning("Learning engine disabled - no data to export")
            return False

        return self.learning_engine.export_learning_data(export_path)

    def cleanup_old_data(self, days_to_keep: int = 90) -> None:
        """
        Clean up old learning data to manage storage space.

        Args:
            days_to_keep: Number of days of data to keep
        """
        if self.learning_engine:
            self.learning_engine.cleanup_old_data(days_to_keep)
        else:
            logger.warning("Learning engine disabled - no cleanup needed")

    def categorize_with_confidence(self, file_info: FileInfo) -> Tuple[Category, ConfidenceScore]:
        """
        Categorize a file with confidence scoring.

        This is the main interface for ML-enhanced categorization with confidence scoring.

        Args:
            file_info: File information object

        Returns:
            Tuple of (category, confidence_score) for the file
        """
        return self.categorize_file_enhanced(file_info)

    # Compatibility methods with BasicCategorizer
    def categorize_file(self, file_info: FileInfo) -> Category:
        """Compatibility method - returns category only (no confidence)."""
        category, _ = self.categorize_file_enhanced(file_info)
        return category

    def categorize_files(self, file_infos: List[FileInfo]) -> Dict[CategoryType, List[FileInfo]]:
        """Compatibility method - returns file infos only (no confidence)."""
        enhanced_results = self.categorize_files_batch(file_infos)
        basic_results = {category_type: [] for category_type in CategoryType}

        for category_type, files_with_confidence in enhanced_results.items():
            basic_results[category_type] = [file_info for file_info, _ in files_with_confidence]

        return basic_results

    def get_category(self, category_type: CategoryType) -> Optional[Category]:
        """Get category from basic categorizer."""
        return self.basic_categorizer.get_category(category_type)

    def get_all_categories(self) -> List[Category]:
        """Get all categories from basic categorizer."""
        return self.basic_categorizer.get_all_categories()
