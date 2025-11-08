"""
Domain-Specific Reward Structures for Mechanical Engineering Agents.

This module implements specialized reward functions for CAD analysis, RAG quality,
and UI generation that align with engineering priorities and safety requirements.
"""

import re
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

import numpy as np

from ..utils.logger import get_logger

logger = get_logger(__name__)


class RewardComponent(Enum):
    """Types of reward components."""

    ACCURACY = "accuracy"
    SAFETY = "safety"
    EFFICIENCY = "efficiency"
    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    STANDARDS_COMPLIANCE = "standards_compliance"
    MANUFACTURABILITY = "manufacturability"
    USER_EXPERIENCE = "user_experience"
    PERFORMANCE = "performance"


class SeverityLevel(Enum):
    """Severity levels for engineering issues."""

    CRITICAL = 5
    HIGH = 4
    MEDIUM = 3
    LOW = 2
    INFO = 1


@dataclass
class EvaluationResult:
    """Result of an evaluation."""

    score: float
    confidence: float
    details: dict[str, Any]
    issues: list[dict[str, Any]] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)


class BaseRewardFunction(ABC):
    """Base class for domain-specific reward functions."""

    def __init__(self, weights: dict[RewardComponent, float]):
        self.weights = weights
        self._validate_weights()

    def _validate_weights(self):
        """Validate that weights sum to 1.0."""
        total = sum(self.weights.values())
        if abs(total - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {total}")

    @abstractmethod
    async def evaluate(self, prediction: Any, ground_truth: Any, context: dict[str, Any]) -> EvaluationResult:
        """Evaluate a prediction against ground truth."""
        pass

    def compute_weighted_reward(self, component_scores: dict[RewardComponent, float]) -> float:
        """Compute weighted reward from component scores."""
        total_reward = 0.0
        for component, score in component_scores.items():
            weight = self.weights.get(component, 0.0)
            total_reward += weight * score
        return total_reward


class CADAnalysisRewardFunction(BaseRewardFunction):
    """Reward function for CAD analysis and design review."""

    def __init__(self):
        # Engineering-focused weights
        weights = {
            RewardComponent.SAFETY: 0.30,  # Highest priority for engineering
            RewardComponent.ACCURACY: 0.25,
            RewardComponent.STANDARDS_COMPLIANCE: 0.20,
            RewardComponent.MANUFACTURABILITY: 0.15,
            RewardComponent.COMPLETENESS: 0.10,
        }
        super().__init__(weights)

    async def evaluate(self, prediction: Any, ground_truth: Any, context: dict[str, Any]) -> EvaluationResult:
        """Evaluate CAD analysis prediction."""
        component_scores = {}

        # Safety evaluation
        safety_score, safety_issues = await self._evaluate_safety(prediction, ground_truth)
        component_scores[RewardComponent.SAFETY] = safety_score

        # Accuracy evaluation
        accuracy_score, accuracy_details = await self._evaluate_accuracy(prediction, ground_truth)
        component_scores[RewardComponent.ACCURACY] = accuracy_score

        # Standards compliance
        compliance_score, compliance_issues = await self._evaluate_standards_compliance(prediction, context)
        component_scores[RewardComponent.STANDARDS_COMPLIANCE] = compliance_score

        # Manufacturability
        manufacturability_score, manufacturing_issues = await self._evaluate_manufacturability(prediction, context)
        component_scores[RewardComponent.MANUFACTURABILITY] = manufacturability_score

        # Completeness
        completeness_score = await self._evaluate_completeness(prediction, ground_truth)
        component_scores[RewardComponent.COMPLETENESS] = completeness_score

        # Compute weighted reward
        total_reward = self.compute_weighted_reward(component_scores)

        # Aggregate all issues
        all_issues = safety_issues + compliance_issues + manufacturing_issues

        # Generate recommendations
        recommendations = await self._generate_recommendations(prediction, all_issues)

        return EvaluationResult(
            score=total_reward,
            confidence=self._compute_confidence(component_scores),
            details={
                "component_scores": {comp.value: score for comp, score in component_scores.items()},
                "weights": {comp.value: weight for comp, weight in self.weights.items()},
            },
            issues=all_issues,
            recommendations=recommendations,
        )

    async def _evaluate_safety(self, prediction: Any, ground_truth: Any) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate safety aspects of CAD analysis."""
        safety_score = 1.0
        safety_issues = []

        # Check for critical safety issues in prediction
        if hasattr(prediction, "recommendations"):
            for rec in prediction.recommendations:
                if rec.severity.value == "critical":
                    safety_score -= 0.3
                    safety_issues.append(
                        {
                            "type": "critical_safety_issue",
                            "description": rec.description,
                            "severity": SeverityLevel.CRITICAL.value,
                        }
                    )
                elif rec.severity.value == "high":
                    safety_score -= 0.1
                    safety_issues.append(
                        {
                            "type": "high_safety_issue",
                            "description": rec.description,
                            "severity": SeverityLevel.HIGH.value,
                        }
                    )

        # Evaluate structural safety if available
        if hasattr(prediction, "structural_data") and prediction.structural_data:
            safety_factors = list(prediction.structural_data.safety_factors.values())
            if safety_factors:
                min_sf = min(safety_factors)
                if min_sf < 1.5:  # Critical safety threshold
                    safety_score -= 0.4
                    safety_issues.append(
                        {
                            "type": "low_safety_factor",
                            "description": f"Minimum safety factor {min_sf:.2f} below critical threshold",
                            "severity": SeverityLevel.CRITICAL.value,
                        }
                    )
                elif min_sf < 2.0:  # Warning threshold
                    safety_score -= 0.2
                    safety_issues.append(
                        {
                            "type": "low_safety_factor",
                            "description": f"Minimum safety factor {min_sf:.2f} below recommended threshold",
                            "severity": SeverityLevel.HIGH.value,
                        }
                    )

        # Acoustic safety (noise levels)
        if hasattr(prediction, "acoustic_data") and prediction.acoustic_data:
            stc = prediction.acoustic_data.predicted_stc
            if stc < 25:  # Poor acoustic performance
                safety_score -= 0.15
                safety_issues.append(
                    {
                        "type": "poor_acoustic_performance",
                        "description": f"STC rating {stc} below recommended minimum",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

        return max(0.0, safety_score), safety_issues

    async def _evaluate_accuracy(self, prediction: Any, ground_truth: Any) -> tuple[float, dict[str, Any]]:
        """Evaluate accuracy of CAD analysis."""
        accuracy_score = 0.8  # Base score
        details = {}

        # Compare with expert rating if available
        if hasattr(ground_truth, "expert_rating") and hasattr(prediction, "overall_rating"):
            expert_rating = ground_truth.expert_rating
            predicted_rating = prediction.overall_rating

            if expert_rating and predicted_rating:
                # Normalize to 0-1 scale
                expert_norm = (expert_rating - 1) / 4  # Assuming 1-5 scale
                predicted_norm = (predicted_rating - 1) / 4

                accuracy_score = 1.0 - abs(expert_norm - predicted_norm)
                details["rating_difference"] = abs(expert_rating - predicted_rating)

        # Check recommendation accuracy
        if hasattr(ground_truth, "expert_recommendations") and hasattr(prediction, "recommendations"):
            expert_recs = ground_truth.expert_recommendations
            predicted_recs = prediction.recommendations

            # Simple similarity check based on severity distribution
            expert_severity_dist = self._get_severity_distribution(expert_recs)
            predicted_severity_dist = self._get_severity_distribution(predicted_recs)

            similarity = sum(
                min(expert_severity_dist.get(sev, 0), predicted_severity_dist.get(sev, 0))
                for sev in ["critical", "high", "medium", "low", "info"]
            )

            details["recommendation_similarity"] = similarity
            accuracy_score = (accuracy_score + similarity) / 2

        return max(0.0, min(1.0, accuracy_score)), details

    async def _evaluate_standards_compliance(
        self, prediction: Any, context: dict[str, Any]
    ) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate compliance with engineering standards."""
        compliance_score = 0.9  # Start with high score
        compliance_issues = []

        # Check for common engineering standards
        standards_to_check = ["ISO", "ASME", "ASTM", "ANSI", "OSHA", "NFPA"]

        mentioned_standards = []
        if hasattr(prediction, "recommendations"):
            recommendation_text = " ".join(rec.description for rec in prediction.recommendations).lower()

            for standard in standards_to_check:
                if standard.lower() in recommendation_text:
                    mentioned_standards.append(standard)

        if not mentioned_standards:
            compliance_score -= 0.2
            compliance_issues.append(
                {
                    "type": "missing_standards_reference",
                    "description": "No engineering standards referenced in analysis",
                    "severity": SeverityLevel.MEDIUM.value,
                }
            )

        # Check for material specifications
        if hasattr(prediction, "material_specifications") and not prediction.material_specifications:
            compliance_score -= 0.1
            compliance_issues.append(
                {
                    "type": "missing_material_specs",
                    "description": "Material specifications not provided",
                    "severity": SeverityLevel.LOW.value,
                }
            )

        # Tolerance specifications
        if hasattr(prediction, "tolerance_analysis") and not prediction.tolerance_analysis:
            compliance_score -= 0.15
            compliance_issues.append(
                {
                    "type": "missing_tolerance_analysis",
                    "description": "Tolerance analysis not performed",
                    "severity": SeverityLevel.MEDIUM.value,
                }
            )

        return max(0.0, compliance_score), compliance_issues

    async def _evaluate_manufacturability(
        self, prediction: Any, context: dict[str, Any]
    ) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate manufacturability aspects."""
        manufacturability_score = 0.85
        manufacturing_issues = []

        if hasattr(prediction, "manufacturing_data") and prediction.manufacturing_data:
            # CNC feasibility
            cnc_feasibility = prediction.manufacturing_data.cnc_feasibility
            if cnc_feasibility < 0.7:
                manufacturability_score -= 0.2
                manufacturing_issues.append(
                    {
                        "type": "low_cnc_feasibility",
                        "description": f"CNC feasibility {cnc_feasibility:.2f} below recommended threshold",
                        "severity": SeverityLevel.HIGH.value,
                    }
                )

            # Tool access issues
            tool_issues = len(prediction.manufacturing_data.tool_access_issues)
            if tool_issues > 5:
                manufacturability_score -= 0.15
                manufacturing_issues.append(
                    {
                        "type": "excessive_tool_access_issues",
                        "description": f"{tool_issues} tool access issues identified",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

            # Cost estimation
            if hasattr(prediction.manufacturing_data, "estimated_cost"):
                cost = prediction.manufacturing_data.estimated_cost
                if cost > 1000:  # High cost threshold
                    manufacturability_score -= 0.1
                    manufacturing_issues.append(
                        {
                            "type": "high_manufacturing_cost",
                            "description": f"Estimated manufacturing cost ${cost:.0f} above target",
                            "severity": SeverityLevel.LOW.value,
                        }
                    )

        return max(0.0, manufacturability_score), manufacturing_issues

    async def _evaluate_completeness(self, prediction: Any, ground_truth: Any) -> float:
        """Evaluate completeness of analysis."""
        completeness_score = 0.0
        total_checks = 0

        # Check for required analysis types
        required_analyses = ["acoustic_analysis", "structural_analysis", "manufacturing_analysis", "recommendations"]

        for analysis in required_analyses:
            total_checks += 1
            if hasattr(prediction, analysis):
                completeness_score += 1.0

        # Check recommendation completeness
        if hasattr(prediction, "recommendations"):
            rec_count = len(prediction.recommendations)
            if rec_count >= 5:
                completeness_score += 1.0
            elif rec_count >= 3:
                completeness_score += 0.7
            elif rec_count >= 1:
                completeness_score += 0.4
            total_checks += 1

        return completeness_score / total_checks if total_checks > 0 else 0.0

    async def _generate_recommendations(self, prediction: Any, issues: list[dict[str, Any]]) -> list[str]:
        """Generate improvement recommendations."""
        recommendations = []

        critical_issues = [issue for issue in issues if issue.get("severity") == SeverityLevel.CRITICAL.value]
        if critical_issues:
            recommendations.append("Address critical safety issues immediately before proceeding")

        high_issues = [issue for issue in issues if issue.get("severity") == SeverityLevel.HIGH.value]
        if high_issues:
            recommendations.append("Review and resolve high-priority engineering concerns")

        if not hasattr(prediction, "material_specifications") or not prediction.material_specifications:
            recommendations.append("Include detailed material specifications in analysis")

        if not hasattr(prediction, "tolerance_analysis") or not prediction.tolerance_analysis:
            recommendations.append("Perform comprehensive tolerance analysis")

        return recommendations

    def _get_severity_distribution(self, recommendations: list[Any]) -> dict[str, float]:
        """Get distribution of recommendation severities."""
        distribution = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        total = len(recommendations)

        if total == 0:
            return distribution

        for rec in recommendations:
            severity = rec.severity.value if hasattr(rec, "severity") else "info"
            if severity in distribution:
                distribution[severity] += 1

        # Convert to proportions
        for key in distribution:
            distribution[key] /= total

        return distribution

    def _compute_confidence(self, component_scores: dict[RewardComponent, float]) -> float:
        """Compute overall confidence based on component score variance."""
        scores = list(component_scores.values())
        if not scores:
            return 0.0

        # Lower variance indicates higher confidence
        variance = np.var(scores)
        confidence = 1.0 / (1.0 + variance * 4)  # Scale variance impact

        return max(0.1, min(1.0, confidence))


class RAGQualityRewardFunction(BaseRewardFunction):
    """Reward function for RAG-based technical Q&A quality."""

    def __init__(self):
        # RAG-specific weights
        weights = {
            RewardComponent.ACCURACY: 0.35,  # Most important for technical answers
            RewardComponent.CLARITY: 0.25,
            RewardComponent.COMPLETENESS: 0.20,
            RewardComponent.SAFETY: 0.15,  # Critical for technical advice
            RewardComponent.STANDARDS_COMPLIANCE: 0.05,
        }
        super().__init__(weights)

    async def evaluate(self, prediction: Any, ground_truth: Any, context: dict[str, Any]) -> EvaluationResult:
        """Evaluate RAG response quality."""
        component_scores = {}

        # Accuracy evaluation
        accuracy_score, accuracy_details = await self._evaluate_answer_accuracy(prediction, ground_truth)
        component_scores[RewardComponent.ACCURACY] = accuracy_score

        # Clarity evaluation
        clarity_score, clarity_issues = await self._evaluate_clarity(prediction)
        component_scores[RewardComponent.CLARITY] = clarity_score

        # Completeness evaluation
        completeness_score, completeness_issues = await self._evaluate_completeness(prediction, ground_truth)
        component_scores[RewardComponent.COMPLETENESS] = completeness_score

        # Safety evaluation
        safety_score, safety_issues = await self._evaluate_safety(prediction, context)
        component_scores[RewardComponent.SAFETY] = safety_score

        # Standards compliance
        compliance_score = await self._evaluate_standards_compliance(prediction)
        component_scores[RewardComponent.STANDARDS_COMPLIANCE] = compliance_score

        # Compute weighted reward
        total_reward = self.compute_weighted_reward(component_scores)

        # Aggregate issues
        all_issues = clarity_issues + completeness_issues + safety_issues

        # Generate recommendations
        recommendations = await self._generate_rag_recommendations(prediction, all_issues)

        return EvaluationResult(
            score=total_reward,
            confidence=self._compute_confidence(component_scores),
            details={
                "component_scores": {comp.value: score for comp, score in component_scores.items()},
                "weights": {comp.value: weight for comp, weight in self.weights.items()},
                "accuracy_details": accuracy_details,
            },
            issues=all_issues,
            recommendations=recommendations,
        )

    async def _evaluate_answer_accuracy(self, prediction: Any, ground_truth: Any) -> tuple[float, dict[str, Any]]:
        """Evaluate accuracy of RAG answer."""
        accuracy_score = 0.0
        details = {}

        if hasattr(prediction, "answer") and hasattr(ground_truth, "expected_answer"):
            predicted_answer = prediction.answer.lower()
            expected_answer = ground_truth.expected_answer.lower()

            # Simple semantic similarity (in practice, use embeddings)
            similarity = self._compute_text_similarity(predicted_answer, expected_answer)
            details["text_similarity"] = similarity
            accuracy_score = similarity * 0.6

            # Check for key concepts
            predicted_concepts = set(self._extract_technical_terms(predicted_answer))
            expected_concepts = set(self._extract_technical_terms(expected_answer))

            if expected_concepts:
                concept_overlap = len(predicted_concepts & expected_concepts) / len(expected_concepts)
                details["concept_overlap"] = concept_overlap
                accuracy_score += concept_overlap * 0.4

            # Check source attribution
            if hasattr(prediction, "sources") and prediction.sources:
                source_count = len(prediction.sources)
                details["source_count"] = source_count
                accuracy_score += min(0.2, source_count * 0.05)  # Bonus for citing sources

        return min(1.0, accuracy_score), details

    async def _evaluate_clarity(self, prediction: Any) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate clarity of RAG response."""
        clarity_score = 0.8
        clarity_issues = []

        if hasattr(prediction, "answer"):
            answer = prediction.answer

            # Check answer length
            if len(answer) < 50:
                clarity_score -= 0.3
                clarity_issues.append(
                    {
                        "type": "answer_too_short",
                        "description": "Answer is too brief to be helpful",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )
            elif len(answer) > 2000:
                clarity_score -= 0.1
                clarity_issues.append(
                    {
                        "type": "answer_too_long",
                        "description": "Answer is excessively long",
                        "severity": SeverityLevel.LOW.value,
                    }
                )

            # Check for technical jargon explanation
            technical_terms = self._extract_technical_terms(answer)
            if len(technical_terms) > 5:
                # Check if terms are explained
                explained_terms = sum(1 for term in technical_terms if f"({term})" in answer or f"{term} is" in answer)
                if explained_terms < len(technical_terms) * 0.5:
                    clarity_score -= 0.2
                    clarity_issues.append(
                        {
                            "type": "unexplained_jargon",
                            "description": f"{len(technical_terms) - explained_terms} technical terms not explained",
                            "severity": SeverityLevel.MEDIUM.value,
                        }
                    )

            # Check structure
            if not any(marker in answer for marker in [":", "•", "-", "1.", "2."]):
                clarity_score -= 0.15
                clarity_issues.append(
                    {
                        "type": "poor_structure",
                        "description": "Answer lacks clear structure or formatting",
                        "severity": SeverityLevel.LOW.value,
                    }
                )

        return max(0.0, clarity_score), clarity_issues

    async def _evaluate_completeness(self, prediction: Any, ground_truth: Any) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate completeness of RAG response."""
        completeness_score = 0.7
        completeness_issues = []

        if hasattr(prediction, "answer") and hasattr(ground_truth, "expected_answer"):
            # Check if all parts of the question are addressed
            expected_sections = self._identify_expected_sections(ground_truth.expected_answer)
            answer_sections = self._identify_expected_sections(prediction.answer)

            missing_sections = expected_sections - answer_sections
            if missing_sections:
                completeness_score -= len(missing_sections) * 0.1
                completeness_issues.append(
                    {
                        "type": "missing_sections",
                        "description": f"Missing sections: {', '.join(missing_sections)}",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

            # Check for actionable advice
            if "how" in ground_truth.expected_answer.lower() and not any(
                step_word in prediction.answer.lower() for step_word in ["step", "first", "then", "next", "finally"]
            ):
                completeness_score -= 0.2
                completeness_issues.append(
                    {
                        "type": "missing_procedure",
                        "description": "Question asks 'how' but no procedure provided",
                        "severity": SeverityLevel.HIGH.value,
                    }
                )

        return max(0.0, completeness_score), completeness_issues

    async def _evaluate_safety(self, prediction: Any, context: dict[str, Any]) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate safety aspects of technical advice."""
        safety_score = 1.0
        safety_issues = []

        if hasattr(prediction, "answer"):
            answer = prediction.answer.lower()

            # Check for safety warnings
            safety_keywords = ["danger", "warning", "caution", "safety", "risk", "hazard"]
            has_safety_warning = any(keyword in answer for keyword in safety_keywords)

            # Check for dangerous procedures
            dangerous_contexts = ["high pressure", "electrical", "chemical", "heat", "moving parts"]
            has_dangerous_context = any(context in answer for context in dangerous_contexts)

            if has_dangerous_context and not has_safety_warning:
                safety_score -= 0.4
                safety_issues.append(
                    {
                        "type": "missing_safety_warning",
                        "description": "Dangerous procedure discussed without safety warnings",
                        "severity": SeverityLevel.HIGH.value,
                    }
                )

            # Check for PPE recommendations
            if has_dangerous_context and not any(
                ppe in answer for ppe in ["ppe", "safety gear", "protective", "equipment"]
            ):
                safety_score -= 0.2
                safety_issues.append(
                    {
                        "type": "missing_ppe_recommendation",
                        "description": "No PPE recommendations for dangerous procedure",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

        return max(0.0, safety_score), safety_issues

    async def _evaluate_standards_compliance(self, prediction: Any) -> float:
        """Evaluate compliance with technical standards."""
        compliance_score = 0.8

        if hasattr(prediction, "answer"):
            answer = prediction.answer.lower()

            # Check for standards references
            standards_patterns = [
                r"\biso\s*\d+",
                r"\basme\s*\d+",
                r"\bansi\s*\d+",
                r"\bastm\s*\d+",
                r"\bosha\s*\d+",
                r"\bnfpa\s*\d+",
            ]

            has_standard_reference = any(re.search(pattern, answer) for pattern in standards_patterns)
            if has_standard_reference:
                compliance_score += 0.1

            # Check for qualified statements
            qualification_words = ["typically", "generally", "usually", "often", "may", "might"]
            has_qualifications = any(word in answer for word in qualification_words)
            if has_qualifications:
                compliance_score += 0.05

        return min(1.0, compliance_score)

    async def _generate_rag_recommendations(self, prediction: Any, issues: list[dict[str, Any]]) -> list[str]:
        """Generate improvement recommendations for RAG responses."""
        recommendations = []

        critical_issues = [issue for issue in issues if issue.get("severity") == SeverityLevel.HIGH.value]
        if critical_issues:
            recommendations.append("Address high-severity issues in technical response")

        if hasattr(prediction, "answer"):
            answer = prediction.answer
            if len(answer) < 100:
                recommendations.append("Provide more detailed and comprehensive answers")

            if not any(marker in answer for marker in [":", "•", "-", "1.", "2."]):
                recommendations.append("Improve answer structure with clear formatting")

            technical_terms = self._extract_technical_terms(answer)
            unexplained_terms = [
                term for term in technical_terms if f"({term})" not in answer and f"{term} is" not in answer
            ]
            if unexplained_terms:
                recommendations.append(f"Explain technical terms: {', '.join(unexplained_terms[:3])}")

        return recommendations

    def _compute_text_similarity(self, text1: str, text2: str) -> float:
        """Compute simple text similarity."""
        # Simple word overlap similarity (in practice, use embeddings)
        words1 = set(text1.split())
        words2 = set(text2.split())

        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0

        intersection = words1 & words2
        union = words1 | words2

        return len(intersection) / len(union)

    def _extract_technical_terms(self, text: str) -> list[str]:
        """Extract technical terms from text."""
        # Simple heuristic for technical terms
        technical_patterns = [
            r"\b[A-Z]{2,}\b",  # Acronyms
            r"\b\d+\s*[a-zA-Z]+\b",  # Technical specifications
            r"\b[a-zA-Z]+\d+\b",  # Part numbers
            r"\b(?:psi|mpa|nm|mm|kg|kw|hp|v|a)\b",  # Units
        ]

        technical_terms = []
        for pattern in technical_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            technical_terms.extend(matches)

        return list(set(technical_terms))

    def _identify_expected_sections(self, text: str) -> set:
        """Identify expected sections in technical answer."""
        section_indicators = [
            "overview",
            "procedure",
            "safety",
            "materials",
            "tools",
            "steps",
            "warning",
            "note",
            "conclusion",
            "summary",
        ]

        found_sections = set()
        text_lower = text.lower()

        for section in section_indicators:
            if section in text_lower:
                found_sections.add(section)

        return found_sections


class UIQualityRewardFunction(BaseRewardFunction):
    """Reward function for industrial UI generation quality."""

    def __init__(self):
        # UI-specific weights
        weights = {
            RewardComponent.USER_EXPERIENCE: 0.30,
            RewardComponent.PERFORMANCE: 0.25,
            RewardComponent.ACCESSIBILITY: 0.20,
            RewardComponent.STANDARDS_COMPLIANCE: 0.15,
            RewardComponent.CLARITY: 0.10,
        }
        super().__init__(weights)

    async def evaluate(self, prediction: Any, ground_truth: Any, context: dict[str, Any]) -> EvaluationResult:
        """Evaluate UI generation quality."""
        component_scores = {}

        # User experience evaluation
        ux_score, ux_issues = await self._evaluate_user_experience(prediction, context)
        component_scores[RewardComponent.USER_EXPERIENCE] = ux_score

        # Performance evaluation
        performance_score, performance_issues = await self._evaluate_performance(prediction)
        component_scores[RewardComponent.PERFORMANCE] = performance_score

        # Accessibility evaluation
        accessibility_score, accessibility_issues = await self._evaluate_accessibility(prediction)
        component_scores[RewardComponent.ACCESSIBILITY] = accessibility_score

        # Standards compliance
        compliance_score = await self._evaluate_html_standards(prediction)
        component_scores[RewardComponent.STANDARDS_COMPLIANCE] = compliance_score

        # Clarity evaluation
        clarity_score = await self._evaluate_code_clarity(prediction)
        component_scores[RewardComponent.CLARITY] = clarity_score

        # Compute weighted reward
        total_reward = self.compute_weighted_reward(component_scores)

        # Aggregate issues
        all_issues = ux_issues + performance_issues + accessibility_issues

        # Generate recommendations
        recommendations = await self._generate_ui_recommendations(prediction, all_issues)

        return EvaluationResult(
            score=total_reward,
            confidence=self._compute_confidence(component_scores),
            details={
                "component_scores": {comp.value: score for comp, score in component_scores.items()},
                "weights": {comp.value: weight for comp, weight in self.weights.items()},
            },
            issues=all_issues,
            recommendations=recommendations,
        )

    async def _evaluate_user_experience(
        self, prediction: Any, context: dict[str, Any]
    ) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate user experience aspects of generated UI."""
        ux_score = 0.8
        ux_issues = []

        if hasattr(prediction, "code"):
            code = prediction.code.lower()

            # Check for responsive design
            if not any(responsive in code for responsive in ["responsive", "mobile", "@media", "flex", "grid"]):
                ux_score -= 0.2
                ux_issues.append(
                    {
                        "type": "missing_responsive_design",
                        "description": "UI not designed for multiple screen sizes",
                        "severity": SeverityLevel.HIGH.value,
                    }
                )

            # Check for high contrast (important for factory environments)
            if "contrast" not in code:
                ux_score -= 0.15
                ux_issues.append(
                    {
                        "type": "low_contrast",
                        "description": "No high contrast considerations for factory environment",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

            # Check for interactive elements
            interactive_elements = ["button", "input", "select", "form", "onclick", "onchange"]
            has_interactive = any(element in code for element in interactive_elements)

            if not has_interactive:
                ux_score -= 0.1
                ux_issues.append(
                    {
                        "type": "missing_interactive_elements",
                        "description": "UI lacks interactive elements",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

            # Check for error handling
            if "error" not in code and "validation" not in code:
                ux_score -= 0.1
                ux_issues.append(
                    {
                        "type": "missing_error_handling",
                        "description": "No error handling or validation implemented",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

        return max(0.0, ux_score), ux_issues

    async def _evaluate_performance(self, prediction: Any) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate performance aspects of generated UI."""
        performance_score = 0.9
        performance_issues = []

        if hasattr(prediction, "code"):
            code = prediction.code

            # Check for large inline styles
            inline_style_pattern = r'syle="[^"]*"'
            inline_styles = re.findall(inline_style_pattern, code)
            if len(inline_styles) > 10:
                performance_score -= 0.1
                performance_issues.append(
                    {
                        "type": "excessive_inline_styles",
                        "description": f"{len(inline_styles)} inline styles may affect performance",
                        "severity": SeverityLevel.LOW.value,
                    }
                )

            # Check for optimized images
            if "img" in code.lower() and "alt" not in code.lower():
                performance_score -= 0.05
                performance_issues.append(
                    {
                        "type": "missing_image_optimization",
                        "description": "Images missing alt attributes for accessibility and performance",
                        "severity": SeverityLevel.LOW.value,
                    }
                )

            # Check for minified code indicators
            if len(code) > 10000 and "\n" in code:  # Large code with newlines
                performance_score -= 0.05
                performance_issues.append(
                    {
                        "type": "unoptimized_code_size",
                        "description": "Large code file could be minified for better performance",
                        "severity": SeverityLevel.LOW.value,
                    }
                )

        return max(0.0, performance_score), performance_issues

    async def _evaluate_accessibility(self, prediction: Any) -> tuple[float, list[dict[str, Any]]]:
        """Evaluate accessibility of generated UI."""
        accessibility_score = 0.8
        accessibility_issues = []

        if hasattr(prediction, "code"):
            code = prediction.code.lower()

            # Check for semantic HTML
            semantic_tags = ["header", "nav", "main", "section", "article", "aside", "footer"]
            has_semantic = any(tag in code for tag in semantic_tags)

            if not has_semantic:
                accessibility_score -= 0.2
                accessibility_issues.append(
                    {
                        "type": "missing_semantic_html",
                        "description": "No semantic HTML5 tags used for accessibility",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

            # Check for ARIA labels
            if "aria-" not in code:
                accessibility_score -= 0.15
                accessibility_issues.append(
                    {
                        "type": "missing_aria_labels",
                        "description": "No ARIA labels for screen reader accessibility",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

            # Check for keyboard navigation
            if "tabindex" not in code and "onkeydown" not in code:
                accessibility_score -= 0.1
                accessibility_issues.append(
                    {
                        "type": "missing_keyboard_navigation",
                        "description": "No keyboard navigation support implemented",
                        "severity": SeverityLevel.MEDIUM.value,
                    }
                )

        return max(0.0, accessibility_score), accessibility_issues

    async def _evaluate_html_standards(self, prediction: Any) -> float:
        """Evaluate compliance with HTML standards."""
        compliance_score = 0.9

        if hasattr(prediction, "code"):
            code = prediction.code

            # Check for proper DOCTYPE
            if not code.strip().startswith("<!DOCTYPE"):
                compliance_score -= 0.1

            # Check for proper HTML structure
            if "<html" not in code or "<head" not in code or "<body" not in code:
                compliance_score -= 0.1

            # Check for proper closing tags
            open_tags = re.findall(r"<(\w+)[^>]*>", code)
            close_tags = re.findall(r"</(\w+)>", code)

            # Self-closing tags don't need closing tags
            self_closing = {"img", "br", "hr", "input", "meta", "link"}
            required_closes = [tag for tag in open_tags if tag not in self_closing]

            if len(required_closes) != len(close_tags):
                compliance_score -= 0.1

        return max(0.0, compliance_score)

    async def _evaluate_code_clarity(self, prediction: Any) -> float:
        """Evaluate code clarity and maintainability."""
        clarity_score = 0.8

        if hasattr(prediction, "code"):
            code = prediction.code

            # Check for comments
            if "//" not in code and "/*" not in code:
                clarity_score -= 0.1

            # Check for consistent indentation
            lines = code.split("\n")
            indented_lines = [line for line in lines if line.strip().startswith((" ", "\t"))]
            if indented_lines and len(indented_lines) < len(lines) * 0.3:
                clarity_score -= 0.1

            # Check for meaningful class/ID names
            if re.search(r'\bclass="(?:c\d+|div\d+|item\d+)"\b', code):
                clarity_score -= 0.05

        return max(0.0, clarity_score)

    async def _generate_ui_recommendations(self, prediction: Any, issues: list[dict[str, Any]]) -> list[str]:
        """Generate improvement recommendations for UI generation."""
        recommendations = []

        if hasattr(prediction, "code"):
            code = prediction.code.lower()

            if "responsive" not in code:
                recommendations.append("Implement responsive design for multiple screen sizes")

            if "contrast" not in code:
                recommendations.append("Add high contrast styling for factory environment visibility")

            if "aria-" not in code:
                recommendations.append("Include ARIA labels for screen reader accessibility")

            interactive_elements = ["button", "input", "select", "form"]
            if not any(element in code for element in interactive_elements):
                recommendations.append("Add interactive elements for better user engagement")

            if "error" not in code:
                recommendations.append("Implement error handling and user feedback")

        return recommendations

    def _compute_confidence(self, component_scores: dict[RewardComponent, float]) -> float:
        """Compute overall confidence based on component score variance."""
        scores = list(component_scores.values())
        if not scores:
            return 0.0

        variance = np.var(scores)
        confidence = 1.0 / (1.0 + variance * 4)

        return max(0.1, min(1.0, confidence))


class RewardFunctionRegistry:
    """Registry for domain-specific reward functions."""

    def __init__(self):
        self._functions = {
            "cad_analysis": CADAnalysisRewardFunction(),
            "rag_quality": RAGQualityRewardFunction(),
            "ui_generation": UIQualityRewardFunction(),
        }

    def get_reward_function(self, domain: str) -> BaseRewardFunction:
        """Get reward function for a specific domain."""
        if domain not in self._functions:
            raise ValueError(f"Unknown domain: {domain}. Available domains: {list(self._functions.keys())}")
        return self._functions[domain]

    def register_reward_function(self, domain: str, function: BaseRewardFunction):
        """Register a new reward function."""
        self._functions[domain] = function

    def list_domains(self) -> list[str]:
        """List available domains."""
        return list(self._functions.keys())
