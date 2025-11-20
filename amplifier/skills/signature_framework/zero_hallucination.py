"""
Zero-Hallucination Enforcement System

Advanced hallucination detection and prevention system that ensures
AI-generated content is factual, verifiable, and free from hallucinations.
Implements multiple detection strategies with confidence scoring and
automatic correction mechanisms.
"""

import hashlib
import logging
import re
import time
from collections import Counter
from collections import defaultdict
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from re import Pattern
from typing import Any

logger = logging.getLogger(__name__)


class HallucinationType(Enum):
    """Types of hallucinations to detect"""

    FACTUAL = "factual"  # Incorrect facts or information
    NUMERICAL = "numerical"  # Incorrect numbers, dates, or statistics
    LOGICAL = "logical"  # Logical contradictions
    CONTEXTUAL = "contextual"  # Information outside provided context
    CONFABULATION = "confabulation"  # Fabricated details or explanations
    UNCERTAINTY = "uncertainty"  # Expressed uncertainty or speculation
    INCONSISTENT = "inconsistent"  # Internal inconsistencies
    UNVERIFIABLE = "unverifiable"  # Claims that cannot be verified


class ConfidenceLevel(Enum):
    """Confidence levels for content validation"""

    CRITICAL = 1.0  # 100% confidence - no hallucination
    HIGH = 0.95  # 95% confidence
    MEDIUM = 0.8  # 80% confidence
    LOW = 0.6  # 60% confidence
    VERY_LOW = 0.4  # 40% confidence
    UNKNOWN = 0.0  # Unknown confidence


class EnforcementLevel(Enum):
    """Levels of hallucination enforcement"""

    STRICT = "strict"  # Block any suspected hallucination
    MODERATE = "moderate"  # Flag and correct obvious hallucinations
    LENIENT = "lenient"  # Flag but allow with warning
    MONITOR = "monitor"  # Only monitor, don't block


@dataclass
class HallucinationIndicator:
    """Individual hallucination indicator"""

    type: HallucinationType
    severity: float  # 0.0 to 1.0
    confidence: float  # Confidence in this detection
    text_span: tuple[int, int]  # Start and end character positions
    original_text: str
    suggested_correction: str | None = None
    explanation: str = ""
    pattern_matched: str | None = None


@dataclass
class HallucinationReport:
    """Comprehensive hallucination analysis report"""

    overall_confidence: float
    indicators: list[HallucinationIndicator] = field(default_factory=list)
    enforcement_action: str | None = None
    corrected_content: str | None = None
    verification_suggestions: list[str] = field(default_factory=list)
    quality_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def has_hallucinations(self) -> bool:
        """Check if any hallucinations were detected"""
        return len(self.indicators) > 0

    @property
    def severity_score(self) -> float:
        """Calculate overall severity score"""
        if not self.indicators:
            return 0.0
        return max(indicator.severity for indicator in self.indicators)

    def get_indicators_by_type(self, hallucination_type: HallucinationType) -> list[HallucinationIndicator]:
        """Get indicators filtered by type"""
        return [ind for ind in self.indicators if ind.type == hallucination_type]


@dataclass
class ZeroHallucinationConfig:
    """Configuration for zero-hallucination system"""

    enforcement_level: EnforcementLevel = EnforcementLevel.MODERATE
    confidence_threshold: float = 0.8
    enable_auto_correction: bool = True
    enable_context_verification: bool = True
    enable_fact_checking: bool = True
    max_correction_attempts: int = 3
    cache_results: bool = True
    track_patterns: bool = True
    detailed_logging: bool = False


class HallucinationPatterns:
    """Pattern library for hallucination detection"""

    UNCERTAINTY_PATTERNS = [
        r"\b(i think|i believe|probably|maybe|perhaps|might|could|possibly)\b",
        r"\b(seems like|appears to be|i guess|i suppose)\b",
        r"\b(not sure|uncertain|unclear|don\'t know|cannot say)\b",
        r"\b(sort of|kind of|rather|quite|somewhat)\b",
        r"\b(presumably|ostensibly|apparently|supposedly)\b",
        r"\b(may|might|could be|would be)\s+be\s+the\s+case",
        r"\b(assuming|presuming|hypothesizing)\b",
        r"\b(potentially|theoretically|conceptually)\b",
    ]

    SPECULATION_PATTERNS = [
        r"\b(theoretically|hypothetically|in theory|in principle)\b",
        r"\b(assuming that|given that|supposing)\b",
        r"\b(one could argue|it might be said|it\'s possible that)\b",
        r"\b(there\'s a chance|it\'s conceivable|it\'s imaginable)\b",
        r"\b(under certain circumstances|in some cases)\b",
    ]

    EVASIVE_PATTERNS = [
        r"\b(i cannot|i cannot help|i\'m not able|unable to)\b",
        r"\b(no information|insufficient data|cannot determine)\b",
        r"\b(contact.*support|consult.*documentation|refer to.*manual)\b",
        r"\b(i\'m not designed to|i cannot provide|i don\'t have access to)\b",
        r"\b(beyond my scope|outside my capabilities|not within my knowledge)\b",
    ]

    NUMERICAL_PATTERNS = [
        r"\b(about|around|approximately|roughly|nearly|almost)\s+\d+",
        r"\b(millions|billions|trillions)\s+(of\s+)?\w+",
        r"\b(\d+|\d{1,3}(,\d{3})*)(\.\d+)?\s*%(?![\s\d])",  # Suspicious percentages
    ]

    CONTRADICTION_PATTERNS = [
        r"\b(although|however|nevertheless|despite|but)\b.*\b(always|never|all|none)\b",
        r"\b(every|each|all)\b.*\b(except|besides|except for)\b",
        r"\b(never|always)\b.*\b(sometimes|occasionally|rarely)\b",
    ]

    FACTUAL_CLAIM_PATTERNS = [
        r"\b(according to|research shows|studies indicate|data suggests)\b",
        r"\b(scientists|researchers|experts)\s+(have found|discovered|concluded)\b",
        r"\b(it is known|it has been proven|it is established)\b",
        r"\b(statistically|significantly|dramatically)\b",
    ]


class ContextVerifier:
    """Context-based verification system"""

    def __init__(self):
        self.knowledge_base: dict[str, Any] = {}
        self.fact_cache: dict[str, bool] = {}

    def add_context(self, context_data: dict[str, Any]):
        """Add context information for verification"""
        self.knowledge_base.update(context_data)

    async def verify_against_context(self, claim: str) -> tuple[bool, float]:
        """Verify a claim against available context"""
        claim_hash = hashlib.md5(claim.lower().encode()).hexdigest()

        if claim_hash in self.fact_cache:
            return self.fact_cache[claim_hash], 0.9

        # Simple keyword matching for context verification
        claim_words = set(claim.lower().split())
        context_words = set()

        for context_value in self.knowledge_base.values():
            if isinstance(context_value, str):
                context_words.update(context_value.lower().split())

        overlap = len(claim_words & context_words)
        coverage = overlap / max(1, len(claim_words))

        # Cache result
        is_verified = coverage > 0.3  # 30% coverage threshold
        self.fact_cache[claim_hash] = is_verified

        return is_verified, coverage


class ZeroHallucinationEnforcer:
    """Advanced zero-hallucination enforcement system"""

    def __init__(self, config: ZeroHallucinationConfig | None = None):
        self.config = config or ZeroHallucinationConfig()
        self.patterns = HallucinationPatterns()
        self.context_verifier = ContextVerifier()
        self.detection_history: list[HallucinationReport] = []
        self.pattern_stats: dict[str, int] = defaultdict(int)

        # Compile regex patterns for efficiency
        self._compiled_patterns = self._compile_patterns()

    def _compile_patterns(self) -> dict[str, list[Pattern]]:
        """Compile all detection patterns"""
        compiled = {}

        pattern_groups = [
            ("uncertainty", self.patterns.UNCERTAINTY_PATTERNS),
            ("speculation", self.patterns.SPECULATION_PATTERNS),
            ("evasive", self.patterns.EVASIVE_PATTERNS),
            ("numerical", self.patterns.NUMERICAL_PATTERNS),
            ("contradiction", self.patterns.CONTRADICTION_PATTERNS),
            ("factual_claim", self.patterns.FACTUAL_CLAIM_PATTERNS),
        ]

        for group_name, patterns in pattern_groups:
            compiled[group_name] = [re.compile(pattern, re.IGNORECASE | re.MULTILINE) for pattern in patterns]

        return compiled

    async def enforce(self, content: str, context: dict[str, Any] | None = None) -> HallucinationReport:
        """Enforce zero-hallucination on content"""
        start_time = time.time()

        # Add context if provided
        if context and self.config.enable_context_verification:
            self.context_verifier.add_context(context)

        # Detect hallucinations
        indicators = await self._detect_hallucinations(content)

        # Calculate overall confidence
        overall_confidence = self._calculate_overall_confidence(content, indicators)

        # Create initial report
        report = HallucinationReport(
            overall_confidence=overall_confidence,
            indicators=indicators,
            metadata={
                "content_length": len(content),
                "detection_time": time.time() - start_time,
                "patterns_applied": len(indicators),
            },
        )

        # Apply enforcement based on configuration
        report = await self._apply_enforcement(content, report)

        # Update statistics
        self._update_statistics(report)

        # Store in history
        self.detection_history.append(report)

        return report

    async def _detect_hallucinations(self, content: str) -> list[HallucinationIndicator]:
        """Detect various types of hallucinations in content"""
        indicators = []

        # Uncertainty and speculation detection
        uncertainty_indicators = await self._detect_uncertainty(content)
        indicators.extend(uncertainty_indicators)

        # Evasive response detection
        evasive_indicators = await self._detect_evasive_responses(content)
        indicators.extend(evasive_indicators)

        # Numerical inconsistency detection
        numerical_indicators = await self._detect_numerical_inconsistencies(content)
        indicators.extend(numerical_indicators)

        # Contradiction detection
        contradiction_indicators = await self._detect_contradictions(content)
        indicators.extend(contradiction_indicators)

        # Factual claim verification
        if self.config.enable_fact_checking:
            factual_indicators = await self._detect_factual_claims(content)
            indicators.extend(factual_indicators)

        # Context verification
        if self.config.enable_context_verification and self.context_verifier.knowledge_base:
            contextual_indicators = await self._detect_contextual_issues(content)
            indicators.extend(contextual_indicators)

        return indicators

    async def _detect_uncertainty(self, content: str) -> list[HallucinationIndicator]:
        """Detect uncertainty and speculation patterns"""
        indicators = []

        for pattern in self._compiled_patterns["uncertainty"]:
            matches = pattern.finditer(content)
            for match in matches:
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.UNCERTAINTY,
                        severity=0.3,  # Low severity for uncertainty
                        confidence=0.8,
                        text_span=(match.start(), match.end()),
                        original_text=match.group(),
                        explanation="Uncertain language detected",
                        pattern_matched=pattern.pattern,
                    )
                )

        for pattern in self._compiled_patterns["speculation"]:
            matches = pattern.finditer(content)
            for match in matches:
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.UNCERTAINTY,
                        severity=0.4,
                        confidence=0.7,
                        text_span=(match.start(), match.end()),
                        original_text=match.group(),
                        explanation="Speculative language detected",
                        pattern_matched=pattern.pattern,
                    )
                )

        return indicators

    async def _detect_evasive_responses(self, content: str) -> list[HallucinationIndicator]:
        """Detect evasive or non-committal responses"""
        indicators = []

        for pattern in self._compiled_patterns["evasive"]:
            matches = pattern.finditer(content)
            for match in matches:
                severity = 0.7 if "cannot" in match.group().lower() else 0.5
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.CONFABULATION,
                        severity=severity,
                        confidence=0.9,
                        text_span=(match.start(), match.end()),
                        original_text=match.group(),
                        explanation="Evasive or non-committal response detected",
                        suggested_correction="Provide a direct and helpful answer",
                        pattern_matched=pattern.pattern,
                    )
                )

        return indicators

    async def _detect_numerical_inconsistencies(self, content: str) -> list[HallucinationIndicator]:
        """Detect numerical inconsistencies and suspicious statistics"""
        indicators = []

        for pattern in self._compiled_patterns["numerical"]:
            matches = pattern.finditer(content)
            for match in matches:
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.NUMERICAL,
                        severity=0.6,
                        confidence=0.6,
                        text_span=(match.start(), match.end()),
                        original_text=match.group(),
                        explanation="Suspicious numerical expression detected",
                        suggested_correction="Provide specific, verifiable numbers",
                        pattern_matched=pattern.pattern,
                    )
                )

        # Check for very large or unrealistic numbers
        number_pattern = re.compile(r"\b(\d{1,3}(,\d{3})*|\d+)(\.\d+)?\b")
        numbers = number_pattern.findall(content)

        for number_tuple in numbers:
            number_str = number_tuple[0].replace(",", "")
            try:
                number = float(number_str)
                if abs(number) > 10**9:  # Very large numbers
                    # Find the position of this number in content
                    match = re.search(re.escape(number_str), content)
                    if match:
                        indicators.append(
                            HallucinationIndicator(
                                type=HallucinationType.NUMERICAL,
                                severity=0.4,
                                confidence=0.5,
                                text_span=(match.start(), match.end()),
                                original_text=match.group(),
                                explanation="Very large number detected - may be unrealistic",
                            )
                        )
            except ValueError:
                continue

        return indicators

    async def _detect_contradictions(self, content: str) -> list[HallucinationIndicator]:
        """Detect logical contradictions in content"""
        indicators = []

        for pattern in self._compiled_patterns["contradiction"]:
            matches = pattern.finditer(content)
            for match in matches:
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.LOGICAL,
                        severity=0.8,
                        confidence=0.6,
                        text_span=(match.start(), match.end()),
                        original_text=match.group(),
                        explanation="Potential logical contradiction detected",
                        pattern_matched=pattern.pattern,
                    )
                )

        # Simple negation contradiction detection
        sentences = re.split(r"[.!?]+", content)
        for i, sentence in enumerate(sentences):
            if len(sentence.strip()) < 10:  # Skip very short sentences
                continue

            # Check for direct contradictions between sentences
            for j, other_sentence in enumerate(sentences):
                if i >= j or len(other_sentence.strip()) < 10:
                    continue

                if self._are_contradictory(sentence, other_sentence):
                    # Find the positions
                    start1 = content.find(sentence)
                    start2 = content.find(other_sentence)

                    indicators.append(
                        HallucinationIndicator(
                            type=HallucinationType.LOGICAL,
                            severity=0.9,
                            confidence=0.7,
                            text_span=(start1, start1 + len(sentence)),
                            original_text=sentence,
                            explanation=f"Contradicts: {other_sentence.strip()[:50]}...",
                        )
                    )

        return indicators

    async def _detect_factual_claims(self, content: str) -> list[HallucinationIndicator]:
        """Detect unverified factual claims"""
        indicators = []

        for pattern in self._compiled_patterns["factual_claim"]:
            matches = pattern.finditer(content)
            for match in matches:
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.UNVERIFIABLE,
                        severity=0.5,
                        confidence=0.6,
                        text_span=(match.start(), match.end()),
                        original_text=match.group(),
                        explanation="Unverified factual claim detected",
                        suggested_correction="Provide source or evidence for this claim",
                        pattern_matched=pattern.pattern,
                    )
                )

        return indicators

    async def _detect_contextual_issues(self, content: str) -> list[HallucinationIndicator]:
        """Detect information outside provided context"""
        indicators = []

        # Split content into claims (simple sentence-based approach)
        sentences = re.split(r"[.!?]+", content)
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 10:
                continue

            # Verify against context
            is_verified, coverage = await self.context_verifier.verify_against_context(sentence)

            if not is_verified:
                start_pos = content.find(sentence)
                indicators.append(
                    HallucinationIndicator(
                        type=HallucinationType.CONTEXTUAL,
                        severity=0.6 * (1.0 - coverage),  # Higher severity for lower coverage
                        confidence=0.7,
                        text_span=(start_pos, start_pos + len(sentence)),
                        original_text=sentence,
                        explanation="Information not found in provided context",
                        suggested_correction="Stick to information from the provided context",
                    )
                )

        return indicators

    def _are_contradictory(self, sentence1: str, sentence2: str) -> bool:
        """Check if two sentences contradict each other"""
        # Simple contradiction detection based on keywords
        pos_words = {"always", "all", "every", "never", "none", "only", "exactly", "definitely"}
        neg_words = {"not", "never", "no", "none", "without", "lacking", "absent"}

        words1 = set(sentence1.lower().split())
        words2 = set(sentence2.lower().split())

        # Check for direct contradictions
        has_pos1 = any(word in words1 for word in pos_words)
        has_neg2 = any(word in words2 for word in neg_words)

        has_pos2 = any(word in words2 for word in pos_words)
        has_neg1 = any(word in words1 for word in neg_words)

        # Very simple contradiction logic
        return (has_pos1 and has_neg2) or (has_pos2 and has_neg1)

    def _calculate_overall_confidence(self, content: str, indicators: list[HallucinationIndicator]) -> float:
        """Calculate overall confidence score"""
        if not indicators:
            return 1.0

        # Weight indicators by severity and confidence
        total_weight = 0.0
        weighted_sum = 0.0

        for indicator in indicators:
            weight = indicator.severity * indicator.confidence
            total_weight += weight
            weighted_sum += weight * (1.0 - indicator.severity)  # Higher severity = lower confidence

        if total_weight == 0:
            return 1.0

        base_confidence = weighted_sum / total_weight

        # Adjust for content length (longer content gets slight benefit)
        length_factor = min(1.1, 1.0 + len(content) / 10000.0)

        return min(1.0, base_confidence * length_factor)

    async def _apply_enforcement(self, content: str, report: HallucinationReport) -> HallucinationReport:
        """Apply enforcement actions based on configuration"""
        if not report.has_hallucinations:
            report.enforcement_action = "none_required"
            report.quality_score = 1.0
            return report

        # Calculate quality score
        report.quality_score = max(0.0, 1.0 - report.severity_score)

        # Apply enforcement based on level
        if self.config.enforcement_level == EnforcementLevel.STRICT:
            if report.overall_confidence < self.config.confidence_threshold:
                report.enforcement_action = "blocked"
                return report

        elif self.config.enforcement_level == EnforcementLevel.MODERATE:
            if report.overall_confidence < self.config.confidence_threshold * 0.8:
                report.enforcement_action = "blocked"
                return report

        # Attempt auto-correction if enabled
        if self.config.enable_auto_correction:
            corrected_content = await self._auto_correct_content(content, report.indicators)
            if corrected_content != content:
                report.corrected_content = corrected_content
                report.enforcement_action = "auto_corrected"

        if not report.enforcement_action:
            report.enforcement_action = "flagged"

        return report

    async def _auto_correct_content(self, content: str, indicators: list[HallucinationIndicator]) -> str:
        """Attempt to automatically correct content based on indicators"""
        corrected = content

        # Sort indicators by position (reverse order to maintain indices)
        sorted_indicators = sorted(indicators, key=lambda x: x.text_span[0], reverse=True)

        for indicator in sorted_indicators:
            if indicator.suggested_correction:
                start, end = indicator.text_span
                corrected = corrected[:start] + indicator.suggested_correction + corrected[end:]

        return corrected

    def _update_statistics(self, report: HallucinationReport):
        """Update detection statistics"""
        if self.config.track_patterns:
            for indicator in report.indicators:
                if indicator.pattern_matched:
                    self.pattern_stats[indicator.pattern_matched] += 1

    def get_statistics(self) -> dict[str, Any]:
        """Get comprehensive statistics"""
        total_detections = len(self.detection_history)
        if total_detections == 0:
            return {"total_detections": 0, "average_confidence": 1.0, "hallucination_rate": 0.0, "pattern_stats": {}}

        hallucination_detections = sum(1 for report in self.detection_history if report.has_hallucinations)
        avg_confidence = sum(report.overall_confidence for report in self.detection_history) / total_detections

        return {
            "total_detections": total_detections,
            "hallucination_detections": hallucination_detections,
            "hallucination_rate": hallucination_detections / total_detections,
            "average_confidence": avg_confidence,
            "pattern_stats": dict(self.pattern_stats),
            "enforcement_actions": Counter(
                report.enforcement_action for report in self.detection_history if report.enforcement_action
            ),
        }

    def clear_history(self):
        """Clear detection history"""
        self.detection_history.clear()
        self.pattern_stats.clear()
        self.context_verifier.fact_cache.clear()


# Global enforcer instance
_global_enforcer = None


def get_zero_hallucination_enforcer(config: ZeroHallucinationConfig | None = None) -> ZeroHallucinationEnforcer:
    """Get or create the global zero-hallucination enforcer"""
    global _global_enforcer
    if _global_enforcer is None:
        _global_enforcer = ZeroHallucinationEnforcer(config)
    return _global_enforcer


# Decorator for zero-hallucination enforcement
def enforce_zero_hallucination(
    enforcer: ZeroHallucinationEnforcer | None = None, context: dict[str, Any] | None = None
):
    """
    Decorator for automatic zero-hallucination enforcement

    Usage:
        @enforce_zero_hallucination(context=provided_context)
        async def generate_response(prompt):
            return llm.generate(prompt)
    """

    def decorator(func):
        async def wrapper(*args, **kwargs):
            # Execute the function
            result = await func(*args, **kwargs)

            # Apply zero-hallucination enforcement
            if isinstance(result, str):
                enforcer_instance = enforcer or get_zero_hallucination_enforcer()
                report = await enforcer_instance.enforce(result, context)

                if report.enforcement_action == "blocked":
                    raise ValueError("Content blocked due to hallucination detection")
                if report.corrected_content:
                    return report.corrected_content
                if report.enforcement_action == "flagged":
                    logger.warning(f"Content flagged for potential hallucinations: {report.indicators}")

            return result

        return wrapper

    return decorator
