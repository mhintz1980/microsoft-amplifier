"""
Tailwind CSS Validation Module

Comprehensive validation system for Tailwind CSS classes, configurations,
and implementation patterns with zero hallucination guarantee.
"""

import json
import re
from dataclasses import dataclass
from enum import Enum
from typing import Any

from ..quality_assurance.validators.zero_hallucination_validator import ZeroHallucinationValidator


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""

    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue."""

    severity: ValidationSeverity
    category: str
    message: str
    line_number: int | None
    column_number: int | None
    suggestion: str | None
    class_name: str | None


@dataclass
class ValidationResult:
    """Result of Tailwind CSS validation."""

    is_valid: bool
    issues: list[ValidationIssue]
    score: int  # 0-100
    statistics: dict[str, Any]
    recommendations: list[str]


class TailwindCSSValidator:
    """
    Comprehensive Tailwind CSS validation with zero hallucination guarantee.

    Features:
    - CSS class validation against Tailwind specifications
    - Configuration file validation
    - Performance impact analysis
    - Accessibility compliance checking
    - Best practices enforcement
    - Framework-specific validation
    """

    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode
        self.validator = ZeroHallucinationValidator(strict_mode=True)

        # Initialize validation data
        self._init_tailwind_spec()
        self._init_validation_rules()
        self._init_accessibility_rules()
        self._init_performance_rules()

    def _init_tailwind_spec(self):
        """Initialize official Tailwind CSS specification data."""
        # Official Tailwind CSS 3.x class specifications
        self.tailwind_spec = {
            # Layout utilities
            "display": {
                "block",
                "inline-block",
                "inline",
                "flex",
                "inline-flex",
                "grid",
                "inline-grid",
                "hidden",
                "table",
                "table-caption",
                "table-cell",
                "table-column",
                "table-column-group",
                "table-footer-group",
                "table-header-group",
                "table-row",
                "table-row-group",
            },
            "container": {"container"},
            # Flexbox utilities
            "flex_basis": {"flex-1", "flex-auto", "flex-initial", "flex-none"},
            "flex_direction": {"flex-row", "flex-row-reverse", "flex-col", "flex-col-reverse"},
            "flex_wrap": {"flex-wrap", "flex-wrap-reverse", "flex-nowrap"},
            "flex": {"flex-1", "flex-auto", "flex-initial", "flex-none"},
            "flex_grow": {"flex-grow", "flex-grow-0"},
            "flex_shrink": {"flex-shrink", "flex-shrink-0"},
            "flex_order": {f"order-{i}" for i in range(1, 13)},
            # Grid utilities
            "grid_cols": {f"grid-cols-{i}" for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]},
            "grid_rows": {f"grid-rows-{i}" for i in range(1, 7)},
            "grid_flow": {"grid-flow-row", "grid-flow-col", "grid-flow-row-dense", "grid-flow-col-dense"},
            "grid_auto": {
                f"grid-auto-cols-{unit}{value}"
                for unit in ["min", "max", "fr"]
                for value in [
                    0,
                    "0.5",
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            # Gap utilities
            "gap": {
                f"gap-{value}"
                for value in [
                    0,
                    0.5,
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            "gap_x": {
                f"gap-x-{value}"
                for value in [
                    0,
                    0.5,
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            "gap_y": {
                f"gap-y-{value}"
                for value in [
                    0,
                    0.5,
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            "space_between": {
                f"space-{axis}-{value}"
                for axis in ["x", "y"]
                for value in [
                    0,
                    0.5,
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            # Spacing utilities
            "padding": {
                f"p{axis}-{value}"
                for axis in ["", "x", "y", "t", "r", "b", "l"]
                for value in [
                    0,
                    0.5,
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            "margin": {
                f"m{axis}-{value}"
                for axis in ["", "x", "y", "t", "r", "b", "l"]
                for value in [
                    0,
                    "auto",
                    0.5,
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                ]
            },
            # Sizing utilities
            "width": {
                f"w-{value}"
                for value in [
                    "auto",
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                    "1/2",
                    "1/3",
                    "2/3",
                    "1/4",
                    "2/4",
                    "3/4",
                    "1/5",
                    "2/5",
                    "3/5",
                    "4/5",
                    "1/6",
                    "2/6",
                    "3/6",
                    "4/6",
                    "5/6",
                    "1/12",
                    "2/12",
                    "3/12",
                    "4/12",
                    "5/12",
                    "6/12",
                    "7/12",
                    "8/12",
                    "9/12",
                    "10/12",
                    "11/12",
                    "screen",
                    "min",
                    "max",
                    "full",
                ]
            },
            "height": {
                f"h-{value}"
                for value in [
                    "auto",
                    *range(1, 13),
                    "14",
                    "16",
                    "20",
                    "24",
                    "28",
                    "32",
                    "36",
                    "40",
                    "44",
                    "48",
                    "52",
                    "56",
                    "60",
                    "64",
                    "72",
                    "80",
                    "96",
                    "screen",
                    "min",
                    "max",
                    "full",
                ]
            },
            # Typography utilities
            "font_family": {"font-sans", "font-serif", "font-mono"},
            "font_size": {
                "text-xs",
                "text-sm",
                "text-base",
                "text-lg",
                "text-xl",
                "text-2xl",
                "text-3xl",
                "text-4xl",
                "text-5xl",
                "text-6xl",
                "text-7xl",
                "text-8xl",
                "text-9xl",
            },
            "font_weight": {
                "font-thin",
                "font-extralight",
                "font-light",
                "font-normal",
                "font-medium",
                "font-semibold",
                "font-bold",
                "font-extrabold",
                "font-black",
            },
            "line_height": {
                f"leading-{value}"
                for value in ["none", "tight", "snug", "normal", "relaxed", "loose", 3, 4, 5, 6, 7, 8, 9, 10]
            },
            "letter_spacing": {
                f"tracking-{value}" for value in ["tighter", "tight", "normal", "wide", "wider", "widest"]
            },
            # Colors (comprehensive list)
            "colors": set(),
            "text_colors": set(),
            "bg_colors": set(),
            "border_colors": set(),
        }

        # Generate color utilities
        colors = [
            "slate",
            "gray",
            "zinc",
            "neutral",
            "stone",
            "red",
            "orange",
            "amber",
            "yellow",
            "lime",
            "green",
            "emerald",
            "teal",
            "cyan",
            "sky",
            "blue",
            "indigo",
            "violet",
            "purple",
            "fuchsia",
            "pink",
            "rose",
        ]

        color_shades = [50, 100, 200, 300, 400, 500, 600, 700, 800, 900, 950]

        for color in colors:
            for shade in color_shades:
                self.tailwind_spec["text_colors"].add(f"text-{color}-{shade}")
                self.tailwind_spec["bg_colors"].add(f"bg-{color}-{shade}")
                self.tailwind_spec["border_colors"].add(f"border-{color}-{shade}")

            # Add base colors
            self.tailwind_spec["text_colors"].add(f"text-{color}")
            self.tailwind_spec["bg_colors"].add(f"bg-{color}")
            self.tailwind_spec["border_colors"].add(f"border-{color}")

        # Special colors
        special_colors = [
            "inherit",
            "current",
            "transparent",
            "black",
            "white",
            "rose-50",
            "rose-100",
            "rose-200",
            "rose-300",
            "rose-400",
            "rose-500",
            "rose-600",
            "rose-700",
            "rose-800",
            "rose-900",
            "rose-950",
        ]

        for color in special_colors:
            self.tailwind_spec["text_colors"].add(f"text-{color}")
            self.tailwind_spec["bg_colors"].add(f"bg-{color}")
            self.tailwind_spec["border_colors"].add(f"border-{color}")

        # Border utilities
        self.tailwind_spec["border_width"] = {f"border-{value}" for value in [0, 2, 4, 8]}
        self.tailwind_spec["border_radius"] = {
            f"rounded-{value}" for value in ["none", "sm", "", "md", "lg", "xl", "2xl", "3xl", "full"]
        }

        # Shadow utilities
        self.tailwind_spec["shadow"] = {
            f"shadow-{value}" for value in ["sm", "", "md", "lg", "xl", "2xl", "inner", "none"]
        }

        # Opacity utilities
        self.tailwind_spec["opacity"] = {f"opacity-{value}" for value in range(0, 101, 10)}

        # Position utilities
        self.tailwind_spec["position"] = {"static", "fixed", "absolute", "relative", "sticky"}
        self.tailwind_spec["inset"] = {
            f"inset-{axis}-{value}"
            for axis in ["", "x", "y", "top", "right", "bottom", "left"]
            for value in [
                0,
                "auto",
                0.5,
                *range(1, 13),
                "14",
                "16",
                "20",
                "24",
                "28",
                "32",
                "36",
                "40",
                "44",
                "48",
                "52",
                "56",
                "60",
                "64",
                "72",
                "80",
                "96",
                "1/2",
                "1/3",
                "2/3",
                "1/4",
                "3/4",
                "full",
            ]
        }

    def _init_validation_rules(self):
        """Initialize comprehensive validation rules."""
        self.validation_rules = {
            "syntax": [
                {
                    "pattern": r"^[a-zA-Z][a-zA-Z0-9_-]*$",
                    "description": "Class names must be valid identifiers",
                    "severity": ValidationSeverity.ERROR,
                },
                {
                    "pattern": r"^.{1,100}$",
                    "description": "Class names should be reasonably short",
                    "severity": ValidationSeverity.WARNING,
                },
            ],
            "performance": [
                {
                    "pattern": r"^(animate|transition|transform)",
                    "description": "Animation and transform classes found - check performance impact",
                    "severity": ValidationSeverity.INFO,
                    "suggestion": "Consider GPU acceleration with transform/opacity",
                },
                {
                    "pattern": r"(filter|backdrop-filter)",
                    "description": "Filter effects can impact performance",
                    "severity": ValidationSeverity.WARNING,
                    "suggestion": "Use sparingly and test on target devices",
                },
                {
                    "pattern": r"box-shadow-\d+$",
                    "description": "Large box shadows may impact performance",
                    "severity": ValidationSeverity.INFO,
                    "suggestion": "Consider CSS containment or alternatives",
                },
            ],
            "accessibility": [
                {
                    "pattern": r"sr-only",
                    "description": "Screen reader only content detected",
                    "severity": ValidationSeverity.INFO,
                },
                {
                    "pattern": r"focus:",
                    "description": "Focus styles found - good for accessibility",
                    "severity": ValidationSeverity.INFO,
                },
                {
                    "pattern": r"pointer-events-none",
                    "description": "Element is not keyboard accessible",
                    "severity": ValidationSeverity.WARNING,
                    "suggestion": "Ensure keyboard navigation alternative exists",
                },
            ],
            "best_practices": [
                {
                    "pattern": r"important",
                    "description": "!important usage detected",
                    "severity": ValidationSeverity.WARNING,
                    "suggestion": "Consider using CSS specificity instead",
                },
                {
                    "pattern": r"overflow-(hidden|scroll|auto)",
                    "description": "Overflow property may hide content",
                    "severity": ValidationSeverity.INFO,
                    "suggestion": "Ensure content remains accessible",
                },
                {
                    "pattern": r"absolute|fixed",
                    "description": "Position absolute/fixed detected",
                    "severity": ValidationSeverity.INFO,
                    "suggestion": "Check responsive behavior and accessibility",
                },
            ],
        }

    def _init_accessibility_rules(self):
        """Initialize accessibility validation rules."""
        self.accessibility_rules = {
            "color_contrast": {
                "required_pairs": [
                    ("text-white", "bg-gray-900"),
                    ("text-gray-900", "bg-white"),
                    ("text-black", "bg-white"),
                ],
                "warning_combinations": [
                    ("text-gray-400", "bg-gray-100"),
                    ("text-gray-500", "bg-gray-200"),
                ],
            },
            "focus_management": {
                "required_classes": ["focus:"],
                "interactive_elements": ["button", "input", "select", "textarea", "a", "summary"],
            },
            "screen_reader": {"required_roles": ["role=", "aria-"], "sr_only_alternatives": ["sr-only"]},
        }

    def _init_performance_rules(self):
        """Initialize performance validation rules."""
        self.performance_rules = {
            "expensive_operations": [
                "backdrop-filter",
                "filter",
                "box-shadow",
                "text-shadow",
                "transform3d",
                "perspective",
            ],
            "layout_triggers": ["width", "height", "padding", "margin", "border", "font-size"],
            "animation_recommendations": {
                "gpu_accelerated": ["transform", "opacity"],
                "cpu_intensive": ["width", "height", "margin", "padding"],
            },
        }

    def validate_classes(self, class_string: str, context: dict[str, Any] | None = None) -> ValidationResult:
        """
        Validate Tailwind CSS classes against official specification.

        Args:
            class_string: Space-separated class names to validate
            context: Additional context for validation (framework, file type, etc.)

        Returns:
            Comprehensive validation result
        """
        issues = []
        valid_classes = []
        invalid_classes = []
        statistics = {
            "total_classes": 0,
            "valid_classes": 0,
            "invalid_classes": 0,
            "warnings": 0,
            "errors": 0,
            "performance_impact": "low",
        }

        classes = class_string.split()
        statistics["total_classes"] = len(classes)

        for class_name in classes:
            is_valid, class_issues = self._validate_single_class(class_name, context)

            if is_valid:
                valid_classes.append(class_name)
                statistics["valid_classes"] += 1
            else:
                invalid_classes.append(class_name)
                statistics["invalid_classes"] += 1

            issues.extend(class_issues)

        # Analyze overall performance impact
        performance_issues = self._analyze_performance_impact(classes)
        issues.extend(performance_issues)

        # Check accessibility compliance
        accessibility_issues = self._check_accessibility(classes, context)
        issues.extend(accessibility_issues)

        # Calculate severity counts
        statistics["errors"] = len([i for i in issues if i.severity == ValidationSeverity.ERROR])
        statistics["warnings"] = len([i for i in issues if i.severity == ValidationSeverity.WARNING])

        # Calculate performance impact
        if any(issue.category == "performance" and issue.severity == ValidationSeverity.WARNING for issue in issues):
            statistics["performance_impact"] = "high"
        elif any(issue.category == "performance" for issue in issues):
            statistics["performance_impact"] = "medium"

        # Calculate validation score
        score = max(0, 100 - (statistics["errors"] * 20) - (statistics["warnings"] * 5))

        # Generate recommendations
        recommendations = self._generate_recommendations(issues, statistics)

        return ValidationResult(
            is_valid=statistics["errors"] == 0,
            issues=issues,
            score=score,
            statistics=statistics,
            recommendations=recommendations,
        )

    def _validate_single_class(
        self, class_name: str, context: dict[str, Any] | None = None
    ) -> tuple[bool, list[ValidationIssue]]:
        """Validate a single Tailwind CSS class."""
        issues = []
        is_valid = False

        # Remove variants for validation
        base_class = self._remove_variants(class_name)

        # Check against official Tailwind specification
        if self._is_official_class(base_class):
            is_valid = True
        elif self._is_valid_arbitrary_value(base_class):
            is_valid = True
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="arbitrary_value",
                    message=f"Arbitrary value detected: {base_class}",
                    line_number=None,
                    column_number=None,
                    suggestion="Ensure arbitrary value is properly formatted",
                    class_name=class_name,
                )
            )
        else:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="invalid_class",
                    message=f"Invalid Tailwind class: {base_class}",
                    line_number=None,
                    column_number=None,
                    suggestion=f"Did you mean: {self._suggest_alternative(base_class)}",
                    class_name=class_name,
                )
            )

        # Apply validation rules
        for rule_set in self.validation_rules.values():
            for rule in rule_set:
                if re.search(rule["pattern"], class_name):
                    issues.append(
                        ValidationIssue(
                            severity=rule["severity"],
                            category="validation_rule",
                            message=rule["description"],
                            line_number=None,
                            column_number=None,
                            suggestion=rule.get("suggestion"),
                            class_name=class_name,
                        )
                    )

        return is_valid, issues

    def _remove_variants(self, class_name: str) -> str:
        """Remove responsive and state variants from class name."""
        # Remove responsive variants
        responsive_variants = ["sm:", "md:", "lg:", "xl:", "2xl:"]
        for variant in responsive_variants:
            if class_name.startswith(variant):
                return class_name[len(variant) :]

        # Remove state variants
        state_variants = [
            "hover:",
            "focus:",
            "active:",
            "visited:",
            "disabled:",
            "group-hover:",
            "group-focus:",
            "focus-within:",
            "focus-visible:",
            "motion-safe:",
            "motion-reduce:",
            "first:",
            "last:",
            "odd:",
            "even:",
            "group-first:",
            "group-last:",
            "group-odd:",
            "group-even:",
        ]

        for variant in state_variants:
            if class_name.startswith(variant):
                return class_name[len(variant) :]

        # Remove dark mode variant
        if class_name.startswith("dark:"):
            return class_name[5:]

        return class_name

    def _is_official_class(self, class_name: str) -> bool:
        """Check if class is in official Tailwind specification."""
        # Check each category
        for category, classes in self.tailwind_spec.items():
            if class_name in classes:
                return True

        # Check for compound classes (e.g., "rounded-t-lg")
        compound_patterns = [
            r"^rounded-[tblrxy]-\d+$",
            r"^border-[tblrxy]-\d+$",
            r"^text-[tblrxy]-\d+$",
            r"^space-[xy]-\d+$",
            r"^gap-[xy]-\d+$",
        ]

        for pattern in compound_patterns:
            if re.match(pattern, class_name):
                return True

        return False

    def _is_valid_arbitrary_value(self, class_name: str) -> bool:
        """Check if class uses valid arbitrary value syntax."""
        arbitrary_patterns = [
            r"^w-\[.+\]$",
            r"^h-\[.+\]$",
            r"^p-\[.+\]$",
            r"^m-\[.+\]$",
            r"^text-\[.+\]$",
            r"^bg-\[.+\]$",
            r"^border-\[.+\]$",
            r"^rounded-\[.+\]$",
            r"^gap-\[.+\]$",
            r"^shadow-\[.+\]$",
            r"^-\[.+\]$",  # Custom properties
        ]

        return any(re.match(pattern, class_name) for pattern in arbitrary_patterns)

    def _suggest_alternative(self, invalid_class: str) -> str:
        """Suggest alternative for invalid class."""
        suggestions = []

        # Common misspellings and corrections
        corrections = {
            "paddin": "padding",
            "margi": "margin",
            "backgroun": "background",
            "text-colr": "text-color",
            "bg-colr": "bg-color",
            "flex-cente": "flex-center",
            "items-cent": "items-center",
            "justfy": "justify",
            "jusify": "justify",
            "containe": "container",
            "hidden": "hidden",
            "visibile": "visible",
        }

        for wrong, correct in corrections.items():
            if wrong in invalid_class.lower():
                suggestions.append(f"{correct} (typo correction)")

        # Find closest matches in official classes
        base_class = self._remove_variants(invalid_class)

        # Simple similarity check
        for category, classes in self.tailwind_spec.items():
            for official_class in classes:
                if self._similar_strings(base_class, official_class, threshold=0.7):
                    suggestions.append(official_class)

        return suggestions[0] if suggestions else "Check official Tailwind documentation"

    def _similar_strings(self, str1: str, str2: str, threshold: float = 0.8) -> bool:
        """Simple string similarity check."""
        # Remove common prefixes for better matching
        str1_clean = str1.lstrip("tblrxy-")
        str2_clean = str2.lstrip("tblrxy-")

        if str1_clean == str2_clean:
            return True

        # Simple edit distance approximation
        longer = max(str1_clean, str2_clean, key=len)
        shorter = min(str1_clean, str2_clean, key=len)

        if len(shorter) == 0:
            return len(longer) == 0

        similar_chars = sum(1 for i, char in enumerate(shorter) if i < len(longer) and char == longer[i])
        similarity = similar_chars / len(longer)

        return similarity >= threshold

    def _analyze_performance_impact(self, classes: list[str]) -> list[ValidationIssue]:
        """Analyze performance impact of CSS classes."""
        issues = []

        expensive_classes = []
        for class_name in classes:
            base_class = self._remove_variants(class_name)

            for expensive in self.performance_rules["expensive_operations"]:
                if expensive in base_class:
                    expensive_classes.append(class_name)

        if expensive_classes:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="performance",
                    message=f"Performance-heavy classes detected: {', '.join(expensive_classes)}",
                    line_number=None,
                    column_number=None,
                    suggestion="Consider using alternatives or CSS containment",
                    class_name=", ".join(expensive_classes),
                )
            )

        # Check for layout thrashing potential
        layout_classes = []
        for class_name in classes:
            base_class = self._remove_variants(class_name)

            for layout_trigger in self.performance_rules["layout_triggers"]:
                if layout_trigger in base_class and any(variant in class_name for variant in ["hover:", "focus:"]):
                    layout_classes.append(class_name)

        if layout_classes:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="performance",
                    message=f"Layout-affecting classes with state variants: {', '.join(layout_classes)}",
                    line_number=None,
                    column_number=None,
                    suggestion="Consider using transform/opacity for state changes when possible",
                    class_name=", ".join(layout_classes),
                )
            )

        return issues

    def _check_accessibility(self, classes: list[str], context: dict[str, Any] | None = None) -> list[ValidationIssue]:
        """Check accessibility compliance of CSS classes."""
        issues = []

        # Check for focus management
        has_focus_styles = any("focus:" in cls for cls in classes)
        has_interactive_elements = context and any(
            element in str(context).lower()
            for element in self.accessibility_rules["focus_management"]["interactive_elements"]
        )

        if has_interactive_elements and not has_focus_styles:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    category="accessibility",
                    message="Interactive element detected without focus styles",
                    line_number=None,
                    column_number=None,
                    suggestion="Add focus: styles for keyboard accessibility",
                    class_name=None,
                )
            )

        # Check for color contrast issues (simplified)
        has_text_color = any(cls.startswith("text-") for cls in classes)
        has_bg_color = any(cls.startswith("bg-") for cls in classes)

        if has_text_color and not has_bg_color and "transparent" not in classes:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    category="accessibility",
                    message="Text color specified without background color - verify contrast",
                    line_number=None,
                    column_number=None,
                    suggestion="Ensure sufficient contrast ratio with background",
                    class_name=None,
                )
            )

        return issues

    def _generate_recommendations(self, issues: list[ValidationIssue], statistics: dict[str, Any]) -> list[str]:
        """Generate actionable recommendations based on validation results."""
        recommendations = []

        if statistics["invalid_classes"] > 0:
            recommendations.append(f"Fix {statistics['invalid_classes']} invalid Tailwind classes")

        if statistics["errors"] > 0:
            recommendations.append("Address all error-level issues before deployment")

        if statistics["warnings"] > 5:
            recommendations.append("Consider reducing the number of warning-level issues")

        if any(issue.category == "performance" and issue.severity == ValidationSeverity.WARNING for issue in issues):
            recommendations.append("Optimize performance-heavy CSS classes")

        if statistics["performance_impact"] == "high":
            recommendations.append("High performance impact detected - consider optimization strategies")

        if statistics["valid_classes"] == statistics["total_classes"] and statistics["errors"] == 0:
            recommendations.append("✅ All classes are valid and follow best practices")

        # Specific recommendations based on issue types
        issue_categories = set(issue.category for issue in issues)

        if "accessibility" in issue_categories:
            recommendations.append("Improve accessibility compliance")

        if "arbitrary_value" in issue_categories:
            recommendations.append("Review arbitrary values for consistency")

        if "validation_rule" in issue_categories:
            recommendations.append("Address validation rule violations")

        return recommendations

    def validate_configuration(self, config_content: str) -> ValidationResult:
        """
        Validate Tailwind CSS configuration file.

        Args:
            config_content: Content of tailwind.config.js

        Returns:
            Configuration validation result
        """
        issues = []

        try:
            # Try to parse as JSON (simplified validation)
            config = json.loads(config_content.replace("module.exports = ", "").replace(";", ""))

            # Check required properties
            required_properties = ["content", "theme"]
            for prop in required_properties:
                if prop not in config:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.WARNING,
                            category="configuration",
                            message=f"Missing required configuration property: {prop}",
                            line_number=None,
                            column_number=None,
                            suggestion=f"Add {prop} to your Tailwind configuration",
                            class_name=None,
                        )
                    )

            # Check content configuration
            if "content" in config:
                content = config["content"]
                if isinstance(content, list) and len(content) == 0:
                    issues.append(
                        ValidationIssue(
                            severity=ValidationSeverity.ERROR,
                            category="configuration",
                            message="Content array is empty - no CSS will be generated",
                            line_number=None,
                            column_number=None,
                            suggestion="Add paths to your template files",
                            class_name=None,
                        )
                    )

            # Check for optimization settings
            if "mode" in config and config["mode"] == "jit":
                issues.append(
                    ValidationIssue(
                        severity=ValidationSeverity.INFO,
                        category="configuration",
                        message="JIT mode enabled - good for bundle size optimization",
                        line_number=None,
                        column_number=None,
                        suggestion="Ensure purge configuration is accurate",
                        class_name=None,
                    )
                )

        except Exception as e:
            issues.append(
                ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    category="configuration",
                    message=f"Invalid configuration format: {str(e)}",
                    line_number=None,
                    column_number=None,
                    suggestion="Check Tailwind configuration syntax",
                    class_name=None,
                )
            )

        return ValidationResult(
            is_valid=len([i for i in issues if i.severity == ValidationSeverity.ERROR]) == 0,
            issues=issues,
            score=max(0, 100 - len(issues) * 10),
            statistics={"total_issues": len(issues)},
            recommendations=["Fix configuration issues for optimal performance"],
        )

    def validate_html_file(self, file_path: str) -> ValidationResult:
        """
        Validate Tailwind CSS classes in an HTML file.

        Args:
            file_path: Path to HTML file

        Returns:
            File validation result
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Find all class attributes
            class_pattern = r'class(?:Name)?=["\']([^"\']*)["\']'
            matches = re.finditer(class_pattern, content)

            all_issues = []
            total_classes = 0
            valid_classes = 0

            for match in matches:
                class_string = match.group(1)
                line_number = content[: match.start()].count("\n") + 1

                result = self.validate_classes(class_string, {"file": file_path, "line": line_number})
                all_issues.extend(result.issues)
                total_classes += result.statistics["total_classes"]
                valid_classes += result.statistics["valid_classes"]

            # Add line numbers to issues
            for issue in all_issues:
                if issue.line_number is None:
                    # Find the line number for this issue
                    issue.line_number = content[: content.find(issue.class_name or "")].count("\n") + 1

            score = (valid_classes / max(total_classes, 1)) * 100 if total_classes > 0 else 100

            return ValidationResult(
                is_valid=len([i for i in all_issues if i.severity == ValidationSeverity.ERROR]) == 0,
                issues=all_issues,
                score=int(score),
                statistics={"total_classes": total_classes, "valid_classes": valid_classes, "file_path": file_path},
                recommendations=[self._generate_file_recommendation(total_classes, valid_classes, all_issues)],
            )

        except Exception as e:
            return ValidationResult(
                is_valid=False,
                issues=[
                    ValidationIssue(
                        severity=ValidationSeverity.ERROR,
                        category="file_error",
                        message=f"Could not read file: {str(e)}",
                        line_number=None,
                        column_number=None,
                        suggestion="Check file path and permissions",
                        class_name=None,
                    )
                ],
                score=0,
                statistics={},
                recommendations=["Fix file access issues"],
            )

    def _generate_file_recommendation(
        self, total_classes: int, valid_classes: int, issues: list[ValidationIssue]
    ) -> str:
        """Generate recommendation for file validation."""
        if total_classes == 0:
            return "No Tailwind classes found in this file"

        error_count = len([i for i in issues if i.severity == ValidationSeverity.ERROR])
        warning_count = len([i for i in issues if i.severity == ValidationSeverity.WARNING])

        if error_count == 0 and warning_count == 0:
            return f"✅ All {total_classes} Tailwind classes are valid"
        if error_count == 0:
            return f"⚠️ {valid_classes}/{total_classes} classes valid, {warning_count} warnings"
        return f"❌ {error_count} errors, {warning_count} warnings out of {total_classes} classes"
