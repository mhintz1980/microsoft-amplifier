"""
Error Detection Engine

Leverages Agent Lightning's RL training capabilities to automatically detect
coding errors, hallucinations, and anti-patterns in skill implementations.
Uses sophisticated pattern recognition and adaptive learning to identify issues
before they impact production.
"""

import asyncio
import json
import logging
import re
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
from collections import defaultdict, Counter

import numpy as np

from .config import PerformanceTrackingConfig

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can be detected"""

    SYNTAX_ERROR = "syntax_error"
    RUNTIME_ERROR = "runtime_error"
    LOGIC_ERROR = "logic_error"
    HALLUCINATION = "hallucination"
    ANTI_PATTERN = "anti_pattern"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_VULNERABILITY = "security_vulnerability"
    RESOURCE_LEAK = "resource_leak"
    INCONSISTENT_BEHAVIOR = "inconsistent_behavior"
    DATA_CORRUPTION = "data_corruption"


class Severity(Enum):
    """Severity levels for detected errors"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ErrorPattern:
    """Represents a detected error pattern"""

    pattern_id: str
    error_type: ErrorType
    severity: Severity
    description: str
    pattern_regex: str
    confidence: float
    frequency: int
    first_detected: datetime
    last_detected: datetime
    affected_skills: Set[str]
    suggested_fix: Optional[str] = None
    false_positive_rate: float = 0.0


@dataclass
class DetectionResult:
    """Result from error detection analysis"""

    execution_id: str
    skill_id: str
    timestamp: datetime
    errors_detected: List[ErrorPattern]
    overall_risk_score: float
    recommendations: List[str]
    requires_immediate_attention: bool


@dataclass
class HallucinationDetection:
    """Detection of hallucination patterns"""

    confidence: float
    indicators: List[str]
    context_analysis: Dict[str, Any]
    factuality_score: float
    consistency_score: float


class ErrorDetectionEngine:
    """Advanced error detection using Agent Lightning's RL capabilities"""

    def __init__(self, config: PerformanceTrackingConfig, storage_path: Path):
        self.config = config
        self.storage_path = storage_path
        self.patterns_path = storage_path / "error_patterns"
        self.patterns_path.mkdir(parents=True, exist_ok=True)

        # Error pattern database
        self.known_patterns: Dict[str, ErrorPattern] = {}
        self.skill_error_history: Dict[str, List[DetectionResult]] = defaultdict(list)

        # RL training data
        self.training_examples: List[Dict] = []
        self.detection_model: Optional[Any] = None

        # Anti-pattern definitions
        self.anti_patterns = self._initialize_anti_patterns()

        # Hallucination detection patterns
        self.hallucination_indicators = self._initialize_hallucination_indicators()

        # Background tasks
        self._training_task: Optional[asyncio.Task] = None
        self._pattern_mining_task: Optional[asyncio.Task] = None
        self._running = False

    async def start(self):
        """Start the error detection engine"""
        if self._running:
            return

        self._running = True
        logger.info("Starting error detection engine")

        # Load existing patterns
        await self._load_error_patterns()
        await self._load_training_data()

        # Start background tasks
        self._training_task = asyncio.create_task(self._training_loop())
        self._pattern_mining_task = asyncio.create_task(self._pattern_mining_loop())

    async def stop(self):
        """Stop the error detection engine"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping error detection engine")

        # Cancel background tasks
        if self._training_task:
            self._training_task.cancel()
        if self._pattern_mining_task:
            self._pattern_mining_task.cancel()

        # Save data
        await self._save_error_patterns()
        await self._save_training_data()

    async def analyze_execution(self, execution_data: Dict[str, Any]) -> DetectionResult:
        """Analyze a skill execution for errors"""
        try:
            skill_id = execution_data.get("skill_id", "unknown")
            execution_id = execution_data.get("execution_id", f"exec_{datetime.now().timestamp()}")

            errors_detected = []
            risk_score = 0.0
            recommendations = []

            # Check for different types of errors
            errors_detected.extend(await self._detect_syntax_errors(execution_data))
            errors_detected.extend(await self._detect_runtime_errors(execution_data))
            errors_detected.extend(await self._detect_logic_errors(execution_data))
            errors_detected.extend(await self._detect_hallucinations(execution_data))
            errors_detected.extend(await self._detect_anti_patterns(execution_data))
            errors_detected.extend(await self._detect_performance_issues(execution_data))
            errors_detected.extend(await self._detect_security_vulnerabilities(execution_data))

            # Calculate overall risk score
            risk_score = self._calculate_risk_score(errors_detected)

            # Generate recommendations
            recommendations = self._generate_recommendations(errors_detected, risk_score)

            # Determine if immediate attention is needed
            requires_immediate = any(error.severity == Severity.CRITICAL for error in errors_detected)

            result = DetectionResult(
                execution_id=execution_id,
                skill_id=skill_id,
                timestamp=datetime.now(),
                errors_detected=errors_detected,
                overall_risk_score=risk_score,
                recommendations=recommendations,
                requires_immediate_attention=requires_immediate,
            )

            # Store result
            self.skill_error_history[skill_id].append(result)

            # Update patterns
            await self._update_error_patterns(errors_detected)

            # Add to training data
            await self._add_training_example(execution_data, result)

            logger.debug(f"Error detection analysis completed for {execution_id}")
            return result

        except Exception as e:
            logger.error(f"Failed to analyze execution: {e}")
            return DetectionResult(
                execution_id=execution_data.get("execution_id", "unknown"),
                skill_id=execution_data.get("skill_id", "unknown"),
                timestamp=datetime.now(),
                errors_detected=[],
                overall_risk_score=0.0,
                recommendations=["Error detection failed - manual review required"],
                requires_immediate_attention=False,
            )

    async def detect_hallucination(self, skill_output: str, context: Dict[str, Any]) -> HallucinationDetection:
        """Detect hallucinations in skill output using sophisticated analysis"""
        try:
            indicators = []
            confidence = 0.0
            factuality_score = 1.0
            consistency_score = 1.0

            # Check for hallucination indicators
            for indicator_name, indicator_pattern in self.hallucination_indicators.items():
                if re.search(indicator_pattern, skill_output, re.IGNORECASE):
                    indicators.append(indicator_name)
                    confidence += 0.1

            # Analyze factual consistency
            factuality_score = await self._analyze_factuality(skill_output, context)

            # Check internal consistency
            consistency_score = await self._analyze_consistency(skill_output)

            # Calculate overall confidence
            confidence = min(confidence + (1.0 - factuality_score) * 0.5 + (1.0 - consistency_score) * 0.3, 1.0)

            # Context analysis
            context_analysis = {
                "output_length": len(skill_output),
                "complexity_score": self._calculate_complexity_score(skill_output),
                "uncertainty_markers": len(
                    re.findall(r"\b(perhaps|maybe|might|could|possibly)\b", skill_output, re.IGNORECASE)
                ),
                "absolute_statements": len(
                    re.findall(r"\b(always|never|all|none|every)\b", skill_output, re.IGNORECASE)
                ),
            }

            return HallucinationDetection(
                confidence=confidence,
                indicators=indicators,
                context_analysis=context_analysis,
                factuality_score=factuality_score,
                consistency_score=consistency_score,
            )

        except Exception as e:
            logger.error(f"Failed to detect hallucination: {e}")
            return HallucinationDetection(
                confidence=0.0, indicators=[], context_analysis={}, factuality_score=1.0, consistency_score=1.0
            )

    async def get_error_trends(self, skill_id: str, days: int = 7) -> Dict[str, Any]:
        """Analyze error trends for a skill"""
        try:
            if skill_id not in self.skill_error_history:
                return {"error": "No error history available"}

            cutoff_date = datetime.now() - timedelta(days=days)
            recent_results = [r for r in self.skill_error_history[skill_id] if r.timestamp >= cutoff_date]

            if not recent_results:
                return {"error": "No recent errors found"}

            # Analyze trends
            error_types = Counter()
            severities = Counter()
            risk_scores = []

            for result in recent_results:
                for error in result.errors_detected:
                    error_types[error.error_type.value] += 1
                    severities[error.severity.value] += 1
                risk_scores.append(result.overall_risk_score)

            return {
                "period_start": cutoff_date.isoformat(),
                "period_end": datetime.now().isoformat(),
                "total_analyses": len(recent_results),
                "error_frequency": dict(error_types),
                "severity_distribution": dict(severities),
                "average_risk_score": np.mean(risk_scores),
                "risk_trend": self._calculate_risk_trend(risk_scores),
                "most_common_errors": error_types.most_common(5),
                "critical_issues": sum(1 for r in recent_results if r.requires_immediate_attention),
            }

        except Exception as e:
            logger.error(f"Failed to get error trends for {skill_id}: {e}")
            return {"error": str(e)}

    # Private methods

    async def _detect_syntax_errors(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect syntax errors in code"""
        errors = []

        try:
            code = execution_data.get("code", "")
            if not code:
                return errors

            # Common syntax error patterns
            syntax_patterns = {
                "unclosed_bracket": r"[\[\{\(][^\]\}\)]*$",
                "invalid_indentation": r"^\s*\t",
                "unclosed_string": r"['\"][^'\"]*$",
                "invalid_keyword": r"\b(?:class|def|if|for|while)\b[^:]*$",
                "missing_colon": r"\b(?:class|def|if|elif|else|for|while|try|except|finally)\s+\w+\s*$",
            }

            for pattern_name, pattern_regex in syntax_patterns.items():
                if re.search(pattern_regex, code, re.MULTILINE):
                    error = ErrorPattern(
                        pattern_id=f"syntax_{pattern_name}",
                        error_type=ErrorType.SYNTAX_ERROR,
                        severity=Severity.HIGH,
                        description=f"Syntax error detected: {pattern_name}",
                        pattern_regex=pattern_regex,
                        confidence=0.9,
                        frequency=1,
                        first_detected=datetime.now(),
                        last_detected=datetime.now(),
                        affected_skills={execution_data.get("skill_id", "unknown")},
                        suggested_fix=self._get_syntax_fix_suggestion(pattern_name),
                    )
                    errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect syntax errors: {e}")

        return errors

    async def _detect_runtime_errors(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect runtime errors from execution output"""
        errors = []

        try:
            error_output = execution_data.get("error_output", "")
            if not error_output:
                return errors

            # Runtime error patterns
            runtime_patterns = {
                "null_pointer": r"(?:NoneType|None).*has no attribute",
                "index_error": r"(?:IndexError|list index out of range)",
                "key_error": r"(?:KeyError|Key not found)",
                "type_error": r"(?:TypeError|Cannot|invalid)",
                "value_error": r"(?:ValueError|invalid literal)",
                "attribute_error": r"(?:AttributeError|has no attribute)",
                "import_error": r"(?:ImportError|No module named)",
                "memory_error": r"(?:MemoryError|out of memory)",
                "division_by_zero": r"(?:ZeroDivisionError|division by zero)",
            }

            for pattern_name, pattern_regex in runtime_patterns.items():
                if re.search(pattern_regex, error_output, re.IGNORECASE):
                    severity = (
                        Severity.CRITICAL if pattern_name in ["memory_error", "division_by_zero"] else Severity.HIGH
                    )

                    error = ErrorPattern(
                        pattern_id=f"runtime_{pattern_name}",
                        error_type=ErrorType.RUNTIME_ERROR,
                        severity=severity,
                        description=f"Runtime error detected: {pattern_name}",
                        pattern_regex=pattern_regex,
                        confidence=0.95,
                        frequency=1,
                        first_detected=datetime.now(),
                        last_detected=datetime.now(),
                        affected_skills={execution_data.get("skill_id", "unknown")},
                        suggested_fix=self._get_runtime_fix_suggestion(pattern_name),
                    )
                    errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect runtime errors: {e}")

        return errors

    async def _detect_logic_errors(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect logic errors through output analysis"""
        errors = []

        try:
            output = execution_data.get("output", "")
            expected_output = execution_data.get("expected_output")

            if expected_output and output != expected_output:
                error = ErrorPattern(
                    pattern_id="logic_output_mismatch",
                    error_type=ErrorType.LOGIC_ERROR,
                    severity=Severity.MEDIUM,
                    description="Output does not match expected result",
                    pattern_regex="",
                    confidence=0.8,
                    frequency=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    affected_skills={execution_data.get("skill_id", "unknown")},
                    suggested_fix="Review algorithm logic and input handling",
                )
                errors.append(error)

            # Check for infinite loops or excessive iteration
            execution_time = execution_data.get("execution_time", 0)
            if execution_time > 30:  # 30 seconds threshold
                error = ErrorPattern(
                    pattern_id="logic_performance_issue",
                    error_type=ErrorType.LOGIC_ERROR,
                    severity=Severity.HIGH,
                    description=f"Excessive execution time: {execution_time:.2f}s",
                    pattern_regex="",
                    confidence=0.7,
                    frequency=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    affected_skills={execution_data.get("skill_id", "unknown")},
                    suggested_fix="Optimize algorithm, check for infinite loops",
                )
                errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect logic errors: {e}")

        return errors

    async def _detect_hallucinations(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect hallucinations in skill output"""
        errors = []

        try:
            output = execution_data.get("output", "")
            if not output:
                return errors

            # Use the hallucination detection system
            context = {
                "skill_id": execution_data.get("skill_id"),
                "input": execution_data.get("input"),
                "execution_context": execution_data.get("context", {}),
            }

            hallucination_result = await self.detect_hallucination(output, context)

            if hallucination_result.confidence > 0.7:
                error = ErrorPattern(
                    pattern_id="hallucination_detected",
                    error_type=ErrorType.HALLUCINATION,
                    severity=Severity.CRITICAL,
                    description=f"Hallucination detected (confidence: {hallucination_result.confidence:.2f})",
                    pattern_regex="",
                    confidence=hallucination_result.confidence,
                    frequency=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    affected_skills={execution_data.get("skill_id", "unknown")},
                    suggested_fix="Implement stronger fact-checking and validation",
                )
                errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect hallucinations: {e}")

        return errors

    async def _detect_anti_patterns(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect anti-patterns in code"""
        errors = []

        try:
            code = execution_data.get("code", "")
            if not code:
                return errors

            for anti_pattern in self.anti_patterns:
                if re.search(anti_pattern["pattern"], code, re.MULTILINE):
                    error = ErrorPattern(
                        pattern_id=f"anti_pattern_{anti_pattern['name']}",
                        error_type=ErrorType.ANTI_PATTERN,
                        severity=Severity.MEDIUM,
                        description=f"Anti-pattern detected: {anti_pattern['description']}",
                        pattern_regex=anti_pattern["pattern"],
                        confidence=0.8,
                        frequency=1,
                        first_detected=datetime.now(),
                        last_detected=datetime.now(),
                        affected_skills={execution_data.get("skill_id", "unknown")},
                        suggested_fix=anti_pattern["suggestion"],
                    )
                    errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect anti-patterns: {e}")

        return errors

    async def _detect_performance_issues(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect performance issues"""
        errors = []

        try:
            execution_time = execution_data.get("execution_time", 0)
            memory_usage = execution_data.get("memory_usage", 0)
            cpu_usage = execution_data.get("cpu_usage", 0)

            # Performance thresholds
            if execution_time > 60:  # 1 minute
                error = ErrorPattern(
                    pattern_id="performance_slow_execution",
                    error_type=ErrorType.PERFORMANCE_ISSUE,
                    severity=Severity.HIGH,
                    description=f"Slow execution detected: {execution_time:.2f}s",
                    pattern_regex="",
                    confidence=0.9,
                    frequency=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    affected_skills={execution_data.get("skill_id", "unknown")},
                    suggested_fix="Profile and optimize performance bottlenecks",
                )
                errors.append(error)

            if memory_usage > 1000:  # 1GB
                error = ErrorPattern(
                    pattern_id="performance_high_memory",
                    error_type=ErrorType.RESOURCE_LEAK,
                    severity=Severity.HIGH,
                    description=f"High memory usage: {memory_usage:.2f}MB",
                    pattern_regex="",
                    confidence=0.8,
                    frequency=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    affected_skills={execution_data.get("skill_id", "unknown")},
                    suggested_fix="Check for memory leaks and optimize data structures",
                )
                errors.append(error)

            if cpu_usage > 90:  # 90%
                error = ErrorPattern(
                    pattern_id="performance_high_cpu",
                    error_type=ErrorType.PERFORMANCE_ISSUE,
                    severity=Severity.MEDIUM,
                    description=f"High CPU usage: {cpu_usage:.1f}%",
                    pattern_regex="",
                    confidence=0.7,
                    frequency=1,
                    first_detected=datetime.now(),
                    last_detected=datetime.now(),
                    affected_skills={execution_data.get("skill_id", "unknown")},
                    suggested_fix="Optimize CPU-intensive operations",
                )
                errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect performance issues: {e}")

        return errors

    async def _detect_security_vulnerabilities(self, execution_data: Dict[str, Any]) -> List[ErrorPattern]:
        """Detect security vulnerabilities"""
        errors = []

        try:
            code = execution_data.get("code", "")
            if not code:
                return errors

            # Security vulnerability patterns
            security_patterns = {
                "sql_injection": r"(?:execute|exec).*\+.*['\"]",
                "command_injection": r"os\.system|subprocess\.call.*\+",
                "hardcoded_secrets": r"(?:password|secret|key)\s*=\s*['\"][^'\"]+['\"]",
                "unsafe_eval": r"eval\s*\(",
                "unsafe_input": r"input\s*\(",
                "weak_crypto": r"md5|sha1",
                "path_traversal": r"\.\.[/\\]",
            }

            for pattern_name, pattern_regex in security_patterns.items():
                if re.search(pattern_regex, code, re.IGNORECASE):
                    severity = (
                        Severity.CRITICAL if pattern_name in ["sql_injection", "command_injection"] else Severity.HIGH
                    )

                    error = ErrorPattern(
                        pattern_id=f"security_{pattern_name}",
                        error_type=ErrorType.SECURITY_VULNERABILITY,
                        severity=severity,
                        description=f"Security vulnerability detected: {pattern_name}",
                        pattern_regex=pattern_regex,
                        confidence=0.9,
                        frequency=1,
                        first_detected=datetime.now(),
                        last_detected=datetime.now(),
                        affected_skills={execution_data.get("skill_id", "unknown")},
                        suggested_fix=self._get_security_fix_suggestion(pattern_name),
                    )
                    errors.append(error)

        except Exception as e:
            logger.error(f"Failed to detect security vulnerabilities: {e}")

        return errors

    def _initialize_anti_patterns(self) -> List[Dict]:
        """Initialize common anti-patterns"""
        return [
            {
                "name": "long_parameter_list",
                "description": "Function has too many parameters",
                "pattern": r"def\s+\w+\([^)]*(,\s*\w+\s*){7,}\)",
                "suggestion": "Use parameter objects or configuration dictionaries",
            },
            {
                "name": "complex_condition",
                "description": "Overly complex conditional logic",
                "pattern": r"if\s+.{200,}",
                "suggestion": "Break down complex conditions into separate functions",
            },
            {
                "name": "magic_numbers",
                "description": "Hardcoded magic numbers",
                "pattern": r"\b(?!0|1|2|10|100)\d{2,}\b",
                "suggestion": "Replace magic numbers with named constants",
            },
            {
                "name": "deep_nesting",
                "description": "Excessive nesting depth",
                "pattern": r"(\s{16,}|\t{4,})",
                "suggestion": "Reduce nesting depth using early returns or guard clauses",
            },
        ]

    def _initialize_hallucination_indicators(self) -> Dict[str, str]:
        """Initialize hallucination detection patterns"""
        return {
            "uncertainty_phrases": r"\b(perhaps|maybe|might|could|possibly|probably|I think|I believe)\b",
            "overconfident_claims": r"\b(always|never|all|none|every|guaranteed|certain)\b",
            "fabricated_statistics": r"\b\d+%\b(?!.*(?:according to|based on|study shows))",
            "vague_references": r"\b(research shows|studies indicate|experts say)\b(?!\s*[:,])",
            "unverifiable_claims": r"\b(obviously|clearly|everyone knows|it's well known)\b",
            "contradictory_statements": r"\b(however|but|although|despite)\b.{0,100}\b(because|therefore|thus)\b",
            "over_specific_details": r"\b\d{1,2}:\d{2}\s*(?:AM|PM|am|pm)\b",
            "fake_quotes": r'"[^"]*"[^,;]*(?:said|stated|mentioned)(?!\s+according\s+to)',
        }

    async def _analyze_factuality(self, output: str, context: Dict[str, Any]) -> float:
        """Analyze factual accuracy of output"""
        try:
            # Check for verifiable claims
            factual_score = 1.0

            # Deduct points for unverified claims
            unverified_patterns = [
                r"\b(according to|research shows|studies indicate)\b(?!\s*[:,])",
                r"\b\d{4}\b(?!\s*[-/])",  # Standalone years
                r"\b\d+%\b(?!\s*.*(?:according|based|study))",
            ]

            for pattern in unverified_patterns:
                matches = len(re.findall(pattern, output, re.IGNORECASE))
                factual_score -= matches * 0.1

            # Check against provided context
            if context and "ground_truth" in context:
                # This would integrate with external fact-checking
                pass

            return max(0.0, factual_score)

        except Exception as e:
            logger.error(f"Failed to analyze factuality: {e}")
            return 1.0

    async def _analyze_consistency(self, output: str) -> float:
        """Analyze internal consistency of output"""
        try:
            consistency_score = 1.0

            # Check for contradictory statements
            contradictory_pairs = [
                (r"\b(always|every|all)\b", r"\b(sometimes|never|none)\b"),
                (r"\b(increase|grow|rise)\b", r"\b(decrease|fall|drop)\b"),
                (r"\b(true|correct|accurate)\b", r"\b(false|incorrect|inaccurate)\b"),
            ]

            for positive_pattern, negative_pattern in contradictory_pairs:
                positive_matches = len(re.findall(positive_pattern, output, re.IGNORECASE))
                negative_matches = len(re.findall(negative_pattern, output, re.IGNORECASE))

                if positive_matches > 0 and negative_matches > 0:
                    consistency_score -= 0.2 * min(positive_matches, negative_matches)

            return max(0.0, consistency_score)

        except Exception as e:
            logger.error(f"Failed to analyze consistency: {e}")
            return 1.0

    def _calculate_complexity_score(self, text: str) -> float:
        """Calculate complexity score of text"""
        if not text:
            return 0.0

        # Simple complexity metrics
        word_count = len(text.split())
        sentence_count = len(re.findall(r"[.!?]+", text))
        avg_sentence_length = word_count / max(sentence_count, 1)

        # Unique words ratio
        words = text.lower().split()
        unique_words = len(set(words))
        unique_ratio = unique_words / len(words) if words else 0

        # Combine metrics
        complexity = (avg_sentence_length / 20 + unique_ratio) / 2
        return min(complexity, 1.0)

    def _calculate_risk_score(self, errors: List[ErrorPattern]) -> float:
        """Calculate overall risk score from detected errors"""
        if not errors:
            return 0.0

        severity_weights = {Severity.LOW: 0.1, Severity.MEDIUM: 0.3, Severity.HIGH: 0.6, Severity.CRITICAL: 1.0}

        total_score = 0.0
        for error in errors:
            weight = severity_weights[error.severity]
            total_score += weight * error.confidence

        # Normalize by number of errors
        normalized_score = total_score / len(errors)

        # Cap at 1.0
        return min(normalized_score, 1.0)

    def _generate_recommendations(self, errors: List[ErrorPattern], risk_score: float) -> List[str]:
        """Generate recommendations based on detected errors"""
        recommendations = []

        if risk_score > 0.8:
            recommendations.append("CRITICAL: Immediate intervention required - multiple severe issues detected")

        # Group errors by type
        error_types = defaultdict(list)
        for error in errors:
            error_types[error.error_type].append(error)

        # Generate specific recommendations
        if ErrorType.SYNTAX_ERROR in error_types:
            recommendations.append("Fix syntax errors before deployment - use code analysis tools")

        if ErrorType.HALLUCINATION in error_types:
            recommendations.append("URGENT: Hallucinations detected - implement stronger validation and fact-checking")

        if ErrorType.SECURITY_VULNERABILITY in error_types:
            recommendations.append("CRITICAL: Security vulnerabilities found - immediate patch required")

        if ErrorType.PERFORMANCE_ISSUE in error_types:
            recommendations.append("Optimize performance bottlenecks - profile and identify hotspots")

        if ErrorType.ANTI_PATTERN in error_types:
            recommendations.append("Refactor anti-patterns - follow best practices and coding standards")

        # General recommendations
        if len(errors) > 5:
            recommendations.append("Consider comprehensive code review - high error density detected")

        return recommendations

    async def _training_loop(self):
        """Background loop for RL training"""
        while self._running:
            try:
                await self._train_detection_model()
                await asyncio.sleep(3600)  # Train every hour
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in training loop: {e}")
                await asyncio.sleep(300)

    async def _pattern_mining_loop(self):
        """Background loop for mining new error patterns"""
        while self._running:
            try:
                await self._mine_new_patterns()
                await asyncio.sleep(1800)  # Mine every 30 minutes
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pattern mining loop: {e}")
                await asyncio.sleep(300)

    async def _train_detection_model(self):
        """Train the RL-based detection model"""
        try:
            if len(self.training_examples) < 100:
                return  # Need sufficient training data

            # This would integrate with Agent Lightning's training system
            # For now, we'll simulate the training process
            logger.info(f"Training detection model with {len(self.training_examples)} examples")

            # TODO: Implement actual RL training using Agent Lightning
            # model = await agent_lightning.train_detection_model(self.training_examples)
            # self.detection_model = model

        except Exception as e:
            logger.error(f"Failed to train detection model: {e}")

    async def _mine_new_patterns(self):
        """Mine new error patterns from recent data"""
        try:
            # Analyze recent errors to find new patterns
            for skill_id, results in self.skill_error_history.items():
                recent_results = results[-20:]  # Last 20 analyses

                # Look for recurring error patterns
                pattern_frequency = defaultdict(int)
                for result in recent_results:
                    for error in result.errors_detected:
                        pattern_frequency[error.pattern_id] += 1

                # Identify new patterns (appearing in multiple recent executions)
                for pattern_id, frequency in pattern_frequency.items():
                    if frequency >= 3 and pattern_id not in self.known_patterns:
                        await self._create_new_pattern(pattern_id, skill_id, recent_results)

        except Exception as e:
            logger.error(f"Failed to mine new patterns: {e}")

    def _get_syntax_fix_suggestion(self, pattern_name: str) -> str:
        """Get fix suggestion for syntax error pattern"""
        suggestions = {
            "unclosed_bracket": "Close all brackets, parentheses, and braces",
            "invalid_indentation": "Use consistent indentation (4 spaces recommended)",
            "unclosed_string": "Close all string literals with matching quotes",
            "invalid_keyword": "Check keyword usage and syntax",
            "missing_colon": "Add colon after class, function, and control statements",
        }
        return suggestions.get(pattern_name, "Review syntax and fix errors")

    def _get_runtime_fix_suggestion(self, pattern_name: str) -> str:
        """Get fix suggestion for runtime error pattern"""
        suggestions = {
            "null_pointer": "Add null checks before accessing object attributes",
            "index_error": "Validate array indices before access",
            "key_error": "Check dictionary key existence with .get() or 'in' operator",
            "type_error": "Add type validation and conversion",
            "value_error": "Validate input values and ranges",
            "attribute_error": "Check object type and attribute existence",
            "import_error": "Verify module imports and installation",
            "memory_error": "Optimize memory usage and process data in chunks",
            "division_by_zero": "Check for zero denominator before division",
        }
        return suggestions.get(pattern_name, "Add proper error handling and validation")

    def _get_security_fix_suggestion(self, pattern_name: str) -> str:
        """Get fix suggestion for security vulnerability pattern"""
        suggestions = {
            "sql_injection": "Use parameterized queries or prepared statements",
            "command_injection": "Validate and sanitize user input, use subprocess with safe parameters",
            "hardcoded_secrets": "Store secrets in environment variables or secure vault",
            "unsafe_eval": "Avoid eval() with user input, use safer alternatives",
            "unsafe_input": "Validate and sanitize all user input",
            "weak_crypto": "Use strong cryptographic algorithms (SHA-256+, bcrypt)",
            "path_traversal": "Validate file paths and use chroot/sandbox",
        }
        return suggestions.get(pattern_name, "Review security best practices")

    async def _create_new_pattern(self, pattern_id: str, skill_id: str, results: List[DetectionResult]):
        """Create a new error pattern from recurring issues"""
        try:
            # Extract common characteristics from the pattern
            related_errors = []
            for result in results:
                for error in result.errors_detected:
                    if error.pattern_id == pattern_id:
                        related_errors.append(error)

            if not related_errors:
                return

            # Create new pattern
            new_pattern = ErrorPattern(
                pattern_id=pattern_id,
                error_type=related_errors[0].error_type,
                severity=related_errors[0].severity,
                description=f"Auto-detected pattern: {pattern_id}",
                pattern_regex=related_errors[0].pattern_regex,
                confidence=sum(e.confidence for e in related_errors) / len(related_errors),
                frequency=len(related_errors),
                first_detected=min(e.first_detected for e in related_errors),
                last_detected=max(e.last_detected for e in related_errors),
                affected_skills={skill_id},
            )

            self.known_patterns[pattern_id] = new_pattern
            logger.info(f"Created new error pattern: {pattern_id}")

        except Exception as e:
            logger.error(f"Failed to create new pattern {pattern_id}: {e}")

    def _calculate_risk_trend(self, risk_scores: List[float]) -> str:
        """Calculate risk trend over time"""
        if len(risk_scores) < 2:
            return "insufficient_data"

        recent_avg = np.mean(risk_scores[-5:])
        early_avg = np.mean(risk_scores[:5])

        if recent_avg > early_avg + 0.1:
            return "increasing"
        elif recent_avg < early_avg - 0.1:
            return "decreasing"
        else:
            return "stable"

    async def _load_error_patterns(self):
        """Load existing error patterns from disk"""
        try:
            patterns_file = self.patterns_path / "known_patterns.json"
            if patterns_file.exists():
                with open(patterns_file, "r") as f:
                    data = json.load(f)
                    for pattern_data in data:
                        pattern = ErrorPattern(**pattern_data)
                        pattern.first_detected = datetime.fromisoformat(pattern.first_detected)
                        pattern.last_detected = datetime.fromisoformat(pattern.last_detected)
                        pattern.affected_skills = set(pattern.affected_skills)
                        self.known_patterns[pattern.pattern_id] = pattern

                logger.info(f"Loaded {len(self.known_patterns)} error patterns")

        except Exception as e:
            logger.error(f"Failed to load error patterns: {e}")

    async def _save_error_patterns(self):
        """Save error patterns to disk"""
        try:
            patterns_file = self.patterns_path / "known_patterns.json"
            patterns_data = []

            for pattern in self.known_patterns.values():
                pattern_dict = asdict(pattern)
                pattern_dict["first_detected"] = pattern.first_detected.isoformat()
                pattern_dict["last_detected"] = pattern.last_detected.isoformat()
                pattern_dict["affected_skills"] = list(pattern.affected_skills)
                patterns_data.append(pattern_dict)

            with open(patterns_file, "w") as f:
                json.dump(patterns_data, f, indent=2)

            logger.info(f"Saved {len(patterns_data)} error patterns")

        except Exception as e:
            logger.error(f"Failed to save error patterns: {e}")

    async def _load_training_data(self):
        """Load training data from disk"""
        try:
            training_file = self.patterns_path / "training_data.json"
            if training_file.exists():
                with open(training_file, "r") as f:
                    self.training_examples = json.load(f)
                logger.info(f"Loaded {len(self.training_examples)} training examples")

        except Exception as e:
            logger.error(f"Failed to load training data: {e}")

    async def _save_training_data(self):
        """Save training data to disk"""
        try:
            training_file = self.patterns_path / "training_data.json"
            with open(training_file, "w") as f:
                json.dump(self.training_examples[-10000:], f)  # Keep last 10k examples
            logger.info(f"Saved training data")

        except Exception as e:
            logger.error(f"Failed to save training data: {e}")

    async def _update_error_patterns(self, errors: List[ErrorPattern]):
        """Update error patterns with new detections"""
        try:
            for error in errors:
                if error.pattern_id in self.known_patterns:
                    # Update existing pattern
                    existing = self.known_patterns[error.pattern_id]
                    existing.frequency += 1
                    existing.last_detected = datetime.now()
                    existing.affected_skills.add(error.error_type.value)  # Temporary fix
                    existing.confidence = (existing.confidence + error.confidence) / 2
                else:
                    # Add new pattern
                    self.known_patterns[error.pattern_id] = error

        except Exception as e:
            logger.error(f"Failed to update error patterns: {e}")

    async def _add_training_example(self, execution_data: Dict[str, Any], result: DetectionResult):
        """Add training example for model training"""
        try:
            training_example = {
                "timestamp": datetime.now().isoformat(),
                "execution_data": execution_data,
                "detection_result": {
                    "errors": [asdict(error) for error in result.errors_detected],
                    "risk_score": result.overall_risk_score,
                    "requires_attention": result.requires_immediate_attention,
                },
            }

            self.training_examples.append(training_example)

            # Keep only recent training examples
            if len(self.training_examples) > 50000:
                self.training_examples = self.training_examples[-25000:]

        except Exception as e:
            logger.error(f"Failed to add training example: {e}")
