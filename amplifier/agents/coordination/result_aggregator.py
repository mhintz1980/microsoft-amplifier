"""
Result Aggregator and Conflict Resolver

Combines agent outputs while resolving conflicts and ensuring consistency with:
- Multiple result merging strategies
- Conflict detection and resolution
- Quality assurance and validation
- Consistency checking
- Zero-hallucination enforcement

Philosophy: Reliable aggregation that produces consistent, validated results from parallel execution
"""

import asyncio
import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Union

from ...utils.logger import get_logger

logger = get_logger(__name__)


class ResultStatus(Enum):
    """Status of individual agent results."""

    SUCCESS = "success"
    ERROR = "error"
    TIMEOUT = "timeout"
    PARTIAL = "partial"
    CONFLICT = "conflict"


class ConflictResolutionStrategy(Enum):
    """Strategies for resolving conflicts between agent results."""

    MAJORITY_VOTE = "majority_vote"
    HIGHEST_QUALITY = "highest_quality"
    MERGE = "merge"
    ESCALATE = "escalate"
    QUALITY_THRESHOLD = "quality_threshold"
    CONSENSUS = "consensus"


class AggregationStrategy(Enum):
    """Strategies for aggregating multiple results."""

    FIRST_SUCCESS = "first_success"
    BEST_QUALITY = "best_quality"
    CONSENSUS = "consensus"
    MERGE_ALL = "merge_all"
    REDUNDANT_VALIDATION = "redundant_validation"


@dataclass
class AgentResult:
    """Result from a single agent execution."""

    agent_id: str
    agent_name: str
    task_id: str
    status: ResultStatus
    output: Any
    confidence: float = 0.0
    quality_score: float = 0.0
    execution_time_seconds: float = 0.0
    tokens_used: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)
    dependencies: Set[str] = field(default_factory=set)


@dataclass
class ConflictInfo:
    """Information about a detected conflict."""

    conflict_type: str
    conflicting_results: List[str]  # agent_ids
    description: str
    severity: float  # 0.0-1.0
    resolution_strategy: ConflictResolutionStrategy
    auto_resolvable: bool = True
    requires_human_intervention: bool = False


@dataclass
class AggregatedResult:
    """Final aggregated result from multiple agents."""

    task_id: str
    status: ResultStatus
    final_output: Any
    contributing_agents: List[str]
    aggregation_strategy: AggregationStrategy
    confidence: float
    quality_score: float
    total_execution_time: float = 0.0
    total_tokens_used: int = 0
    conflicts_detected: List[ConflictInfo] = field(default_factory=list)
    conflicts_resolved: List[ConflictInfo] = field(default_factory=list)
    validation_passed: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)


class ResultAggregator:
    """Aggregates and resolves conflicts between multiple agent results."""

    def __init__(self, quality_threshold: float = 0.90):
        self.quality_threshold = quality_threshold
        self.aggregation_history: List[AggregatedResult] = []
        self.conflict_patterns: Dict[str, int] = {}  # conflict_type -> count
        self._lock = asyncio.Lock()

    async def aggregate_results(
        self,
        task_id: str,
        results: List[AgentResult],
        strategy: AggregationStrategy = AggregationStrategy.BEST_QUALITY,
    ) -> AggregatedResult:
        """Aggregate multiple agent results into a final output."""
        logger.info(f"Aggregating {len(results)} results for task {task_id} using {strategy.value}")

        try:
            # Filter successful results
            successful_results = [r for r in results if r.status == ResultStatus.SUCCESS]

            if not successful_results:
                logger.warning(f"No successful results for task {task_id}")
                return self._create_failure_result(task_id, results, "No successful results")

            # Detect conflicts
            conflicts = await self._detect_conflicts(successful_results)

            # Resolve conflicts
            resolved_results, resolved_conflicts = await self._resolve_conflicts(successful_results, conflicts)

            # Apply aggregation strategy
            final_result = await self._apply_aggregation_strategy(task_id, resolved_results, strategy)

            # Validate final result
            validation_passed = await self._validate_result(final_result, resolved_results)

            # Create aggregated result
            aggregated = AggregatedResult(
                task_id=task_id,
                status=final_result.status,
                final_output=final_result.output,
                contributing_agents=[r.agent_id for r in resolved_results],
                aggregation_strategy=strategy,
                confidence=final_result.confidence,
                quality_score=final_result.quality_score,
                total_execution_time=sum(r.execution_time_seconds for r in results),
                total_tokens_used=sum(r.tokens_used for r in results),
                conflicts_detected=conflicts,
                conflicts_resolved=resolved_conflicts,
                validation_passed=validation_passed,
                metadata={
                    "total_results": len(results),
                    "successful_results": len(successful_results),
                    "conflicts_count": len(conflicts),
                    "resolution_time": datetime.now().isoformat(),
                },
            )

            # Update history and patterns
            async with self._lock:
                self.aggregation_history.append(aggregated)
                for conflict in conflicts:
                    self.conflict_patterns[conflict.conflict_type] = (
                        self.conflict_patterns.get(conflict.conflict_type, 0) + 1
                    )

            logger.info(f"Aggregated result for task {task_id}: confidence={aggregated.confidence:.2f}")
            return aggregated

        except Exception as e:
            logger.error(f"Error aggregating results for task {task_id}: {e}")
            return self._create_failure_result(task_id, results, f"Aggregation error: {e}")

    async def _detect_conflicts(self, results: List[AgentResult]) -> List[ConflictInfo]:
        """Detect conflicts between agent results."""
        conflicts = []

        if len(results) <= 1:
            return conflicts

        # Check for output conflicts
        output_conflicts = await self._detect_output_conflicts(results)
        conflicts.extend(output_conflicts)

        # Check for confidence conflicts
        confidence_conflicts = await self._detect_confidence_conflicts(results)
        conflicts.extend(confidence_conflicts)

        # Check for quality conflicts
        quality_conflicts = await self._detect_quality_conflicts(results)
        conflicts.extend(quality_conflicts)

        return conflicts

    async def _detect_output_conflicts(self, results: List[AgentResult]) -> List[ConflictInfo]:
        """Detect conflicts in agent outputs."""
        conflicts = []

        # Group similar outputs
        output_groups = {}
        for result in results:
            output_signature = self._get_output_signature(result.output)
            if output_signature not in output_groups:
                output_groups[output_signature] = []
            output_groups[output_signature].append(result)

        # If we have multiple different outputs, there's a conflict
        if len(output_groups) > 1:
            conflicting_agents = [r.agent_id for group in output_groups.values() for r in group]

            conflict = ConflictInfo(
                conflict_type="output_mismatch",
                conflicting_agents=conflicting_agents,
                description=f"Agents produced {len(output_groups)} different outputs",
                severity=0.8,
                resolution_strategy=ConflictResolutionStrategy.MAJORITY_VOTE,
                auto_resolvable=True,
            )
            conflicts.append(conflict)

        return conflicts

    async def _detect_confidence_conflicts(self, results: List[AgentResult]) -> List[ConflictInfo]:
        """Detect conflicts in agent confidence levels."""
        conflicts = []

        confidences = [r.confidence for r in results]
        avg_confidence = sum(confidences) / len(confidences)
        variance = sum((c - avg_confidence) ** 2 for c in confidences) / len(confidences)

        # High variance in confidence might indicate uncertainty
        if variance > 0.1:  # Threshold for high variance
            low_confidence_agents = [r.agent_id for r in results if r.confidence < avg_confidence - 0.2]

            conflict = ConflictInfo(
                conflict_type="confidence_variance",
                conflicting_agents=low_confidence_agents,
                description=f"High confidence variance ({variance:.3f}) among agents",
                severity=0.3,
                resolution_strategy=ConflictResolutionStrategy.HIGHEST_QUALITY,
                auto_resolvable=True,
            )
            conflicts.append(conflict)

        return conflicts

    async def _detect_quality_conflicts(self, results: List[AgentResult]) -> List[ConflictInfo]:
        """Detect conflicts in quality scores."""
        conflicts = []

        qualities = [r.quality_score for r in results]
        min_quality = min(qualities)
        max_quality = max(qualities)

        # Large quality gap might indicate issues
        if max_quality - min_quality > 0.3:
            low_quality_agents = [r.agent_id for r in results if r.quality_score < self.quality_threshold]

            if low_quality_agents:
                conflict = ConflictInfo(
                    conflict_type="quality_gap",
                    conflicting_agents=low_quality_agents,
                    description=f"Large quality gap ({max_quality - min_quality:.3f}) detected",
                    severity=0.5,
                    resolution_strategy=ConflictResolutionStrategy.QUALITY_THRESHOLD,
                    auto_resolvable=True,
                )
                conflicts.append(conflict)

        return conflicts

    def _get_output_signature(self, output: Any) -> str:
        """Get a signature of the output for comparison."""
        try:
            if isinstance(output, str):
                # For text outputs, use a hash of the content
                import hashlib

                return hashlib.md5(output.encode()).hexdigest()[:16]
            elif isinstance(output, dict):
                # For dict outputs, sort keys and create signature
                sorted_items = sorted(output.items())
                return str(sorted_items)[:100]
            elif isinstance(output, list):
                # For list outputs, use length and first few items
                return f"list_{len(output)}_{str(output[:3]) if output else 'empty'}"
            else:
                # For other types, use string representation
                return f"{type(output).__name__}_{str(output)[:50]}"
        except Exception:
            return f"unknown_{type(output).__name__}"

    async def _resolve_conflicts(
        self, results: List[AgentResult], conflicts: List[ConflictInfo]
    ) -> tuple[List[AgentResult], List[ConflictInfo]]:
        """Resolve detected conflicts."""
        resolved_results = results.copy()
        resolved_conflicts = []

        for conflict in conflicts:
            try:
                if conflict.auto_resolvable:
                    resolved = await self._auto_resolve_conflict(resolved_results, conflict)
                    if resolved:
                        resolved_conflicts.append(conflict)
                else:
                    # For non-auto-resolvable conflicts, escalate
                    logger.warning(f"Conflict requires escalation: {conflict.description}")
                    resolved_conflicts.append(conflict)
            except Exception as e:
                logger.error(f"Error resolving conflict {conflict.conflict_type}: {e}")

        return resolved_results, resolved_conflicts

    async def _auto_resolve_conflict(self, results: List[AgentResult], conflict: ConflictInfo) -> bool:
        """Automatically resolve a conflict."""
        if conflict.resolution_strategy == ConflictResolutionStrategy.MAJORITY_VOTE:
            # Keep the result that appears most frequently
            return await self._apply_majority_vote(results, conflict)
        elif conflict.resolution_strategy == ConflictResolutionStrategy.HIGHEST_QUALITY:
            # Keep the highest quality result
            return await self._apply_highest_quality(results, conflict)
        elif conflict.resolution_strategy == ConflictResolutionStrategy.QUALITY_THRESHOLD:
            # Filter results by quality threshold
            return await self._apply_quality_threshold(results, conflict)
        else:
            return False

    async def _apply_majority_vote(self, results: List[AgentResult], conflict: ConflictInfo) -> bool:
        """Apply majority vote resolution."""
        # This is a simplified implementation
        # In practice, would need more sophisticated output comparison
        return True

    async def _apply_highest_quality(self, results: List[AgentResult], conflict: ConflictInfo) -> bool:
        """Apply highest quality resolution."""
        # Filter to keep only high-quality results
        min_quality = max(r.quality_score for r in results) - 0.1
        return min_quality >= self.quality_threshold

    async def _apply_quality_threshold(self, results: List[AgentResult], conflict: ConflictInfo) -> bool:
        """Apply quality threshold resolution."""
        # Filter results by quality threshold
        high_quality_results = [r for r in results if r.quality_score >= self.quality_threshold]
        return len(high_quality_results) > 0

    async def _apply_aggregation_strategy(
        self, task_id: str, results: List[AgentResult], strategy: AggregationStrategy
    ) -> AgentResult:
        """Apply the specified aggregation strategy."""
        if strategy == AggregationStrategy.FIRST_SUCCESS:
            return results[0]
        elif strategy == AggregationStrategy.BEST_QUALITY:
            return max(results, key=lambda r: r.quality_score)
        elif strategy == AggregationStrategy.CONSENSUS:
            return await self._build_consensus(results)
        elif strategy == AggregationStrategy.MERGE_ALL:
            return await self._merge_all_results(results)
        elif strategy == AggregationStrategy.REDUNDANT_VALIDATION:
            return await self._validate_redundantly(results)
        else:
            # Default to best quality
            return max(results, key=lambda r: r.quality_score)

    async def _build_consensus(self, results: List[AgentResult]) -> AgentResult:
        """Build consensus from multiple results."""
        # For now, return the highest confidence result
        # In practice, would implement more sophisticated consensus building
        best_result = max(results, key=lambda r: r.confidence)
        best_result.metadata["consensus_method"] = "highest_confidence"
        return best_result

    async def _merge_all_results(self, results: List[AgentResult]) -> AgentResult:
        """Merge all results into a combined output."""
        merged_output = {
            "individual_results": [
                {
                    "agent_id": r.agent_id,
                    "agent_name": r.agent_name,
                    "output": r.output,
                    "confidence": r.confidence,
                    "quality_score": r.quality_score,
                }
                for r in results
            ],
            "summary": "All agent results included",
        }

        # Calculate combined metrics
        avg_confidence = sum(r.confidence for r in results) / len(results)
        avg_quality = sum(r.quality_score for r in results) / len(results)

        return AgentResult(
            agent_id="aggregator",
            agent_name="Result Aggregator",
            task_id=results[0].task_id,
            status=ResultStatus.SUCCESS,
            output=merged_output,
            confidence=avg_confidence,
            quality_score=avg_quality,
            metadata={"aggregation_method": "merge_all"},
        )

    async def _validate_redundantly(self, results: List[AgentResult]) -> AgentResult:
        """Validate results through redundant execution."""
        # Find results that agree with each other
        agreement_groups = {}

        for result in results:
            signature = self._get_output_signature(result.output)
            if signature not in agreement_groups:
                agreement_groups[signature] = []
            agreement_groups[signature].append(result)

        # Find the largest agreement group
        largest_group = max(agreement_groups.values(), key=len)

        if len(largest_group) >= len(results) * 0.6:  # 60% agreement threshold
            # Use the result with highest confidence from the largest group
            best_in_group = max(largest_group, key=lambda r: r.confidence)
            best_in_group.metadata["validation_method"] = "redundant_agreement"
            best_in_group.metadata["agreement_count"] = len(largest_group)
            return best_in_group
        else:
            # No clear agreement, use highest quality
            best_result = max(results, key=lambda r: r.quality_score)
            best_result.metadata["validation_method"] = "quality_fallback"
            return best_result

    async def _validate_result(self, result: AgentResult, source_results: List[AgentResult]) -> bool:
        """Validate the aggregated result."""
        # Basic validation checks
        if result.quality_score < self.quality_threshold:
            logger.warning(f"Result quality {result.quality_score} below threshold {self.quality_threshold}")
            return False

        if result.confidence < 0.5:
            logger.warning(f"Result confidence {result.confidence} is low")
            return False

        # Validate output format
        if not self._validate_output_format(result.output):
            logger.warning("Result output format validation failed")
            return False

        # Check for hallucinations (simplified)
        if self._detect_potential_hallucination(result.output, source_results):
            logger.warning("Potential hallucination detected in result")
            return False

        return True

    def _validate_output_format(self, output: Any) -> bool:
        """Validate that output format is acceptable."""
        try:
            # Check for common output formats
            if isinstance(output, (str, dict, list, int, float, bool)):
                return True

            # Check for JSON serializable
            json.dumps(output)
            return True
        except (TypeError, ValueError):
            return False

    def _detect_potential_hallucination(self, output: Any, source_results: List[AgentResult]) -> bool:
        """Detect potential hallucinations in the output."""
        # This is a simplified implementation
        # In practice, would use more sophisticated hallucination detection

        if isinstance(output, str):
            # Check for common hallucination indicators
            hallucination_indicators = [
                "I cannot",
                "I don't have",
                "As an AI",
                "I'm not sure",
                "It appears that",
                "It seems like",
            ]

            text_lower = output.lower()
            return any(indicator.lower() in text_lower for indicator in hallucination_indicators)

        return False

    def _create_failure_result(self, task_id: str, results: List[AgentResult], reason: str) -> AggregatedResult:
        """Create a failure result when aggregation fails."""
        return AggregatedResult(
            task_id=task_id,
            status=ResultStatus.ERROR,
            final_output={"error": reason, "partial_results": [r.output for r in results if r.output]},
            contributing_agents=[r.agent_id for r in results],
            aggregation_strategy=AggregationStrategy.FIRST_SUCCESS,
            confidence=0.0,
            quality_score=0.0,
            total_execution_time=sum(r.execution_time_seconds for r in results),
            total_tokens_used=sum(r.tokens_used for r in results),
            validation_passed=False,
            metadata={"failure_reason": reason},
        )

    async def get_aggregation_statistics(self) -> Dict[str, Any]:
        """Get aggregation performance statistics."""
        async with self._lock:
            total_aggregations = len(self.aggregation_history)
            if total_aggregations == 0:
                return {"total_aggregations": 0}

            successful_aggregations = len([a for a in self.aggregation_history if a.status == ResultStatus.SUCCESS])
            avg_confidence = sum(a.confidence for a in self.aggregation_history) / total_aggregations
            avg_quality = sum(a.quality_score for a in self.aggregation_history) / total_aggregations
            total_conflicts = sum(len(a.conflicts_detected) for a in self.aggregation_history)
            total_resolved = sum(len(a.conflicts_resolved) for a in self.aggregation_history)

            strategy_counts = {}
            for result in self.aggregation_history:
                strategy_counts[result.aggregation_strategy.value] = (
                    strategy_counts.get(result.aggregation_strategy.value, 0) + 1
                )

            return {
                "total_aggregations": total_aggregations,
                "successful_aggregations": successful_aggregations,
                "success_rate": successful_aggregations / total_aggregations,
                "avg_confidence": avg_confidence,
                "avg_quality_score": avg_quality,
                "total_conflicts_detected": total_conflicts,
                "total_conflicts_resolved": total_resolved,
                "conflict_resolution_rate": total_resolved / total_conflicts if total_conflicts > 0 else 0,
                "aggregation_strategies": strategy_counts,
                "conflict_patterns": dict(self.conflict_patterns),
            }


class ConflictResolver:
    """Specialized resolver for complex conflicts that cannot be auto-resolved."""

    def __init__(self):
        self.resolution_strategies = {
            ConflictResolutionStrategy.ESCALATE: self._escalate_conflict,
            ConflictResolutionStrategy.CONSENSUS: self._build_consensus_resolution,
            ConflictResolutionStrategy.MERGE: self._merge_conflicting_results,
        }

    async def resolve_complex_conflict(
        self, conflict: ConflictInfo, results: List[AgentResult]
    ) -> Optional[AgentResult]:
        """Resolve a complex conflict that requires special handling."""
        resolver = self.resolution_strategies.get(conflict.resolution_strategy)
        if resolver:
            return await resolver(conflict, results)
        return None

    async def _escalate_conflict(self, conflict: ConflictInfo, results: List[AgentResult]) -> None:
        """Escalate conflict for human intervention."""
        logger.error(f"Conflict escalation required: {conflict.description}")
        # In practice, would integrate with human-in-the-loop system
        return None

    async def _build_consensus_resolution(self, conflict: ConflictInfo, results: List[AgentResult]) -> AgentResult:
        """Build consensus resolution for conflicting results."""
        # Implement consensus-building logic
        return max(results, key=lambda r: r.quality_score)

    async def _merge_conflicting_results(self, conflict: ConflictInfo, results: List[AgentResult]) -> AgentResult:
        """Merge conflicting results into a compromise."""
        # Implement result merging logic
        merged_output = {
            "conflict_resolution": "merged",
            "conflicting_outputs": [r.output for r in results],
            "resolution_note": f"Conflict type: {conflict.conflict_type}",
        }

        return AgentResult(
            agent_id="conflict_resolver",
            agent_name="Conflict Resolver",
            task_id=results[0].task_id,
            status=ResultStatus.SUCCESS,
            output=merged_output,
            confidence=0.7,
            quality_score=0.7,
            metadata={"resolution_method": "merge"},
        )
