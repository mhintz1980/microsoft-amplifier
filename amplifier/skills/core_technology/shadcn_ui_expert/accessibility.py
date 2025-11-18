"""
ShadCN/ui Accessibility Expert

Comprehensive accessibility compliance and validation for ShadCN/ui components.
Ensures WCAG 2.1 AA compliance with proper ARIA attributes and keyboard navigation.
"""

import re
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class WCAGLevel(Enum):
    """WCAG compliance levels."""

    A = "A"
    AA = "AA"
    AAA = "AAA"


class AccessibilityRole(Enum):
    """Common accessibility roles."""

    BUTTON = "button"
    LINK = "link"
    NAVIGATION = "navigation"
    MAIN = "main"
    BANNER = "banner"
    CONTENTINFO = "contentinfo"
    SEARCH = "search"
    DIALOG = "dialog"
    ALERT = "alert"
    ALERTDIALOG = "alertdialog"
    MENU = "menu"
    MENUBAR = "menubar"
    MENUITEM = "menuitem"
    OPTION = "option"
    TAB = "tab"
    TABLIST = "tablist"
    TABPANEL = "tabpanel"
    SPINBUTTON = "spinbutton"
    SLIDER = "slider"
    TEXTBOX = "textbox"
    CHECKBOX = "checkbox"
    RADIO = "radio"
    RADIOGROUP = "radiogroup"
    TREE = "tree"
    TREEITEM = "treeitem"
    GRID = "grid"
    GRIDCELL = "gridcell"
    ROW = "row"
    ROWGROUP = "rowgroup"
    ROWHEADER = "rowheader"
    COLUMNHEADER = "columnheader"


@dataclass
class AccessibilityIssue:
    """Represents an accessibility issue found during validation."""

    severity: str  # "critical", "serious", "moderate", "minor"
    type: str  # "aria", "keyboard", "color", "focus", "semantic", "language"
    description: str
    wcag_criterion: str  # e.g., "1.1.1 Non-text Content"
    component: str
    line_number: Optional[int] = None
    fix_suggestion: str = ""
    automated_fix: Optional[str] = None


@dataclass
class AccessibilityScore:
    """Accessibility scoring for components."""

    overall_score: int  # 0-100
    color_contrast: int
    keyboard_navigation: int
    screen_reader: int
    cognitive_load: int
    seizure_safety: int
    wcag_level: WCAGLevel
    issues_found: int
    issues_fixed: int


class AccessibilityExpert:
    """
    Comprehensive accessibility expert for ShadCN/ui components.

    Provides:
    - WCAG 2.1 AA compliance validation
    - ARIA attribute management
    - Keyboard navigation testing
    - Color contrast analysis
    - Screen reader compatibility
    - Focus management
    - Cognitive load assessment
    """

    def __init__(self):
        self.wcag_guidelines = self._init_wcag_guidelines()
        self.color_contrast_ratios = self._init_color_contrast_ratios()
        self.keyboard_patterns = self._init_keyboard_patterns()
        self.aria_patterns = self._init_aria_patterns()
        self.test_cases = self._init_test_cases()

    def _init_wcag_guidelines(self) -> Dict[str, Any]:
        """Initialize WCAG 2.1 guidelines."""
        return {
            "1.1.1": {
                "title": "Non-text Content",
                "description": "All non-text content has a text alternative",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Icons, images, charts in components",
            },
            "1.3.1": {
                "title": "Info and Relationships",
                "description": "Information, structure, and relationships can be programmatically determined",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Form labels, table headers, list structures",
            },
            "1.4.1": {
                "title": "Use of Color",
                "description": "Color is not used as the only visual means of conveying information",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Button states, form validation, error indicators",
            },
            "1.4.3": {
                "title": "Contrast (Minimum)",
                "description": "Text has a contrast ratio of at least 4.5:1",
                "level": WCAGLevel.AA,
                "shadcn_relevance": "All text in components",
            },
            "2.1.1": {
                "title": "Keyboard",
                "description": "All functionality is available from a keyboard",
                "level": WCAGLevel.A,
                "shadcn_relevance": "All interactive components",
            },
            "2.1.2": {
                "title": "No Keyboard Trap",
                "description": "Keyboard focus does not get trapped",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Modal dialogs, dropdowns, complex forms",
            },
            "2.4.1": {
                "title": "Bypass Blocks",
                "description": "A mechanism is available to bypass blocks of content",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Navigation menus, page layouts",
            },
            "2.4.2": {
                "title": "Page Titled",
                "description": "Web pages have titles that describe topic or purpose",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Page-level components, routing",
            },
            "2.4.3": {
                "title": "Focus Order",
                "description": "Focus order is logical and intuitive",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Form layouts, tab orders",
            },
            "3.1.1": {
                "title": "Language of Page",
                "description": "Language of page can be programmatically determined",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Page components, internationalization",
            },
            "3.2.1": {
                "title": "On Focus",
                "description": "Component behavior does not change on focus",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Form components, interactive elements",
            },
            "3.2.2": {
                "title": "On Input",
                "description": "Changing settings does not automatically change context",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Form components, settings panels",
            },
            "3.3.1": {
                "title": "Error Identification",
                "description": "Errors are identified and described to the user",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Form validation, error handling",
            },
            "3.3.2": {
                "title": "Labels or Instructions",
                "description": "Labels or instructions are provided when content requires input",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Form fields, input components",
            },
            "3.3.3": {
                "title": "Error Suggestion",
                "description": "Suggestions for fixing errors are provided when possible",
                "level": WCAGLevel.AA,
                "shadcn_relevance": "Form validation, error messages",
            },
            "3.3.4": {
                "title": "Error Prevention",
                "description": "For legal, financial, or data transactions, errors are prevented or reversible",
                "level": WCAGLevel.AA,
                "shadcn_relevance": "Forms, delete operations, transactions",
            },
            "4.1.1": {
                "title": "Parsing",
                "description": "Markup languages have been used correctly",
                "level": WCAGLevel.A,
                "shadcn_relevance": "Component HTML structure",
            },
            "4.1.2": {
                "title": "Name, Role, Value",
                "description": "Name, role, value can be programmatically determined",
                "level": WCAGLevel.A,
                "shadcn_relevance": "All interactive components",
            },
        }

    def _init_color_contrast_ratios(self) -> Dict[str, float]:
        """Initialize required color contrast ratios."""
        return {
            "AA_normal": 4.5,
            "AA_large": 3.0,
            "AAA_normal": 7.0,
            "AAA_large": 4.5,
            "AA_graphical": 3.0,
        }

    def _init_keyboard_patterns(self) -> Dict[str, List[str]]:
        """Initialize keyboard interaction patterns."""
        return {
            "button": ["Enter", "Space"],
            "link": ["Enter"],
            "checkbox": ["Space"],
            "radio": ["Arrow keys", "Space"],
            "select": ["Arrow keys", "Enter", "Space", "Escape"],
            "textbox": ["All characters", "Arrow keys", "Home/End", "Ctrl+A"],
            "slider": ["Arrow keys", "Home/End", "Page Up/Down"],
            "tab": ["Arrow keys", "Enter"],
            "dialog": ["Tab", "Shift+Tab", "Escape"],
            "menu": ["Arrow keys", "Enter", "Space", "Escape"],
            "listbox": ["Arrow keys", "Home/End", "Enter", "Space"],
            "grid": ["Arrow keys", "Tab", "Enter", "Space"],
        }

    def _init_aria_patterns(self) -> Dict[str, Dict[str, Any]]:
        """Initialize ARIA attribute patterns."""
        return {
            "required": {
                "attributes": ["aria-label", "aria-labelledby"],
                "description": "For components without visible text labels",
                "examples": ["Icon-only buttons", "Custom controls"],
            },
            "describedby": {
                "attributes": ["aria-describedby"],
                "description": "For additional description or help text",
                "examples": ["Field validation errors", "Helper text"],
            },
            "expanded": {
                "attributes": ["aria-expanded"],
                "description": "For collapsible content",
                "values": ["true", "false"],
            },
            "selected": {
                "attributes": ["aria-selected"],
                "description": "For selectable items in lists",
                "values": ["true", "false", "undefined"],
            },
            "pressed": {
                "attributes": ["aria-pressed"],
                "description": "For toggle buttons",
                "values": ["true", "false", "mixed", "undefined"],
            },
            "invalid": {
                "attributes": ["aria-invalid"],
                "description": "For form field validation states",
                "values": ["true", "false"],
            },
            "live": {
                "attributes": ["aria-live"],
                "description": "For dynamic content regions",
                "values": ["polite", "assertive", "off"],
            },
            "modal": {"attributes": ["aria-modal"], "description": "For modal dialogs", "values": ["true", "false"]},
        }

    def _init_test_cases(self) -> Dict[str, List[Dict[str, Any]]]:
        """Initialize accessibility test cases."""
        return {
            "button": [
                {
                    "name": "Has accessible name",
                    "test": lambda code: "aria-label" in code or any(text in code for text in ["<", ">"]),
                    "critical": True,
                },
                {
                    "name": "Keyboard accessible",
                    "test": lambda code: "onClick" in code or "onKeyDown" in code,
                    "critical": True,
                },
                {
                    "name": "Focus indicator",
                    "test": lambda code: "focus:" in code or "focus-visible" in code,
                    "critical": True,
                },
            ],
            "form": [
                {
                    "name": "Labels for all inputs",
                    "test": lambda code: code.count("<label") >= code.count("<input"),
                    "critical": True,
                },
                {
                    "name": "Error messages announced",
                    "test": lambda code: "aria-describedby" in code or "aria-invalid" in code,
                    "critical": True,
                },
                {
                    "name": "Required fields indicated",
                    "test": lambda code: "required" in code or "aria-required" in code,
                    "critical": False,
                },
            ],
        }

    def analyze_accessibility(self, code: str, component_type: str = "generic") -> int:
        """
        Analyze accessibility compliance and return score (0-100).

        Args:
            code: Component code to analyze
            component_type: Type of component being analyzed

        Returns:
            Accessibility score (0-100)
        """
        score = 100
        issues = []

        # Check for basic accessibility patterns
        if component_type in ["button", "Button"]:
            if "aria-label" not in code and not self._has_visible_text(code):
                score -= 20
                issues.append("Button missing accessible label")

            if "onKeyDown" not in code and "onClick" not in code:
                score -= 15
                issues.append("Button not keyboard accessible")

        if component_type in ["input", "Input", "textarea", "Textarea"]:
            if "htmlFor" not in code and "for=" not in code:
                score -= 25
                issues.append("Input missing proper label association")

            if "aria-describedby" not in code and "aria-invalid" not in code:
                score -= 10
                issues.append("Input missing error handling")

        # Check focus management
        if "focus:" not in code and "focus-visible" not in code:
            score -= 10
            issues.append("Missing focus indicators")

        # Check ARIA attributes
        aria_patterns = ["aria-label", "aria-describedby", "aria-expanded", "aria-selected"]
        for pattern in aria_patterns:
            if pattern in code:
                score += 5  # Bonus for proper ARIA usage

        # Check semantic HTML
        semantic_tags = ["nav", "main", "header", "footer", "section", "article"]
        for tag in semantic_tags:
            if f"<{tag}" in code:
                score += 2  # Bonus for semantic structure

        return max(0, min(100, score))

    def validate_wcag_compliance(self, code: str) -> List[AccessibilityIssue]:
        """
        Validate WCAG 2.1 AA compliance for component code.

        Args:
            code: Component code to validate

        Returns:
            List of accessibility issues found
        """
        issues = []

        # Check for proper labeling (1.3.1)
        if "<button" in code:
            button_count = len(re.findall(r"<button[^>]*>", code))
            aria_label_count = len(re.findall(r"aria-label=", code))
            if aria_label_count < button_count and not self._has_visible_text(code):
                issues.append(
                    AccessibilityIssue(
                        severity="critical",
                        type="aria",
                        description="Button missing accessible name",
                        wcag_criterion="1.3.1 Info and Relationships",
                        component="button",
                        fix_suggestion="Add aria-label or visible text to button",
                        automated_fix='aria-label="Button action"',
                    )
                )

        # Check keyboard accessibility (2.1.1)
        if "onClick" in code and "onKeyDown" not in code:
            issues.append(
                AccessibilityIssue(
                    severity="serious",
                    type="keyboard",
                    description="Component may not be fully keyboard accessible",
                    wcag_criterion="2.1.1 Keyboard",
                    component="interactive",
                    fix_suggestion="Add keyboard event handlers for click interactions",
                    automated_fix="onKeyDown={handleKeyPress}",
                )
            )

        # Check focus indicators (2.4.3)
        if "focus:" not in code and "focus-visible" not in code:
            issues.append(
                AccessibilityIssue(
                    severity="moderate",
                    type="focus",
                    description="Missing focus indicators for interactive elements",
                    wcag_criterion="2.4.3 Focus Order",
                    component="interactive",
                    fix_suggestion="Add focus styles using Tailwind focus: or focus-visible: classes",
                    automated_fix="className='focus:ring-2 focus:ring-blue-500'",
                )
            )

        # Check form labeling (1.3.1)
        input_count = len(re.findall(r"<(input|textarea|select)[^>]*>", code))
        label_count = len(re.findall(r"<label[^>]*>", code))
        if input_count > label_count:
            issues.append(
                AccessibilityIssue(
                    severity="critical",
                    type="semantic",
                    description="Form inputs without proper labels",
                    wcag_criterion="1.3.1 Info and Relationships",
                    component="form",
                    fix_suggestion="Add labels with htmlFor attributes or aria-label for form inputs",
                    automated_fix="<label htmlFor='input-id'>Label text</label>",
                )
            )

        # Check color usage (1.4.1)
        if "text-red-" in code or "text-green-" in code or "text-blue-" in code:
            if "aria-label" not in code and "aria-describedby" not in code:
                issues.append(
                    AccessibilityIssue(
                        severity="moderate",
                        type="color",
                        description="Color used as only means of conveying information",
                        wcag_criterion="1.4.1 Use of Color",
                        component="status",
                        fix_suggestion="Add text or icons to supplement color-based indicators",
                        automated_fix="aria-label='Status: Success'",
                    )
                )

        # Check ARIA attributes (4.1.2)
        if "aria-" in code:
            # Validate common ARIA patterns
            for aria_attr in re.findall(r"aria-([a-zA-Z-]+)=", code):
                if self._is_invalid_aria_usage(aria_attr, code):
                    issues.append(
                        AccessibilityIssue(
                            severity="moderate",
                            type="aria",
                            description=f"Invalid or redundant ARIA attribute: aria-{aria_attr}",
                            wcag_criterion="4.1.2 Name, Role, Value",
                            component="aria",
                            fix_suggestion=f"Review aria-{aria_attr} usage and remove if redundant",
                            automated_fix="# Remove aria-{aria_attr} if redundant",
                        )
                    )

        return issues

    def generate_accessibility_markup(
        self, component_code: str, compliance_level: WCAGLevel = WCAGLevel.AA
    ) -> Dict[str, Any]:
        """
        Generate accessibility markup for a component.

        Args:
            component_code: Base component code
            compliance_level: Target WCAG compliance level

        Returns:
            Enhanced component with accessibility markup
        """
        enhanced_code = component_code
        enhancements = []

        # Add ARIA attributes
        if "Button" in component_code and "aria-label" not in component_code:
            if not self._has_visible_text(component_code):
                enhanced_code = re.sub(r"<Button([^>]*?)>", r'<Button\1 aria-label="Action button">', enhanced_code)
                enhancements.append("Added aria-label to button")

        # Add focus management
        if "focus:" not in component_code:
            enhanced_code = re.sub(
                r'className="([^"]*)"',
                r'className="\1 focus:ring-2 focus:ring-blue-500 focus:outline-none"',
                enhanced_code,
            )
            enhancements.append("Added focus styles")

        # Add form validation
        if "Input" in component_code and "aria-describedby" not in component_code:
            enhanced_code = re.sub(
                r"<Input([^>]*?)>", r'<Input\1 aria-describedby="input-error input-helper">', enhanced_code
            )
            enhancements.append("Added aria-describedby for input")

        return {
            "enhanced_code": enhanced_code,
            "enhancements": enhancements,
            "compliance_level": compliance_level.value,
            "score": self.analyze_accessibility(enhanced_code),
        }

    def _has_visible_text(self, code: str) -> bool:
        """Check if component has visible text content."""
        # Look for text between tags
        text_pattern = r">([^<\s][^<]*[^<\s])<"
        matches = re.findall(text_pattern, code)
        return len(matches) > 0

    def _is_invalid_aria_usage(self, aria_attr: str, code: str) -> bool:
        """Check for invalid ARIA attribute usage."""
        # Check for redundant aria-label on elements with visible text
        if aria_attr == "label" and self._has_visible_text(code):
            return True

        # Check for invalid aria-hidden on focusable elements
        if aria_attr == "hidden" and ("button" in code or "input" in code or "a href" in code):
            return True

        return False

    def get_keyboard_navigation_guide(self) -> Dict[str, Any]:
        """Get comprehensive keyboard navigation guide."""
        return {
            "patterns": self.keyboard_patterns,
            "best_practices": [
                "All interactive elements should be keyboard accessible",
                "Focus should be visible and clearly indicated",
                "Tab order should follow logical reading order",
                "Custom components should support standard keyboard patterns",
                "Modal dialogs should trap focus within the dialog",
                "Escape key should close overlays and return focus",
                "Arrow keys should navigate within composite components",
                "Enter/Space should activate buttons and toggle switches",
                "Tab should move between focusable elements",
                "Shift+Tab should move backwards through focusable elements",
            ],
            "test_procedures": [
                "Navigate through page using only Tab key",
                "Verify all interactive elements receive focus",
                "Check that focus is clearly visible",
                "Test Enter and Space key activation",
                "Verify Escape key closes modals/dropdowns",
                "Test arrow key navigation in lists/menus",
                "Ensure no keyboard traps exist",
                "Verify focus is properly managed in dynamic content",
            ],
        }

    def get_screen_reader_guide(self) -> Dict[str, Any]:
        """Get screen reader compatibility guide."""
        return {
            "requirements": [
                "All images have alt text",
                "Form fields have proper labels",
                "Buttons have accessible names",
                "Links make sense out of context",
                "Page structure is semantic",
                "Dynamic content changes are announced",
                "Error messages are associated with inputs",
                "Role and state are properly communicated",
            ],
            "testing_tools": [
                "NVDA (Free)",
                "JAWS (Commercial)",
                "VoiceOver (Built into macOS/iOS)",
                "TalkBack (Built into Android)",
                "ChromeVox (Chrome extension)",
                "Windows Narrator (Built into Windows)",
            ],
            "common_issues": [
                "Missing alt text for images",
                "Unlabeled form fields",
                "Vague link text like 'Click here'",
                "Div elements used instead of semantic HTML",
                "ARIA attributes used incorrectly",
                "Focus not managed properly in dynamic content",
                "No announcements for error messages",
                "Poor heading structure",
            ],
        }

    def get_color_contrast_requirements(self) -> Dict[str, Any]:
        """Get color contrast requirements and guidelines."""
        return {
            "wcag_aa": {"normal_text": 4.5, "large_text": 3.0, "graphical_objects": 3.0},
            "wcag_aaa": {"normal_text": 7.0, "large_text": 4.5, "graphical_objects": 4.5},
            "text_size_classification": {
                "large_text": "18pt or 14pt bold",
                "normal_text": "Below 18pt and below 14pt bold",
            },
            "shadcn_colors": {
                "primary_foreground": "hsl(0 0% 98%)",
                "background": "hsl(0 0% 100%)",
                "muted_foreground": "hsl(240 3.8% 46.1%)",
                "destructive": "hsl(0 84.2% 60.2%)",
            },
            "testing_tools": [
                "WebAIM Contrast Checker",
                "Adobe Color Contrast Analyzer",
                "Colour Contrast Analyser (TPGi)",
                "Chrome DevTools Lighthouse",
                "axe DevTools",
            ],
        }

    def get_accessibility_checklist(self) -> Dict[str, List[str]]:
        """Get comprehensive accessibility checklist."""
        return {
            "structural": [
                "Use semantic HTML elements (nav, main, header, footer, section)",
                "Ensure proper heading hierarchy (h1 → h2 → h3)",
                "Provide page title that describes content",
                "Use lists appropriately for related items",
                "Include skip links for navigation",
                "Group related controls with fieldset/legend",
                "Use landmarks for major page sections",
            ],
            "interactive": [
                "All functionality available via keyboard",
                "Focus indicators visible and clear",
                "Logical tab order",
                "No keyboard traps",
                "Custom components support keyboard patterns",
                "Appropriate ARIA roles and properties",
                "Form fields have proper labels",
                "Buttons have accessible names",
            ],
            "visual": [
                "Sufficient color contrast (4.5:1 for normal text)",
                "Don't rely on color alone for information",
                "Text can be resized to 200% without breaking layout",
                "Focus indicators are clearly visible",
                "No flashing content (or controls provided)",
                "Consistent navigation and orientation",
                "Clear indication of interactive elements",
            ],
            "auditory": [
                "Provide text alternatives for audio content",
                "Ensure auto-playing audio can be paused",
                "Background audio is low volume or can be disabled",
                "Screen reader compatibility tested",
                "Error messages announced to screen readers",
                "Dynamic content changes are announced",
                "No auto-playing content without user control",
            ],
            "cognitive": [
                "Clear and simple language",
                "Consistent navigation and labeling",
                "Help and error recovery provided",
                "Sufficient time limits with extensions",
                "Clear instructions and feedback",
                "Predictable functionality",
                "Minimal distractions and interruptions",
                "Memory requirements minimized",
            ],
        }
