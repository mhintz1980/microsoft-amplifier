"""
Base Types for Signature-Based Skill Framework

Core type definitions and interfaces that provide the foundation for
type-safe, zero-hallucination skill execution with BootstrapFewShot optimization.
"""

import logging
import time
from abc import ABC
from abc import abstractmethod
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any
from typing import Generic
from typing import Protocol
from typing import TypeVar
from typing import runtime_checkable

from pydantic import BaseModel
from pydantic import Field
from pydantic import ValidationError

logger = logging.getLogger(__name__)

# Type variables for generic type safety
T_Input = TypeVar("T_Input")
T_Output = TypeVar("T_Output")
T_Config = TypeVar("T_Config", bound="SkillConfig")


class ValidationMode(Enum):
    """Validation strategies for skill inputs/outputs"""

    STRICT = "strict"  # Fail on any validation error
    LENIENT = "lenient"  # Log errors but continue
    PERMISSIVE = "permissive"  # Skip validation entirely
    SANITIZE = "sanitize"  # Attempt to fix invalid data


class ConfidenceLevel(Enum):
    """Confidence levels for skill execution"""

    CRITICAL = 1.0  # 100% confidence - zero hallucination
    HIGH = 0.95  # 95% confidence
    MEDIUM = 0.8  # 80% confidence
    LOW = 0.6  # 60% confidence
    UNKNOWN = 0.0  # Unknown confidence


class SkillPriority(Enum):
    """Priority levels for skill execution"""

    CRITICAL = 1  # Must succeed
    HIGH = 2  # Important but not critical
    NORMAL = 3  # Normal priority
    LOW = 4  # Can be deferred
    BACKGROUND = 5  # Background processing


@dataclass
class SkillMetrics:
    """Comprehensive metrics for skill performance tracking"""

    executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    average_execution_time: float = 0.0
    average_confidence: float = 0.0
    average_tokens_used: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    hallucination_detections: int = 0
    validation_errors: int = 0
    optimization_score: float = 1.0  # BootstrapFewShot score
    last_execution: float | None = None
    total_tokens_saved: int = 0

    @property
    def success_rate(self) -> float:
        """Calculate success rate"""
        if self.executions == 0:
            return 0.0
        return self.successful_executions / self.executions

    @property
    def error_rate(self) -> float:
        """Calculate error rate"""
        return 1.0 - self.success_rate

    @property
    def cache_hit_rate(self) -> float:
        """Calculate cache hit rate"""
        total_cache_requests = self.cache_hits + self.cache_misses
        if total_cache_requests == 0:
            return 0.0
        return self.cache_hits / total_cache_requests

    @property
    def performance_score(self) -> float:
        """Overall performance score (0-1)"""
        # Weighted combination of success rate, speed, and optimization
        success_weight = 0.4
        speed_weight = 0.3
        optimization_weight = 0.3

        # Normalize execution time (lower is better)
        speed_score = max(0, 1.0 - (self.average_execution_time / 10.0))  # 10s = 0 score

        return (
            self.success_rate * success_weight
            + speed_score * speed_weight
            + self.optimization_score * optimization_weight
        )


@dataclass
class ExecutionContext:
    """Execution context for skill with Agent Lightning integration"""

    user_id: str | None = None
    session_id: str | None = None
    request_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    timeout: float | None = None
    priority: SkillPriority = SkillPriority.NORMAL
    validation_mode: ValidationMode = ValidationMode.STRICT
    enable_caching: bool = True
    enable_optimization: bool = True
    zero_hallucination: bool = True
    max_retries: int = 3
    retry_delay: float = 1.0

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class ValidationResult:
    """Result of input/output validation"""

    is_valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    sanitized_data: Any | None = None
    confidence_adjustment: float = 0.0

    def add_error(self, error: str) -> None:
        """Add an error message"""
        self.errors.append(error)
        self.confidence_adjustment -= 0.1

    def add_warning(self, warning: str) -> None:
        """Add a warning message"""
        self.warnings.append(warning)
        self.confidence_adjustment -= 0.05


@dataclass
class SkillResult(Generic[T_Output]):
    """Enhanced result from skill execution with confidence tracking"""

    success: bool
    data: T_Output | None = None
    error: str | None = None
    execution_time: float = 0.0
    confidence: float = 1.0
    tokens_used: int = 0
    validation_result: ValidationResult | None = None
    metrics: SkillMetrics | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    optimization_applied: bool = False
    cache_hit: bool = False
    hallucination_score: float = 0.0  # 0 = no hallucination, 1 = certain hallucination

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class SkillConfig(BaseModel):
    """Base configuration for all signature-based skills"""

    skill_id: str = Field(description="Unique identifier for the skill")
    name: str = Field(description="Human-readable name")
    description: str = Field(description="Detailed description of what the skill does")
    version: str = Field(default="1.0.0", description="Skill version")
    author: str | None = Field(default=None, description="Skill author")

    # Performance settings
    timeout: float = Field(default=30.0, description="Timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    enable_caching: bool = Field(default=True, description="Enable result caching")
    enable_optimization: bool = Field(default=True, description="Enable BootstrapFewShot optimization")

    # Validation settings
    validation_mode: ValidationMode = Field(default=ValidationMode.STRICT)
    confidence_threshold: float = Field(default=0.8, description="Minimum confidence threshold")

    # Zero-hallucination settings
    zero_hallucination: bool = Field(default=True, description="Enforce zero-hallucination mode")
    hallucination_threshold: float = Field(default=0.1, description="Max acceptable hallucination score")

    # Meta-skill settings
    compound_multiplier: float = Field(default=1.0, description="Performance multiplier from meta-skills")
    progressive_disclosure: bool = Field(default=True, description="Enable progressive disclosure")

    class Config:
        use_enum_values = True


class TypeContract(ABC):
    """Abstract base class for type contracts"""

    @abstractmethod
    def validate(self, data: Any) -> ValidationResult:
        """Validate data against the contract"""
        pass

    @abstractmethod
    def get_schema(self) -> dict[str, Any]:
        """Get JSON schema for the contract"""
        pass

    @abstractmethod
    def sanitize(self, data: Any) -> tuple[Any, ValidationResult]:
        """Attempt to sanitize invalid data"""
        pass


class PydanticContract(TypeContract):
    """Type contract using Pydantic models"""

    def __init__(self, model_class: type[BaseModel]):
        self.model_class = model_class

    def validate(self, data: Any) -> ValidationResult:
        """Validate data using Pydantic model"""
        try:
            self.model_class.model_validate(data)
            return ValidationResult(is_valid=True)
        except ValidationError as e:
            result = ValidationResult(is_valid=False)
            for error in e.errors():
                result.add_error(f"{'.'.join(str(loc) for loc in error['loc'])}: {error['msg']}")
            return result
        except Exception as e:
            return ValidationResult(is_valid=False, errors=[f"Validation error: {str(e)}"])

    def get_schema(self) -> dict[str, Any]:
        """Get Pydantic model schema"""
        return self.model_class.model_json_schema()

    def sanitize(self, data: Any) -> tuple[Any, ValidationResult]:
        """Attempt to sanitize data to fit the model"""
        try:
            # Try to validate first
            model = self.model_class.model_validate(data)
            return model.model_dump(), ValidationResult(is_valid=True)
        except ValidationError:
            # If validation fails, try basic sanitization
            try:
                if isinstance(data, dict):
                    # Remove unknown fields and try again
                    schema = self.get_schema()
                    known_fields = set(schema.get("properties", {}).keys())
                    sanitized_data = {k: v for k, v in data.items() if k in known_fields}

                    model = self.model_class.model_validate(sanitized_data)
                    return model.model_dump(), ValidationResult(
                        is_valid=True, warnings=["Some fields were removed during sanitization"]
                    )
            except Exception:
                pass

            return data, ValidationResult(is_valid=False, errors=["Data could not be sanitized to fit the contract"])


@runtime_checkable
class SkillSignature(Protocol[T_Input, T_Output]):
    """Protocol defining the signature interface for skills"""

    def get_input_contract(self) -> TypeContract:
        """Get input type contract"""
        ...

    def get_output_contract(self) -> TypeContract:
        """Get output type contract"""
        ...

    def get_config(self) -> SkillConfig:
        """Get skill configuration"""
        ...

    async def execute_with_signature(self, input_data: T_Input, context: ExecutionContext) -> SkillResult[T_Output]:
        """Execute with full signature validation and optimization"""
        ...

    def get_metrics(self) -> SkillMetrics:
        """Get performance metrics"""
        ...


class SkillInterface(ABC, Generic[T_Input, T_Output]):
    """Abstract base class implementing the SkillSignature protocol"""

    def __init__(self, config: SkillConfig):
        self.config = config
        self.metrics = SkillMetrics()
        self._input_contract: TypeContract | None = None
        self._output_contract: TypeContract | None = None
        self._setup_contracts()

    def _setup_contracts(self):
        """Setup input/output contracts - override in subclasses"""
        pass

    @abstractmethod
    async def execute_core(self, input_data: T_Input, context: ExecutionContext) -> T_Output:
        """Core skill execution logic - must be implemented by subclasses"""
        pass

    def get_input_contract(self) -> TypeContract:
        """Get input type contract"""
        if not self._input_contract:
            raise NotImplementedError("Input contract not defined")
        return self._input_contract

    def get_output_contract(self) -> TypeContract:
        """Get output type contract"""
        if not self._output_contract:
            raise NotImplementedError("Output contract not defined")
        return self._output_contract

    def get_config(self) -> SkillConfig:
        """Get skill configuration"""
        return self.config

    def get_metrics(self) -> SkillMetrics:
        """Get performance metrics"""
        return self.metrics

    async def execute_with_signature(self, input_data: T_Input, context: ExecutionContext) -> SkillResult[T_Output]:
        """Execute with full signature validation and optimization"""
        start_time = time.time()

        try:
            # Input validation
            validation_result = await self._validate_input(input_data, context)

            if not validation_result.is_valid and context.validation_mode == ValidationMode.STRICT:
                return SkillResult[T_Output](
                    success=False,
                    error=f"Input validation failed: {'; '.join(validation_result.errors)}",
                    validation_result=validation_result,
                    execution_time=time.time() - start_time,
                )

            # Use sanitized data if available and validation mode is SANITIZE
            effective_input = validation_result.sanitized_data if validation_result.sanitized_data else input_data

            # Zero-hallucination check
            if context.zero_hallucination:
                hallucination_score = await self._check_hallucination(effective_input)
                if hallucination_score > self.config.hallucination_threshold:
                    self.metrics.hallucination_detections += 1
                    return SkillResult[T_Output](
                        success=False,
                        error=f"Hallucination detected: score {hallucination_score:.2f} exceeds threshold {self.config.hallucination_threshold}",
                        hallucination_score=hallucination_score,
                        execution_time=time.time() - start_time,
                    )

            # Execute core skill
            output_data = await self.execute_core(effective_input, context)

            # Output validation
            output_validation = await self._validate_output(output_data, context)

            execution_time = time.time() - start_time

            # Update metrics
            self._update_metrics(execution_time, validation_result.confidence_adjustment, hallucination_score)

            return SkillResult[T_Output](
                success=True,
                data=output_data,
                execution_time=execution_time,
                confidence=max(0.0, 1.0 + validation_result.confidence_adjustment - hallucination_score),
                validation_result=output_validation,
                metrics=self.metrics,
                hallucination_score=hallucination_score,
            )

        except Exception as e:
            execution_time = time.time() - start_time
            self.metrics.failed_executions += 1
            self.metrics.executions += 1

            logger.error(f"Skill {self.config.skill_id} execution failed: {e}")

            return SkillResult[T_Output](
                success=False, error=str(e), execution_time=execution_time, metrics=self.metrics
            )

    async def _validate_input(self, input_data: T_Input, context: ExecutionContext) -> ValidationResult:
        """Validate input data against contract"""
        if context.validation_mode == ValidationMode.PERMISSIVE:
            return ValidationResult(is_valid=True)

        validation_result = self.get_input_contract().validate(input_data)

        if not validation_result.is_valid and context.validation_mode == ValidationMode.SANITIZE:
            sanitized_data, sanitization_result = self.get_input_contract().sanitize(input_data)
            validation_result.sanitized_data = sanitized_data
            validation_result.warnings.extend(sanitization_result.warnings)

        self.metrics.validation_errors += len(validation_result.errors)
        return validation_result

    async def _validate_output(self, output_data: T_Output, context: ExecutionContext) -> ValidationResult:
        """Validate output data against contract"""
        if context.validation_mode == ValidationMode.PERMISSIVE:
            return ValidationResult(is_valid=True)

        return self.get_output_contract().validate(output_data)

    async def _check_hallucination(self, data: Any) -> float:
        """Check for hallucinations in input/output data"""
        # Basic hallucination detection - can be enhanced with sophisticated models
        hallucination_score = 0.0

        if isinstance(data, str):
            # Check for uncertain language patterns
            uncertain_patterns = [
                "i think",
                "i believe",
                "probably",
                "might be",
                "could be",
                "perhaps",
                "maybe",
                "possibly",
                "likely",
                "uncertain",
            ]

            text_lower = data.lower()
            pattern_matches = sum(1 for pattern in uncertain_patterns if pattern in text_lower)

            # Calculate score based on pattern density
            words = len(text_lower.split())
            if words > 0:
                hallucination_score = min(1.0, pattern_matches / max(1, words * 0.1))

        return hallucination_score

    def _update_metrics(self, execution_time: float, confidence_adjustment: float, hallucination_score: float) -> None:
        """Update skill metrics after execution"""
        self.metrics.executions += 1
        self.metrics.successful_executions += 1

        # Update averages
        total_time = self.metrics.average_execution_time * (self.metrics.executions - 1)
        self.metrics.average_execution_time = (total_time + execution_time) / self.metrics.executions

        confidence = max(0.0, 1.0 + confidence_adjustment - hallucination_score)
        total_confidence = self.metrics.average_confidence * (self.metrics.executions - 1)
        self.metrics.average_confidence = (total_confidence + confidence) / self.metrics.executions

        self.metrics.last_execution = time.time()


# Type aliases for cleaner code
SkillHandler = Callable[[Any, ExecutionContext], Any]
ValidationFunction = Callable[[Any], ValidationResult]
OptimizationFunction = Callable[[SkillMetrics], float]
