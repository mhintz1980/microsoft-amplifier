"""
Feedback Models

Data structures for user feedback collection and learning session management.
"""

from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel, Field

from ...models.file_models import CategoryType
from .learning_models import ConfidenceScore, FeatureVector


class FeedbackType(str, Enum):
    """Types of user feedback for learning."""

    CORRECTION = "correction"
    CONFIRMATION = "confirmation"
    IMPROVEMENT = "improvement"
    IGNORE = "ignore"


class UserFeedback(BaseModel):
    """Individual user feedback on categorization decisions."""

    id: str = Field(description="Unique feedback identifier")
    file_path: Path = Field(description="Path to the file that was categorized")
    predicted_category: CategoryType = Field(description="ML-predicted category")
    user_category: Optional[CategoryType] = Field(None, description="User-specified category")
    confidence: ConfidenceScore = Field(description="Original confidence scores")
    feedback_type: FeedbackType = Field(description="Type of feedback provided")
    user_comment: Optional[str] = Field(None, description="User's comment on the categorization")
    was_correct: bool = Field(description="Whether original prediction was correct")
    timestamp: datetime = Field(description="When feedback was provided")
    processing_time_ms: int = Field(ge=0, description="Time taken to process categorization")

    @property
    def is_correction(self) -> bool:
        """Check if this feedback is a correction."""
        return self.feedback_type == FeedbackType.CORRECTION

    @property
    def is_improvement(self) -> bool:
        """Check if this feedback suggests improvement."""
        return self.feedback_type == FeedbackType.IMPROVEMENT


class LearningSession(BaseModel):
    """A learning session that tracks progress over time."""

    session_id: str = Field(description="Unique session identifier")
    start_time: datetime = Field(description="When session started")
    end_time: Optional[datetime] = Field(None, description="When session ended")
    files_processed: int = Field(ge=0, default=0, description="Files processed in this session")
    feedback_items: List[UserFeedback] = Field(default_factory=list, description="Feedback collected")
    performance_metrics: Dict[str, float] = Field(default_factory=dict, description="Performance metrics")

    @property
    def duration_minutes(self) -> float:
        """Calculate session duration in minutes."""
        end = self.end_time or datetime.now()
        return (end - self.start_time).total_seconds() / 60

    @property
    def feedback_rate(self) -> float:
        """Calculate rate of feedback per processed file."""
        if self.files_processed == 0:
            return 0.0
        return len(self.feedback_items) / self.files_processed

    def add_feedback(self, feedback: UserFeedback) -> None:
        """Add feedback to the session."""
        self.feedback_items.append(feedback)

    def complete_session(self) -> None:
        """Mark the session as complete."""
        self.end_time = datetime.now()


class ModelPerformance(BaseModel):
    """Performance metrics for the ML categorization model."""

    accuracy: float = Field(ge=0.0, le=1.0, description="Overall accuracy")
    precision: Dict[CategoryType, float] = Field(default_factory=dict, description="Precision per category")
    recall: Dict[CategoryType, float] = Field(default_factory=dict, description="Recall per category")
    f1_score: Dict[CategoryType, float] = Field(default_factory=dict, description="F1 score per category")

    # Performance characteristics
    avg_confidence_correct: float = Field(ge=0.0, le=1.0, description="Average confidence for correct predictions")
    avg_confidence_incorrect: float = Field(ge=0.0, le=1.0, description="Average confidence for incorrect predictions")
    processing_time_avg_ms: int = Field(ge=0, description="Average processing time in milliseconds")

    # User behavior metrics
    user_satisfaction_rate: float = Field(ge=0.0, le=1.0, description="User satisfaction with predictions")
    correction_rate: float = Field(ge=0.0, le=1.0, description="Rate of user corrections")

    last_updated: datetime = Field(description="When metrics were last calculated")

    @property
    def is_performing_well(self) -> bool:
        """Check if model is performing well overall."""
        return self.accuracy >= 0.8 and self.correction_rate <= 0.2

    @property
    def needs_retraining(self) -> bool:
        """Check if model needs retraining based on performance."""
        return self.accuracy < 0.7 or self.correction_rate > 0.3


class BatchLearningResult(BaseModel):
    """Results from a batch learning operation."""

    total_files: int = Field(description="Total files processed")
    successful_categorizations: int = Field(description="Successfully categorized files")
    user_corrections: int = Field(description="Number of user corrections")
    new_patterns_learned: int = Field(description="New patterns discovered")
    accuracy_improvement: float = Field(description="Improvement in accuracy from previous session")
    processing_time_seconds: float = Field(description="Total processing time")
    patterns_updated: List[str] = Field(default_factory=list, description="Updated pattern IDs")

    @property
    def success_rate(self) -> float:
        """Calculate success rate for this batch."""
        if self.total_files == 0:
            return 0.0
        return self.successful_categorizations / self.total_files

    @property
    def learning_effectiveness(self) -> float:
        """Calculate learning effectiveness (patterns learned per correction)."""
        if self.user_corrections == 0:
            return 0.0
        return self.new_patterns_learned / self.user_corrections
