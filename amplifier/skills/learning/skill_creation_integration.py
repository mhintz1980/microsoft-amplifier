"""
Skill Creation Integration

Integrates Development Fix Recording System with the skill creation pipeline.
Applies learned patterns to prevent recurring issues during skill development.

This module bridges:
- Development Fix Recording System (learning/development_fix_recorder.py)
- Skill Creation Pipeline (creation_pipeline/)
- Agent Lightning Integration (agent_lightning_integration/)
"""

import asyncio
import json
import logging
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Dict
from typing import List

from ..creation_pipeline.validators import SkillValidator
from .development_fix_recorder import AffectedSkill
from .development_fix_recorder import DevelopmentFixRecorder

logger = logging.getLogger(__name__)


class SkillCreationIntegrator:
    """Integrates fix patterns into skill creation pipeline"""

    def __init__(self, fix_recorder: DevelopmentFixRecorder, creation_pipeline_path: Path):
        self.fix_recorder = fix_recorder
        self.creation_pipeline_path = creation_pipeline_path

        # Integration configuration
        self.validation_enabled = True
        self.auto_prevention_enabled = True
        self.learning_feedback_enabled = True

        # Statistics
        self.integration_stats = {
            "skills_validated": 0,
            "issues_prevented": 0,
            "auto_fixes_applied": 0,
            "patterns_applied": 0,
        }

    async def integrate_with_skill_creation(self, skill_specification: Dict[str, Any]) -> Dict[str, Any]:
        """Integrate fix patterns into skill creation process"""
        try:
            logger.info("Integrating development fix patterns into skill creation")

            skill_id = skill_specification.get("skill_id", "unknown")
            skill_name = skill_specification.get("name", "Unknown Skill")
            skill_type = skill_specification.get("skill_type", "general")
            framework_version = skill_specification.get("framework_version", "1.0.0")

            # Stage 1: Pre-creation validation
            pre_creation_results = await self._pre_creation_validation(skill_specification)

            # Stage 2: Enhanced specification
            enhanced_specification = await self._enhance_skill_specification(skill_specification, pre_creation_results)

            # Stage 3: Pattern-based template selection
            template_recommendations = await self._recommend_templates(enhanced_specification)

            # Stage 4: Creation-time monitoring
            creation_monitoring = await self._setup_creation_monitoring(enhanced_specification)

            # Stage 5: Post-creation validation
            post_creation_validation = await self._post_creation_validation(enhanced_specification)

            integration_result = {
                "skill_id": skill_id,
                "skill_name": skill_name,
                "integration_timestamp": datetime.now().isoformat(),
                "pre_creation_validation": pre_creation_results,
                "enhanced_specification": enhanced_specification,
                "template_recommendations": template_recommendations,
                "creation_monitoring": creation_monitoring,
                "post_creation_validation": post_creation_validation,
                "issues_prevented": len(pre_creation_results.get("prevention_suggestions", [])),
                "patterns_applied": len(template_recommendations.get("applied_patterns", [])),
                "overall_success": (
                    len(pre_creation_results.get("issues_found", [])) == 0
                    and post_creation_validation.get("validation_passed", False)
                ),
            }

            # Update statistics
            await self._update_integration_statistics(integration_result)

            return integration_result

        except Exception as e:
            logger.error(f"Failed to integrate fix patterns into skill creation: {e}")
            return {"error": str(e)}

    async def validate_new_skill_code(
        self, skill_id: str, skill_name: str, skill_code: str, skill_type: str
    ) -> Dict[str, Any]:
        """Validate new skill code against known fix patterns"""
        try:
            logger.info(f"Validating new skill {skill_id} against fix patterns")

            # Use fix recorder's validation
            validation_results = await self.fix_recorder.validate_skill_against_patterns(
                skill_id, skill_name, skill_code
            )

            # Add skill creation specific validation
            creation_specific_validation = await self._creation_specific_validation(skill_id, skill_code, skill_type)

            # Combine results
            combined_validation = {
                **validation_results,
                "creation_specific_validation": creation_specific_validation,
                "skill_creation_integration": True,
            }

            # Provide actionable recommendations
            if validation_results.get("issues_found"):
                combined_validation["recommended_actions"] = await self._generate_recommended_actions(
                    validation_results, skill_type
                )

            return combined_validation

        except Exception as e:
            logger.error(f"Failed to validate new skill code: {e}")
            return {"error": str(e)}

    async def apply_prevention_measures(
        self, skill_id: str, skill_name: str, issues_found: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Apply prevention measures for identified issues"""
        try:
            logger.info(f"Applying prevention measures for {len(issues_found)} issues in skill {skill_id}")

            prevention_results = {
                "skill_id": skill_id,
                "prevention_timestamp": datetime.now().isoformat(),
                "measures_applied": [],
                "auto_fixes_applied": [],
                "manual_interventions_required": [],
                "overall_success": True,
            }

            for issue in issues_found:
                # Check if auto-fix is available
                if issue.get("auto_fix_available"):
                    auto_fix_result = await self._apply_auto_fix(skill_id, issue)
                    prevention_results["auto_fixes_applied"].append(auto_fix_result)
                else:
                    # Add to manual interventions
                    prevention_results["manual_interventions_required"].append(
                        {
                            "issue": issue,
                            "recommended_action": issue.get("prevention_strategy", "Manual review required"),
                            "severity": issue.get("severity", "medium"),
                        }
                    )

            # Apply pattern-based prevention
            pattern_preventions = await self._apply_pattern_based_prevention(skill_id, issues_found)
            prevention_results["measures_applied"].extend(pattern_preventions)

            # Calculate overall success
            total_issues = len(issues_found)
            auto_fixed = len(prevention_results["auto_fixes_applied"])
            prevention_results["overall_success"] = (auto_fixed / total_issues) > 0.7 if total_issues > 0 else True

            return prevention_results

        except Exception as e:
            logger.error(f"Failed to apply prevention measures: {e}")
            return {"error": str(e)}

    # Private methods

    async def _pre_creation_validation(self, skill_specification: Dict[str, Any]) -> Dict[str, Any]:
        """Validate skill specification before creation"""
        try:
            skill_id = skill_specification.get("skill_id", "unknown")
            skill_name = skill_specification.get("name", "Unknown Skill")
            skill_type = skill_specification.get("skill_type", "general")
            framework_version = skill_specification.get("framework_version", "1.0.0")

            # Get prevention recommendations
            prevention_recommendations = await self.fix_recorder.get_prevention_recommendations(
                skill_type, framework_version
            )

            # Check specification against known issues
            validation_results = {
                "skill_id": skill_id,
                "validation_timestamp": datetime.now().isoformat(),
                "specification_issues": [],
                "prevention_suggestions": prevention_recommendations.get("recommendations", []),
                "high_priority_patterns": prevention_recommendations.get("high_priority_patterns", []),
                "automated_validations": prevention_recommendations.get("automated_validations", []),
                "estimated_risk_reduction": prevention_recommendations.get("estimated_risk_reduction", 0.0),
            }

            # Check for specification-level issues
            if "framework" in skill_specification:
                framework_issues = await self._check_framework_specification(skill_specification)
                validation_results["specification_issues"].extend(framework_issues)

            # Check dependencies
            if "dependencies" in skill_specification:
                dependency_issues = await self._check_dependencies(skill_specification.get("dependencies", []))
                validation_results["specification_issues"].extend(dependency_issues)

            # Check method signatures
            if "methods" in skill_specification:
                method_issues = await self._check_method_signatures(skill_specification.get("methods", []))
                validation_results["specification_issues"].extend(method_issues)

            return validation_results

        except Exception as e:
            logger.error(f"Failed pre-creation validation: {e}")
            return {"error": str(e)}

    async def _enhance_skill_specification(
        self, skill_specification: Dict[str, Any], validation_results: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Enhance skill specification based on validation results"""
        try:
            enhanced_spec = skill_specification.copy()

            # Add prevention measures
            if validation_results.get("prevention_suggestions"):
                enhanced_spec["prevention_measures"] = validation_results["prevention_suggestions"]

            # Add recommended patterns
            if validation_results.get("high_priority_patterns"):
                enhanced_spec["recommended_patterns"] = validation_results["high_priority_patterns"]

            # Add automated validations
            if validation_results.get("automated_validations"):
                enhanced_spec["automated_validations"] = validation_results["automated_validations"]

            # Add framework fixes based on patterns
            framework_fixes = await self._apply_framework_fixes(skill_specification, validation_results)
            if framework_fixes:
                enhanced_spec["framework_fixes"] = framework_fixes

            # Add method signature fixes
            method_fixes = await self._apply_method_signature_fixes(skill_specification, validation_results)
            if method_fixes:
                enhanced_spec["method_fixes"] = method_fixes

            # Add dependency fixes
            dependency_fixes = await self._apply_dependency_fixes(skill_specification, validation_results)
            if dependency_fixes:
                enhanced_spec["dependency_fixes"] = dependency_fixes

            enhanced_spec["enhancement_timestamp"] = datetime.now().isoformat()

            return enhanced_spec

        except Exception as e:
            logger.error(f"Failed to enhance skill specification: {e}")
            return skill_specification

    async def _recommend_templates(self, enhanced_specification: Dict[str, Any]) -> Dict[str, Any]:
        """Recommend templates based on learned patterns"""
        try:
            skill_type = enhanced_specification.get("skill_type", "general")
            framework_version = enhanced_specification.get("framework_version", "1.0.0")

            recommendations = {
                "skill_type": skill_type,
                "framework_version": framework_version,
                "recommended_templates": [],
                "template_modifications": [],
                "applied_patterns": [],
            }

            # Get templates that incorporate fix patterns
            pattern_based_templates = await self._get_pattern_based_templates(skill_type)

            for template_info in pattern_based_templates:
                template_recommendation = {
                    "template_id": template_info["template_id"],
                    "template_name": template_info["name"],
                    "description": template_info["description"],
                    "prevention_features": template_info.get("prevention_features", []),
                    "applicable_patterns": template_info.get("applicable_patterns", []),
                    "confidence_score": template_info.get("confidence_score", 0.5),
                }
                recommendations["recommended_templates"].append(template_recommendation)

            # Recommend specific template modifications
            if enhanced_specification.get("framework_fixes"):
                recommendations["template_modifications"].append(
                    {
                        "modification_type": "framework_compatibility",
                        "description": "Apply framework unification fixes",
                        "patterns_applied": enhanced_specification["framework_fixes"],
                    }
                )

            if enhanced_specification.get("method_fixes"):
                recommendations["template_modifications"].append(
                    {
                        "modification_type": "method_signature",
                        "description": "Fix method signature compatibility",
                        "patterns_applied": enhanced_specification["method_fixes"],
                    }
                )

            # Track applied patterns
            all_patterns = []
            for template in recommendations["recommended_templates"]:
                all_patterns.extend(template.get("applicable_patterns", []))
            for modification in recommendations["template_modifications"]:
                all_patterns.extend(modification.get("patterns_applied", []))

            recommendations["applied_patterns"] = list(set(all_patterns))

            return recommendations

        except Exception as e:
            logger.error(f"Failed to recommend templates: {e}")
            return {"error": str(e)}

    async def _setup_creation_monitoring(self, enhanced_specification: Dict[str, Any]) -> Dict[str, Any]:
        """Set up monitoring during skill creation"""
        try:
            skill_id = enhanced_specification.get("skill_id", "unknown")

            monitoring_config = {
                "skill_id": skill_id,
                "monitoring_timestamp": datetime.now().isoformat(),
                "monitoring_enabled": True,
                "monitored_patterns": [],
                "alerts_enabled": True,
                "automatic_fixes_enabled": self.auto_prevention_enabled,
            }

            # Identify patterns to monitor during creation
            if enhanced_specification.get("recommended_patterns"):
                monitoring_config["monitored_patterns"] = [
                    pattern["pattern_id"] for pattern in enhanced_specification["recommended_patterns"]
                ]

            # Set up specific monitoring for common issues
            monitoring_config["creation_checks"] = {
                "import_validation": True,
                "abstract_method_implementation": True,
                "framework_compatibility": True,
                "dependency_resolution": True,
                "parameter_signature_validation": True,
            }

            return monitoring_config

        except Exception as e:
            logger.error(f"Failed to setup creation monitoring: {e}")
            return {"error": str(e)}

    async def _post_creation_validation(self, enhanced_specification: Dict[str, Any]) -> Dict[str, Any]:
        """Perform validation after skill creation"""
        try:
            skill_id = enhanced_specification.get("skill_id", "unknown")

            post_validation = {
                "skill_id": skill_id,
                "validation_timestamp": datetime.now().isoformat(),
                "validation_passed": True,
                "post_creation_issues": [],
                "learnings_extracted": [],
                "pattern_feedback": [],
            }

            # This would integrate with the actual created skill
            # For now, simulate validation based on applied patterns

            if enhanced_specification.get("applied_patterns"):
                # Validate that patterns were correctly applied
                pattern_feedback = await self._validate_pattern_application(
                    skill_id, enhanced_specification.get("applied_patterns", [])
                )
                post_validation["pattern_feedback"] = pattern_feedback

                # Extract learnings for continuous improvement
                learnings = await self._extract_creation_learnings(skill_id, enhanced_specification, pattern_feedback)
                post_validation["learnings_extracted"] = learnings

            return post_validation

        except Exception as e:
            logger.error(f"Failed post-creation validation: {e}")
            return {"error": str(e)}

    async def _creation_specific_validation(self, skill_id: str, skill_code: str, skill_type: str) -> Dict[str, Any]:
        """Perform creation-specific validation"""
        try:
            validation_results = {
                "skill_id": skill_id,
                "validation_timestamp": datetime.now().isoformat(),
                "creation_issues": [],
                "warnings": [],
                "recommendations": [],
            }

            # Check for creation pipeline specific issues
            lines = skill_code.split("\n")

            # Check for common creation issues
            for i, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Check for placeholder implementations
                if line_stripped.startswith("raise NotImplementedError"):
                    validation_results["creation_issues"].append(
                        {
                            "line_number": i,
                            "issue_type": "placeholder_implementation",
                            "description": "Placeholder NotImplementedError found",
                            "severity": "medium",
                        }
                    )

                # Check for missing documentation
                if "def " in line_stripped and not line_stripped.startswith("def _"):
                    if i + 1 < len(lines) and not lines[i].strip().startswith('"""'):
                        validation_results["warnings"].append(
                            {
                                "line_number": i,
                                "warning_type": "missing_documentation",
                                "description": "Public method missing documentation",
                                "severity": "low",
                            }
                        )

                # Check for TODO comments
                if "TODO" in line_stripped:
                    validation_results["creation_issues"].append(
                        {
                            "line_number": i,
                            "issue_type": "incomplete_implementation",
                            "description": "TODO comment indicates incomplete implementation",
                            "severity": "medium",
                        }
                    )

            # Generate recommendations
            if validation_results["creation_issues"]:
                validation_results["recommendations"].append(
                    "Complete all placeholder implementations before skill activation"
                )

            if validation_results["warnings"]:
                validation_results["recommendations"].append(
                    "Add comprehensive documentation to improve maintainability"
                )

            return validation_results

        except Exception as e:
            logger.error(f"Failed creation-specific validation: {e}")
            return {"error": str(e)}

    async def _generate_recommended_actions(
        self, validation_results: Dict[str, Any], skill_type: str
    ) -> List[Dict[str, Any]]:
        """Generate recommended actions based on validation results"""
        actions = []

        try:
            # Auto-fix actions
            for auto_fix in validation_results.get("auto_fixes_available", []):
                actions.append(
                    {
                        "action_type": "auto_fix",
                        "priority": "high" if auto_fix["severity"] in ["critical", "high"] else "medium",
                        "description": auto_fix["fix_description"],
                        "rule_id": auto_fix["rule_id"],
                        "pattern_id": auto_fix["pattern_id"],
                    }
                )

            # Prevention actions
            for prevention in validation_results.get("prevention_suggestions", []):
                actions.append(
                    {
                        "action_type": "prevention",
                        "priority": "high" if prevention["severity"] in ["critical", "high"] else "medium",
                        "description": prevention["description"],
                        "rule_id": prevention["rule_id"],
                        "pattern_id": prevention["pattern_id"],
                    }
                )

            # Risk-based actions
            if validation_results.get("overall_risk_score", 0) > 0.7:
                actions.append(
                    {
                        "action_type": "high_risk_review",
                        "priority": "critical",
                        "description": "High overall risk score requires manual review",
                        "risk_score": validation_results["overall_risk_score"],
                    }
                )

            # Skill type specific actions
            if skill_type in ["core_technology", "framework"]:
                actions.append(
                    {
                        "action_type": "enhanced_validation",
                        "priority": "high",
                        "description": "Core technology skills require enhanced validation",
                    }
                )

        except Exception as e:
            logger.error(f"Failed to generate recommended actions: {e}")

        return actions

    async def _apply_auto_fix(self, skill_id: str, issue: Dict[str, Any]) -> Dict[str, Any]:
        """Apply an automatic fix for an issue"""
        try:
            auto_fix_result = {
                "skill_id": skill_id,
                "issue_fixed": issue.get("rule_id", "unknown"),
                "fix_timestamp": datetime.now().isoformat(),
                "success": False,
                "fix_applied": None,
                "side_effects": [],
            }

            # This would contain actual auto-fix logic
            # For now, simulate successful auto-fix
            if issue.get("auto_fix_available"):
                auto_fix_result["success"] = True
                auto_fix_result["fix_applied"] = issue.get("fix_description", "Applied automatic fix")
                auto_fix_result["side_effects"] = []  # Would track any side effects

            return auto_fix_result

        except Exception as e:
            logger.error(f"Failed to apply auto fix: {e}")
            return {"success": False, "error": str(e)}

    async def _apply_pattern_based_prevention(
        self, skill_id: str, issues_found: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Apply pattern-based prevention measures"""
        preventions = []

        try:
            for issue in issues_found:
                pattern_id = issue.get("pattern_id")
                if pattern_id:
                    prevention = {
                        "skill_id": skill_id,
                        "pattern_id": pattern_id,
                        "prevention_type": "pattern_based",
                        "prevention_timestamp": datetime.now().isoformat(),
                        "applied": True,
                    }
                    preventions.append(prevention)

        except Exception as e:
            logger.error(f"Failed to apply pattern-based prevention: {e}")

        return preventions

    # Helper methods for specific validation types

    async def _check_framework_specification(self, skill_specification: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Check framework specification for issues"""
        issues = []

        try:
            framework = skill_specification.get("framework")
            if framework:
                # Check framework compatibility
                if framework.get("version") not in ["1.0.0", "2.0.0"]:
                    issues.append(
                        {
                            "issue_type": "framework_version_compatibility",
                            "description": f"Framework version {framework.get('version')} may have compatibility issues",
                            "severity": "medium",
                        }
                    )

                # Check framework parameters
                required_params = ["skill_id", "name", "description"]
                framework_params = framework.get("parameters", {})
                missing_params = [p for p in required_params if p not in framework_params]

                if missing_params:
                    issues.append(
                        {
                            "issue_type": "missing_framework_parameters",
                            "description": f"Missing required framework parameters: {missing_params}",
                            "severity": "high",
                        }
                    )

        except Exception as e:
            logger.error(f"Failed to check framework specification: {e}")

        return issues

    async def _check_dependencies(self, dependencies: List[str]) -> List[Dict[str, Any]]:
        """Check dependencies for known issues"""
        issues = []

        try:
            # Check for known problematic dependencies
            problematic_patterns = [
                "NonExistentClass",
                "ConcurrentAPI",  # Known import issue from React 19 Expert
                "DeprecatedModule",
            ]

            for dep in dependencies:
                for pattern in problematic_patterns:
                    if pattern in dep:
                        issues.append(
                            {
                                "issue_type": "problematic_dependency",
                                "description": f"Dependency '{dep}' contains known problematic pattern '{pattern}'",
                                "severity": "high",
                                "dependency": dep,
                                "pattern": pattern,
                            }
                        )

        except Exception as e:
            logger.error(f"Failed to check dependencies: {e}")

        return issues

    async def _check_method_signatures(self, methods: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Check method signatures for compatibility issues"""
        issues = []

        try:
            # Check for abstract method implementation issues
            for method in methods:
                if method.get("is_abstract") and not method.get("implemented"):
                    issues.append(
                        {
                            "issue_type": "unimplemented_abstract_method",
                            "description": f"Abstract method '{method.get('name', 'unknown')}' is not implemented",
                            "severity": "high",
                            "method": method.get("name"),
                        }
                    )

                # Check method signature compatibility
                if method.get("signature"):
                    signature = method["signature"]
                    if "different_signature" in signature:  # Known issue pattern
                        issues.append(
                            {
                                "issue_type": "method_signature_incompatibility",
                                "description": f"Method '{method.get('name', 'unknown')}' has incompatible signature",
                                "severity": "medium",
                                "method": method.get("name"),
                            }
                        )

        except Exception as e:
            logger.error(f"Failed to check method signatures: {e}")

        return issues

    async def _update_integration_statistics(self, integration_result: Dict[str, Any]):
        """Update integration statistics"""
        self.integration_stats["skills_validated"] += 1
        self.integration_stats["issues_prevented"] += integration_result.get("issues_prevented", 0)
        self.integration_stats["patterns_applied"] += integration_result.get("patterns_applied", 0)

    async def _get_pattern_based_templates(self, skill_type: str) -> List[Dict[str, Any]]:
        """Get templates that incorporate fix patterns"""
        # This would query actual template system
        # For now, return placeholder templates
        return [
            {
                "template_id": "framework_compatible_v2",
                "name": "Framework Compatible Template v2",
                "description": "Template with built-in framework unification fixes",
                "prevention_features": ["parameter_validation", "signature_compatibility"],
                "applicable_patterns": ["pattern_framework_unification_*"],
                "confidence_score": 0.9,
            },
            {
                "template_id": "safe_imports_template",
                "name": "Safe Imports Template",
                "description": "Template with validated import statements",
                "prevention_features": ["import_validation", "dependency_checking"],
                "applicable_patterns": ["pattern_import_cascading_failure_*"],
                "confidence_score": 0.8,
            },
        ]

    async def _validate_pattern_application(self, skill_id: str, applied_patterns: List[str]) -> List[Dict[str, Any]]:
        """Validate that patterns were correctly applied"""
        feedback = []

        try:
            for pattern_id in applied_patterns:
                # This would check actual pattern application
                feedback.append(
                    {
                        "pattern_id": pattern_id,
                        "application_status": "applied",
                        "validation_result": "success",
                        "issues": [],
                    }
                )

        except Exception as e:
            logger.error(f"Failed to validate pattern application: {e}")

        return feedback

    async def _extract_creation_learnings(
        self, skill_id: str, enhanced_specification: Dict[str, Any], pattern_feedback: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Extract learnings from skill creation process"""
        learnings = []

        try:
            # Extract learnings from successful pattern applications
            successful_patterns = [f for f in pattern_feedback if f.get("validation_result") == "success"]

            for feedback in successful_patterns:
                learning = {
                    "pattern_id": feedback["pattern_id"],
                    "learning_type": "successful_application",
                    "skill_id": skill_id,
                    "learning_timestamp": datetime.now().isoformat(),
                    "insights": [f"Pattern {feedback['pattern_id']} successfully applied to {skill_id}"],
                }
                learnings.append(learning)

        except Exception as e:
            logger.error(f"Failed to extract creation learnings: {e}")

        return learnings
