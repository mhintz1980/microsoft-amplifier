"""
Learning Models

Data structures for machine learning components including
pattern recognition, confidence scoring, and feature extraction.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union
from pydantic import BaseModel, Field

from ...models.file_models import FileInfo, CategoryType


class PatternType(str, Enum):
    """Types of patterns that can be learned."""

    EXTENSION_PATTERN = "extension"
    NAME_PATTERN = "name"
    SIZE_PATTERN = "size"
    CONTENT_PATTERN = "content"
    PATH_PATTERN = "path"
    BEHAVIOR_PATTERN = "behavior"


class ConfidenceScore(BaseModel):
    """Confidence score for categorization decisions."""

    overall: float = Field(ge=0.0, le=1.0, description="Overall confidence score")
    extension_match: float = Field(ge=0.0, le=1.0, default=0.0, description="Extension-based confidence")
    pattern_match: float = Field(ge=0.0, le=1.0, default=0.0, description="Pattern-based confidence")
    content_match: float = Field(ge=0.0, le=1.0, default=0.0, description="Content-based confidence")
    user_behavior: float = Field(ge=0.0, le=1.0, default=0.0, description="User behavior-based confidence")
    ml_prediction: float = Field(ge=0.0, le=1.0, default=0.0, description="ML model prediction confidence")

    @property
    def is_high_confidence(self) -> bool:
        """Check if confidence is high enough for automatic categorization."""
        return self.overall >= 0.8

    @property
    def is_medium_confidence(self) -> bool:
        """Check if confidence is medium (requires user confirmation)."""
        return 0.6 <= self.overall < 0.8

    @property
    def is_low_confidence(self) -> bool:
        """Check if confidence is low (should be reviewed)."""
        return self.overall < 0.6


class FeatureVector(BaseModel):
    """Feature representation of a file for ML analysis."""

    # Basic features
    file_size_norm: float = Field(ge=0.0, description="Normalized file size (0-1)")
    extension_features: Dict[str, float] = Field(default_factory=dict, description="Extension one-hot encoding")
    path_depth: int = Field(ge=0, description="Directory path depth")

    # Content features
    text_length: int = Field(ge=0, description="Length of text content if readable")
    keyword_features: Dict[str, float] = Field(default_factory=dict, description="Keyword presence scores")
    language_score: float = Field(ge=0.0, le=1.0, default=0.0, description="Text-based language detection")

    # Pattern features
    name_patterns: Dict[str, float] = Field(default_factory=dict, description="Name pattern matches")
    date_features: Dict[str, float] = Field(default_factory=dict, description="Date-based patterns")

    # User behavior features
    user_category_history: float = Field(ge=0.0, le=1.0, default=0.0, description="User categorization history")
    correction_frequency: float = Field(ge=0.0, le=1.0, default=0.0, description="How often this type is corrected")


class PatternRule(BaseModel):
    """Learned pattern rule for categorization."""

    id: str = Field(description="Unique pattern identifier")
    pattern_type: PatternType = Field(description="Type of pattern")
    category_type: CategoryType = Field(description="Category this pattern applies to")
    rule_value: str = Field(description="Pattern value (regex, keyword, etc.)")
    confidence_weight: float = Field(ge=0.0, le=1.0, description="Weight in confidence calculation")
    success_rate: float = Field(ge=0.0, le=1.0, default=1.0, description="Historical success rate")
    usage_count: int = Field(ge=0, default=0, description="Times this pattern has been applied")
    correction_count: int = Field(ge=0, default=0, description="Times this pattern was corrected")
    created_at: datetime = Field(description="When this pattern was created")
    last_used: Optional[datetime] = Field(None, description="When this pattern was last used")

    @property
    def is_reliable(self) -> bool:
        """Check if pattern is reliable enough for automatic use."""
        return self.success_rate >= 0.8 and self.usage_count >= 5

    def update_success(self, was_correct: bool) -> None:
        """Update success statistics based on usage feedback."""
        self.usage_count += 1
        if not was_correct:
            self.correction_count += 1

        # Recalculate success rate
        if self.usage_count > 0:
            self.success_rate = (self.usage_count - self.correction_count) / self.usage_count

        self.last_used = datetime.now()


class UserCorrection(BaseModel):
    """Record of user correcting categorization decisions."""

    id: str = Field(description="Unique correction identifier")
    file_path: Path = Field(description="Path to the corrected file")
    predicted_category: CategoryType = Field(description="Original ML prediction")
    correct_category: CategoryType = Field(description="User-specified correct category")
    original_confidence: ConfidenceScore = Field(description="Original confidence scores")
    correction_reason: Optional[str] = Field(None, description="User-provided reason for correction")
    timestamp: datetime = Field(description="When correction was made")

    @property
    def was_improvement(self) -> bool:
        """Check if correction improved categorization."""
        # In a real system, this would compare against ground truth
        # For now, assume user corrections are always improvements
        return True


class LearningData(BaseModel):
    """Container for all learning data and patterns."""

    pattern_rules: Dict[str, PatternRule] = Field(default_factory=dict, description="Learned pattern rules")
    user_corrections: List[UserCorrection] = Field(default_factory=list, description="User correction history")
    feature_cache: Dict[str, FeatureVector] = Field(default_factory=dict, description="Cached feature vectors")

    # Performance metrics
    total_categorizations: int = Field(ge=0, default=0, description="Total files categorized")
    correct_predictions: int = Field(ge=0, default=0, description="Correct categorizations")
    user_interventions: int = Field(ge=0, default=0, description="Times user corrected predictions")

    # Learning parameters
    learning_enabled: bool = Field(True, description="Whether learning is enabled")
    min_confidence_threshold: float = Field(
        ge=0.0, le=1.0, default=0.7, description="Minimum confidence for auto-categorization"
    )

    @property
    def accuracy(self) -> float:
        """Calculate current categorization accuracy."""
        if self.total_categorizations == 0:
            return 0.0
        return self.correct_predictions / self.total_categorizations

    @property
    def intervention_rate(self) -> float:
        """Calculate rate of user interventions."""
        if self.total_categorizations == 0:
            return 0.0
        return self.user_interventions / self.total_categorizations

    def add_correction(self, correction: UserCorrection) -> None:
        """Add a user correction to the learning data."""
        self.user_corrections.append(correction)
        self.user_interventions += 1

        # If original prediction was wrong, decrement correct count
        if self.total_categorizations > 0:
            self.correct_predictions = max(0, self.correct_predictions - 1)

    def add_pattern_rule(self, rule: PatternRule) -> None:
        """Add or update a pattern rule."""
        self.pattern_rules[rule.id] = rule

    def get_reliable_patterns(self, category_type: CategoryType) -> List[PatternRule]:
        """Get reliable patterns for a specific category."""
        return [
            rule for rule in self.pattern_rules.values() if rule.category_type == category_type and rule.is_reliable
        ]

    def should_auto_categorize(self, confidence: ConfidenceScore) -> bool:
        """Determine if file should be auto-categorized based on confidence."""
        return confidence.overall >= self.min_confidence_threshold
