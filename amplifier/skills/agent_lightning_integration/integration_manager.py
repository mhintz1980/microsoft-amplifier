"""
Agent Lightning Integration Manager

Main orchestrator for the Agent Lightning integration system.
Coordinates all components and provides a unified interface for
skill optimization, quality assurance, and continuous improvement.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict

from .config import AgentLightningIntegrationConfig
from .skill_performance_tracker import SkillPerformanceTracker, SkillExecutionMetrics
from .error_detection_engine import ErrorDetectionEngine, DetectionResult
from .continuous_optimizer import ContinuousOptimizer, OptimizationType, OptimizationResult
from .quality_gate_enforcer import QualityGateEnforcer, QualityGateEvaluation, QualityGateResult
from .knowledge_transfer_system import KnowledgeTransferSystem, PatternType
from .mcp_storage_integration import MCPStorageIntegration
from .performance_monitor import PerformanceMonitor

logger = logging.getLogger(__name__)


@dataclass
class SystemStatus:
    """Overall system status"""

    healthy: bool
    component_status: Dict[str, bool]
    active_optimizations: int
    total_skills_monitored: int
    last_update: datetime
    issues: List[str]


@dataclass
class IntegrationRequest:
    """Request for integration services"""

    request_id: str
    skill_id: str
    request_type: str
    parameters: Dict[str, Any]
    timestamp: datetime
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None


class AgentLightningIntegrationManager:
    """Main integration manager for Agent Lightning system"""

    def __init__(self, config_path: Optional[Path] = None):
        # Load configuration
        if config_path and config_path.exists():
            with open(config_path, "r") as f:
                config_data = json.load(f)
            self.config = AgentLightningIntegrationConfig(**config_data)
        else:
            self.config = AgentLightningIntegrationConfig()

        # Initialize storage path
        self.config.storage_root.mkdir(parents=True, exist_ok=True)

        # Initialize components
        self.storage = MCPStorageIntegration(self.config)
        self.performance_tracker = SkillPerformanceTracker(
            self.config.performance_tracking, self.config.storage_path / "performance"
        )
        self.error_detector = ErrorDetectionEngine(
            self.config.performance_tracking, self.config.storage_path / "error_detection"
        )
        self.optimizer = ContinuousOptimizer(
            self.config.rl_training,
            self.config.storage_path / "optimizer",
            self.performance_tracker,
            self.error_detector,
        )
        self.quality_enforcer = QualityGateEnforcer(
            self.config.quality_gates,
            self.config.storage_path / "quality_gates",
            self.performance_tracker,
            self.error_detector,
        )
        self.knowledge_transfer = KnowledgeTransferSystem(
            self.config.knowledge_transfer,
            self.config.storage_path / "knowledge",
            self.performance_tracker,
            self.optimizer,
        )
        self.performance_monitor = PerformanceMonitor(
            self.config.monitoring,
            self.storage,
            {
                "performance_tracker": self.performance_tracker,
                "error_detector": self.error_detector,
                "optimizer": self.optimizer,
                "quality_enforcer": self.quality_enforcer,
                "knowledge_transfer": self.knowledge_transfer,
            },
        )

        # System state
        self._running = False
        self.active_requests: Dict[str, IntegrationRequest] = {}
        self.system_stats = {
            "total_requests": 0,
            "successful_requests": 0,
            "optimizations_completed": 0,
            "quality_gates_passed": 0,
            "transfers_completed": 0,
        }

        logger.info("Agent Lightning Integration Manager initialized")

    async def start(self):
        """Start the integration system"""
        if self._running:
            logger.warning("Integration system already running")
            return

        logger.info("Starting Agent Lightning Integration System")
        self._running = True

        try:
            # Start all components in order
            await self.storage.start()
            await self.performance_tracker.start()
            await self.error_detector.start()
            await self.optimizer.start()
            await self.quality_enforcer.start()
            await self.knowledge_transfer.start()
            await self.performance_monitor.start()

            logger.info("All components started successfully")

        except Exception as e:
            logger.error(f"Failed to start integration system: {e}")
            await self.stop()
            raise

    async def stop(self):
        """Stop the integration system"""
        if not self._running:
            return

        logger.info("Stopping Agent Lightning Integration System")
        self._running = False

        try:
            # Stop components in reverse order
            await self.performance_monitor.stop()
            await self.knowledge_transfer.stop()
            await self.quality_enforcer.stop()
            await self.optimizer.stop()
            await self.error_detector.stop()
            await self.performance_tracker.stop()
            await self.storage.stop()

            logger.info("Integration system stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping integration system: {e}")

    async def process_skill_execution(self, execution_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a skill execution through the integration pipeline"""
        request_id = f"exec_{int(datetime.now().timestamp())}"
        request = IntegrationRequest(
            request_id=request_id,
            skill_id=execution_data.get("skill_id", "unknown"),
            request_type="skill_execution",
            parameters=execution_data,
            timestamp=datetime.now(),
        )

        self.active_requests[request_id] = request
        self.system_stats["total_requests"] += 1

        try:
            logger.info(f"Processing skill execution {request_id}")

            # Create execution metrics
            metrics = SkillExecutionMetrics(
                skill_id=execution_data.get("skill_id", "unknown"),
                skill_name=execution_data.get("skill_name", "Unknown Skill"),
                execution_id=execution_data.get("execution_id", request_id),
                timestamp=datetime.now(),
                execution_time=execution_data.get("execution_time", 0.0),
                success=execution_data.get("success", False),
                error_type=execution_data.get("error_type"),
                error_message=execution_data.get("error_message"),
                accuracy_score=execution_data.get("accuracy_score", 0.0),
                user_satisfaction=execution_data.get("user_satisfaction"),
                hallucination_detected=execution_data.get("hallucination_detected", False),
                hallucination_score=execution_data.get("hallucination_score", 0.0),
                memory_usage_mb=execution_data.get("memory_usage_mb", 0.0),
                cpu_usage_percent=execution_data.get("cpu_usage_percent", 0.0),
                tokens_used=execution_data.get("tokens_used", 0),
                context_size_tokens=execution_data.get("context_size_tokens", 0),
                response_size_tokens=execution_data.get("response_size_tokens", 0),
                user_feedback=execution_data.get("user_feedback"),
                optimization_version=execution_data.get("optimization_version", 1),
            )

            # Store metrics
            await self.storage.store_performance_metrics(metrics)

            # Error detection
            error_result = await self.error_detector.analyze_execution(execution_data)
            await self.storage.store_error_detection(error_result)

            # Check if optimization is needed
            optimization_needed = (
                not metrics.success
                or metrics.accuracy_score < 0.8
                or metrics.execution_time > 10.0
                or error_result.overall_risk_score > 0.5
            )

            optimization_results = []
            if optimization_needed and self.config.auto_optimization_enabled:
                try:
                    proposals = await self.optimizer.optimize_skill(metrics.skill_id)
                    if proposals:
                        # Implement best proposal
                        best_proposal = max(proposals, key=lambda p: p.expected_improvement * p.confidence)
                        opt_result = await self.optimizer.implement_optimization(best_proposal.proposal_id)
                        await self.storage.store_optimization_result(opt_result)
                        optimization_results.append(
                            {
                                "proposal_id": opt_result.proposal_id,
                                "improvement": opt_result.actual_improvement,
                                "success": opt_result.success,
                            }
                        )
                        self.system_stats["optimizations_completed"] += 1
                except Exception as e:
                    logger.error(f"Optimization failed for {metrics.skill_id}: {e}")

            # Quality gate evaluation (periodic or on issues)
            quality_result = None
            if not metrics.success or error_result.overall_risk_score > 0.7:
                quality_result = await self.quality_enforcer.evaluate_quality_gate(
                    metrics.skill_id, execution_data.get("skill_version", "1.0.0")
                )
                await self.storage.store_quality_gate_evaluation(quality_result)

                if quality_result.overall_result == QualityGateResult.PASS:
                    self.system_stats["quality_gates_passed"] += 1

            # Knowledge transfer (periodic)
            transfer_results = []
            if self.system_stats["total_requests"] % 100 == 0:  # Every 100 executions
                try:
                    patterns = await self.knowledge_transfer.extract_patterns_from_skill(metrics.skill_id)
                    for pattern in patterns:
                        await self.storage.store_knowledge_pattern(pattern)

                    opportunities = await self.knowledge_transfer.find_transfer_opportunities(metrics.skill_id)
                    for proposal in opportunities[:2]:  # Top 2 opportunities
                        try:
                            transfer_result = await self.knowledge_transfer.implement_transfer(proposal.proposal_id)
                            transfer_results.append(
                                {
                                    "proposal_id": transfer_result.proposal_id,
                                    "benefit": transfer_result.actual_benefit,
                                    "success": transfer_result.transfer_result.value == "successful",
                                }
                            )
                            self.system_stats["transfers_completed"] += 1
                        except Exception as e:
                            logger.error(f"Transfer failed: {e}")
                except Exception as e:
                    logger.error(f"Knowledge transfer failed for {metrics.skill_id}: {e}")

            # Compile results
            result = {
                "request_id": request_id,
                "skill_id": metrics.skill_id,
                "execution_successful": metrics.success,
                "performance_metrics": {
                    "execution_time": metrics.execution_time,
                    "accuracy_score": metrics.accuracy_score,
                    "success_rate": 1.0 if metrics.success else 0.0,
                },
                "error_detection": {
                    "risk_score": error_result.overall_risk_score,
                    "errors_found": len(error_result.errors_detected),
                    "requires_attention": error_result.requires_immediate_attention,
                },
                "optimization": {"needed": optimization_needed, "results": optimization_results},
                "quality_gate": {
                    "evaluated": quality_result is not None,
                    "result": quality_result.overall_result.value if quality_result else None,
                    "score": quality_result.overall_score if quality_result else None,
                },
                "knowledge_transfer": {
                    "patterns_extracted": len(
                        await self.knowledge_transfer.extract_patterns_from_skill(metrics.skill_id)
                    ),
                    "transfers_completed": len(transfer_results),
                },
            }

            request.status = "completed"
            request.result = result
            self.system_stats["successful_requests"] += 1

            return result

        except Exception as e:
            logger.error(f"Failed to process skill execution {request_id}: {e}")
            request.status = "failed"
            request.result = {"error": str(e)}
            return {"error": str(e)}

        finally:
            # Clean up old requests
            await self._cleanup_old_requests()

    async def optimize_skill(self, skill_id: str, optimization_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """Manually trigger optimization for a skill"""
        try:
            logger.info(f"Manual optimization triggered for skill {skill_id}")

            # Convert string types to enum if needed
            if optimization_types:
                opt_types = [OptimizationType(t) for t in optimization_types]
            else:
                opt_types = None

            proposals = await self.optimizer.optimize_skill(skill_id, opt_types)

            return {
                "skill_id": skill_id,
                "proposals_generated": len(proposals),
                "proposals": [
                    {
                        "proposal_id": p.proposal_id,
                        "type": p.optimization_type.value,
                        "description": p.description,
                        "expected_improvement": p.expected_improvement,
                        "confidence": p.confidence,
                        "complexity": p.implementation_complexity,
                    }
                    for p in proposals
                ],
            }

        except Exception as e:
            logger.error(f"Manual optimization failed for {skill_id}: {e}")
            return {"error": str(e)}

    async def evaluate_quality_gate(self, skill_id: str, skill_version: str) -> Dict[str, Any]:
        """Manually trigger quality gate evaluation"""
        try:
            logger.info(f"Manual quality gate evaluation for skill {skill_id} v{skill_version}")

            evaluation = await self.quality_enforcer.evaluate_quality_gate(skill_id, skill_version)

            return {
                "skill_id": skill_id,
                "skill_version": skill_version,
                "result": evaluation.overall_result.value,
                "overall_score": evaluation.overall_score,
                "critical_issues": evaluation.critical_issues,
                "recommendations": evaluation.recommendations,
                "metrics": [
                    {
                        "dimension": metric.dimension.value,
                        "value": metric.value,
                        "threshold": metric.threshold,
                        "passed": metric.passed,
                    }
                    for metric in evaluation.metrics
                ],
            }

        except Exception as e:
            logger.error(f"Quality gate evaluation failed for {skill_id}: {e}")
            return {"error": str(e)}

    async def get_skill_insights(self, skill_id: str) -> Dict[str, Any]:
        """Get comprehensive insights for a skill"""
        try:
            # Get performance summary
            performance_summary = await self.performance_tracker.get_skill_summary(skill_id)

            # Get error trends
            error_trends = await self.error_detector.get_error_trends(skill_id)

            # Get optimization status
            optimization_status = await self.optimizer.get_optimization_status(skill_id)

            # Get quality status
            quality_status = await self.quality_enforcer.get_quality_status(skill_id)

            # Get knowledge transfer recommendations
            transfer_recommendations = await self.knowledge_transfer.recommend_patterns_for_skill(skill_id)

            return {
                "skill_id": skill_id,
                "performance": asdict(performance_summary) if performance_summary else None,
                "error_trends": error_trends,
                "optimization": optimization_status,
                "quality": quality_status,
                "knowledge_transfer": transfer_recommendations,
                "last_updated": datetime.now().isoformat(),
            }

        except Exception as e:
            logger.error(f"Failed to get skill insights for {skill_id}: {e}")
            return {"error": str(e)}

    async def get_system_status(self) -> SystemStatus:
        """Get overall system status"""
        try:
            # Check component health
            component_status = {
                "storage": True,  # Would implement health checks
                "performance_tracker": True,
                "error_detector": True,
                "optimizer": True,
                "quality_enforcer": True,
                "knowledge_transfer": True,
                "performance_monitor": True,
            }

            # Count active optimizations
            active_optimizations = len(self.optimizer.active_proposals)

            # Count monitored skills
            total_skills = len(self.performance_tracker.recent_metrics)

            # Identify issues
            issues = []
            if not all(component_status.values()):
                issues.append("Some components are unhealthy")
            if active_optimizations > 10:
                issues.append("High number of active optimizations")
            if self.system_stats["successful_requests"] / max(self.system_stats["total_requests"], 1) < 0.9:
                issues.append("Low request success rate")

            return SystemStatus(
                healthy=len(issues) == 0,
                component_status=component_status,
                active_optimizations=active_optimizations,
                total_skills_monitored=total_skills,
                last_update=datetime.now(),
                issues=issues,
            )

        except Exception as e:
            logger.error(f"Failed to get system status: {e}")
            return SystemStatus(
                healthy=False,
                component_status={},
                active_optimizations=0,
                total_skills_monitored=0,
                last_update=datetime.now(),
                issues=[f"Status check failed: {str(e)}"],
            )

    async def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive system statistics"""
        try:
            # Get storage statistics
            storage_stats = await self.storage.get_storage_statistics()

            # Get knowledge base statistics
            knowledge_stats = await self.knowledge_transfer.get_knowledge_base_stats()

            # Get performance monitoring statistics
            monitoring_stats = await self.performance_monitor.get_statistics()

            return {
                "requests": {
                    "total": self.system_stats["total_requests"],
                    "successful": self.system_stats["successful_requests"],
                    "success_rate": self.system_stats["successful_requests"]
                    / max(self.system_stats["total_requests"], 1),
                    "active": len(self.active_requests),
                },
                "optimizations": {
                    "completed": self.system_stats["optimizations_completed"],
                    "success_rate": "N/A",  # Would calculate from optimizer data
                },
                "quality_gates": {
                    "passed": self.system_stats["quality_gates_passed"],
                    "pass_rate": "N/A",  # Would calculate from quality enforcer data
                },
                "knowledge_transfer": {
                    "completed": self.system_stats["transfers_completed"],
                    "patterns": knowledge_stats.get("total_patterns", 0),
                    "success_rate": knowledge_stats.get("transfer_success_rate", 0),
                },
                "storage": asdict(storage_stats),
                "monitoring": monitoring_stats,
                "uptime": (datetime.now() - datetime.now()).total_seconds() if self._running else 0,
            }

        except Exception as e:
            logger.error(f"Failed to get system statistics: {e}")
            return {"error": str(e)}

    async def create_backup(self, backup_name: Optional[str] = None) -> str:
        """Create a system-wide backup"""
        try:
            return await self.storage.create_backup(backup_name)
        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    async def restore_from_backup(self, backup_name: str) -> bool:
        """Restore system from backup"""
        try:
            return await self.storage.restore_from_backup(backup_name)
        except Exception as e:
            logger.error(f"Failed to restore from backup: {e}")
            return False

    # Private methods

    async def _cleanup_old_requests(self):
        """Clean up old completed requests"""
        try:
            cutoff_time = datetime.now() - timedelta(hours=24)
            expired_requests = [
                request_id
                for request_id, request in self.active_requests.items()
                if request.timestamp < cutoff_time and request.status in ["completed", "failed"]
            ]

            for request_id in expired_requests:
                del self.active_requests[request_id]

        except Exception as e:
            logger.error(f"Failed to cleanup old requests: {e}")
