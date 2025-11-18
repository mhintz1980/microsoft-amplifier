"""
Advanced Tailwind CSS Patterns Library

Comprehensive collection of production-tested UI patterns and
design system components built with Tailwind CSS utility classes.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class PatternCategory(Enum):
    """Categories for UI patterns."""

    LAYOUT = "layout"
    NAVIGATION = "navigation"
    FORMS = "forms"
    FEEDBACK = "feedback"
    OVERLAY = "overlay"
    MEDIA = "media"
    DATA_DISPLAY = "data_display"


@dataclass
class UIComponent:
    """A complete UI component with Tailwind classes."""

    name: str
    description: str
    category: PatternCategory
    html_structure: str
    tailwind_classes: str
    variants: Dict[str, str]
    accessibility_features: List[str]
    responsive_modifications: Dict[str, str]
    performance_score: int
    custom_css_required: Optional[str] = None
    dark_mode_classes: Optional[str] = None


@dataclass
class DesignToken:
    """Design token for consistent styling."""

    token_name: str
    css_property: str
    value: str
    description: str
    usage_examples: List[str]


class TailwindPatternsLibrary:
    """
    Comprehensive library of Tailwind CSS patterns and design tokens.
    Provides production-tested UI components with accessibility and performance focus.
    """

    def __init__(self):
        self._init_component_library()
        self._init_design_tokens()
        self._init_responsive_patterns()
        self._init_animation_patterns()

    def _init_component_library(self):
        """Initialize comprehensive component library."""
        self.components = {
            # Layout Patterns
            "hero_section": UIComponent(
                name="Hero Section",
                description="Full-width hero section with background and CTA",
                category=PatternCategory.LAYOUT,
                html_structure="""<section class="hero">
    <div class="container">
        <div class="hero-content">
            <h1 class="hero-title"></h1>
            <p class="hero-subtitle"></p>
            <div class="hero-actions">
                <button class="btn-primary"></button>
                <button class="btn-secondary"></button>
            </div>
        </div>
        <div class="hero-visual">
            <!-- Hero image/video -->
        </div>
    </div>
</section>""",
                tailwind_classes="relative bg-gradient-to-br from-blue-50 to-indigo-100 py-20 px-4 sm:px-6 lg:px-8",
                variants={
                    "centered": "text-center items-center",
                    "split": "flex items-center justify-between",
                    "overlay": "relative bg-gray-900 text-white",
                },
                accessibility_features=["landmark role", "skip links", "focus management"],
                responsive_modifications={"mobile": "py-16 text-center", "tablet": "py-18", "desktop": "py-24"},
                performance_score=95,
                dark_mode_classes="bg-gradient-to-br from-gray-900 to-gray-800 text-white",
            ),
            "feature_grid": UIComponent(
                name="Feature Grid",
                description="Responsive grid of feature cards",
                category=PatternCategory.LAYOUT,
                html_structure="""<div class="feature-grid">
    <div class="feature-card">
        <div class="feature-icon"></div>
        <h3 class="feature-title"></h3>
        <p class="feature-description"></p>
    </div>
    <!-- More cards -->
</div>""",
                tailwind_classes="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-6xl mx-auto",
                variants={
                    "tight": "gap-4",
                    "spacious": "gap-12",
                    "asymmetric": "grid-cols-1 md:grid-cols-3 lg:grid-cols-4",
                },
                accessibility_features=["grid role", "item labeling"],
                responsive_modifications={
                    "mobile": "grid-cols-1 gap-6",
                    "tablet": "grid-cols-2 gap-8",
                    "desktop": "grid-cols-3 gap-8",
                },
                performance_score=92,
            ),
            # Navigation Patterns
            "main_navigation": UIComponent(
                name="Main Navigation",
                description="Responsive navigation with mobile menu",
                category=PatternCategory.NAVIGATION,
                html_structure="""<nav class="main-nav" role="navigation" aria-label="Main navigation">
    <div class="nav-container">
        <div class="nav-brand">
            <a href="/" class="brand-link"></a>
        </div>
        <ul class="nav-menu" role="menubar">
            <li class="nav-item" role="none">
                <a href="#" class="nav-link" role="menuitem"></a>
            </li>
            <!-- More items -->
        </ul>
        <button class="nav-toggle" aria-expanded="false" aria-controls="nav-menu">
            <span class="sr-only">Toggle navigation</span>
            <div class="hamburger"></div>
        </button>
    </div>
</nav>""",
                tailwind_classes="bg-white shadow-sm sticky top-0 z-50 border-b border-gray-200",
                variants={
                    "transparent": "bg-transparent border-transparent absolute top-0",
                    "dark": "bg-gray-900 border-gray-700",
                    "centered": "nav-brand:mx-auto",
                },
                accessibility_features=["ARIA labels", "keyboard navigation", "focus management", "skip links"],
                responsive_modifications={"mobile": "relative", "desktop": "static"},
                performance_score=88,
                dark_mode_classes="bg-gray-900 border-gray-700",
            ),
            "breadcrumb": UIComponent(
                name="Breadcrumb Navigation",
                description="Hierarchical navigation trail",
                category=PatternCategory.NAVIGATION,
                html_structure="""<nav class="breadcrumb" aria-label="Breadcrumb">
    <ol class="breadcrumb-list">
        <li class="breadcrumb-item">
            <a href="#" class="breadcrumb-link"></a>
        </li>
        <li class="breadcrumb-item" aria-current="page">
            <span class="breadcrumb-current"></span>
        </li>
    </ol>
</nav>""",
                tailwind_classes="flex items-center space-x-2 text-sm text-gray-600 py-3",
                variants={
                    "centered": "justify-center",
                    "separated": "divide-x divide-gray-300",
                },
                accessibility_features=["ARIA current", "semantic markup"],
                responsive_modifications={},
                performance_score=96,
            ),
            # Form Patterns
            "form_field": UIComponent(
                name="Form Field",
                description="Complete form input with label and validation",
                category=PatternCategory.FORMS,
                html_structure="""<div class="form-field">
    <label class="form-label" for="input-id">
        Label text
        <span class="required-indicator" aria-hidden="true">*</span>
    </label>
    <div class="input-wrapper">
        <input
            type="text"
            id="input-id"
            class="form-input"
            placeholder="Placeholder text"
            aria-describedby="input-description"
            required
        >
        <div class="input-icon"></div>
    </div>
    <p class="form-help" id="input-description">Help text</p>
    <div class="form-error" role="alert" id="input-error"></div>
</div>""",
                tailwind_classes="space-y-1",
                variants={
                    "error": "text-red-600 border-red-500",
                    "success": "text-green-600 border-green-500",
                    "disabled": "opacity-50 cursor-not-allowed",
                },
                accessibility_features=[
                    "form labels",
                    "field descriptions",
                    "error announcements",
                    "required indicators",
                ],
                responsive_modifications={},
                performance_score=94,
            ),
            "form_group": UIComponent(
                name="Form Group",
                description="Related form fields grouped together",
                category=PatternCategory.FORMS,
                html_structure="""<fieldset class="form-group">
    <legend class="form-legend">Group title</legend>
    <div class="form-group-content">
        <!-- Form fields -->
    </div>
    <p class="form-group-description">Group description</p>
</fieldset>""",
                tailwind_classes="space-y-4 p-4 border border-gray-200 rounded-lg",
                variants={
                    "inline": "flex flex-wrap items-center gap-4",
                    "card": "bg-white shadow-sm p-6",
                    "compact": "space-y-2 p-2",
                },
                accessibility_features=["fieldset/legend", "group labeling"],
                responsive_modifications={"mobile": "p-3", "desktop": "p-6"},
                performance_score=90,
            ),
            # Feedback Patterns
            "alert": UIComponent(
                name="Alert/Notification",
                description="Contextual alert messages",
                category=PatternCategory.FEEDBACK,
                html_structure="""<div class="alert" role="alert" aria-live="polite">
    <div class="alert-icon" aria-hidden="true"></div>
    <div class="alert-content">
        <h3 class="alert-title">Alert title</h3>
        <p class="alert-message">Alert message</p>
    </div>
    <button class="alert-close" aria-label="Close alert">
        <span aria-hidden="true">&times;</span>
    </button>
</div>""",
                tailwind_classes="flex items-start p-4 rounded-lg border",
                variants={
                    "info": "bg-blue-50 border-blue-200 text-blue-800",
                    "success": "bg-green-50 border-green-200 text-green-800",
                    "warning": "bg-yellow-50 border-yellow-200 text-yellow-800",
                    "error": "bg-red-50 border-red-200 text-red-800",
                    "dismissible": "justify-between",
                },
                accessibility_features=["ARIA live regions", "role alerts", "dismissibility"],
                responsive_modifications={},
                performance_score=93,
            ),
            "toast": UIComponent(
                name="Toast Notification",
                description="Fixed position toast messages",
                category=PatternCategory.FEEDBACK,
                html_structure="""<div class="toast" role="alert" aria-live="polite" aria-atomic="true">
    <div class="toast-content">
        <div class="toast-icon" aria-hidden="true"></div>
        <div class="toast-message">Toast message</div>
    </div>
    <button class="toast-close" aria-label="Close toast">
        <span aria-hidden="true">&times;</span>
    </button>
</div>""",
                tailwind_classes="fixed bottom-4 right-4 bg-white rounded-lg shadow-lg border border-gray-200 p-4 max-w-sm",
                variants={
                    "top": "bottom-auto top-4",
                    "left": "right-auto left-4",
                    "center": "left-1/2 transform -translate-x-1/2",
                    "stacked": "space-y-2",
                },
                accessibility_features=["ARIA live", "focus management", "timed dismissal"],
                responsive_modifications={"mobile": "left-4 right-4 max-w-none", "desktop": "max-w-sm"},
                performance_score=85,
            ),
            # Overlay Patterns
            "modal": UIComponent(
                name="Modal Dialog",
                description="Overlay modal dialog with backdrop",
                category=PatternCategory.OVERLAY,
                html_structure="""<div class="modal-overlay" role="dialog" aria-modal="true" aria-labelledby="modal-title">
    <div class="modal-backdrop"></div>
    <div class="modal-container">
        <div class="modal-header">
            <h2 class="modal-title" id="modal-title">Modal title</h2>
            <button class="modal-close" aria-label="Close modal">
                <span aria-hidden="true">&times;</span>
            </button>
        </div>
        <div class="modal-body">
            <!-- Modal content -->
        </div>
        <div class="modal-footer">
            <button class="btn-secondary">Cancel</button>
            <button class="btn-primary">Confirm</button>
        </div>
    </div>
</div>""",
                tailwind_classes="fixed inset-0 z-50 flex items-center justify-center p-4",
                variants={
                    "fullscreen": "modal-container:w-full h-full rounded-none",
                    "small": "modal-container:max-w-md",
                    "large": "modal-container:max-w-4xl",
                    "centered": "items-center justify-center",
                },
                accessibility_features=["ARIA modal", "focus trap", "escape key", "focus management"],
                responsive_modifications={
                    "mobile": "modal-container:w-full p-4",
                    "desktop": "modal-container:max-w-2xl",
                },
                performance_score=82,
                custom_css_required="backdrop-filter: blur(4px);",
            ),
            "dropdown": UIComponent(
                name="Dropdown Menu",
                description="Click-to-open dropdown menu",
                category=PatternCategory.OVERLAY,
                html_structure="""<div class="dropdown">
    <button class="dropdown-trigger" aria-expanded="false" aria-haspopup="menu">
        Trigger button
        <span class="dropdown-arrow" aria-hidden="true"></span>
    </button>
    <ul class="dropdown-menu" role="menu" aria-orientation="vertical">
        <li role="none">
            <a href="#" class="dropdown-item" role="menuitem">Menu item 1</a>
        </li>
        <li role="none">
            <a href="#" class="dropdown-item" role="menuitem">Menu item 2</a>
        </li>
    </ul>
</div>""",
                tailwind_classes="relative",
                variants={
                    "right": "dropdown-menu:right-0",
                    "up": "dropdown-menu:bottom-full mb-2",
                    "large": "dropdown-menu:w-64",
                },
                accessibility_features=["ARIA menu", "keyboard navigation", "focus management"],
                responsive_modifications={},
                performance_score=87,
            ),
            # Media Patterns
            "image_gallery": UIComponent(
                name="Image Gallery",
                description="Responsive image gallery with lightbox",
                category=PatternCategory.MEDIA,
                html_structure="""<div class="gallery">
    <div class="gallery-main">
        <img class="gallery-main-image" src="" alt="">
    </div>
    <div class="gallery-thumbnails">
        <button class="gallery-thumbnail" aria-pressed="false">
            <img src="" alt="" loading="lazy">
        </button>
        <!-- More thumbnails -->
    </div>
</div>""",
                tailwind_classes="space-y-4",
                variants={
                    "grid": "grid grid-cols-2 md:grid-cols-3 gap-4",
                    "carousel": "overflow-x-auto flex space-x-4",
                    "masonry": "columns-1 md:columns-2 lg:columns-3 gap-4",
                },
                accessibility_features=["alt text", "button states", "keyboard navigation"],
                responsive_modifications={"mobile": "space-y-2", "desktop": "space-y-4"},
                performance_score=79,
            ),
            # Data Display Patterns
            "data_table": UIComponent(
                name="Data Table",
                description="Accessible data table with sorting",
                category=PatternCategory.DATA_DISPLAY,
                html_structure="""<div class="table-container">
    <table class="data-table">
        <thead>
            <tr>
                <th class="table-header" scope="col">
                    <button class="table-sort" aria-label="Sort by column">
                        Column header
                        <span class="sort-indicator" aria-hidden="true"></span>
                    </button>
                </th>
                <!-- More headers -->
            </tr>
        </thead>
        <tbody>
            <tr class="table-row">
                <td class="table-cell">Cell content</td>
                <!-- More cells -->
            </tr>
        </tbody>
    </table>
</div>""",
                tailwind_classes="w-full border-collapse",
                variants={
                    "striped": "tbody tr:nth-child(even)",
                    "bordered": "border border-gray-200",
                    "compact": "text-sm",
                },
                accessibility_features=["table headers", "scope attributes", "sorting announcements"],
                responsive_modifications={
                    "mobile": "table-container:overflow-x-auto",
                    "desktop": "table-container:overflow-visible",
                },
                performance_score=91,
            ),
            "stat_card": UIComponent(
                name="Statistics Card",
                description="Display key metrics and statistics",
                category=PatternCategory.DATA_DISPLAY,
                html_structure="""<div class="stat-card">
    <div class="stat-header">
        <h3 class="stat-title">Metric name</h3>
        <div class="stat-icon" aria-hidden="true"></div>
    </div>
    <div class="stat-value">123,456</div>
    <div class="stat-change">
        <span class="change-indicator"></span>
        <span class="change-value">+12.5%</span>
    </div>
    <div class="stat-description">Description of change</div>
</div>""",
                tailwind_classes="bg-white rounded-lg shadow-sm p-6 border border-gray-200",
                variants={
                    "large": "p-8",
                    "compact": "p-4",
                    "trend_up": "text-green-600",
                    "trend_down": "text-red-600",
                },
                accessibility_features=["metric labeling", "change indicators"],
                responsive_modifications={"mobile": "p-4 text-center", "desktop": "p-6"},
                performance_score=94,
                dark_mode_classes="bg-gray-800 border-gray-700",
            ),
        }

    def _init_design_tokens(self):
        """Initialize comprehensive design token system."""
        self.design_tokens = {
            # Color Tokens
            "primary": DesignToken(
                token_name="primary",
                css_property="color",
                value="#3b82f6",
                description="Primary brand color",
                usage_examples=[
                    "bg-primary: Primary background",
                    "text-primary: Primary text color",
                    "border-primary: Primary border",
                ],
            ),
            "primary-light": DesignToken(
                token_name="primary-light",
                css_property="color",
                value="#dbeafe",
                description="Light variant of primary color",
                usage_examples=[
                    "bg-primary-light: Light primary background",
                    "border-primary-light: Light primary border",
                ],
            ),
            "secondary": DesignToken(
                token_name="secondary",
                css_property="color",
                value="#6b7280",
                description="Secondary gray color",
                usage_examples=["text-secondary: Secondary text", "border-secondary: Secondary border"],
            ),
            "success": DesignToken(
                token_name="success",
                css_property="color",
                value="#10b981",
                description="Success state color",
                usage_examples=[
                    "bg-success: Success background",
                    "text-success: Success text",
                    "border-success: Success border",
                ],
            ),
            "warning": DesignToken(
                token_name="warning",
                css_property="color",
                value="#f59e0b",
                description="Warning state color",
                usage_examples=["bg-warning: Warning background", "text-warning: Warning text"],
            ),
            "error": DesignToken(
                token_name="error",
                css_property="color",
                value="#ef4444",
                description="Error state color",
                usage_examples=["bg-error: Error background", "text-error: Error text", "border-error: Error border"],
            ),
            # Spacing Tokens
            "spacing-xs": DesignToken(
                token_name="spacing-xs",
                css_property="spacing",
                value="0.25rem",
                description="Extra small spacing (4px)",
                usage_examples=[
                    "p-spacing-xs: Extra small padding",
                    "m-spacing-xs: Extra small margin",
                    "space-y-spacing-xs: Extra small vertical space",
                ],
            ),
            "spacing-sm": DesignToken(
                token_name="spacing-sm",
                css_property="spacing",
                value="0.5rem",
                description="Small spacing (8px)",
                usage_examples=["p-spacing-sm: Small padding", "gap-spacing-sm: Small gap"],
            ),
            "spacing-md": DesignToken(
                token_name="spacing-md",
                css_property="spacing",
                value="1rem",
                description="Medium spacing (16px)",
                usage_examples=["p-spacing-md: Medium padding", "m-spacing-md: Medium margin"],
            ),
            "spacing-lg": DesignToken(
                token_name="spacing-lg",
                css_property="spacing",
                value="1.5rem",
                description="Large spacing (24px)",
                usage_examples=["p-spacing-lg: Large padding", "space-y-spacing-lg: Large vertical space"],
            ),
            "spacing-xl": DesignToken(
                token_name="spacing-xl",
                css_property="spacing",
                value="2rem",
                description="Extra large spacing (32px)",
                usage_examples=["p-spacing-xl: Extra large padding", "gap-spacing-xl: Extra large gap"],
            ),
            # Typography Tokens
            "font-primary": DesignToken(
                token_name="font-primary",
                css_property="font-family",
                value="'Inter', system-ui, sans-serif",
                description="Primary font family",
                usage_examples=["font-font-primary: Primary font"],
            ),
            "font-heading": DesignToken(
                token_name="font-heading",
                css_property="font-family",
                value="'Inter', system-ui, sans-serif",
                description="Heading font family",
                usage_examples=["font-font-heading: Heading font"],
            ),
            "text-xs": DesignToken(
                token_name="text-xs",
                css_property="font-size",
                value="0.75rem",
                description="Extra small text size",
                usage_examples=["text-text-xs: Extra small text"],
            ),
            "text-sm": DesignToken(
                token_name="text-sm",
                css_property="font-size",
                value="0.875rem",
                description="Small text size",
                usage_examples=["text-text-sm: Small text"],
            ),
            "text-base": DesignToken(
                token_name="text-base",
                css_property="font-size",
                value="1rem",
                description="Base text size",
                usage_examples=["text-text-base: Base text"],
            ),
            "text-lg": DesignToken(
                token_name="text-lg",
                css_property="font-size",
                value="1.125rem",
                description="Large text size",
                usage_examples=["text-text-lg: Large text"],
            ),
            "text-xl": DesignToken(
                token_name="text-xl",
                css_property="font-size",
                value="1.25rem",
                description="Extra large text size",
                usage_examples=["text-text-xl: Extra large text"],
            ),
            # Border Radius Tokens
            "radius-sm": DesignToken(
                token_name="radius-sm",
                css_property="border-radius",
                value="0.25rem",
                description="Small border radius (4px)",
                usage_examples=["rounded-radius-sm: Small border radius"],
            ),
            "radius-md": DesignToken(
                token_name="radius-md",
                css_property="border-radius",
                value="0.375rem",
                description="Medium border radius (6px)",
                usage_examples=["rounded-radius-md: Medium border radius"],
            ),
            "radius-lg": DesignToken(
                token_name="radius-lg",
                css_property="border-radius",
                value="0.5rem",
                description="Large border radius (8px)",
                usage_examples=["rounded-radius-lg: Large border radius"],
            ),
            "radius-xl": DesignToken(
                token_name="radius-xl",
                css_property="border-radius",
                value="0.75rem",
                description="Extra large border radius (12px)",
                usage_examples=["rounded-radius-xl: Extra large border radius"],
            ),
            # Shadow Tokens
            "shadow-sm": DesignToken(
                token_name="shadow-sm",
                css_property="box-shadow",
                value="0 1px 2px 0 rgba(0, 0, 0, 0.05)",
                description="Small shadow",
                usage_examples=["shadow-shadow-sm: Small shadow"],
            ),
            "shadow-md": DesignToken(
                token_name="shadow-md",
                css_property="box-shadow",
                value="0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)",
                description="Medium shadow",
                usage_examples=["shadow-shadow-md: Medium shadow"],
            ),
            "shadow-lg": DesignToken(
                token_name="shadow-lg",
                css_property="box-shadow",
                value="0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)",
                description="Large shadow",
                usage_examples=["shadow-shadow-lg: Large shadow"],
            ),
        }

    def _init_responsive_patterns(self):
        """Initialize responsive design patterns."""
        self.responsive_patterns = {
            "container_queries": {
                "description": "Container-based responsive design",
                "pattern": "@container",
                "usage": "Use when components need to respond to their container rather than viewport",
                "example": """@container (min-width: 300px) {
  .card { @apply grid-cols-2; }
}""",
                "browser_support": "Chrome 105+, Edge 105+, Safari 16+",
            },
            "mobile_first": {
                "description": "Mobile-first responsive design approach",
                "pattern": "Base styles + progressive enhancement",
                "usage": "Default approach for all responsive design",
                "example": """.card {
  @apply w-full p-4; /* Mobile styles */
  @apply md:w-1/2 md:p-6; /* Tablet styles */
  @apply lg:w-1/3 lg:p-8; /* Desktop styles */
}""",
                "browser_support": "Universal",
            },
            "clamp_function": {
                "description": "Fluid typography and spacing",
                "pattern": "clamp() CSS function",
                "usage": "Create fluid values that scale between breakpoints",
                "example": "font-size: clamp(1rem, 2.5vw, 2rem);",
                "browser_support": "Chrome 79+, Edge 79+, Safari 13.1+",
            },
            "aspect_ratio": {
                "description": "Consistent aspect ratios for media",
                "pattern": "aspect-ratio property",
                "usage": "Maintain consistent proportions for images and videos",
                "example": "aspect-ratio: 16/9;",
                "browser_support": "Chrome 88+, Edge 88+, Safari 15+",
            },
        }

    def _init_animation_patterns(self):
        """Initialize animation and motion patterns."""
        self.animation_patterns = {
            "micro_interactions": {
                "description": "Subtle animations for user feedback",
                "duration": "200ms",
                "easing": "ease-out",
                "examples": {
                    "button_press": "scale: 0.95 → 1.0",
                    "hover_lift": "translateY: 0 → -2px",
                    "focus_ring": "scale: 0.9 → 1.1",
                    "loading_spin": "rotate: 0 → 360deg",
                },
            },
            "page_transitions": {
                "description": "Smooth page and route transitions",
                "duration": "300ms",
                "easing": "ease-in-out",
                "examples": {
                    "fade_in": "opacity: 0 → 1",
                    "slide_up": "translateY: 20px → 0",
                    "scale_in": "scale: 0.9 → 1.0",
                },
            },
            "loading_states": {
                "description": "Animations for content loading",
                "duration": "1000ms",
                "easing": "ease-in-out",
                "examples": {
                    "skeleton": "background-position animation",
                    "spinner": "rotate: 0 → 360deg",
                    "pulse": "opacity: 1 → 0.5 → 1",
                    "shimmer": "background-position slide",
                },
            },
        }

    def get_component(self, component_name: str) -> Optional[UIComponent]:
        """Get a specific component by name."""
        return self.components.get(component_name)

    def get_components_by_category(self, category: PatternCategory) -> List[UIComponent]:
        """Get all components in a specific category."""
        return [comp for comp in self.components.values() if comp.category == category]

    def search_components(self, query: str) -> List[UIComponent]:
        """Search components by name or description."""
        query_lower = query.lower()
        return [
            comp
            for comp in self.components.values()
            if query_lower in comp.name.lower() or query_lower in comp.description.lower()
        ]

    def get_design_token(self, token_name: str) -> Optional[DesignToken]:
        """Get a specific design token by name."""
        return self.design_tokens.get(token_name)

    def get_tokens_by_property(self, property_name: str) -> List[DesignToken]:
        """Get all design tokens for a specific CSS property."""
        return [token for token in self.design_tokens.values() if token.css_property == property_name]

    def generate_component_code(self, component_name: str, variant: Optional[str] = None) -> str:
        """Generate complete HTML code for a component."""
        component = self.get_component(component_name)
        if not component:
            return f"Component '{component_name}' not found"

        html = component.html_structure

        # Apply variant modifications if specified
        if variant and variant in component.variants:
            # Add variant classes to the main element
            html = html.replace(
                f'class="{component.tailwind_classes.split()[0]}"',
                f'class="{component.tailwind_classes.split()[0]} {component.variants[variant]}"',
                1,
            )

        return html

    def generate_responsive_modifications(self, component_name: str) -> str:
        """Generate responsive CSS modifications for a component."""
        component = self.get_component(component_name)
        if not component:
            return ""

        modifications = []
        for breakpoint, classes in component.responsive_modifications.items():
            if breakpoint == "mobile":
                modifications.append(f"/* Mobile styles */\n{classes}")
            elif breakpoint == "tablet":
                modifications.append(f"/* Tablet styles (md:) */\n@apply md:{classes}")
            elif breakpoint == "desktop":
                modifications.append(f"/* Desktop styles (lg:) */\n@apply lg:{classes}")

        return "\n\n".join(modifications)

    def validate_component_accessibility(self, component_name: str) -> Dict[str, Any]:
        """Validate component accessibility features."""
        component = self.get_component(component_name)
        if not component:
            return {"error": f"Component '{component_name}' not found"}

        validation_result = {
            "component": component_name,
            "accessibility_score": 0,
            "missing_features": [],
            "present_features": component.accessibility_features,
            "recommendations": [],
        }

        # Check for essential accessibility features
        required_features = {
            "form": ["form labels", "field descriptions"],
            "navigation": ["ARIA labels", "keyboard navigation"],
            "modal": ["ARIA modal", "focus trap"],
            "alert": ["ARIA live regions"],
            "dropdown": ["ARIA menu", "keyboard navigation"],
        }

        for category, features in required_features.items():
            if category in component.name.lower():
                for feature in features:
                    if feature not in component.accessibility_features:
                        validation_result["missing_features"].append(feature)
                    else:
                        validation_result["accessibility_score"] += 25

        # Generate recommendations
        if not validation_result["missing_features"]:
            validation_result["recommendations"].append("✅ Component has good accessibility support")
        else:
            validation_result["recommendations"].append(
                f"⚠️ Missing accessibility features: {', '.join(validation_result['missing_features'])}"
            )

        return validation_result

    def get_performance_optimizations(self, component_name: str) -> List[str]:
        """Get performance optimization recommendations for a component."""
        component = self.get_component(component_name)
        if not component:
            return []

        optimizations = []

        if component.performance_score < 80:
            optimizations.append("Consider optimizing animations and transitions")
            optimizations.append("Reduce unnecessary DOM elements")

        if "animation" in component.name.lower() and component.custom_css_required:
            optimizations.append("Use CSS transform and opacity for better performance")

        if component.custom_css_required and "backdrop-filter" in component.custom_css_required:
            optimizations.append("Consider alternative to backdrop-filter for better performance")

        # Component-specific optimizations
        if "gallery" in component.name.lower():
            optimizations.append("Implement lazy loading for images")
            optimizations.append("Use srcset for responsive images")

        if "table" in component.name.lower():
            optimizations.append("Use CSS containment for better layout performance")
            optimizations.append("Consider virtual scrolling for large datasets")

        if component.performance_score >= 90:
            optimizations.append("✅ Component is well-optimized for performance")

        return optimizations

    def generate_css_variables(self) -> str:
        """Generate CSS custom properties from design tokens."""
        css_vars = ["/* CSS Custom Properties from Design Tokens */\n:root {"]

        # Group tokens by property
        grouped_tokens = {}
        for token in self.design_tokens.values():
            if token.css_property not in grouped_tokens:
                grouped_tokens[token.css_property] = []
            grouped_tokens[token.css_property].append(token)

        # Generate variables
        for property, tokens in grouped_tokens.items():
            css_vars.append(f"\n  /* {property.title()} Tokens */")
            for token in tokens:
                var_name = token.token_name.replace("_", "-")
                css_vars.append(f"  --{var_name}: {token.value};")

        css_vars.append("\n}")

        return "\n".join(css_vars)

    def export_design_system(self) -> Dict[str, Any]:
        """Export complete design system for documentation."""
        return {
            "components": {
                name: {
                    "name": comp.name,
                    "description": comp.description,
                    "category": comp.category.value,
                    "performance_score": comp.performance_score,
                    "accessibility_features": comp.accessibility_features,
                }
                for name, comp in self.components.items()
            },
            "design_tokens": {
                name: {
                    "name": token.token_name,
                    "property": token.css_property,
                    "value": token.value,
                    "description": token.description,
                }
                for name, token in self.design_tokens.items()
            },
            "responsive_patterns": self.responsive_patterns,
            "animation_patterns": self.animation_patterns,
            "css_variables": self.generate_css_variables(),
        }
