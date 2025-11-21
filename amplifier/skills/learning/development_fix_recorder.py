"""
Development Fix Recording System

Bridges development fixes to Agent Lightning's learning patterns.
Captures systematic fixes and converts them into transferable knowledge
for future skill development and prevention of recurring issues.

This system connects development fixes to existing learning infrastructure:
- Pattern Learning System (meta_skills/pattern_learning_system.py)
- Knowledge Transfer System (agent_lightning_integration/knowledge_transfer_system.py)
- Error Detection Engine (agent_lightning_integration/error_detection_engine.py)
"""

import asyncio
import json
import logging
from collections import defaultdict
from dataclasses import asdict
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any
from typing import Optional
from typing import Type

from amplifier.mcp.persistent_storage import store_result

logger = logging.getLogger(__name__)


class FixType(Enum):
    """Types of development fixes"""

    FRAMEWORK_UNIFICATION = "framework_unification"
    IMPORT_CASCADING_FAILURE = "import_cascading_failure"
    ABSTRACT_METHOD_IMPLEMENTATION = "abstract_method_implementation"
    REGISTRATION_SYSTEM_INCOMPATIBILITY = "registration_system_incompatibility"
    PARAMETER_MISMATCH = "parameter_mismatch"
    DEPENDENCY_CONFLICT = "dependency_conflict"
    CONFIGURATION_ERROR = "configuration_error"
    VALIDATION_FAILURE = "validation_failure"
    PERFORMANCE_ISSUE = "performance_issue"
    SECURITY_FIX = "security_fix"


class SeverityLevel(Enum):
    """Severity levels for fixes"""

    CRITICAL = "critical"  # Blocks skill development completely
    HIGH = "high"  # Major functionality impact
    MEDIUM = "medium"  # Moderate impact, workaround exists
    LOW = "low"  # Minor issue, cosmetic or small improvement


class PreventionStrategy(Enum):
    """Types of prevention strategies"""

    AUTATED_VALIDATION = "automated_validation"  # Add automated checks
    TEMPLATE_UPDATE = "template_update"  # Update code templates
    DOCUMENTATION = "documentation"  # Improve documentation
    FRAMEWORK_CHANGE = "framework_change"  # Modify frameworks
    TESTING_REQUIREMENT = "testing_requirement"  # Add mandatory tests
    CODE_GENERATION = "code_generation"  # Generate code to prevent issue


@dataclass
class AffectedSkill:
    """Information about a skill affected by a fix"""

    skill_id: str
    skill_name: str
    framework_version: str
    impact_description: str
    fix_status: str = "fixed"  # "fixed", "pending", "failed"
    fix_timestamp: Optional[datetime] = None


@dataclass
class FixPattern:
    """A transferable pattern extracted from a development fix"""

    pattern_id: str
    fix_type: FixType
    title: str
    description: str
    symptoms: list[str]
    root_cause: str
    solution_approach: str
    implementation_details: dict[str, Any]
    prevention_strategy: PreventionStrategy
    transferability_score: float  # 0-1, how applicable to other skills
    confidence: float  # 0-1, confidence in the fix pattern
    effectiveness_score: float  # 0-1, how effective the fix was
    created_at: datetime
    applications_count: int = 0
    successful_applications: int = 0


@dataclass
class DevelopmentFix:
    """Record of a specific development fix"""

    fix_id: str
    fix_type: FixType
    severity: SeverityLevel
    title: str
    description: str
    issue_description: str
    root_cause_analysis: str
    solution_implementation: str
    affected_skills: list[AffectedSkill]
    fix_timestamp: datetime
    fixed_by: str  # "claude", "user", "automated"
    verification_status: str = "verified"  # "verified", "pending", "failed"
    lessons_learned: list[str] = field(default_factory=list)
    prevention_measures: list[str] = field(default_factory=list)
    related_patterns: list[str] = field(default_factory=list)  # pattern_ids


@dataclass
class ValidationRule:
    """Validation rule to prevent future occurrences"""

    rule_id: str
    pattern_id: str
    fix_type: FixType
    rule_name: str
    validation_logic: str  # Description or code for validation
    severity: SeverityLevel
    auto_fix_available: bool
    auto_fix_implementation: Optional[str]
    created_at: datetime
    active: bool = True


@dataclass
class FixApplication:
    """Application of a fix pattern to a new skill"""

    application_id: str
    pattern_id: str
    target_skill_id: str
    target_skill_name: str
    application_timestamp: datetime
    prevention_applied: bool
    validation_results: dict[str, Any]
    success: bool
    issues_prevented: list[str]
    new_issues_introduced: list[str] = field(default_factory=list)
    lessons_learned: list[str] = field(default_factory=list)


class DevelopmentFixRecorder:
    """Main system for recording and learning from development fixes"""

    def __init__(self, storage_path: Path):
        self.storage_path = storage_path
        self.storage_path.mkdir(parents=True, exist_ok=True)

        # Storage
        self.fixes: dict[str, DevelopmentFix] = {}
        self.patterns: dict[str, FixPattern] = {}
        self.validation_rules: dict[str, ValidationRule] = {}
        self.applications: dict[str, FixApplication] = {}

        # Statistics
        self.fix_statistics: dict[str, Any] = {
            "total_fixes": 0,
            "fixes_by_type": defaultdict(int),
            "fixes_by_severity": defaultdict(int),
            "patterns_created": 0,
            "successful_preventions": 0,
        }

        # Integration flags
        self.knowledge_transfer_enabled = True
        self.pattern_learning_enabled = True

    async def record_fix(
        self,
        fix_type: FixType,
        severity: SeverityLevel,
        title: str,
        issue_description: str,
        root_cause_analysis: str,
        solution_implementation: str,
        affected_skills: list[AffectedSkill],
        fixed_by: str = "claude",
        symptoms: Optional[list[str]] = None,
        implementation_details: Optional[dict[str, Any]] = None,
    ) -> DevelopmentFix:
        """Record a new development fix"""
        try:
            logger.info(f"Recording development fix: {title}")

            # Create fix record
            fix = DevelopmentFix(
                fix_id=f"fix_{fix_type.value}_{int(datetime.now().timestamp())}",
                fix_type=fix_type,
                severity=severity,
                title=title,
                description=f"Fix for {fix_type.value}: {title}",
                issue_description=issue_description,
                root_cause_analysis=root_cause_analysis,
                solution_implementation=solution_implementation,
                affected_skills=affected_skills,
                fix_timestamp=datetime.now(),
                fixed_by=fixed_by,
            )

            # Store fix
            self.fixes[fix.fix_id] = fix

            # Extract pattern from fix
            pattern = await self._extract_pattern_from_fix(fix, symptoms, implementation_details)
            if pattern:
                self.patterns[pattern.pattern_id] = pattern
                fix.related_patterns.append(pattern.pattern_id)

                # Create validation rules
                await self._create_validation_rules(pattern)

                # Integrate with existing learning systems
                await self._integrate_with_learning_systems(pattern)

            # Update statistics
            await self._update_statistics(fix)

            # Persist data
            await self._save_fix_data()

            logger.info(
                f"Successfully recorded fix {fix.fix_id} and extracted pattern {pattern.pattern_id if pattern else 'None'}"
            )
            return fix

        except Exception as e:
            logger.error(f"Failed to record development fix: {e}")
            raise

    async def validate_skill_against_patterns(self, skill_id: str, skill_name: str, skill_code: str) -> dict[str, Any]:
        """Validate a new skill against known fix patterns to prevent issues"""
        try:
            logger.info(f"Validating skill {skill_id} against {len(self.patterns)} fix patterns")

            validation_results = {
                "skill_id": skill_id,
                "validation_timestamp": datetime.now().isoformat(),
                "issues_found": [],
                "prevention_suggestions": [],
                "auto_fixes_available": [],
                "overall_risk_score": 0.0,
            }

            high_risk_issues = []

            # Check against all validation rules
            for rule in self.validation_rules.values():
                if not rule.active:
                    continue

                rule_violations = await self._check_validation_rule(rule, skill_code)
                if rule_violations:
                    validation_results["issues_found"].extend(rule_violations)

                    # Add prevention suggestions
                    if rule.auto_fix_available:
                        validation_results["auto_fixes_available"].append(
                            {
                                "rule_id": rule.rule_id,
                                "pattern_id": rule.pattern_id,
                                "fix_description": rule.auto_fix_implementation,
                                "severity": rule.severity.value,
                            }
                        )
                    else:
                        validation_results["prevention_suggestions"].append(
                            {
                                "rule_id": rule.rule_id,
                                "pattern_id": rule.pattern_id,
                                "prevention_strategy": "Manual review required",
                                "description": rule.validation_logic,
                                "severity": rule.severity.value,
                            }
                        )

                    # Track high-risk issues
                    if rule.severity in [SeverityLevel.CRITICAL, SeverityLevel.HIGH]:
                        high_risk_issues.extend(rule_violations)

            # Calculate overall risk score
            if self.validation_rules:
                critical_count = sum(
                    1
                    for issue in validation_results["issues_found"]
                    if any(
                        r.severity == SeverityLevel.CRITICAL
                        for r in self.validation_rules.values()
                        if r.validation_logic in str(issue)
                    )
                )
                high_count = sum(
                    1
                    for issue in validation_results["issues_found"]
                    if any(
                        r.severity == SeverityLevel.HIGH
                        for r in self.validation_rules.values()
                        if r.validation_logic in str(issue)
                    )
                )

                validation_results["overall_risk_score"] = min(
                    1.0, (critical_count * 0.8 + high_count * 0.4) / len(self.validation_rules)
                )

            # Record validation
            if validation_results["issues_found"]:
                await self._record_validation_application(skill_id, skill_name, validation_results)

            logger.info(f"Validation completed for {skill_id}: {len(validation_results['issues_found'])} issues found")
            return validation_results

        except Exception as e:
            logger.error(f"Failed to validate skill {skill_id}: {e}")
            return {"error": str(e)}

    async def get_fix_patterns_for_type(self, fix_type: FixType) -> list[FixPattern]:
        """Get all fix patterns for a specific type"""
        return [pattern for pattern in self.patterns.values() if pattern.fix_type == fix_type]

    async def get_prevention_recommendations(self, skill_type: str, framework_version: str) -> dict[str, Any]:
        """Get prevention recommendations for a new skill"""
        try:
            recommendations = {
                "skill_type": skill_type,
                "framework_version": framework_version,
                "recommendations": [],
                "high_priority_patterns": [],
                "automated_validations": [],
                "estimated_risk_reduction": 0.0,
            }

            # Find relevant patterns based on skill type and framework
            relevant_patterns = []
            for pattern in self.patterns.values():
                if pattern.transferability_score > 0.6:  # Highly transferable
                    relevant_patterns.append(pattern)

            # Sort by effectiveness and transferability
            relevant_patterns.sort(key=lambda p: p.effectiveness_score * p.transferability_score, reverse=True)

            # Generate recommendations
            for pattern in relevant_patterns[:5]:  # Top 5 recommendations
                recommendation = {
                    "pattern_id": pattern.pattern_id,
                    "title": pattern.title,
                    "description": pattern.description,
                    "prevention_strategy": pattern.prevention_strategy.value,
                    "confidence": pattern.confidence,
                    "expected_benefit": pattern.effectiveness_score * pattern.transferability_score,
                }
                recommendations["recommendations"].append(recommendation)

                if pattern.effectiveness_score > 0.8 and pattern.transferability_score > 0.7:
                    recommendations["high_priority_patterns"].append(recommendation)

            # Add automated validations
            automated_rules = [
                rule for rule in self.validation_rules.values() if rule.auto_fix_available and rule.active
            ]

            for rule in automated_rules:
                recommendations["automated_validations"].append(
                    {
                        "rule_id": rule.rule_id,
                        "rule_name": rule.rule_name,
                        "auto_fix_description": rule.auto_fix_implementation,
                        "severity": rule.severity.value,
                    }
                )

            # Calculate estimated risk reduction
            if recommendations["recommendations"]:
                avg_benefit = sum(r["expected_benefit"] for r in recommendations["recommendations"]) / len(
                    recommendations["recommendations"]
                )
                recommendations["estimated_risk_reduction"] = min(0.9, avg_benefit)

            return recommendations

        except Exception as e:
            logger.error(f"Failed to get prevention recommendations: {e}")
            return {"error": str(e)}

    # Private methods for pattern extraction and integration

    async def _extract_pattern_from_fix(
        self,
        fix: DevelopmentFix,
        symptoms: Optional[list[str]] = None,
        implementation_details: Optional[dict[str, Any]] = None,
    ) -> Optional[FixPattern]:
        """Extract a transferable pattern from a development fix"""
        try:
            # Determine transferability based on fix characteristics
            transferability_score = self._calculate_transferability_score(fix)

            if transferability_score < 0.3:  # Not transferable enough
                return None

            # Determine prevention strategy
            prevention_strategy = self._determine_prevention_strategy(fix)

            # Create pattern
            pattern = FixPattern(
                pattern_id=f"pattern_{fix.fix_type.value}_{int(datetime.now().timestamp())}",
                fix_type=fix.fix_type,
                title=fix.title,
                description=fix.description,
                symptoms=symptoms or [fix.issue_description],
                root_cause=fix.root_cause_analysis,
                solution_approach=fix.solution_implementation,
                implementation_details=implementation_details or {},
                prevention_strategy=prevention_strategy,
                transferability_score=transferability_score,
                confidence=0.8,  # Default confidence
                effectiveness_score=0.9,  # Assume high effectiveness for recorded fixes
                created_at=datetime.now(),
            )

            return pattern

        except Exception as e:
            logger.error(f"Failed to extract pattern from fix {fix.fix_id}: {e}")
            return None

    def _calculate_transferability_score(self, fix: DevelopmentFix) -> float:
        """Calculate how transferable this fix pattern is"""
        score = 0.5  # Base score

        # Framework-level fixes are highly transferable
        if fix.fix_type in [
            FixType.FRAMEWORK_UNIFICATION,
            FixType.IMPORT_CASCADING_FAILURE,
            FixType.ABSTRACT_METHOD_IMPLEMENTATION,
        ]:
            score += 0.3

        # Multiple affected skills indicates transferability
        if len(fix.affected_skills) > 1:
            score += 0.2

        # Systematic issues are more transferable
        if "framework" in fix.root_cause_analysis.lower() or "system" in fix.root_cause_analysis.lower():
            score += 0.1

        # Clear solution approach increases transferability
        if len(fix.solution_implementation) > 100:  # Detailed solution
            score += 0.1

        return min(score, 1.0)

    def _determine_prevention_strategy(self, fix: DevelopmentFix) -> PreventionStrategy:
        """Determine the best prevention strategy for this fix type"""
        strategy_mapping = {
            FixType.FRAMEWORK_UNIFICATION: PreventionStrategy.FRAMEWORK_CHANGE,
            FixType.IMPORT_CASCADING_FAILURE: PreventionStrategy.AUTATED_VALIDATION,
            FixType.ABSTRACT_METHOD_IMPLEMENTATION: PreventionStrategy.TEMPLATE_UPDATE,
            FixType.REGISTRATION_SYSTEM_INCOMPATIBILITY: PreventionStrategy.FRAMEWORK_CHANGE,
            FixType.PARAMETER_MISMATCH: PreventionStrategy.AUTATED_VALIDATION,
            FixType.DEPENDENCY_CONFLICT: PreventionStrategy.AUTATED_VALIDATION,
            FixType.CONFIGURATION_ERROR: PreventionStrategy.TEMPLATE_UPDATE,
            FixType.VALIDATION_FAILURE: PreventionStrategy.CODE_GENERATION,
        }

        return strategy_mapping.get(fix.fix_type, PreventionStrategy.DOCUMENTATION)

    async def _create_validation_rules(self, pattern: FixPattern):
        """Create validation rules from a fix pattern"""
        try:
            # Create validation rule based on pattern type
            rule = ValidationRule(
                rule_id=f"rule_{pattern.pattern_id}",
                pattern_id=pattern.pattern_id,
                fix_type=pattern.fix_type,
                rule_name=f"Prevent {pattern.fix_type.value}",
                validation_logic=self._generate_validation_logic(pattern),
                severity=SeverityLevel.HIGH if pattern.effectiveness_score > 0.8 else SeverityLevel.MEDIUM,
                auto_fix_available=pattern.prevention_strategy
                in [
                    PreventionStrategy.AUTATED_VALIDATION,
                    PreventionStrategy.CODE_GENERATION,
                ],
                auto_fix_implementation=self._generate_auto_fix_implementation(pattern),
                created_at=datetime.now(),
            )

            self.validation_rules[rule.rule_id] = rule
            logger.info(f"Created validation rule {rule.rule_id} for pattern {pattern.pattern_id}")

        except Exception as e:
            logger.error(f"Failed to create validation rules for pattern {pattern.pattern_id}: {e}")

    def _generate_validation_logic(self, pattern: FixPattern) -> str:
        """Generate validation logic description for a pattern"""
        logic_templates = {
            FixType.FRAMEWORK_UNIFICATION: "Check skill framework compatibility and parameter signatures",
            FixType.IMPORT_CASCADING_FAILURE: "Validate all import statements and class dependencies",
            FixType.ABSTRACT_METHOD_IMPLEMENTATION: "Ensure all abstract methods are properly implemented",
            FixType.REGISTRATION_SYSTEM_INCOMPATIBILITY: "Verify skill registration follows framework requirements",
            FixType.PARAMETER_MISMATCH: "Validate method signatures match framework expectations",
            FixType.DEPENDENCY_CONFLICT: "Check for conflicting dependency versions",
        }

        return logic_templates.get(pattern.fix_type, f"Validate {pattern.fix_type.value} requirements")

    def _generate_auto_fix_implementation(self, pattern: FixPattern) -> Optional[str]:
        """Generate auto-fix implementation description"""
        fix_templates = {
            FixType.IMPORT_CASCADING_FAILURE: "Automatically remove invalid imports and suggest correct alternatives",
            FixType.ABSTRACT_METHOD_IMPLEMENTATION: "Generate missing abstract method implementations with proper signatures",
            FixType.PARAMETER_MISMATCH: "Update method signatures to match framework requirements",
            FixType.DEPENDENCY_CONFLICT: "Update dependency versions to compatible combinations",
        }

        return fix_templates.get(pattern.fix_type)

    async def _check_validation_rule(self, rule: ValidationRule, skill_code: str) -> list[str]:
        """Check if a skill violates a validation rule"""
        violations = []

        try:
            # This would contain actual validation logic
            # For now, simulate checking based on rule type and code content

            if rule.fix_type == FixType.IMPORT_CASCADING_FAILURE:
                # Check for problematic imports
                if "from NonExistentClass" in skill_code or "import NonExistentModule" in skill_code:
                    violations.append(f"Invalid import detected: {rule.validation_logic}")

            elif rule.fix_type == FixType.ABSTRACT_METHOD_IMPLEMENTATION:
                # Check for missing abstract methods
                if "abstractmethod" in skill_code and "pass" in skill_code:
                    violations.append(f"Unimplemented abstract method: {rule.validation_logic}")

            elif rule.fix_type == FixType.FRAMEWORK_UNIFICATION:
                # Check for framework mismatches
                if "def __init__(self, different_signature)" in skill_code:
                    violations.append(f"Framework signature mismatch: {rule.validation_logic}")

        except Exception as e:
            logger.error(f"Failed to check validation rule {rule.rule_id}: {e}")

        return violations

    async def _integrate_with_learning_systems(self, pattern: FixPattern):
        """Integrate fix pattern with Agent Lightning's learning systems"""
        try:
            if not self.knowledge_transfer_enabled and not self.pattern_learning_enabled:
                return

            # Convert to knowledge transfer format
            if self.knowledge_transfer_enabled:
                await self._sync_to_knowledge_transfer_system(pattern)

            # Convert to pattern learning format
            if self.pattern_learning_enabled:
                await self._sync_to_pattern_learning_system(pattern)

        except Exception as e:
            logger.error(f"Failed to integrate pattern {pattern.pattern_id} with learning systems: {e}")

    async def _sync_to_knowledge_transfer_system(self, pattern: FixPattern):
        """Sync pattern to Agent Lightning's Knowledge Transfer System"""
        try:
            # Convert to Agent Lightning skill pattern format
            from ..agent_lightning_integration.knowledge_transfer_system import PatternType, SkillPattern

            pattern_type_mapping = {
                FixType.FRAMEWORK_UNIFICATION: PatternType.CODE_STRUCTURE,
                FixType.IMPORT_CASCADING_FAILURE: PatternType.ERROR_HANDLING,
                FixType.ABSTRACT_METHOD_IMPLEMENTATION: PatternType.CODE_STRUCTURE,
                FixType.PERFORMANCE_ISSUE: PatternType.PERFORMANCE_OPTIMIZATION,
                FixType.SECURITY_FIX: PatternType.ERROR_HANDLING,
            }

            al_pattern_type = pattern_type_mapping.get(pattern.fix_type, PatternType.CODE_STRUCTURE)

            # Create skill pattern for knowledge transfer
            skill_pattern = SkillPattern(
                pattern_id=pattern.pattern_id,
                source_skill_id="development_fixes",
                pattern_type=al_pattern_type,
                description=pattern.description,
                implementation_details=pattern.implementation_details,
                performance_impact=pattern.effectiveness_score,
                success_rate=pattern.confidence,
                complexity_score=0.5,
                transferability_score=pattern.transferability_score,
                created_at=pattern.created_at,
            )

            # Store for knowledge transfer system integration
            await store_result(
                namespace="knowledge_transfer_patterns",
                key=pattern.pattern_id,
                data=asdict(skill_pattern),
            )

            logger.info(f"Synced pattern {pattern.pattern_id} to Knowledge Transfer System")

        except Exception as e:
            logger.warning(f"Failed to sync to Knowledge Transfer System: {e}")

    async def _sync_to_pattern_learning_system(self, pattern: FixPattern):
        """Sync pattern to Agent Lightning's Pattern Learning System"""
        try:
            # Convert to pattern learning format
            pattern_data = {
                "pattern_id": pattern.pattern_id,
                "pattern_type": "development_fix",
                "fix_type": pattern.fix_type.value,
                "description": pattern.description,
                "symptoms": pattern.symptoms,
                "solution_approach": pattern.solution_approach,
                "prevention_strategy": pattern.prevention_strategy.value,
                "transferability_score": pattern.transferability_score,
                "confidence": pattern.confidence,
                "effectiveness_score": pattern.effectiveness_score,
                "created_at": pattern.created_at.isoformat(),
            }

            await store_result(
                namespace="pattern_learning_system",
                key=f"development_fix_{pattern.pattern_id}",
                data=pattern_data,
            )

            logger.info(f"Synced pattern {pattern.pattern_id} to Pattern Learning System")

        except Exception as e:
            logger.warning(f"Failed to sync to Pattern Learning System: {e}")

    async def _record_validation_application(self, skill_id: str, skill_name: str, validation_results: dict[str, Any]):
        """Record application of validation to a skill"""
        try:
            application = FixApplication(
                application_id=f"validation_{skill_id}_{int(datetime.now().timestamp())}",
                pattern_id="validation_check",
                target_skill_id=skill_id,
                target_skill_name=skill_name,
                application_timestamp=datetime.now(),
                prevention_applied=len(validation_results["prevention_suggestions"]) > 0,
                validation_results=validation_results,
                success=len(validation_results["issues_found"]) == 0,
                issues_prevented=validation_results["prevention_suggestions"],
            )

            self.applications[application.application_id] = application

        except Exception as e:
            logger.error(f"Failed to record validation application: {e}")

    async def _update_statistics(self, fix: DevelopmentFix):
        """Update system statistics"""
        self.fix_statistics["total_fixes"] += 1
        self.fix_statistics["fixes_by_type"][fix.fix_type.value] += 1
        self.fix_statistics["fixes_by_severity"][fix.severity.value] += 1

    async def _save_fix_data(self):
        """Save all fix data to persistent storage"""
        try:
            # Save fixes
            await store_result(
                namespace="development_fixes",
                key="all_fixes",
                data={fix_id: asdict(fix) for fix_id, fix in self.fixes.items()},
            )

            # Save patterns
            await store_result(
                namespace="development_fixes",
                key="all_patterns",
                data={pattern_id: asdict(pattern) for pattern_id, pattern in self.patterns.items()},
            )

            # Save validation rules
            await store_result(
                namespace="development_fixes",
                key="validation_rules",
                data={rule_id: asdict(rule) for rule_id, rule in self.validation_rules.items()},
            )

            # Save statistics
            await store_result(
                namespace="development_fixes",
                key="statistics",
                data=self.fix_statistics,
            )

            logger.info("Saved fix recording data to persistent storage")

        except Exception as e:
            logger.error(f"Failed to save fix data: {e}")

    async def get_system_statistics(self) -> dict[str, Any]:
        """Get comprehensive system statistics"""
        return {
            **self.fix_statistics,
            "total_patterns": len(self.patterns),
            "active_validation_rules": len([r for r in self.validation_rules.values() if r.active]),
            "total_validations": len(self.applications),
            "prevention_success_rate": (
                len([a for a in self.applications.values() if a.success]) / len(self.applications)
                if self.applications
                else 0.0
            ),
        }
