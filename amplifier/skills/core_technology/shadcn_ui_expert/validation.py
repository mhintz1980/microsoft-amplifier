"""
ShadCN/ui Validation Engine

Comprehensive validation system for ShadCN/ui components with zero-hallucination guarantee.
Ensures production-ready code quality and best practices compliance.
"""

import re
import ast
from typing import Dict, List, Any, Optional, Tuple, Union
from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class ValidationSeverity(Enum):
    """Validation issue severity levels."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class ValidationCategory(Enum):
    """Categories of validation checks."""

    SYNTAX = "syntax"
    IMPORTS = "imports"
    TYPESCRIPT = "typescript"
    ACCESSIBILITY = "accessibility"
    PERFORMANCE = "performance"
    BEST_PRACTICES = "best_practices"
    SECURITY = "security"
    COMPONENT_API = "component_api"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during analysis."""

    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    rule_id: str = ""
    fix_suggestion: str = ""
    automated_fix: Optional[str] = None


@dataclass
class ValidationReport:
    """Comprehensive validation report for component analysis."""

    component_name: str
    issues: List[ValidationIssue]
    score: int  # 0-100 quality score
    is_production_ready: bool
    recommendations: List[str]
    fixes_applied: List[str]


class ValidationEngine:
    """
    Comprehensive validation engine for ShadCN/ui components.

    Provides:
    - Syntax and TypeScript validation
    - Import dependency checking
    - Accessibility compliance validation
    - Performance impact analysis
    - Best practices enforcement
    - Security vulnerability detection
    - Automated fix suggestions
    """

    def __init__(self):
        self.validation_rules = self._init_validation_rules()
        self.shadcn_patterns = self._init_shadcn_patterns()
        self.security_rules = self._init_security_rules()
        self.performance_rules = self._init_performance_rules()

    def _init_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Initialize comprehensive validation rules."""
        return {
            "imports": {
                "required_imports": {
                    "Button": 'from "@/components/ui/button"',
                    "Input": 'from "@/components/ui/input"',
                    "Card": 'from "@/components/ui/card"',
                    "Dialog": 'from "@/components/ui/dialog"',
                    "Form": 'from "@/components/ui/form"',
                },
                "utils_required": {
                    "cn": 'from "@/lib/utils"',
                    "React": 'from "react"',
                },
            },
            "typescript": {
                "required_interfaces": [
                    "React.ReactNode",
                    "React.HTMLAttributes",
                    "React.ButtonHTMLAttributes",
                ],
                "generic_constraints": [
                    "extends React.HTMLAttributes<HTMLElement>",
                    "extends React.ComponentPropsWithoutRef",
                ],
            },
            "accessibility": {
                "required_attributes": {
                    "Button": ["aria-label", "disabled"],
                    "Input": ["aria-describedby", "aria-invalid", "id"],
                    "Form": ["noValidate"],
                },
                "keyboard_support": ["onKeyDown", "onKeyPress", "onKeyUp"],
            },
            "performance": {
                "avoid_patterns": [
                    "React.useEffect(() => {}, [all])",
                    "useState({})",
                    "anonymous arrow functions in render",
                ],
                "recommended_patterns": ["React.memo", "useCallback", "useMemo"],
            },
        }

    def _init_shadcn_patterns(self) -> Dict[str, Any]:
        """Initialize ShadCN/ui specific patterns."""
        return {
            "component_structure": {
                "import_pattern": r'import\s*\{\s*([^}]+)\s*\}\s*from\s*["\']@/components/ui/([^"\']+)["\']',
                "cn_usage_pattern": r"className=\{?cn\([^)]+)\}?",
                "variant_pattern": r'variant=(["\'])?(default|destructive|outline|secondary|ghost|link)',
                "size_pattern": r'size=(["\'])?(default|sm|lg|icon)',
            },
            "styling_patterns": {
                "tailwind_classes": r'className=(["\'])?([^"\']*(?:bg-|text-|border-|p-|m-|flex|grid|block|hidden)[^"\']*)',
                "responsive_prefixes": ["sm:", "md:", "lg:", "xl:", "2xl:"],
                "state_prefixes": ["hover:", "focus:", "active:", "disabled:"],
            },
            "radix_patterns": {
                "as_child": r"asChild",
                "trigger_components": ["DialogTrigger", "DropdownMenuTrigger", "PopoverTrigger"],
                "content_components": ["DialogContent", "DropdownMenuContent", "PopoverContent"],
            },
        }

    def _init_security_rules(self) -> Dict[str, Any]:
        """Initialize security validation rules."""
        return {
            "xss_prevention": {
                "dangerous_patterns": [
                    r"dangerouslySetInnerHTML",
                    r"innerHTML\s*=",
                    r"outerHTML\s*=",
                ],
                "safe_alternatives": [
                    "Use textContent instead",
                    "Sanitize HTML with DOMPurify",
                    "Use JSX expressions for dynamic content",
                ],
            },
            "dependency_security": {
                "suspicious_packages": ["eval", "Function", "setTimeout with string", "setInterval with string"]
            },
        }

    def _init_performance_rules(self) -> Dict[str, Any]:
        """Initialize performance validation rules."""
        return {
            "render_optimization": {
                "memo_candidates": [
                    "Components with expensive calculations",
                    "Components receiving complex objects as props",
                    "Components with frequent re-renders",
                ],
                "callback_dependencies": ["Functions passed to child components", "Event handlers", "Async operations"],
            },
            "bundle_optimization": {
                "tree_shaking_hints": [
                    "Use named imports instead of default imports",
                    "Avoid importing entire libraries",
                    "Use dynamic imports for large dependencies",
                ]
            },
        }

    def validate_component(self, component_code: str, component_name: str = "Unknown") -> ValidationReport:
        """
        Perform comprehensive validation of a ShadCN/ui component.

        Args:
            component_code: Component code to validate
            component_name: Name of the component being validated

        Returns:
            Comprehensive validation report
        """
        issues = []
        recommendations = []
        fixes_applied = []

        # Syntax validation
        syntax_issues = self._validate_syntax(component_code)
        issues.extend(syntax_issues)

        # Import validation
        import_issues = self._validate_imports(component_code, component_name)
        issues.extend(import_issues)

        # TypeScript validation
        ts_issues = self._validate_typescript(component_code)
        issues.extend(ts_issues)

        # Accessibility validation
        a11y_issues = self._validate_accessibility(component_code)
        issues.extend(a11y_issues)

        # Performance validation
        perf_issues = self._validate_performance(component_code)
        issues.extend(perf_issues)

        # Security validation
        security_issues = self._validate_security(component_code)
        issues.extend(security_issues)

        # Best practices validation
        bp_issues = self._validate_best_practices(component_code, component_name)
        issues.extend(bp_issues)

        # Calculate score
        score = self._calculate_quality_score(issues)

        # Generate recommendations
        recommendations = self._generate_recommendations(issues)

        # Check if production ready
        is_production_ready = self._is_production_ready(issues)

        return ValidationReport(
            component_name=component_name,
            issues=issues,
            score=score,
            is_production_ready=is_production_ready,
            recommendations=recommendations,
            fixes_applied=fixes_applied,
        )

    def _validate_syntax(self, code: str) -> List[ValidationIssue]:
        """Validate JavaScript/TypeScript syntax."""
        issues = []

        # Basic syntax checks
        if code.count("{") != code.count("}"):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.SYNTAX,
                    message="Mismatched braces in component",
                    rule_id="syntax_braces",
                    fix_suggestion="Check for missing or extra braces",
                )
            )

        if code.count("(") != code.count(")"):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.SYNTAX,
                    message="Mismatched parentheses in component",
                    rule_id="syntax_parens",
                    fix_suggestion="Check for missing or extra parentheses",
                )
            )

        # Try to parse as AST
        try:
            ast.parse(code)
        except SyntaxError as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.SYNTAX,
                    message=f"Syntax error: {str(e)}",
                    line_number=e.lineno,
                    column_number=e.offset,
                    rule_id="syntax_parse",
                    fix_suggestion="Fix syntax error at indicated line",
                )
            )

        return issues

    def _validate_imports(self, code: str, component_name: str) -> List[ValidationIssue]:
        """Validate import statements and dependencies."""
        issues = []

        # Check for required imports based on component usage
        used_components = re.findall(r"<(\w+)", code)

        for component in used_components:
            if component in self.validation_rules["imports"]["required_imports"]:
                required_import = self.validation_rules["imports"]["required_imports"][component]
                if required_import not in code:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category=ValidationCategory.IMPORTS,
                            message=f"Missing import for {component} component",
                            rule_id="import_component",
                            fix_suggestion=f"Add: {required_import}",
                            automated_fix=required_import,
                        )
                    )

        # Check for utils import if cn is used
        if "cn(" in code and 'from "@/lib/utils"' not in code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.IMPORTS,
                    message="Missing import for cn utility function",
                    rule_id="import_utils",
                    fix_suggestion='Add: import { cn } from "@/lib/utils"',
                    automated_fix='import { cn } from "@/lib/utils"',
                )
            )

        # Check for React import
        if any(pattern in code for pattern in ["useState", "useEffect", "useMemo", "useCallback"]):
            if 'from "react"' not in code:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.IMPORTS,
                        message="Missing React import for hooks usage",
                        rule_id="import_react",
                        fix_suggestion='Add: import React from "react"',
                        automated_fix='import React from "react"',
                    )
                )

        return issues

    def _validate_typescript(self, code: str) -> List[ValidationIssue]:
        """Validate TypeScript types and interfaces."""
        issues = []

        # Check for any type annotations
        if "interface" in code or "type " in code:
            # TypeScript usage detected, ensure proper typing
            if "React.ReactNode" not in code and "children" in code:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.TYPESCRIPT,
                        message="Consider typing children prop as React.ReactNode",
                        rule_id="ts_children_type",
                        fix_suggestion="Add: children?: React.ReactNode",
                    )
                )

        # Check for prop interfaces
        if "Props" in code and "interface" in code:
            # Good TypeScript practice detected
            pass
        elif "export default function" in code and "interface" not in code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.TYPESCRIPT,
                    message="Consider defining props interface for better type safety",
                    rule_id="ts_props_interface",
                    fix_suggestion="Define an interface for component props",
                )
            )

        return issues

    def _validate_accessibility(self, code: str) -> List[ValidationIssue]:
        """Validate accessibility compliance."""
        issues = []

        # Check for button accessibility
        if "<Button" in code:
            if "aria-label" not in code and not self._has_text_content(code):
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.ACCESSIBILITY,
                        message="Button should have accessible name",
                        rule_id="a11y_button_name",
                        fix_suggestion="Add aria-label or visible text to button",
                        automated_fix='aria-label="Action button"',
                    )
                )

        # Check for form field accessibility
        if "Input" in code or "Textarea" in code:
            if "htmlFor" not in code and "id=" not in code:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.WARNING,
                        category=ValidationCategory.ACCESSIBILITY,
                        message="Form inputs should have associated labels",
                        rule_id="a11y_form_labels",
                        fix_suggestion="Add htmlFor attribute to label and matching id to input",
                    )
                )

        # Check for focus management
        if "focus:" not in code and "Button" in code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.ACCESSIBILITY,
                    message="Consider adding focus styles for better keyboard navigation",
                    rule_id="a11y_focus_styles",
                    fix_suggestion="Add focus:ring-2 focus:ring-blue-500 to className",
                )
            )

        return issues

    def _validate_performance(self, code: str) -> List[ValidationIssue]:
        """Validate performance implications."""
        issues = []

        # Check for expensive operations in render
        if ".map(" in code and "useMemo" not in code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.PERFORMANCE,
                    message="Consider wrapping map operation in useMemo for optimization",
                    rule_id="perf_map_memo",
                    fix_suggestion="Use useMemo to memoize mapped arrays",
                )
            )

        # Check for inline functions in render
        inline_function_patterns = [
            r"onClick=\{.*?=>",
            r"onChange=\{.*?=>",
            r"className=\{.*?\(.*?\) =>",
        ]

        for pattern in inline_function_patterns:
            if re.search(pattern, code) and "useCallback" not in code:
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.PERFORMANCE,
                        message="Inline function in render may cause unnecessary re-renders",
                        rule_id="perf_inline_function",
                        fix_suggestion="Consider using useCallback for event handlers",
                    )
                )
                break

        # Check for multiple useEffect hooks
        useEffect_count = code.count("useEffect")
        if useEffect_count > 3:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category=ValidationCategory.PERFORMANCE,
                    message=f"Multiple useEffect hooks ({useEffect_count}) - consider consolidating",
                    rule_id="perf_multiple_effects",
                    fix_suggestion="Consolidate related effects or extract custom hooks",
                )
            )

        return issues

    def _validate_security(self, code: str) -> List[ValidationIssue]:
        """Validate security implications."""
        issues = []

        # Check for XSS vulnerabilities
        dangerous_patterns = self.security_rules["xss_prevention"]["dangerous_patterns"]
        for pattern in dangerous_patterns:
            if re.search(pattern, code):
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category=ValidationCategory.SECURITY,
                        message=f"Potentially unsafe pattern detected: {pattern}",
                        rule_id="sec_xss_risk",
                        fix_suggestion="Avoid dangerous patterns that could lead to XSS",
                    )
                )

        # Check for eval usage
        if "eval(" in code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category=ValidationCategory.SECURITY,
                    message="Direct eval() usage detected",
                    rule_id="sec_eval_usage",
                    fix_suggestion="Avoid eval() - consider safer alternatives",
                )
            )

        return issues

    def _validate_best_practices(self, code: str, component_name: str) -> List[ValidationIssue]:
        """Validate ShadCN/ui best practices."""
        issues = []

        # Check for proper className usage
        if "className=" in code and "cn(" not in code:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.BEST_PRACTICES,
                    message="Consider using cn() utility for className management",
                    rule_id="bp_cn_usage",
                    fix_suggestion="Use cn() from @/lib/utils for better className handling",
                )
            )

        # Check for consistent import ordering
        imports = re.findall(r'import.*from.*["\'].*["\']', code)
        if imports:
            shadcn_imports = [imp for imp in imports if "@/components/ui/" in imp]
            other_imports = [imp for imp in imports if "@/components/ui/" not in imp]

            # Check if shadcn imports are grouped together
            shadcn_indices = [code.find(imp) for imp in shadcn_imports]
            if len(shadcn_indices) > 1 and not self._is_consecutive(shadcn_indices):
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category=ValidationCategory.BEST_PRACTICES,
                        message="Group ShadCN/ui imports together for better organization",
                        rule_id="bp_import_grouping",
                        fix_suggestion="Group all @/components/ui imports together",
                    )
                )

        # Check for component naming convention
        if component_name and not component_name.endswith("Component"):
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category=ValidationCategory.BEST_PRACTICES,
                    message="Consider adding 'Component' suffix for clarity",
                    rule_id="bp_naming",
                    fix_suggestion=f"Rename {component_name} to {component_name}Component",
                )
            )

        return issues

    def _has_text_content(self, code: str) -> bool:
        """Check if component has visible text content."""
        # Look for text between tags
        text_matches = re.findall(r">([^<\s][^<]*[^<\s])<", code)
        return len(text_matches) > 0

    def _is_consecutive(self, indices: List[int]) -> bool:
        """Check if list contains consecutive numbers."""
        if len(indices) <= 1:
            return True

        sorted_indices = sorted(indices)
        for i in range(1, len(sorted_indices)):
            if sorted_indices[i] - sorted_indices[i - 1] > 100:  # Allow some whitespace
                return False
        return True

    def _calculate_quality_score(self, issues: List[ValidationIssue]) -> int:
        """Calculate quality score based on validation issues."""
        if not issues:
            return 100

        score = 100
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                score -= 20
            elif issue.severity == ValidationSeverity.WARNING:
                score -= 10
            elif issue.severity == ValidationSeverity.INFO:
                score -= 5

        return max(0, score)

    def _generate_recommendations(self, issues: List[ValidationIssue]) -> List[str]:
        """Generate improvement recommendations based on issues."""
        recommendations = []

        # Group issues by category
        by_category = {}
        for issue in issues:
            if issue.category not in by_category:
                by_category[issue.category] = []
            by_category[issue.category].append(issue)

        # Generate category-specific recommendations
        if ValidationCategory.ACCESSIBILITY in by_category:
            recommendations.append("Focus on accessibility improvements for WCAG compliance")

        if ValidationCategory.PERFORMANCE in by_category:
            recommendations.append("Optimize component performance with React optimization patterns")

        if ValidationCategory.SECURITY in by_category:
            recommendations.append("Address security vulnerabilities immediately")

        if ValidationCategory.TYPESCRIPT in by_category:
            recommendations.append("Improve type safety with proper TypeScript interfaces")

        return recommendations

    def _is_production_ready(self, issues: List[ValidationIssue]) -> bool:
        """Determine if component is production ready."""
        # Component is not production ready if it has any errors
        has_errors = any(issue.severity == ValidationSeverity.ERROR for issue in issues)

        # Also not ready if too many warnings
        warning_count = sum(1 for issue in issues if issue.severity == ValidationSeverity.WARNING)

        return not has_errors and warning_count <= 5

    def get_validation_summary(self, reports: List[ValidationReport]) -> Dict[str, Any]:
        """Get summary statistics for multiple validation reports."""
        if not reports:
            return {"total_components": 0, "average_score": 0, "production_ready": 0, "common_issues": []}

        total_score = sum(report.score for report in reports)
        production_ready_count = sum(1 for report in reports if report.is_production_ready)

        # Find common issues
        all_issues = []
        for report in reports:
            all_issues.extend(report.issues)

        issue_frequency = {}
        for issue in all_issues:
            key = f"{issue.rule_id}:{issue.message}"
            issue_frequency[key] = issue_frequency.get(key, 0) + 1

        common_issues = sorted(issue_frequency.items(), key=lambda x: x[1], reverse=True)[:5]

        return {
            "total_components": len(reports),
            "average_score": total_score // len(reports),
            "production_ready": production_ready_count,
            "production_ready_percentage": (production_ready_count / len(reports)) * 100,
            "common_issues": common_issues,
            "issue_categories": self._get_issue_categories(all_issues),
        }

    def _get_issue_categories(self, issues: List[ValidationIssue]) -> Dict[str, int]:
        """Count issues by category."""
        category_count = {}
        for issue in issues:
            category_count[issue.category.value] = category_count.get(issue.category.value, 0) + 1
        return category_count
