"""
Knowledge Transfer Bridge

Bridges Development Fix Recording System to Agent Lightning's Knowledge Transfer System.
Provides bi-directional knowledge flow between development fixes and skill patterns.

This module enables:
- Sync of development fix patterns to Knowledge Transfer System
- Import of successful skill patterns back to development fixes
- Cross-system learning and pattern sharing
- Unified knowledge management across systems
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List
from typing import Optional

from .development_fix_recorder import FixPattern
from .development_fix_recorder import DevelopmentFixRecorder

logger = logging.getLogger(__name__)


class KnowledgeTransferBridge:
    """Bridge between development fixes and Agent Lightning's Knowledge Transfer System"""

    def __init__(self, fix_recorder: DevelopmentFixRecorder, agent_lightning_path: Path):
        self.fix_recorder = fix_recorder
        self.agent_lightning_path = agent_lightning_path

        # Bridge configuration
        self.sync_enabled = True
        self.bidirectional_sync = True
        self.auto_sync_interval = 3600  # 1 hour

        # Sync statistics
        self.sync_stats = {
            "patterns_exported": 0,
            "patterns_imported": 0,
            "sync_cycles": 0,
            "last_sync_timestamp": None,
            "sync_errors": 0,
        }

        # Background task
        self._sync_task: Optional[asyncio.Task] = None
        self._running = False

    async def start_bridge(self):
        """Start the knowledge transfer bridge"""
        if self._running:
            return

        self._running = True
        logger.info("Starting Knowledge Transfer Bridge")

        # Initial sync
        await self.perform_full_sync()

        # Start background sync task
        if self.sync_enabled:
            self._sync_task = asyncio.create_task(self._background_sync_loop())

    async def stop_bridge(self):
        """Stop the knowledge transfer bridge"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping Knowledge Transfer Bridge")

        if self._sync_task:
            self._sync_task.cancel()
            try:
                await self._sync_task
            except asyncio.CancelledError:
                pass

    async def perform_full_sync(self) -> Dict[str, Any]:
        """Perform a full synchronization between systems"""
        try:
            logger.info("Starting full knowledge transfer sync")

            sync_results = {
                "sync_timestamp": datetime.now().isoformat(),
                "export_results": {},
                "import_results": {},
                "overall_success": True,
                "sync_cycle": self.sync_stats["sync_cycles"] + 1,
            }

            # Export development fix patterns to Knowledge Transfer System
            if self.sync_enabled:
                export_results = await self._export_patterns_to_knowledge_transfer()
                sync_results["export_results"] = export_results

            # Import successful skill patterns from Knowledge Transfer System
            if self.bidirectional_sync:
                import_results = await self._import_patterns_from_knowledge_transfer()
                sync_results["import_results"] = import_results

            # Update statistics
            await self._update_sync_statistics(sync_results)

            logger.info(f"Full sync completed: {sync_results}")
            return sync_results

        except Exception as e:
            logger.error(f"Failed to perform full sync: {e}")
            self.sync_stats["sync_errors"] += 1
            return {"error": str(e), "overall_success": False}

    async def export_pattern(self, pattern_id: str) -> Dict[str, Any]:
        """Export a specific pattern to Knowledge Transfer System"""
        try:
            if pattern_id not in self.fix_recorder.patterns:
                raise ValueError(f"Pattern {pattern_id} not found")

            pattern = self.fix_recorder.patterns[pattern_id]
            export_result = await self._convert_and_export_pattern(pattern)

            logger.info(f"Exported pattern {pattern_id} to Knowledge Transfer System")
            return export_result

        except Exception as e:
            logger.error(f"Failed to export pattern {pattern_id}: {e}")
            return {"success": False, "error": str(e)}

    async def import_success_patterns(self, skill_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Import successful patterns from Knowledge Transfer System"""
        try:
            logger.info(f"Importing successful patterns from Knowledge Transfer System (skill_type: {skill_type})")

            # Query Knowledge Transfer System for successful patterns
            successful_patterns = await self._query_successful_patterns(skill_type)

            imported_patterns = []
            for al_pattern in successful_patterns:
                converted_pattern = await self._convert_al_pattern_to_fix_pattern(al_pattern)
                if converted_pattern:
                    imported_patterns.append(converted_pattern)

            logger.info(f"Imported {len(imported_patterns)} patterns from Knowledge Transfer System")
            return imported_patterns

        except Exception as e:
            logger.error(f"Failed to import success patterns: {e}")
            return []

    async def get_cross_system_recommendations(self, skill_id: str) -> Dict[str, Any]:
        """Get recommendations combining both systems' knowledge"""
        try:
            logger.info(f"Getting cross-system recommendations for skill {skill_id}")

            recommendations = {
                "skill_id": skill_id,
                "recommendation_timestamp": datetime.now().isoformat(),
                "fix_based_recommendations": [],
                "knowledge_transfer_recommendations": [],
                "combined_priorities": [],
                "estimated_benefit": 0.0,
            }

            # Get recommendations from development fix patterns
            fix_recommendations = await self._get_fix_based_recommendations(skill_id)
            recommendations["fix_based_recommendations"] = fix_recommendations

            # Get recommendations from Knowledge Transfer System
            kt_recommendations = await self._get_knowledge_transfer_recommendations(skill_id)
            recommendations["knowledge_transfer_recommendations"] = kt_recommendations

            # Combine and prioritize recommendations
            combined = await self._combine_recommendations(fix_recommendations, kt_recommendations)
            recommendations["combined_priorities"] = combined
            recommendations["estimated_benefit"] = sum(r.get("expected_benefit", 0) for r in combined)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get cross-system recommendations: {e}")
            return {"error": str(e)}

    # Private methods

    async def _background_sync_loop(self):
        """Background loop for periodic synchronization"""
        while self._running:
            try:
                await asyncio.sleep(self.auto_sync_interval)
                if self._running and self.sync_enabled:
                    await self.perform_full_sync()

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in background sync loop: {e}")
                self.sync_stats["sync_errors"] += 1
                await asyncio.sleep(300)  # Wait 5 minutes before retry

    async def _export_patterns_to_knowledge_transfer(self) -> Dict[str, Any]:
        """Export all development fix patterns to Knowledge Transfer System"""
        try:
            export_results = {
                "patterns_processed": 0,
                "patterns_exported": 0,
                "patterns_skipped": 0,
                "export_errors": [],
            }

            for pattern_id, pattern in self.fix_recorder.patterns.items():
                export_results["patterns_processed"] += 1

                try:
                    # Check if pattern should be exported
                    if pattern.transferability_score < 0.5:
                        export_results["patterns_skipped"] += 1
                        continue

                    # Convert and export pattern
                    export_result = await self._convert_and_export_pattern(pattern)
                    if export_result.get("success", False):
                        export_results["patterns_exported"] += 1
                    else:
                        export_results["export_errors"].append(
                            {
                                "pattern_id": pattern_id,
                                "error": export_result.get("error", "Unknown error"),
                            }
                        )

                except Exception as e:
                    export_results["export_errors"].append(
                        {
                            "pattern_id": pattern_id,
                            "error": str(e),
                        }
                    )

            self.sync_stats["patterns_exported"] += export_results["patterns_exported"]
            return export_results

        except Exception as e:
            logger.error(f"Failed to export patterns to Knowledge Transfer System: {e}")
            return {"error": str(e)}

    async def _import_patterns_from_knowledge_transfer(self) -> Dict[str, Any]:
        """Import successful patterns from Knowledge Transfer System"""
        try:
            import_results = {
                "patterns_queried": 0,
                "patterns_imported": 0,
                "patterns_skipped": 0,
                "import_errors": [],
            }

            # Get successful patterns from Knowledge Transfer System
            successful_patterns = await self._query_successful_patterns()

            import_results["patterns_queried"] = len(successful_patterns)

            for al_pattern in successful_patterns:
                try:
                    # Convert AL pattern to fix pattern
                    fix_pattern = await self._convert_al_pattern_to_fix_pattern(al_pattern)

                    if fix_pattern:
                        # Check if pattern already exists
                        if fix_pattern.pattern_id not in self.fix_recorder.patterns:
                            self.fix_recorder.patterns[fix_pattern.pattern_id] = fix_pattern
                            import_results["patterns_imported"] += 1
                        else:
                            import_results["patterns_skipped"] += 1
                    else:
                        import_results["patterns_skipped"] += 1

                except Exception as e:
                    import_results["import_errors"].append(
                        {
                            "pattern_id": al_pattern.get("pattern_id", "unknown"),
                            "error": str(e),
                        }
                    )

            self.sync_stats["patterns_imported"] += import_results["patterns_imported"]
            return import_results

        except Exception as e:
            logger.error(f"Failed to import patterns from Knowledge Transfer System: {e}")
            return {"error": str(e)}

    async def _convert_and_export_pattern(self, pattern: FixPattern) -> Dict[str, Any]:
        """Convert a development fix pattern to Agent Lightning format and export"""
        try:
            # Import Agent Lightning components
            from ..agent_lightning_integration.knowledge_transfer_system import PatternType, SkillPattern

            # Map fix types to Agent Lightning pattern types
            pattern_type_mapping = {
                "framework_unification": PatternType.CODE_STRUCTURE,
                "import_cascading_failure": PatternType.ERROR_HANDLING,
                "abstract_method_implementation": PatternType.CODE_STRUCTURE,
                "registration_system_incompatibility": PatternType.CODE_STRUCTURE,
                "parameter_mismatch": PatternType.ERROR_HANDLING,
                "dependency_conflict": PatternType.ERROR_HANDLING,
                "performance_issue": PatternType.PERFORMANCE_OPTIMIZATION,
                "security_fix": PatternType.ERROR_HANDLING,
            }

            al_pattern_type = pattern_type_mapping.get(pattern.fix_type.value, PatternType.ERROR_HANDLING)

            # Create Agent Lightning skill pattern
            al_pattern = SkillPattern(
                pattern_id=pattern.pattern_id,
                source_skill_id="development_fixes",
                pattern_type=al_pattern_type,
                description=f"Development Fix: {pattern.description}",
                implementation_details={
                    "fix_type": pattern.fix_type.value,
                    "root_cause": pattern.root_cause,
                    "solution_approach": pattern.solution_approach,
                    "symptoms": pattern.symptoms,
                    "prevention_strategy": pattern.prevention_strategy.value,
                    **pattern.implementation_details,
                },
                performance_impact=pattern.effectiveness_score,
                success_rate=pattern.confidence,
                complexity_score=0.5,  # Default complexity
                transferability_score=pattern.transferability_score,
                created_at=pattern.created_at,
            )

            # Store pattern for Knowledge Transfer System
            from amplifier.mcp.persistent_storage import store_result

            await store_result(
                namespace="knowledge_transfer_patterns",
                key=pattern.pattern_id,
                data=al_pattern.__dict__,
            )

            return {"success": True, "pattern_id": pattern.pattern_id}

        except Exception as e:
            logger.error(f"Failed to convert and export pattern {pattern.pattern_id}: {e}")
            return {"success": False, "error": str(e)}

    async def _query_successful_patterns(self, skill_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Query Knowledge Transfer System for successful patterns"""
        try:
            # This would query actual Agent Lightning Knowledge Transfer System
            # For now, return placeholder successful patterns

            successful_patterns = [
                {
                    "pattern_id": "al_perf_caching_success",
                    "pattern_type": "performance_optimization",
                    "source_skill_id": "react_optimized_expert",
                    "description": "Successful caching implementation for performance",
                    "performance_impact": 0.4,
                    "success_rate": 0.95,
                    "transferability_score": 0.8,
                    "implementation_details": {
                        "caching_strategy": "memoization",
                        "cache_size": "adaptive",
                        "hit_rate": 0.85,
                    },
                },
                {
                    "pattern_id": "al_error_handling_robust",
                    "pattern_type": "error_handling",
                    "source_skill_id": "api_resilience_expert",
                    "description": "Robust error handling with recovery mechanisms",
                    "performance_impact": 0.2,
                    "success_rate": 0.98,
                    "transferability_score": 0.9,
                    "implementation_details": {
                        "error_recovery": True,
                        "retry_logic": "exponential_backoff",
                        "fallback_strategies": 3,
                    },
                },
            ]

            # Filter by skill type if specified
            if skill_type:
                successful_patterns = [
                    p for p in successful_patterns if skill_type.lower() in p["source_skill_id"].lower()
                ]

            return successful_patterns

        except Exception as e:
            logger.error(f"Failed to query successful patterns: {e}")
            return []

    async def _convert_al_pattern_to_fix_pattern(self, al_pattern: Dict[str, Any]) -> Optional[FixPattern]:
        """Convert Agent Lightning pattern to development fix pattern"""
        try:
            from .development_fix_recorder import FixType, PreventionStrategy

            # Map Agent Lightning pattern types to fix types
            fix_type_mapping = {
                "performance_optimization": FixType.PERFORMANCE_ISSUE,
                "error_handling": FixType.SECURITY_FIX,  # Security covers general robustness
                "code_structure": FixType.FRAMEWORK_UNIFICATION,
                "algorithm_pattern": FixType.VALIDATION_FAILURE,
                "test_strategy": FixType.CONFIGURATION_ERROR,
                "resource_management": FixType.PERFORMANCE_ISSUE,
            }

            fix_type = fix_type_mapping.get(
                al_pattern.get("pattern_type", "error_handling"),
                FixType.SECURITY_FIX,
            )

            # Extract implementation details
            impl_details = al_pattern.get("implementation_details", {})

            # Create development fix pattern
            fix_pattern = FixPattern(
                pattern_id=f"imported_{al_pattern.get('pattern_id', 'unknown')}",
                fix_type=fix_type,
                title=f"Imported: {al_pattern.get('description', 'Unknown pattern')}",
                description=f"Pattern imported from Agent Lightning: {al_pattern.get('description', '')}",
                symptoms=[impl_details.get("symptoms", "Imported from successful skill")],
                root_cause=impl_details.get("root_cause", "Pattern identified through success analysis"),
                solution_approach=impl_details.get("solution_approach", al_pattern.get("description", "")),
                implementation_details=impl_details,
                prevention_strategy=PreventionStrategy.TEMPLATE_UPDATE,  # Default for imported patterns
                transferability_score=al_pattern.get("transferability_score", 0.7),
                confidence=al_pattern.get("success_rate", 0.8),
                effectiveness_score=al_pattern.get("performance_impact", 0.5),
                created_at=datetime.now(),
            )

            return fix_pattern

        except Exception as e:
            logger.error(f"Failed to convert AL pattern to fix pattern: {e}")
            return None

    async def _get_fix_based_recommendations(self, skill_id: str) -> List[Dict[str, Any]]:
        """Get recommendations based on development fix patterns"""
        try:
            recommendations = []

            # Get relevant fix patterns
            for pattern in self.fix_recorder.patterns.values():
                if pattern.transferability_score > 0.6:
                    recommendation = {
                        "pattern_id": pattern.pattern_id,
                        "source": "development_fixes",
                        "title": pattern.title,
                        "description": pattern.description,
                        "prevention_strategy": pattern.prevention_strategy.value,
                        "confidence": pattern.confidence,
                        "expected_benefit": pattern.effectiveness_score * pattern.transferability_score,
                        "fix_type": pattern.fix_type.value,
                    }
                    recommendations.append(recommendation)

            # Sort by expected benefit
            recommendations.sort(key=lambda r: r["expected_benefit"], reverse=True)
            return recommendations[:5]  # Top 5 recommendations

        except Exception as e:
            logger.error(f"Failed to get fix-based recommendations: {e}")
            return []

    async def _get_knowledge_transfer_recommendations(self, skill_id: str) -> List[Dict[str, Any]]:
        """Get recommendations from Knowledge Transfer System"""
        try:
            # This would query actual Knowledge Transfer System
            # For now, return placeholder recommendations

            recommendations = [
                {
                    "pattern_id": "kt_performance_caching",
                    "source": "knowledge_transfer",
                    "title": "Performance Caching Pattern",
                    "description": "Apply successful caching strategies from high-performing skills",
                    "expected_benefit": 0.35,
                    "confidence": 0.85,
                    "source_skill": "react_performance_expert",
                },
                {
                    "pattern_id": "kt_error_resilience",
                    "source": "knowledge_transfer",
                    "title": "Error Resilience Pattern",
                    "description": "Implement robust error handling from resilient skills",
                    "expected_benefit": 0.25,
                    "confidence": 0.9,
                    "source_skill": "api_stability_expert",
                },
            ]

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get knowledge transfer recommendations: {e}")
            return []

    async def _combine_recommendations(
        self, fix_recommendations: List[Dict[str, Any]], kt_recommendations: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Combine recommendations from both systems"""
        try:
            combined = []

            # Add all recommendations with source tagging
            for rec in fix_recommendations:
                rec["priority_score"] = rec["expected_benefit"] * rec["confidence"]
                combined.append(rec)

            for rec in kt_recommendations:
                rec["priority_score"] = rec["expected_benefit"] * rec["confidence"]
                combined.append(rec)

            # Sort by priority score
            combined.sort(key=lambda r: r["priority_score"], reverse=True)

            # Add cross-system insights
            for i, rec in enumerate(combined):
                rec["rank"] = i + 1
                rec["cross_system_validation"] = self._validate_cross_system_support(rec, combined)

            return combined[:10]  # Top 10 combined recommendations

        except Exception as e:
            logger.error(f"Failed to combine recommendations: {e}")
            return []

    def _validate_cross_system_support(
        self, recommendation: Dict[str, Any], all_recommendations: List[Dict[str, Any]]
    ) -> bool:
        """Validate if recommendation has support from both systems"""
        try:
            # Check if similar recommendations exist from other system
            source = recommendation.get("source")
            rec_type = recommendation.get("fix_type", "general")

            other_system_recommendations = [
                r for r in all_recommendations if r.get("source") != source and rec_type in r.get("fix_type", "")
            ]

            return len(other_system_recommendations) > 0

        except Exception:
            return False

    async def _update_sync_statistics(self, sync_results: Dict[str, Any]):
        """Update synchronization statistics"""
        self.sync_stats["sync_cycles"] += 1
        self.sync_stats["last_sync_timestamp"] = sync_results["sync_timestamp"]

        if not sync_results.get("overall_success", True):
            self.sync_stats["sync_errors"] += 1

    async def get_bridge_statistics(self) -> Dict[str, Any]:
        """Get comprehensive bridge statistics"""
        return {
            "bridge_status": "running" if self._running else "stopped",
            "sync_enabled": self.sync_enabled,
            "bidirectional_sync": self.bidirectional_sync,
            "auto_sync_interval": self.auto_sync_interval,
            **self.sync_stats,
            "fix_patterns_count": len(self.fix_recorder.patterns),
            "last_sync_ago": (
                datetime.now() - datetime.fromisoformat(self.sync_stats["last_sync_timestamp"])
                if self.sync_stats["last_sync_timestamp"]
                else None
            ),
        }
