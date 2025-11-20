"""
Frontend Skill Monitor

Real-time monitoring and optimization system for all frontend skills.
Integrates Agent Lightning's continuous optimization with React 19, TypeScript,
and Vite specialization for zero-hallucination enforcement.
"""

import asyncio
import json
import logging
import time
from dataclasses import asdict
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..quality_assurance.validators.zero_hallucination_validator import ZeroHallucinationValidator
from .config import PerformanceTrackingConfig
from .config import RLTrainingConfig
from .error_detection_engine import Severity

logger = logging.getLogger(__name__)


class FrontendTechnology(Enum):
    """Frontend technologies being monitored"""

    REACT_19 = "react_19"
    TYPESCRIPT = "typescript"
    VITE = "vite"
    VUE = "vue"
    STREAMLIT = "streamlit"
    NEXT_JS = "next_js"


@dataclass
class FrontendSkillMetrics:
    """Metrics for frontend skill performance"""

    skill_id: str
    technology: FrontendTechnology
    code_quality_score: float
    compilation_success_rate: float
    runtime_error_rate: float
    hallucination_risk_score: float
    performance_grade: str  # A, B, C, D, F
    last_updated: datetime
    api_accuracy_score: float
    type_safety_score: float
    build_success_rate: float


@dataclass
class RealTimeAlert:
    """Real-time alert for frontend skill issues"""

    alert_id: str
    skill_id: str
    technology: FrontendTechnology
    alert_type: str
    severity: Severity
    message: str
    detected_at: datetime
    requires_immediate_action: bool
    auto_fix_available: bool
    suggested_actions: list[str]


class FrontendSkillMonitor:
    """Real-time monitoring and optimization for frontend skills"""

    def __init__(
        self,
        rl_config: RLTrainingConfig,
        perf_config: PerformanceTrackingConfig,
        storage_path: Path,
        frontend_skills_dir: Path = None,
    ):
        self.rl_config = rl_config
        self.perf_config = perf_config
        self.storage_path = storage_path
        self.frontend_skills_dir = frontend_skills_dir or Path("scenarios/industrial_agents/frontend_assistant")

        # Initialize components
        self.zero_hallucination_validator = ZeroHallucinationValidator(
            accuracy_threshold=0.99,  # 99% accuracy requirement
            enable_external_validation=True,
            strict_mode=True,
        )

        # Frontend-specific monitoring
        self.skill_metrics: dict[str, FrontendSkillMetrics] = {}
        self.active_alerts: dict[str, RealTimeAlert] = {}
        self.technology_patterns: dict[FrontendTechnology, dict[str, Any]] = {}

        # Background monitoring
        self._monitoring_task: asyncio.Task | None = None
        self._validation_task: asyncio.Task | None = None
        self._optimization_task: asyncio.Task | None = None
        self._running = False

        # Initialize technology-specific patterns
        self._initialize_technology_patterns()

    async def start(self):
        """Start the frontend skill monitoring system"""
        if self._running:
            return

        self._running = True
        logger.info("🚀 Starting Agent Lightning Frontend Skill Monitor")

        # Discover frontend skills
        await self._discover_frontend_skills()

        # Start monitoring tasks
        self._monitoring_task = asyncio.create_task(self._monitoring_loop())
        self._validation_task = asyncio.create_task(self._validation_loop())
        self._optimization_task = asyncio.create_task(self._optimization_loop())

        logger.info("✅ Frontend Skill Monitor started - monitoring React 19, TypeScript, and Vite skills")

    async def stop(self):
        """Stop the monitoring system"""
        if not self._running:
            return

        self._running = False
        logger.info("Stopping Frontend Skill Monitor")

        # Cancel background tasks
        if self._monitoring_task:
            self._monitoring_task.cancel()
        if self._validation_task:
            self._validation_task.cancel()
        if self._optimization_task:
            self._optimization_task.cancel()

        # Save monitoring data
        await self._save_monitoring_data()

    async def scan_frontend_skill(self, skill_path: Path) -> FrontendSkillMetrics:
        """Comprehensive scan of a frontend skill"""
        try:
            skill_id = skill_path.name

            # Detect technology
            technology = await self._detect_technology(skill_path)

            # Zero-hallucination validation
            validation_report = await self.zero_hallucination_validator.validate_skill(skill_path)

            # Code quality analysis
            code_quality_score = await self._analyze_code_quality(skill_path, technology)

            # Compilation and build testing
            compilation_success = await self._test_compilation(skill_path, technology)

            # Runtime error detection
            runtime_errors = await self._detect_runtime_errors(skill_path, technology)

            # API accuracy validation
            api_accuracy = await self._validate_api_accuracy(skill_path, technology)

            # Type safety for TypeScript
            type_safety = await self._check_type_safety(skill_path, technology)

            # Build success rate
            build_success = await self._test_build_process(skill_path, technology)

            # Calculate performance grade
            performance_grade = self._calculate_performance_grade(
                code_quality_score, compilation_success, api_accuracy, validation_report.overall_confidence, type_safety
            )

            # Calculate hallucination risk
            hallucination_risk = 1.0 - validation_report.overall_confidence

            metrics = FrontendSkillMetrics(
                skill_id=skill_id,
                technology=technology,
                code_quality_score=code_quality_score,
                compilation_success_rate=compilation_success,
                runtime_error_rate=runtime_errors,
                hallucination_risk_score=hallucination_risk,
                performance_grade=performance_grade,
                last_updated=datetime.now(),
                api_accuracy_score=api_accuracy,
                type_safety_score=type_safety,
                build_success_rate=build_success,
            )

            # Store metrics
            self.skill_metrics[skill_id] = metrics

            # Generate alerts if needed
            await self._generate_alerts(metrics, validation_report)

            logger.info(f"✅ Scanned frontend skill {skill_id}: Grade {performance_grade} ({technology.value})")
            return metrics

        except Exception as e:
            logger.error(f"❌ Failed to scan frontend skill {skill_path}: {e}")
            raise

    async def get_frontend_skill_status(self, skill_id: str) -> dict[str, Any]:
        """Get comprehensive status of a frontend skill"""
        try:
            if skill_id not in self.skill_metrics:
                return {"error": f"Skill {skill_id} not found in monitoring"}

            metrics = self.skill_metrics[skill_id]

            # Get active alerts
            alerts = [alert for alert in self.active_alerts.values() if alert.skill_id == skill_id]

            # Get recent optimization status
            optimization_status = await self._get_optimization_status(skill_id)

            # Technology-specific insights
            technology_insights = await self._get_technology_insights(metrics.technology)

            return {
                "skill_id": skill_id,
                "technology": metrics.technology.value,
                "performance_grade": metrics.performance_grade,
                "metrics": asdict(metrics),
                "active_alerts": [asdict(alert) for alert in alerts],
                "critical_alerts": len([a for a in alerts if a.severity == Severity.CRITICAL]),
                "optimization_status": optimization_status,
                "technology_insights": technology_insights,
                "last_scan": metrics.last_updated.isoformat(),
                "health_score": self._calculate_health_score(metrics),
            }

        except Exception as e:
            logger.error(f"Failed to get frontend skill status {skill_id}: {e}")
            return {"error": str(e)}

    async def optimize_frontend_skill(self, skill_id: str, optimization_targets: list[str] = None) -> dict[str, Any]:
        """Trigger optimization for a frontend skill"""
        try:
            if skill_id not in self.skill_metrics:
                return {"error": f"Skill {skill_id} not found in monitoring"}

            metrics = self.skill_metrics[skill_id]

            # Determine optimization priorities
            if not optimization_targets:
                optimization_targets = self._identify_optimization_priorities(metrics)

            logger.info(f"🚀 Starting optimization for {skill_id}: {optimization_targets}")

            # Apply technology-specific optimizations
            optimizations_applied = []

            for target in optimization_targets:
                if target == "zero_hallucination":
                    result = await self._fix_hallucination_issues(skill_id)
                    optimizations_applied.append(result)
                elif target == "api_accuracy":
                    result = await self._fix_api_accuracy_issues(skill_id, metrics.technology)
                    optimizations_applied.append(result)
                elif target == "type_safety":
                    result = await self._improve_type_safety(skill_id, metrics.technology)
                    optimizations_applied.append(result)
                elif target == "performance":
                    result = await self._optimize_performance(skill_id, metrics.technology)
                    optimizations_applied.append(result)
                elif target == "build_issues":
                    result = await self._fix_build_issues(skill_id, metrics.technology)
                    optimizations_applied.append(result)

            # Re-scan skill to measure improvements
            skill_path = self.frontend_skills_dir / skill_id
            new_metrics = await self.scan_frontend_skill(skill_path)

            # Calculate improvements
            improvements = self._calculate_improvements(metrics, new_metrics)

            logger.info(f"✅ Optimization completed for {skill_id}: {improvements}")

            return {
                "skill_id": skill_id,
                "optimizations_applied": optimizations_applied,
                "improvements": improvements,
                "before_metrics": asdict(metrics),
                "after_metrics": asdict(new_metrics),
                "success": True,
            }

        except Exception as e:
            logger.error(f"Failed to optimize frontend skill {skill_id}: {e}")
            return {"error": str(e), "success": False}

    # Private methods

    async def _discover_frontend_skills(self):
        """Discover all frontend skills in the codebase"""
        try:
            logger.info("🔍 Discovering frontend skills...")

            # Look in known frontend directories
            frontend_directories = [
                self.frontend_skills_dir,
                Path("scenarios/industrial_agents/frontend_assistant/generators"),
                Path("amplifier/career_copilot/frontend"),
            ]

            for directory in frontend_directories:
                if directory.exists():
                    for item in directory.iterdir():
                        if item.is_dir() and not item.name.startswith("."):
                            # Scan this skill
                            await self.scan_frontend_skill(item)

            logger.info(f"✅ Discovered and monitoring {len(self.skill_metrics)} frontend skills")

        except Exception as e:
            logger.error(f"Failed to discover frontend skills: {e}")

    async def _monitoring_loop(self):
        """Continuous monitoring loop"""
        while self._running:
            try:
                logger.debug("Running frontend skill monitoring cycle...")

                # Re-scan all skills
                for skill_id in list(self.skill_metrics.keys()):
                    skill_path = self.frontend_skills_dir / skill_id
                    if skill_path.exists():
                        await self.scan_frontend_skill(skill_path)

                # Check for new skills
                await self._discover_frontend_skills()

                # Sleep for monitoring interval
                await asyncio.sleep(300)  # 5 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                await asyncio.sleep(60)

    async def _validation_loop(self):
        """Continuous validation loop"""
        while self._running:
            try:
                logger.debug("Running zero-hallucination validation cycle...")

                # Validate all skills for hallucinations
                for skill_id in self.skill_metrics.keys():
                    skill_path = self.frontend_skills_dir / skill_id
                    if skill_path.exists():
                        await self._validate_hallucination_free(skill_path, skill_id)

                await asyncio.sleep(1800)  # 30 minutes

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in validation loop: {e}")
                await asyncio.sleep(300)

    async def _optimization_loop(self):
        """Continuous optimization loop"""
        while self._running:
            try:
                logger.debug("Running continuous optimization cycle...")

                # Identify skills needing optimization
                skills_to_optimize = [
                    skill_id
                    for skill_id, metrics in self.skill_metrics.items()
                    if metrics.performance_grade in ["D", "F"] or metrics.hallucination_risk_score > 0.1
                ]

                for skill_id in skills_to_optimize:
                    try:
                        await self.optimize_frontend_skill(skill_id)
                        await asyncio.sleep(60)  # Pause between optimizations
                    except Exception as e:
                        logger.error(f"Failed to optimize {skill_id}: {e}")

                await asyncio.sleep(3600)  # 1 hour between optimization cycles

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in optimization loop: {e}")
                await asyncio.sleep(600)

    async def _detect_technology(self, skill_path: Path) -> FrontendTechnology:
        """Detect the frontend technology used"""
        try:
            # Check for React 19
            if await self._check_for_react_19(skill_path):
                return FrontendTechnology.REACT_19

            # Check for TypeScript
            if await self._check_for_typescript(skill_path):
                return FrontendTechnology.TYPESCRIPT

            # Check for Vite
            if await self._check_for_vite(skill_path):
                return FrontendTechnology.VITE

            # Check for Vue
            if await self._check_for_vue(skill_path):
                return FrontendTechnology.VUE

            # Check for Streamlit
            if await self._check_for_streamlit(skill_path):
                return FrontendTechnology.STREAMLIT

            # Default to generic
            return FrontendTechnology.REACT_19  # Default assumption

        except Exception as e:
            logger.error(f"Failed to detect technology for {skill_path}: {e}")
            return FrontendTechnology.REACT_19

    async def _check_for_react_19(self, skill_path: Path) -> bool:
        """Check if skill uses React 19"""
        try:
            # Look for package.json with React 19
            package_json = skill_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    react_version = data.get("dependencies", {}).get("react", "")
                    if "19" in react_version:
                        return True

            # Look for React 19 patterns in code
            for py_file in skill_path.glob("**/*.py"):
                content = py_file.read_text()
                if "React 19" in content or "react@19" in content:
                    return True

            return False

        except Exception:
            return False

    async def _check_for_typescript(self, skill_path: Path) -> bool:
        """Check if skill uses TypeScript"""
        try:
            # Look for TypeScript files
            ts_files = list(skill_path.glob("**/*.ts")) + list(skill_path.glob("**/*.tsx"))
            if ts_files:
                return True

            # Look for tsconfig.json
            if (skill_path / "tsconfig.json").exists():
                return True

            return False

        except Exception:
            return False

    async def _check_for_vite(self, skill_path: Path) -> bool:
        """Check if skill uses Vite"""
        try:
            # Look for vite.config files
            vite_configs = list(skill_path.glob("**/vite.config.*"))
            if vite_configs:
                return True

            # Look for Vite in package.json
            package_json = skill_path / "package.json"
            if package_json.exists():
                with open(package_json) as f:
                    data = json.load(f)
                    if "vite" in data.get("devDependencies", {}):
                        return True

            return False

        except Exception:
            return False

    async def _check_for_vue(self, skill_path: Path) -> bool:
        """Check if skill uses Vue"""
        try:
            # Look for Vue files
            vue_files = list(skill_path.glob("**/*.vue"))
            if vue_files:
                return True

            return False

        except Exception:
            return False

    async def _check_for_streamlit(self, skill_path: Path) -> bool:
        """Check if skill uses Streamlit"""
        try:
            for py_file in skill_path.glob("**/*.py"):
                content = py_file.read_text()
                if "import streamlit" in content or "from streamlit" in content:
                    return True

            return False

        except Exception:
            return False

    async def _initialize_technology_patterns(self):
        """Initialize technology-specific patterns and validation rules"""

        # React 19 patterns
        self.technology_patterns[FrontendTechnology.REACT_19] = {
            "api_patterns": [
                r"use\(state\)",
                r"use\(effect\)",
                r"use\(callback\)",
                r"use\(memo\)",
                r"useRef\(.*\)",
                r"forwardRef\(.*\)",
                r"useDeferredValue\(.*\)",
                r"useTransition\(\)",
            ],
            "common_errors": [
                "Invalid hook call",
                "Hook rules violation",
                "Stale closure",
                "React render error",
                "Component re-render infinite loop",
            ],
            "optimization_patterns": [
                "useMemo for expensive calculations",
                "useCallback for function references",
                "React.memo for component memoization",
                "useDeferredValue for non-urgent updates",
            ],
        }

        # TypeScript patterns
        self.technology_patterns[FrontendTechnology.TYPESCRIPT] = {
            "api_patterns": [
                r"interface\s+\w+",
                r"type\s+\w+",
                r"enum\s+\w+",
                r":\s*\w+(\[\])?",
                r"<\w+>",
                r"implements\s+\w+",
            ],
            "common_errors": [
                "Type error",
                "Property does not exist",
                "Type mismatch",
                "Cannot find module",
                "Implicit any",
            ],
            "optimization_patterns": [
                "Strict TypeScript configuration",
                "Proper typing for all functions",
                "Interface definitions for data structures",
                "Generic type parameters",
            ],
        }

        # Vite patterns
        self.technology_patterns[FrontendTechnology.VITE] = {
            "api_patterns": [
                r"import\.meta\.env",
                r"defineConfig\(",
                r"vite\s*\(",
                r"@vitejs/plugin-",
                r"build\s*:",
                r"server\s*:",
            ],
            "common_errors": [
                "Module resolution error",
                "Build configuration error",
                "Development server error",
                "Hot module replacement error",
            ],
            "optimization_patterns": [
                "Optimized build configuration",
                "Proper module resolution",
                "Environment variable handling",
                "Code splitting configuration",
            ],
        }

    async def _validate_hallucination_free(self, skill_path: Path, skill_id: str):
        """Validate that skill is hallucination-free"""
        try:
            validation_report = await self.zero_hallucination_validator.validate_skill(skill_path)

            if not validation_report.overall_passed:
                # Create critical alert
                alert = RealTimeAlert(
                    alert_id=f"hallucination_{skill_id}_{int(time.time())}",
                    skill_id=skill_id,
                    technology=self.skill_metrics.get(skill_id, FrontendTechnology.REACT_19),
                    alert_type="hallucination_detected",
                    severity=Severity.CRITICAL,
                    message=f"Zero-hallucination validation failed: {len(validation_report.critical_issues)} issues",
                    detected_at=datetime.now(),
                    requires_immediate_action=True,
                    auto_fix_available=True,
                    suggested_actions=[
                        "Run zero-hallucination fix",
                        "Validate API references",
                        "Check React 19 API accuracy",
                        "Verify TypeScript types",
                    ],
                )

                self.active_alerts[alert.alert_id] = alert
                logger.warning(f"🚨 CRITICAL: Hallucination detected in {skill_id}")

        except Exception as e:
            logger.error(f"Failed hallucination validation for {skill_id}: {e}")

    def _calculate_performance_grade(self, *scores) -> str:
        """Calculate overall performance grade"""
        try:
            avg_score = sum(scores) / len(scores)

            if avg_score >= 0.95:
                return "A"
            if avg_score >= 0.90:
                return "B"
            if avg_score >= 0.80:
                return "C"
            if avg_score >= 0.70:
                return "D"
            return "F"

        except Exception:
            return "F"

    def _calculate_health_score(self, metrics: FrontendSkillMetrics) -> float:
        """Calculate overall health score for a skill"""
        weights = {
            "code_quality": 0.2,
            "compilation_success": 0.25,
            "api_accuracy": 0.25,
            "type_safety": 0.15,
            "build_success": 0.15,
        }

        score = (
            metrics.code_quality_score * weights["code_quality"]
            + metrics.compilation_success_rate * weights["compilation_success"]
            + metrics.api_accuracy_score * weights["api_accuracy"]
            + metrics.type_safety_score * weights["type_safety"]
            + metrics.build_success_rate * weights["build_success"]
        )

        # Penalize for hallucination risk
        score *= 1.0 - metrics.hallucination_risk_score

        return max(0.0, min(1.0, score))

    async def _save_monitoring_data(self):
        """Save monitoring data to persistent storage"""
        try:
            # Save skill metrics
            metrics_file = self.storage_path / "frontend_skill_metrics.json"
            metrics_data = {skill_id: asdict(metrics) for skill_id, metrics in self.skill_metrics.items()}

            with open(metrics_file, "w") as f:
                json.dump(metrics_data, f, indent=2, default=str)

            # Save alerts
            alerts_file = self.storage_path / "frontend_skill_alerts.json"
            alerts_data = {alert_id: asdict(alert) for alert_id, alert in self.active_alerts.items()}

            with open(alerts_file, "w") as f:
                json.dump(alerts_data, f, indent=2, default=str)

            logger.info("💾 Frontend skill monitoring data saved")

        except Exception as e:
            logger.error(f"Failed to save monitoring data: {e}")
