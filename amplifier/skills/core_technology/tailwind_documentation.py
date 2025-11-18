"""
Tailwind CSS Progressive Documentation System

Comprehensive documentation with progressive disclosure levels,
examples, and practical implementation guidance.
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class DocumentationLevel(Enum):
    """Progressive documentation levels."""
    QUICK_START = "quick_start"      # Get started in 5 minutes
    ESSENTIALS = "essentials"        # Core concepts and usage
    INTERMEDIATE = "intermediate"    # Advanced patterns and optimization
    EXPERT = "expert"               // Production strategies and mastery


@dataclass
class DocumentationSection:
    """A documentation section with progressive content."""
    title: str
    description: str
    level: DocumentationLevel
    content: str
    examples: List[str]
    prerequisites: List[str]
    next_steps: List[str]
    code_snippets: Dict[str, str]
    interactive_demos: List[str]


class TailwindDocumentationGenerator:
    """
    Progressive documentation system for Tailwind CSS expertise.

    Provides structured learning paths from beginner to expert level
    with practical examples and real-world implementations.
    """

    def __init__(self):
        self._init_documentation_structure()
        self._init_examples_library()
        self._init_tutorials()
        self._init_best_practices()

    def _init_documentation_structure(self):
        """Initialize comprehensive documentation structure."""
        self.documentation_sections = {
            # Quick Start Level
            "installation": DocumentationSection(
                title="Installation and Setup",
                description="Get Tailwind CSS running in your project in minutes",
                level=DocumentationLevel.QUICK_START,
                content=self._get_quick_start_content(),
                examples=["npm installation", "CDN setup", "CLI initialization"],
                prerequisites=["Node.js 16+", "npm/yarn", "Basic HTML/CSS knowledge"],
                next_steps=["Basic usage", "Configuration", "First component"],
                code_snippets={
                    "package.json": self._get_package_json_example(),
                    "tailwind.config": self._get_basic_config_example(),
                    "css_input": self._get_css_input_example(),
                    "html_usage": self._get_html_usage_example()
                },
                interactive_demos=[" playground.tailwindcss.com"]
            ),

            "first_steps": DocumentationSection(
                title="Your First Styled Component",
                description="Create your first Tailwind-styled component",
                level=DocumentationLevel.QUICK_START,
                content=self._get_first_steps_content(),
                examples=["Button component", "Card layout", "Navigation bar"],
                prerequisites=["Installation complete", "HTML structure"],
                next_steps=["Utility classes", "Responsive design", "Colors and spacing"],
                code_snippets={
                    "button": self._get_button_example(),
                    "card": self._get_card_example(),
                    "navigation": self._get_navigation_example()
                },
                interactive_demos=["Component builder", "Class explorer"]
            ),

            # Essentials Level
            "utility_classes": DocumentationSection(
                title="Understanding Utility Classes",
                description="Master the core concept of utility-first CSS",
                level=DocumentationLevel.ESSENTIALS,
                content=self._get_utility_classes_content(),
                examples=["Spacing", "Typography", "Colors", "Layout"],
                prerequisites=["Installation", "Basic HTML/CSS"],
                next_steps=["Responsive design", "State variants", "Custom configuration"],
                code_snippets={
                    "spacing_demo": self._get_spacing_demo(),
                    "typography_demo": self._get_typography_demo(),
                    "color_demo": self._get_color_demo(),
                    "layout_demo": self._get_layout_demo()
                },
                interactive_demos=["Utility class explorer", "Live coding playground"]
            ),

            "responsive_design": DocumentationSection(
                title="Responsive Design Made Simple",
                description="Create beautiful interfaces that work on all devices",
                level=DocumentationLevel.ESSENTIALS,
                content=self._get_responsive_content(),
                examples=["Mobile-first design", "Breakpoint usage", "Responsive grids"],
                prerequisites=["Utility classes", "HTML layout"],
                next_steps=["Dark mode", "Component patterns", "Performance optimization"],
                code_snippets={
                    "responsive_grid": self._get_responsive_grid_example(),
                    "responsive_typography": self._get_responsive_typography_example(),
                    "responsive_navigation": self._get_responsive_navigation_example()
                },
                interactive_demos=["Responsive playground", "Device testing"]
            ),

            # Intermediate Level
            "component_patterns": DocumentationSection(
                title="Advanced Component Patterns",
                description="Build complex, reusable UI components",
                level=DocumentationLevel.INTERMEDIATE,
                content=self._get_component_patterns_content(),
                examples=["Cards", "Forms", "Modals", "Navigation systems"],
                prerequisites=["Responsive design", "Utility mastery"],
                next_steps=["Design systems", "Performance optimization", "Framework integration"],
                code_snippets={
                    "component_library": self._get_component_library_example(),
                    "form_patterns": self._get_form_patterns_example(),
                    "modal_system": self._get_modal_system_example()
                },
                interactive_demos=["Component library builder", "Pattern explorer"]
            ),

            "customization": DocumentationSection(
                title="Customization and Theming",
                description="Tailor Tailwind to your specific needs",
                level=DocumentationLevel.INTERMEDIATE,
                content=self._get_customization_content(),
                examples=["Custom colors", "Typography systems", "Spacing scales"],
                prerequisites=["Component patterns", "Configuration knowledge"],
                next_steps=["Plugin development", "Design tokens", "Brand systems"],
                code_snippets={
                    "custom_colors": self._get_custom_colors_example(),
                    "typography_system": self._get_typography_system_example(),
                    "spacing_system": self._get_spacing_system_example()
                },
                interactive_demos=["Theme customizer", "Design token editor"]
            ),

            # Expert Level
            "performance_optimization": DocumentationSection(
                title="Performance Optimization Strategies",
                description="Optimize your Tailwind CSS for production",
                level=DocumentationLevel.EXPERT,
                content=self._get_performance_content(),
                examples=["JIT compilation", "PurgeCSS", "Bundle analysis", "Critical CSS"],
                prerequisites=["Customization", "Build tools knowledge"],
                next_steps=["Advanced configuration", "Monitoring", "Scaling strategies"],
                code_snippets={
                    "jit_config": self._get_jit_config_example(),
                    "purge_config": self._get_purge_config_example(),
                    "build_optimization": self._get_build_optimization_example()
                },
                interactive_demos=["Bundle analyzer", "Performance profiler"]
            ),

            "advanced_patterns": DocumentationSection(
                title="Advanced Patterns and Techniques",
                description="Master complex UI patterns and optimization",
                level=DocumentationLevel.EXPERT,
                content=self._get_advanced_patterns_content(),
                examples=["Layout systems", "Animation patterns", "Dark mode", "Accessibility"],
                prerequisites=["Performance optimization", "Design systems"],
                next_steps=["Architecture design", "Team workflows", "Cutting-edge techniques"],
                code_snippets={
                    "layout_systems": self._get_layout_systems_example(),
                    "animation_patterns": self._get_animation_patterns_example(),
                    "accessibility_patterns": self._get_accessibility_patterns_example()
                },
                interactive_demos=["Pattern library", "Accessibility tester"]
            ),

            "enterprise_integration": DocumentationSection(
                title="Enterprise and Team Integration",
                description="Scale Tailwind CSS in large organizations",
                level=DocumentationLevel.EXPERT,
                content=self._get_enterprise_content(),
                examples=["Design systems", "Component libraries", "CI/CD integration"],
                prerequisites=["Advanced patterns", "Team collaboration"],
                next_steps=["Architecture patterns", "Tooling", "Best practices"],
                code_snippets={
                    "design_system": self._get_design_system_example(),
                    "component_library": self._get_component_library_advanced_example(),
                    "ci_cd_integration": self._get_ci_cd_integration_example()
                },
                interactive_demos=["Enterprise setup wizard", "Team workflow planner"]
            )
        }

    def _init_examples_library(self):
        """Initialize comprehensive examples library."""
        self.examples_library = {
            "quick_start": {
                "business_card": {
                    title: "Business Card",
                    description: "Simple business card with Tailwind",
                    code: self._get_business_card_example(),
                    concepts: ["spacing", "typography", "colors"]
                },
                "button_collection": {
                    title: "Button Collection",
                    description: "Various button styles and states",
                    code: self._get_button_collection_example(),
                    concepts: ["colors", "spacing", "states"]
                },
                "pricing_cards": {
                    title: "Pricing Cards",
                    description="Responsive pricing card layout",
                    code: self._get_pricing_cards_example(),
                    concepts: ["grid", "responsive", "typography"]
                }
            },
            "intermediate": {
                "dashboard_layout": {
                    title: "Dashboard Layout",
                    description="Complex dashboard with sidebar and content",
                    code: self._get_dashboard_layout_example(),
                    concepts: ["grid", "flexbox", "responsive", "components"]
                },
                "form_system": {
                    title": "Form System",
                    description="Complete form with validation states",
                    code: self._get_form_system_example(),
                    concepts": ["forms", "states", "accessibility", "validation"]
                },
                "navigation_system": {
                    title: "Navigation System",
                    description="Multi-level navigation with mobile menu",
                    code: self._get_navigation_system_example(),
                    concepts": ["responsive", "states", "components", "javascript"]
                }
            },
            "advanced": {
                "ecommerce_page": {
                    title: "E-commerce Product Page",
                    description="Full product page with gallery, reviews, and purchase flow",
                    code: self._get_ecommerce_page_example(),
                    concepts: ["layout", "components", "states", "javascript", "accessibility"]
                },
                "admin_panel": {
                    title: "Admin Panel",
                    description="Complex admin interface with tables, charts, and forms",
                    code: self._get_admin_panel_example(),
                    concepts: ["tables", "forms", "dashboard", "components", "javascript"]
                },
                "social_media_feed": {
                    title: "Social Media Feed",
                    description="Interactive social media feed with comments and reactions",
                    code: self._get_social_media_feed_example(),
                    concepts: ["layout", "components", "states", "javascript", "real-time"]
                }
            }
        }

    def _init_tutorials(self):
        """Initialize step-by-step tutorials."""
        self.tutorials = {
            "build_portfolio": {
                title: "Build a Portfolio Website",
                duration: "2 hours",
                difficulty: "Beginner",
                steps: [
                    "Project setup and Tailwind installation",
                    "Create hero section with call-to-action",
                    "Build responsive project gallery",
                    "Add contact form with validation",
                    "Implement dark mode toggle",
                    "Optimize for production"
                ]
            },
            "design_system": {
                title: "Create a Design System",
                duration: "4 hours",
                difficulty: "Intermediate",
                steps: [
                    "Define design tokens and variables",
                    "Create component library structure",
                    "Build core components (buttons, inputs, cards)",
                    "Implement responsive design patterns",
                    "Add documentation and usage examples",
                    "Set up automated testing"
                ]
            },
            "ecommerce_site": {
                title: "Build an E-commerce Site",
                duration: "8 hours",
                difficulty: "Advanced",
                steps: [
                    "Project architecture and setup",
                    "Create product catalog and filtering",
                    "Build shopping cart functionality",
                    "Implement checkout process",
                    "Add user account management",
                    "Optimize performance and SEO"
                ]
            }
        }

    def _init_best_practices(self):
        """Initialize best practices and guidelines."""
        self.best_practices = {
            "performance": [
                "Enable JIT compilation mode",
                "Configure purge paths accurately",
                "Use CSS containment for complex layouts",
                "Optimize images with responsive techniques",
                "Monitor bundle size regularly"
            ],
            "accessibility": [
                "Always provide focus indicators",
                "Ensure sufficient color contrast",
                "Use semantic HTML structure",
                "Test with keyboard navigation",
                "Include screen reader labels"
            ],
            "maintainability": [
                "Use consistent naming conventions",
                "Create reusable component patterns",
                "Document custom utilities and configurations",
                "Keep configuration files organized",
                "Use version control for design tokens"
            ],
            "team_collaboration": [
                "Establish shared design system",
                "Create component documentation",
                "Use design tokens for consistency",
                "Implement code review guidelines",
                "Automate testing and validation"
            ]
        }

    def get_documentation(self, section_name: str, level: Optional[DocumentationLevel] = None) -> Optional[DocumentationSection]:
        """Get documentation section with optional level filtering."""
        section = self.documentation_sections.get(section_name)
        if not section:
            return None

        if level and section.level != level:
            return None

        return section

    def get_learning_path(self, user_level: str) -> List[DocumentationSection]:
        """Get recommended learning path based on user experience."""
        if user_level == "beginner":
            return [
                self.get_documentation("installation"),
                self.get_documentation("first_steps"),
                self.get_documentation("utility_classes"),
                self.get_documentation("responsive_design")
            ]
        elif user_level == "intermediate":
            return [
                self.get_documentation("component_patterns"),
                self.get_documentation("customization")
            ]
        elif user_level == "expert":
            return [
                self.get_documentation("performance_optimization"),
                self.get_documentation("advanced_patterns"),
                self.get_documentation("enterprise_integration")
            ]
        else:
            return list(self.documentation_sections.values())

    def get_example(self, category: str, example_name: str) -> Optional[Dict[str, Any]]:
        """Get specific example from the examples library."""
        return self.examples_library.get(category, {}).get(example_name)

    def get_tutorial(self, tutorial_name: str) -> Optional[Dict[str, Any]]:
        """Get specific tutorial."""
        return self.tutorials.get(tutorial_name)

    def generate_quick_reference(self) -> str:
        """Generate quick reference guide."""
        reference = """
# Tailwind CSS Quick Reference

## Core Concepts
- Utility-first CSS framework
- Mobile-first responsive design
- Customizable design system
- Zero runtime JavaScript

## Installation
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

## Basic Usage
```html
<div class="bg-blue-500 text-white p-4 rounded-lg">
  Hello Tailwind!
</div>
```

## Responsive Design
```html
<div class="w-full md:w-1/2 lg:w-1/3">
  Responsive width
</div>
```

## Common Utilities
- **Spacing**: p-4 m-2 space-y-4
- **Colors**: bg-blue-500 text-white border-gray-200
- **Typography**: text-lg font-bold leading-relaxed
- **Layout**: flex grid container
- **Sizing**: w-full h-screen max-w-4xl

## Breakpoints
- sm: 640px+
- md: 768px+
- lg: 1024px+
- xl: 1280px+
- 2xl: 1536px+

## State Variants
- hover: - Hover state
- focus: - Focus state
- active: - Active state
- disabled: - Disabled state

## Dark Mode
```javascript
// tailwind.config.js
module.exports = {
  darkMode: 'class', // or 'media'
}
```
        """
        return reference.strip()

    def generate_cheat_sheet(self) -> str:
        """Generate comprehensive cheat sheet."""
        cheat_sheet = """
# Tailwind CSS Cheat Sheet

## Layout
```html
<!-- Display -->
<div class="block hidden flex inline-flex grid inline-grid"></div>

<!-- Container -->
<div class="container mx-auto px-4"></div>

<!-- Flexbox -->
<div class="flex flex-row flex-col items-center justify-between flex-1"></div>

<!-- Grid -->
<div class="grid grid-cols-3 grid-rows-2 gap-4"></div>
```

## Spacing
```html
<!-- Padding -->
<div class="p-4 px-2 py-3 pt-2 pr-4 pb-6 pl-8"></div>

<!-- Margin -->
<div class="m-4 mx-auto my-2 mt-6 mr-4 mb-3 ml-2"></div>

<!-- Space Between -->
<div class="space-y-4 space-x-2"></div>
```

## Typography
```html
<!-- Font Size -->
<p class="text-xs text-sm text-base text-lg text-xl text-2xl"></p>

<!-- Font Weight -->
<span class="font-light font-normal font-medium font-bold"></span>

<!-- Line Height -->
<p class="leading-tight leading-normal leading-relaxed leading-loose"></p>

<!-- Text Alignment -->
<p class="text-left text-center text-right justify"></p>

<!-- Text Color -->
<p class="text-gray-900 text-blue-500 text-white"></p>
```

## Colors
```html
<!-- Background -->
<div class="bg-white bg-gray-100 bg-blue-500 bg-transparent"></div>

<!-- Text -->
<span class="text-black text-gray-500 text-blue-600 text-white"></span>

<!-- Border -->
<div class="border border-gray-300 border-blue-500 border-dashed"></div>
```

## Sizing
```html
<!-- Width/Height -->
<div class="w-full w-auto w-1/2 w-screen w-64 w-px"></div>
<div class="h-full h-auto h-screen h-32 h-px"></div>

<!-- Max/Min -->
<div class="max-w-4xl min-h-screen max-w-full"></div>
```

## Borders
```html
<!-- Border Radius -->
<div class="rounded rounded-sm rounded-lg rounded-full"></div>

<!-- Border Width -->
<div class="border border-2 border-4 border-8"></div>
```

## Shadows
```html
<div class="shadow shadow-sm shadow-md shadow-lg shadow-xl"></div>
<div class="shadow-inner shadow-none"></div>
```

## Opacity
```html
<div class="opacity-0 opacity-25 opacity-50 opacity-75 opacity-100"></div>
```

## Position
```html
<div class="static fixed absolute relative sticky"></div>
```

## Z-Index
```html
<div class="z-0 z-10 z-20 z-30 z-40 z-50"></div>
```

## Transforms
```html
<div class="transform scale-95 rotate-45 translate-x-2 translate-y-4"></div>
```

## Transitions
```html
<button class="transition-all duration-300 ease-in-out hover:scale-105">
  Animated Button
</button>
```

## Animation
```html
<div class="animate-spin animate-ping animate-pulse animate-bounce"></div>
```

## Responsive Variants
```html
<div class="w-full md:w-1/2 lg:w-1/3 xl:w-1/4 2xl:w-1/6"></div>
```

## Dark Mode
```html
<div class="bg-white dark:bg-gray-900 text-gray-900 dark:text-white">
  Adaptive content
</div>
```

## Common Patterns
```html
<!-- Card -->
<div class="bg-white rounded-lg shadow-md p-6 max-w-sm">
  <h3 class="text-lg font-semibold mb-2">Card Title</h3>
  <p class="text-gray-600">Card content</p>
</div>

<!-- Button -->
<button class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600">
  Click me
</button>

<!-- Input -->
<input class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500">
```
        """
        return cheat_sheet.strip()

    # Content generation methods
    def _get_quick_start_content(self) -> str:
        return """
## Getting Started with Tailwind CSS

Tailwind CSS is a utility-first CSS framework that provides low-level utility classes to build custom designs without writing CSS.

### Why Tailwind?

✅ **Rapid Development**: Build interfaces faster without writing CSS
✅ **Consistent Design**: Enforce design system consistency automatically
✅ **Small Bundle Size**: Only includes the CSS you actually use
✅ **Highly Customizable**: Tailor every aspect to your needs
✅ **Framework Agnostic**: Works with any frontend framework

### Installation Options

#### 1. NPM/Yarn (Recommended)
```bash
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```

#### 2. CDN (Quick Start)
```html
<script src="https://cdn.tailwindcss.com"></script>
```

### Basic Setup Process

1. **Install dependencies** using your preferred package manager
2. **Initialize configuration** with `npx tailwindcss init`
3. **Configure template paths** in your tailwind.config.js
4. **Add CSS directives** to your main CSS file
5. **Build your CSS** with the Tailwind CLI or through your build process

### First Styled Element

Once set up, you can start styling immediately:

```html
<div class="bg-blue-500 text-white p-4 rounded-lg">
  Hello, Tailwind!
</div>
```

This single div has:
- Blue background (`bg-blue-500`)
- White text (`text-white`)
- 1rem padding (`p-4`)
- Large rounded corners (`rounded-lg`)

### Next Steps

After completing installation:
1. Learn utility classes and their patterns
2. Understand responsive design with Tailwind
3. Explore component-based thinking
4. Master customization and theming
5. Optimize for production
        """

    def _get_package_json_example(self) -> str:
        return '''
{
  "name": "my-tailwind-project",
  "version": "1.0.0",
  "devDependencies": {
    "tailwindcss": "^3.4.0",
    "postcss": "^8.4.0",
    "autoprefixer": "^10.4.0"
  },
  "scripts": {
    "dev": "npx tailwindcss -i ./src/input.css -o ./dist/output.css --watch",
    "build": "npx tailwindcss -i ./src/input.css -o ./dist/output.css --minify"
  }
}
        '''

    def _get_basic_config_example(self) -> str:
        return '''
module.exports = {
  content: [
    "./src/**/*.{html,js}",
    "./public/**/*.html"
  ],
  theme: {
    extend: {},
  },
  plugins: []
}
        '''

    def _get_css_input_example(self) -> str:
        return '''
@tailwind base;
@tailwind components;
@tailwind utilities;
        '''

    def _get_html_usage_example(self) -> str:
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>My Tailwind App</title>
    <link href="/dist/output.css" rel="stylesheet">
</head>
<body>
    <div class="bg-white min-h-screen">
        <div class="container mx-auto px-4 py-8">
            <h1 class="text-4xl font-bold text-center mb-8">
                Welcome to Tailwind CSS
            </h1>
            <div class="max-w-md mx-auto bg-gray-100 rounded-lg p-6">
                <p class="text-gray-700 text-center">
                    Your first Tailwind-styled component!
                </p>
            </div>
        </div>
    </div>
</body>
</html>
        '''

    # Additional content generation methods would be implemented here...
    def _get_button_example(self) -> str:
        return '''
<!-- Primary Button -->
<button class="px-4 py-2 bg-blue-500 text-white rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500">
  Primary Button
</button>

<!-- Secondary Button -->
<button class="px-4 py-2 bg-gray-200 text-gray-900 rounded-lg hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500">
  Secondary Button
</button>

<!-- Outline Button -->
<button class="px-4 py-2 border-2 border-blue-500 text-blue-500 rounded-lg hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-blue-500">
  Outline Button
</button>
        '''

    # Add more content generation methods as needed...

    def export_documentation(self, format: str = "markdown") -> str:
        """Export complete documentation in specified format."""
        if format == "markdown":
            return self._export_markdown_documentation()
        elif format == "html":
            return self._export_html_documentation()
        else:
            raise ValueError(f"Unsupported format: {format}")

    def _export_markdown_documentation(self) -> str:
        """Export documentation as markdown."""
        sections = []

        for name, section in self.documentation_sections.items():
            sections.append(f"# {section.title}\n")
            sections.append(f"{section.description}\n")
            sections.append(f"**Level**: {section.level.value}\n")
            sections.append(f"**Prerequisites**: {', '.join(section.prerequisites)}\n")
            sections.append("## Content\n")
            sections.append(section.content)

            if section.examples:
                sections.append("\n## Examples\n")
                for example in section.examples:
                    sections.append(f"- {example}")

            if section.code_snippets:
                sections.append("\n## Code Examples\n")
                for title, code in section.code_snippets.items():
                    sections.append(f"### {title}\n```{code}```\n")

            sections.append("\n---\n")

        return "\n".join(sections)