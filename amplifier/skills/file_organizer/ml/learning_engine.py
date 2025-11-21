"""
Learning Engine Module

Machine learning engine for learning from user feedback and improving
categorization accuracy over time. Implements pattern recognition,
confidence calculation, and adaptive rule generation.
"""

import json
import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
import uuid
import hashlib

from ..models.file_models import FileInfo, CategoryType
from .models.learning_models import (
    LearningData,
    PatternRule,
    UserCorrection,
    ConfidenceScore,
    FeatureVector,
    PatternType,
)
from .models.feedback_models import UserFeedback, FeedbackType, LearningSession, ModelPerformance, BatchLearningResult

logger = logging.getLogger(__name__)


class LearningEngine:
    """
    Machine learning engine that learns from user feedback to improve
    file categorization accuracy.

    Features:
    - Pattern learning from user corrections
    - Confidence score calculation
    - User behavior tracking
    - Persistent learning data storage
    - Performance monitoring and adaptation
    """

    def __init__(
        self,
        learning_data_path: Optional[Union[str, Path]] = None,
        enable_persistence: bool = True,
        min_corrections_for_pattern: int = 3,
    ):
        """
        Initialize the learning engine.

        Args:
            learning_data_path: Path to store learning data (str or Path)
            enable_persistence: Whether to persist learning data
            min_corrections_for_pattern: Minimum corrections needed to create patterns
        """
        # Initialize attributes first
        self.min_corrections_for_pattern = min_corrections_for_pattern
        self.db_path = None

        # Handle both string and Path inputs
        if isinstance(learning_data_path, str):
            if learning_data_path == ":memory:":
                self.db_path = ":memory:"
                self.learning_data_path = Path.home() / ".amplifier" / "file_organizer_learning"
                self.enable_persistence = False  # Can't persist with :memory:
            else:
                self.learning_data_path = Path(learning_data_path)
                self.enable_persistence = enable_persistence
        else:
            self.learning_data_path = learning_data_path or Path.home() / ".amplifier" / "file_organizer_learning"
            self.enable_persistence = enable_persistence

        # Initialize learning data
        self.learning_data = LearningData()

        # Database connection for persistence
        if self.db_path != ":memory:":
            self.db_path = self.learning_data_path / "learning_data.db"

        # Ensure learning directory exists
        if self.enable_persistence:
            self.learning_data_path.mkdir(parents=True, exist_ok=True)
            self._init_database()
            self._load_learning_data()

    def _init_database(self) -> None:
        """Initialize SQLite database for learning data persistence."""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("""
                    CREATE TABLE IF NOT EXISTS user_corrections (
                        id TEXT PRIMARY KEY,
                        file_path TEXT NOT NULL,
                        predicted_category TEXT NOT NULL,
                        correct_category TEXT NOT NULL,
                        original_confidence TEXT NOT NULL,
                        correction_reason TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS pattern_rules (
                        id TEXT PRIMARY KEY,
                        pattern_type TEXT NOT NULL,
                        category_type TEXT NOT NULL,
                        rule_value TEXT NOT NULL,
                        confidence_weight REAL NOT NULL,
                        success_rate REAL NOT NULL,
                        usage_count INTEGER NOT NULL,
                        correction_count INTEGER NOT NULL,
                        created_at TEXT NOT NULL,
                        last_used TEXT
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS performance_metrics (
                        timestamp TEXT PRIMARY KEY,
                        accuracy REAL NOT NULL,
                        precision TEXT NOT NULL,
                        recall TEXT NOT NULL,
                        user_satisfaction_rate REAL NOT NULL,
                        correction_rate REAL NOT NULL
                    )
                """)

                conn.execute("""
                    CREATE TABLE IF NOT EXISTS learning_sessions (
                        session_id TEXT PRIMARY KEY,
                        start_time TEXT NOT NULL,
                        end_time TEXT,
                        files_processed INTEGER NOT NULL,
                        feedback_items TEXT NOT NULL,
                        performance_metrics TEXT NOT NULL
                    )
                """)

                conn.commit()

        except Exception as e:
            logger.warning(f"Failed to initialize learning database: {e}")
            self.enable_persistence = False

    def _load_learning_data(self) -> None:
        """Load learning data from persistent storage."""
        if not self.enable_persistence:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                # Load pattern rules
                cursor = conn.execute("SELECT * FROM pattern_rules")
                for row in cursor.fetchall():
                    pattern_rule = PatternRule(
                        id=row[0],
                        pattern_type=PatternType(row[1]),
                        category_type=CategoryType(row[2]),
                        rule_value=row[3],
                        confidence_weight=row[4],
                        success_rate=row[5],
                        usage_count=row[6],
                        correction_count=row[7],
                        created_at=datetime.fromisoformat(row[8]),
                        last_used=datetime.fromisoformat(row[9]) if row[9] else None,
                    )
                    self.learning_data.add_pattern_rule(pattern_rule)

                # Load user corrections (only recent ones to manage memory)
                cutoff_date = datetime.now() - timedelta(days=30)
                cursor = conn.execute("SELECT * FROM user_corrections WHERE timestamp >= ?", (cutoff_date.isoformat(),))
                for row in cursor.fetchall():
                    confidence_data = json.loads(row[3])
                    correction = UserCorrection(
                        id=row[0],
                        file_path=Path(row[1]),
                        predicted_category=CategoryType(row[2]),
                        correct_category=CategoryType(row[3]),
                        original_confidence=ConfidenceScore(**confidence_data),
                        correction_reason=row[4],
                        timestamp=datetime.fromisoformat(row[5]),
                    )
                    self.learning_data.add_correction(correction)

                # Update counters
                cursor = conn.execute("SELECT COUNT(*) FROM user_corrections")
                self.learning_data.user_interventions = cursor.fetchone()[0]

                cursor = conn.execute(
                    "SELECT COUNT(*) FROM user_corrections WHERE predicted_category != correct_category"
                )
                incorrect_predictions = cursor.fetchone()[0]

                cursor = conn.execute("SELECT COUNT(*) FROM user_corrections")
                total_corrections = cursor.fetchone()[0]

                # Estimate total categorizations (this is approximate)
                self.learning_data.total_categorizations = total_corrections * 5  # Assume 80% accuracy
                self.learning_data.correct_predictions = (
                    self.learning_data.total_categorizations - incorrect_predictions
                )

        except Exception as e:
            logger.warning(f"Failed to load learning data: {e}")

    def _save_correction(self, correction: UserCorrection) -> None:
        """Save a user correction to persistent storage."""
        if not self.enable_persistence:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO user_corrections
                    (id, file_path, predicted_category, correct_category,
                     original_confidence, correction_reason, timestamp)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        correction.id,
                        str(correction.file_path),
                        correction.predicted_category.value,
                        correction.correct_category.value,
                        correction.original_confidence.model_dump_json(),
                        correction.correction_reason,
                        correction.timestamp.isoformat(),
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.warning(f"Failed to save correction: {e}")

    def _save_pattern_rule(self, rule: PatternRule) -> None:
        """Save a pattern rule to persistent storage."""
        if not self.enable_persistence:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute(
                    """
                    INSERT OR REPLACE INTO pattern_rules
                    (id, pattern_type, category_type, rule_value,
                     confidence_weight, success_rate, usage_count,
                     correction_count, created_at, last_used)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                    (
                        rule.id,
                        rule.pattern_type.value,
                        rule.category_type.value,
                        rule.rule_value,
                        rule.confidence_weight,
                        rule.success_rate,
                        rule.usage_count,
                        rule.correction_count,
                        rule.created_at.isoformat(),
                        rule.last_used.isoformat() if rule.last_used else None,
                    ),
                )
                conn.commit()

        except Exception as e:
            logger.warning(f"Failed to save pattern rule: {e}")

    def process_feedback(self, feedback: UserFeedback) -> None:
        """
        Process user feedback and update learning data.

        Args:
            feedback: User feedback on categorization
        """
        if feedback.feedback_type == FeedbackType.CORRECTION:
            correction = UserCorrection(
                id=str(uuid.uuid4()),
                file_path=feedback.file_path,
                predicted_category=feedback.predicted_category,
                correct_category=feedback.user_category or feedback.predicted_category,
                original_confidence=feedback.confidence,
                correction_reason=feedback.user_comment,
                timestamp=feedback.timestamp,
            )

            self.learning_data.add_correction(correction)
            self._save_correction(correction)

            # Learn patterns from correction
            self._learn_from_correction(correction)

        # Update performance metrics
        self.learning_data.total_categorizations += 1
        if feedback.was_correct:
            self.learning_data.correct_predictions += 1

    def _learn_from_correction(self, correction: UserCorrection) -> None:
        """
        Learn patterns from a user correction.

        Args:
            correction: User correction to learn from
        """
        try:
            file_path = correction.file_path
            file_name = file_path.name.lower()
            file_ext = file_path.suffix.lower().lstrip(".")

            # Learn extension-based patterns
            if file_ext:
                extension_pattern_id = f"ext_{file_ext}_{correction.correct_category.value}"
                existing_rule = self.learning_data.pattern_rules.get(extension_pattern_id)

                if existing_rule:
                    # Update existing rule
                    existing_rule.update_success(was_correct=False)
                else:
                    # Create new extension rule
                    new_rule = PatternRule(
                        id=extension_pattern_id,
                        pattern_type=PatternType.EXTENSION_PATTERN,
                        category_type=correction.correct_category,
                        rule_value=file_ext,
                        confidence_weight=0.8,
                        success_rate=0.7,  # Start with moderate confidence
                        usage_count=1,
                        correction_count=1,
                        created_at=datetime.now(),
                    )
                    self.learning_data.add_pattern_rule(new_rule)
                    self._save_pattern_rule(new_rule)

            # Learn name-based patterns
            name_patterns = self._extract_name_patterns(file_name)
            for pattern in name_patterns:
                pattern_id = f"name_{hashlib.md5(pattern.encode()).hexdigest()[:8]}_{correction.correct_category.value}"
                existing_rule = self.learning_data.pattern_rules.get(pattern_id)

                if existing_rule:
                    existing_rule.update_success(was_correct=False)
                else:
                    new_rule = PatternRule(
                        id=pattern_id,
                        pattern_type=PatternType.NAME_PATTERN,
                        category_type=correction.correct_category,
                        rule_value=pattern,
                        confidence_weight=0.6,
                        success_rate=0.7,
                        usage_count=1,
                        correction_count=1,
                        created_at=datetime.now(),
                    )
                    self.learning_data.add_pattern_rule(new_rule)
                    self._save_pattern_rule(new_rule)

        except Exception as e:
            logger.warning(f"Failed to learn from correction: {e}")

    def _extract_name_patterns(self, file_name: str) -> List[str]:
        """
        Extract meaningful patterns from file names.

        Args:
            file_name: Lowercase file name

        Returns:
            List of pattern strings
        """
        patterns = []

        # Extract common prefixes/suffixes
        if file_name.startswith("temp") or file_name.startswith("tmp"):
            patterns.append("temp_*")

        if file_name.startswith("backup") or "copy" in file_name:
            patterns.append("backup_*")

        if "readme" in file_name:
            patterns.append("*readme*")

        if "config" in file_name or "setting" in file_name:
            patterns.append("*config*")

        # Extract date patterns
        import re

        date_matches = re.findall(r"\d{4}", file_name)
        if date_matches:
            patterns.append("*_YYYY_*")

        # Extract version patterns
        version_matches = re.findall(r"v?\d+\.\d+", file_name)
        if version_matches:
            patterns.append("*_vX.Y_*")

        return patterns

    def calculate_confidence_score(
        self, file_info: FileInfo, predicted_category: CategoryType, feature_vector: FeatureVector
    ) -> ConfidenceScore:
        """
        Calculate confidence score for categorization prediction.

        Args:
            file_info: File information
            predicted_category: ML-predicted category
            feature_vector: Extracted features

        Returns:
            Confidence score with breakdown
        """
        # Extension-based confidence
        extension_confidence = self._calculate_extension_confidence(file_info, predicted_category)

        # Pattern-based confidence
        pattern_confidence = self._calculate_pattern_confidence(file_info, predicted_category)

        # Content-based confidence
        content_confidence = self._calculate_content_confidence(feature_vector, predicted_category)

        # User behavior confidence
        behavior_confidence = self._calculate_behavior_confidence(file_info, predicted_category)

        # ML model confidence (placeholder for now)
        ml_confidence = 0.7  # Would be calculated by actual ML model

        # Combine confidences with weights
        weights = {"extension": 0.3, "pattern": 0.25, "content": 0.2, "behavior": 0.15, "ml": 0.1}

        overall = (
            extension_confidence * weights["extension"]
            + pattern_confidence * weights["pattern"]
            + content_confidence * weights["content"]
            + behavior_confidence * weights["behavior"]
            + ml_confidence * weights["ml"]
        )

        return ConfidenceScore(
            overall=min(overall, 1.0),
            extension_match=extension_confidence,
            pattern_match=pattern_confidence,
            content_match=content_confidence,
            user_behavior=behavior_confidence,
            ml_prediction=ml_confidence,
        )

    def _calculate_extension_confidence(self, file_info: FileInfo, predicted_category: CategoryType) -> float:
        """Calculate extension-based confidence."""
        if not file_info.extension:
            return 0.0

        # Look for extension patterns for this category
        patterns = self.learning_data.get_reliable_patterns(predicted_category)
        ext_lower = file_info.extension.lower()

        for pattern in patterns:
            if pattern.pattern_type == PatternType.EXTENSION_PATTERN:
                if pattern.rule_value == ext_lower:
                    return pattern.success_rate

        # Default confidence based on known mappings
        extension_mappings = {
            CategoryType.CODE: ["py", "js", "ts", "html", "css", "java", "cpp", "c"],
            CategoryType.DOCUMENTS: ["pdf", "doc", "docx", "txt", "md", "rtf"],
            CategoryType.IMAGES: ["jpg", "jpeg", "png", "gif", "bmp", "svg"],
            CategoryType.VIDEOS: ["mp4", "avi", "mkv", "mov", "wmv"],
            CategoryType.AUDIO: ["mp3", "wav", "flac", "aac", "ogg"],
            CategoryType.ARCHIVES: ["zip", "rar", "7z", "tar", "gz"],
        }

        if ext_lower in extension_mappings.get(predicted_category, []):
            return 0.9

        return 0.0

    def _calculate_pattern_confidence(self, file_info: FileInfo, predicted_category: CategoryType) -> float:
        """Calculate pattern-based confidence."""
        patterns = self.learning_data.get_reliable_patterns(predicted_category)
        file_name = file_info.name.lower()

        max_confidence = 0.0
        for pattern in patterns:
            if pattern.pattern_type == PatternType.NAME_PATTERN:
                # Simple pattern matching
                import fnmatch

                if fnmatch.fnmatch(file_name, pattern.rule_value):
                    max_confidence = max(max_confidence, pattern.success_rate)

        return max_confidence

    def _calculate_content_confidence(self, feature_vector: FeatureVector, predicted_category: CategoryType) -> float:
        """Calculate content-based confidence."""
        confidence = 0.0

        # Language score for code files
        if predicted_category == CategoryType.CODE:
            confidence = max(confidence, feature_vector.language_score)

        # Keyword matching
        category_keywords = {
            CategoryType.DOCUMENTS: ["contract", "report", "invoice", "documentation"],
            CategoryType.CODE: ["function", "class", "import", "variable"],
            CategoryType.SYSTEM: ["config", "setting", "database", "server"],
        }

        if predicted_category in category_keywords:
            keyword_score = sum(
                score
                for keyword, score in feature_vector.keyword_features.items()
                if keyword in category_keywords[predicted_category]
            )
            confidence = max(confidence, min(keyword_score, 1.0))

        return confidence

    def _calculate_behavior_confidence(self, file_info: FileInfo, predicted_category: CategoryType) -> float:
        """Calculate confidence based on user behavior patterns."""
        # This would track user's historical categorization preferences
        # For now, return a baseline based on overall accuracy
        return min(self.learning_data.accuracy + 0.1, 1.0)

    def get_learning_statistics(self) -> Dict[str, Union[int, float, str]]:
        """
        Get comprehensive learning statistics.

        Returns:
            Dictionary with learning statistics
        """
        return {
            "total_categorizations": self.learning_data.total_categorizations,
            "correct_predictions": self.learning_data.correct_predictions,
            "user_corrections": len(self.learning_data.user_corrections),
            "accuracy": self.learning_data.accuracy,
            "intervention_rate": self.learning_data.intervention_rate,
            "pattern_rules": len(self.learning_data.pattern_rules),
            "reliable_patterns": sum(1 for rule in self.learning_data.pattern_rules.values() if rule.is_reliable),
            "learning_enabled": self.learning_data.learning_enabled,
            "min_confidence_threshold": self.learning_data.min_confidence_threshold,
            "last_updated": datetime.now().isoformat(),
        }

    def create_learning_session(self) -> LearningSession:
        """
        Create a new learning session.

        Returns:
            New learning session object
        """
        return LearningSession(
            session_id=str(uuid.uuid4()),
            start_time=datetime.now(),
            files_processed=0,
            feedback_items=[],
            performance_metrics={},
        )

    def should_auto_categorize(self, confidence: ConfidenceScore) -> bool:
        """
        Determine if file should be auto-categorized based on confidence.

        Args:
            confidence: Confidence score for prediction

        Returns:
            True if should auto-categorize, False if user review needed
        """
        return self.learning_data.should_auto_categorize(confidence)

    def batch_learning_session(self, session: LearningSession) -> BatchLearningResult:
        """
        Process a batch learning session and calculate results.

        Args:
            session: Completed learning session

        Returns:
            Batch learning results
        """
        if not session.end_time:
            session.complete_session()

        # Calculate statistics
        total_files = session.files_processed
        successful_categorizations = total_files - len([f for f in session.feedback_items if f.is_correction])
        user_corrections = len([f for f in session.feedback_items if f.feedback_type == FeedbackType.CORRECTION])

        # Calculate new patterns learned (simplified)
        new_patterns = len([r for r in self.learning_data.pattern_rules.values() if r.created_at >= session.start_time])

        # Calculate accuracy improvement (simplified)
        accuracy_improvement = 0.0
        if session.performance_metrics.get("previous_accuracy"):
            current_accuracy = successful_categorizations / max(total_files, 1)
            accuracy_improvement = current_accuracy - session.performance_metrics["previous_accuracy"]

        processing_time = (session.end_time - session.start_time).total_seconds()

        return BatchLearningResult(
            total_files=total_files,
            successful_categorizations=successful_categorizations,
            user_corrections=user_corrections,
            new_patterns_learned=new_patterns,
            accuracy_improvement=accuracy_improvement,
            processing_time_seconds=processing_time,
            patterns_updated=[
                rule.id
                for rule in self.learning_data.pattern_rules.values()
                if rule.last_used and rule.last_used >= session.start_time
            ],
        )

    def export_learning_data(self, export_path: Path) -> bool:
        """
        Export learning data for backup or analysis.

        Args:
            export_path: Path to export learning data

        Returns:
            True if export successful, False otherwise
        """
        try:
            export_data = {
                "learning_data": self.learning_data.model_dump(),
                "statistics": self.get_learning_statistics(),
                "export_timestamp": datetime.now().isoformat(),
            }

            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            return True

        except Exception as e:
            logger.error(f"Failed to export learning data: {e}")
            return False

    def cleanup_old_data(self, days_to_keep: int = 90) -> None:
        """
        Clean up old learning data to manage storage space.

        Args:
            days_to_keep: Number of days of data to keep
        """
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)

        # Remove old corrections from memory
        self.learning_data.user_corrections = [
            c for c in self.learning_data.user_corrections if c.timestamp >= cutoff_date
        ]

        # Remove old data from database
        if self.enable_persistence:
            try:
                with sqlite3.connect(self.db_path) as conn:
                    conn.execute("DELETE FROM user_corrections WHERE timestamp < ?", (cutoff_date.isoformat(),))
                    conn.execute("DELETE FROM learning_sessions WHERE start_time < ?", (cutoff_date.isoformat(),))
                    conn.commit()

            except Exception as e:
                logger.warning(f"Failed to cleanup old data: {e}")
