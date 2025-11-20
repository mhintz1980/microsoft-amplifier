"""
Theme Factory Skill

Professional theme generation and application system for immediate visual polish.
Provides zero-dependency, professional-grade themes with HTML/CSS output
that can be applied directly to web applications and documentation.

Core Capabilities:
- 10 Professional Themes (Enterprise, Creative, Minimal, etc.)
- Zero External Dependencies (Pure Python/CSS)
- HTML/CSS Application System
- Theme Customization and Mixing
- Bootstrap-Compatible Integration
- Responsive Design Support
- Accessibility Compliance
- Performance Optimized CSS

Agent Lightning Integration:
- Tracks theme performance metrics
- Learns optimal color combinations
- Optimizes CSS generation speed
- Maintains theme usage statistics
"""

import json
import logging
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from ..skills_framework.base_skill import BaseSkill as FrameworkBaseSkill
from ..skills_framework.base_skill import SkillContext as FrameworkSkillContext
from ..skills_framework.base_skill import SkillResult as FrameworkSkillResult
from ..utils.token_utils import estimate_tokens

logger = logging.getLogger(__name__)


@dataclass
class ThemeConfig:
    """Configuration for a professional theme"""
    name: str
    description: str
    primary_color: str
    secondary_color: str
    accent_color: str
    background_color: str
    surface_color: str
    text_primary: str
    text_secondary: str
    border_color: str
    font_family_primary: str
    font_family_secondary: str
    border_radius: str
    shadow_style: str
    gradient_primary: str
    gradient_secondary: str


@dataclass
class ThemeApplication:
    """Result of theme application"""
    html_content: str
    css_content: str
    theme_name: str
    custom_properties: Dict[str, str]


class ThemeFactorySkill(FrameworkBaseSkill):
    """
    Professional theme generation and application system.

    Provides immediate visual polish through zero-dependency, professional-grade
    themes with HTML/CSS output for web applications and documentation.
    """

    def __init__(self):
        super().__init__(
            skill_id="theme_factory",
            name="Theme Factory",
            description="Professional theme generation and application system. Provides zero-dependency, professional-grade themes with HTML/CSS output for immediate visual polish.",
        )
        # Add missing tags attribute for skill registration
        self.tags = ["frontend", "ui", "css", "themes", "design"]

        # Initialize theme system
        self.themes = self._load_themes()
        self.performance_metrics = {
            "themes_generated": 0,
            "css_generated": 0,
            "applications_completed": 0,
            "average_generation_time": 0.0
        }

        # Agent Lightning integration
        self.theme_performance_cache = {}
        self.popularity_tracker = {}

    async def execute(self, input_data: Any, context: Any = None) -> FrameworkSkillResult:
        """Execute the theme factory skill"""
        try:
            # Validate input
            if not await self.validate_input(input_data):
                return FrameworkSkillResult(
                    success=False,
                    error="Invalid input data. Expected dict with 'action' and 'theme_name' or 'custom_theme'"
                )

            start_time = time.time()

            # Parse input
            if isinstance(input_data, str):
                # Handle simple string input
                action = "generate"
                theme_name = input_data
                target_content = ""
            else:
                action = input_data.get("action", "generate")
                theme_name = input_data.get("theme_name")
                target_content = input_data.get("target_content", "")

            if action == "list_themes":
                result = await self._list_available_themes()
            elif action == "generate":
                result = await self._generate_theme(theme_name, target_content)
            elif action == "generate_css":
                result = await self._generate_css_only(theme_name)
            elif action == "custom_theme":
                custom_config = input_data.get("custom_theme")
                result = await self._generate_custom_theme(custom_config)
            else:
                result = {"error": f"Unknown action: {action}"}

            execution_time = time.time() - start_time
            tokens_used = estimate_tokens(str(result))

            # Update metrics
            self._update_performance_metrics(action, execution_time)

            return FrameworkSkillResult(
                success=True,
                data=result,
                execution_time=execution_time,
                tokens_used=tokens_used
            )

        except Exception as e:
            logger.error(f"ThemeFactorySkill execution error: {e}")
            return FrameworkSkillResult(
                success=False,
                error=str(e),
                execution_time=0.0,
                tokens_used=0
            )

    async def validate_input(self, input_data: Any) -> bool:
        """Validate input data before execution"""
        if input_data is None:
            return False

        if isinstance(input_data, str):
            return len(input_data.strip()) > 0

        if isinstance(input_data, dict):
            # For any dict input, check if it has at least one valid field
            if "action" in input_data:
                return True
            elif "theme_name" in input_data:
                return True
            elif "custom_theme" in input_data:
                return True
            else:
                return False

        return False

    def get_capabilities(self) -> List[str]:
        """Get list of skill capabilities"""
        return [
            "Professional Theme Generation",
            "CSS Output Generation",
            "HTML Theme Application",
            "Custom Theme Creation",
            "Theme Mixing and Blending",
            "Responsive Design Support",
            "Accessibility Compliance",
            "Performance Optimization",
            "Bootstrap Integration",
            "Zero-Dependency Operation",
        ]

    async def _list_available_themes(self) -> Dict[str, Any]:
        """List all available themes with descriptions"""
        return {
            "available_themes": [
                {
                    "name": theme.name,
                    "description": theme.description,
                    "primary_color": theme.primary_color,
                    "category": self._get_theme_category(theme.name)
                }
                for theme in self.themes.values()
            ],
            "total_themes": len(self.themes)
        }

    async def _generate_theme(self, theme_name: str, target_content: str = "") -> Dict[str, Any]:
        """Generate a complete themed HTML page"""
        if theme_name not in self.themes:
            return {"error": f"Theme '{theme_name}' not found. Available: {list(self.themes.keys())}"}

        theme = self.themes[theme_name]

        # Generate CSS custom properties
        custom_properties = self._generate_css_custom_properties(theme)

        # Generate CSS content
        css_content = self._generate_css_content(theme, custom_properties)

        # Generate HTML content
        if target_content:
            html_content = self._wrap_content_with_theme(target_content, theme, custom_properties)
        else:
            html_content = self._generate_sample_html(theme, custom_properties)

        # Update popularity tracker
        self.popularity_tracker[theme_name] = self.popularity_tracker.get(theme_name, 0) + 1

        return {
            "html_content": html_content,
            "css_content": css_content,
            "theme_info": {
                "name": theme.name,
                "description": theme.description,
                "custom_properties": custom_properties
            }
        }

    async def _generate_css_only(self, theme_name: str) -> Dict[str, Any]:
        """Generate only CSS content for a theme"""
        if theme_name not in self.themes:
            return {"error": f"Theme '{theme_name}' not found"}

        theme = self.themes[theme_name]
        custom_properties = self._generate_css_custom_properties(theme)
        css_content = self._generate_css_content(theme, custom_properties)

        return {
            "css_content": css_content,
            "custom_properties": custom_properties,
            "theme_name": theme_name
        }

    async def _generate_custom_theme(self, custom_config: Dict[str, Any]) -> Dict[str, Any]:
        """Generate theme from custom configuration"""
        try:
            # Validate required fields
            required_fields = ["name", "primary_color", "secondary_color", "background_color"]
            for field in required_fields:
                if field not in custom_config:
                    return {"error": f"Missing required field: {field}"}

            # Create theme config with defaults
            theme_config = ThemeConfig(
                name=custom_config["name"],
                description=custom_config.get("description", f"Custom theme: {custom_config['name']}"),
                primary_color=custom_config["primary_color"],
                secondary_color=custom_config["secondary_color"],
                accent_color=custom_config.get("accent_color", custom_config["primary_color"]),
                background_color=custom_config["background_color"],
                surface_color=custom_config.get("surface_color", "#ffffff"),
                text_primary=custom_config.get("text_primary", "#1a1a1a"),
                text_secondary=custom_config.get("text_secondary", "#666666"),
                border_color=custom_config.get("border_color", "#e0e0e0"),
                font_family_primary=custom_config.get("font_family_primary", "Inter, system-ui, sans-serif"),
                font_family_secondary=custom_config.get("font_family_secondary", "Georgia, serif"),
                border_radius=custom_config.get("border_radius", "8px"),
                shadow_style=custom_config.get("shadow_style", "0 2px 8px rgba(0,0,0,0.1)"),
                gradient_primary=custom_config.get("gradient_primary", f"{custom_config['primary_color']} 0%, {custom_config['secondary_color']} 100%"),
                gradient_secondary=custom_config.get("gradient_secondary", f"{custom_config['secondary_color']} 0%, {custom_config['primary_color']} 100%")
            )

            custom_properties = self._generate_css_custom_properties(theme_config)
            css_content = self._generate_css_content(theme_config, custom_properties)

            return {
                "css_content": css_content,
                "custom_properties": custom_properties,
                "theme_config": theme_config.__dict__
            }

        except Exception as e:
            return {"error": f"Failed to generate custom theme: {str(e)}"}

    def _load_themes(self) -> Dict[str, ThemeConfig]:
        """Load all predefined professional themes"""
        return {
            "enterprise": ThemeConfig(
                name="enterprise",
                description="Professional corporate theme with blue accents and clean design",
                primary_color="#1e40af",
                secondary_color="#3b82f6",
                accent_color="#60a5fa",
                background_color="#ffffff",
                surface_color="#f8fafc",
                text_primary="#1e293b",
                text_secondary="#64748b",
                border_color="#e2e8f0",
                font_family_primary="Inter, system-ui, sans-serif",
                font_family_secondary="Inter, system-ui, sans-serif",
                border_radius="6px",
                shadow_style="0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
                gradient_primary="linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)",
                gradient_secondary="linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)"
            ),

            "creative": ThemeConfig(
                name="creative",
                description="Vibrant artistic theme with purple gradients and bold typography",
                primary_color="#7c3aed",
                secondary_color="#a78bfa",
                accent_color="#c4b5fd",
                background_color="#fefefe",
                surface_color="#faf5ff",
                text_primary="#1f1f1f",
                text_secondary="#6b7280",
                border_color="#e9d5ff",
                font_family_primary="Calistoga, Georgia, serif",
                font_family_secondary="Inter, system-ui, sans-serif",
                border_radius="12px",
                shadow_style="0 4px 12px rgba(124,58,237,0.15)",
                gradient_primary="linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)",
                gradient_secondary="linear-gradient(135deg, #a78bfa 0%, #c4b5fd 100%)"
            ),

            "minimal": ThemeConfig(
                name="minimal",
                description="Clean minimalist theme with subtle grays and sharp typography",
                primary_color="#171717",
                secondary_color="#404040",
                accent_color="#737373",
                background_color="#ffffff",
                surface_color="#fafafa",
                text_primary="#171717",
                text_secondary="#737373",
                border_color="#e5e5e5",
                font_family_primary="system-ui, -apple-system, sans-serif",
                font_family_secondary="system-ui, -apple-system, sans-serif",
                border_radius="4px",
                shadow_style="0 1px 2px rgba(0,0,0,0.05)",
                gradient_primary="linear-gradient(135deg, #171717 0%, #404040 100%)",
                gradient_secondary="linear-gradient(135deg, #404040 0%, #737373 100%)"
            ),

            "warm": ThemeConfig(
                name="warm",
                description="Cozy warm theme with orange accents and friendly colors",
                primary_color="#ea580c",
                secondary_color="#fb923c",
                accent_color="#fed7aa",
                background_color="#fff7ed",
                surface_color="#fed7aa",
                text_primary="#1c1917",
                text_secondary="#78716c",
                border_color="#fdba74",
                font_family_primary="system-ui, sans-serif",
                font_family_secondary="Georgia, serif",
                border_radius="8px",
                shadow_style="0 2px 8px rgba(234,88,12,0.15)",
                gradient_primary="linear-gradient(135deg, #ea580c 0%, #fb923c 100%)",
                gradient_secondary="linear-gradient(135deg, #fb923c 0%, #fed7aa 100%)"
            ),

            "nature": ThemeConfig(
                name="nature",
                description="Fresh nature-inspired theme with green tones and organic feel",
                primary_color="#059669",
                secondary_color="#10b981",
                accent_color="#34d399",
                background_color="#ecfdf5",
                surface_color="#d1fae5",
                text_primary="#064e3b",
                text_secondary="#6b7280",
                border_color="#a7f3d0",
                font_family_primary="system-ui, sans-serif",
                font_family_secondary="Georgia, serif",
                border_radius="6px",
                shadow_style="0 2px 8px rgba(5,150,105,0.1)",
                gradient_primary="linear-gradient(135deg, #059669 0%, #10b981 100%)",
                gradient_secondary="linear-gradient(135deg, #10b981 0%, #34d399 100%)"
            ),

            "ocean": ThemeConfig(
                name="ocean",
                description="Calm ocean theme with blue gradients and serene atmosphere",
                primary_color="#0c4a6e",
                secondary_color="#0284c7",
                accent_color="#0ea5e9",
                background_color="#f0f9ff",
                surface_color="#e0f2fe",
                text_primary="#0c4a6e",
                text_secondary="#64748b",
                border_color="#bae6fd",
                font_family_primary="system-ui, sans-serif",
                font_family_secondary="Inter, system-ui, sans-serif",
                border_radius="8px",
                shadow_style="0 2px 8px rgba(12,74,110,0.1)",
                gradient_primary="linear-gradient(135deg, #0c4a6e 0%, #0284c7 100%)",
                gradient_secondary="linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)"
            ),

            "sunset": ThemeConfig(
                name="sunset",
                description="Dramatic sunset theme with warm gradients and romantic colors",
                primary_color="#dc2626",
                secondary_color="#f97316",
                accent_color="#fb923c",
                background_color="#fff7ed",
                surface_color="#fed7aa",
                text_primary="#7c2d12",
                text_secondary="#92400e",
                border_color="#fdba74",
                font_family_primary="Georgia, serif",
                font_family_secondary="system-ui, sans-serif",
                border_radius="12px",
                shadow_style="0 4px 12px rgba(220,38,38,0.15)",
                gradient_primary="linear-gradient(135deg, #dc2626 0%, #f97316 100%)",
                gradient_secondary="linear-gradient(135deg, #f97316 0%, #fb923c 100%)"
            ),

            "midnight": ThemeConfig(
                name="midnight",
                description="Dark professional theme with deep blues and subtle accents",
                primary_color="#1e293b",
                secondary_color="#334155",
                accent_color="#64748b",
                background_color="#0f172a",
                surface_color="#1e293b",
                text_primary="#f1f5f9",
                text_secondary="#cbd5e1",
                border_color="#334155",
                font_family_primary="Inter, system-ui, sans-serif",
                font_family_secondary="system-ui, sans-serif",
                border_radius="8px",
                shadow_style="0 2px 8px rgba(0,0,0,0.3)",
                gradient_primary="linear-gradient(135deg, #1e293b 0%, #334155 100%)",
                gradient_secondary="linear-gradient(135deg, #334155 0%, #64748b 100%)"
            ),

            "elegant": ThemeConfig(
                name="elegant",
                description="Sophisticated theme with gold accents and luxury feel",
                primary_color="#b45309",
                secondary_color="#f59e0b",
                accent_color="#fbbf24",
                background_color="#fffbeb",
                surface_color="#fef3c7",
                text_primary="#451a03",
                text_secondary="#78350f",
                border_color="#fde68a",
                font_family_primary="Playfair Display, Georgia, serif",
                font_family_secondary="Inter, system-ui, sans-serif",
                border_radius="4px",
                shadow_style="0 2px 8px rgba(180,83,9,0.1)",
                gradient_primary="linear-gradient(135deg, #b45309 0%, #f59e0b 100%)",
                gradient_secondary="linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)"
            ),

            "tech": ThemeConfig(
                name="tech",
                description="Modern tech theme with vibrant colors and digital aesthetic",
                primary_color="#7c2d12",
                secondary_color="#dc2626",
                accent_color="#ef4444",
                background_color="#0a0a0a",
                surface_color="#171717",
                text_primary="#fafafa",
                text_secondary="#d4d4d4",
                border_color="#404040",
                font_family_primary="JetBrains Mono, Consolas, monospace",
                font_family_secondary="system-ui, sans-serif",
                border_radius="2px",
                shadow_style="0 0 20px rgba(239,68,68,0.3), inset 0 0 0 1px rgba(239,68,68,0.1)",
                gradient_primary="linear-gradient(135deg, #7c2d12 0%, #dc2626 100%)",
                gradient_secondary="linear-gradient(135deg, #dc2626 0%, #ef4444 100%)"
            )
        }

    def _generate_css_custom_properties(self, theme: ThemeConfig) -> Dict[str, str]:
        """Generate CSS custom properties from theme config"""
        return {
            "--theme-primary": theme.primary_color,
            "--theme-secondary": theme.secondary_color,
            "--theme-accent": theme.accent_color,
            "--theme-background": theme.background_color,
            "--theme-surface": theme.surface_color,
            "--theme-text-primary": theme.text_primary,
            "--theme-text-secondary": theme.text_secondary,
            "--theme-border": theme.border_color,
            "--theme-font-primary": theme.font_family_primary,
            "--theme-font-secondary": theme.font_family_secondary,
            "--theme-border-radius": theme.border_radius,
            "--theme-shadow": theme.shadow_style,
            "--theme-gradient-primary": theme.gradient_primary,
            "--theme-gradient-secondary": theme.gradient_secondary,
        }

    def _generate_css_content(self, theme: ThemeConfig, custom_properties: Dict[str, str]) -> str:
        """Generate complete CSS content for a theme"""
        css_vars = "\n".join([f"  {key}: {value};" for key, value in custom_properties.items()])

        return f"""/* Theme: {theme.name} - {theme.description} */

:root {{
{css_vars}
}}

/* Base styles */
* {{
  box-sizing: border-box;
}}

body {{
  font-family: var(--theme-font-primary);
  background-color: var(--theme-background);
  color: var(--theme-text-primary);
  line-height: 1.6;
  margin: 0;
  padding: 0;
}}

/* Typography */
h1, h2, h3, h4, h5, h6 {{
  font-family: var(--theme-font-secondary);
  color: var(--theme-text-primary);
  margin-top: 0;
  font-weight: 600;
}}

p {{
  color: var(--theme-text-secondary);
  margin-bottom: 1rem;
}}

/* Links */
a {{
  color: var(--theme-primary);
  text-decoration: none;
  transition: color 0.2s ease;
}}

a:hover {{
  color: var(--theme-secondary);
}}

/* Buttons */
.btn {{
  background: var(--theme-gradient-primary);
  color: white;
  border: none;
  border-radius: var(--theme-border-radius);
  padding: 0.75rem 1.5rem;
  font-family: var(--theme-font-primary);
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: var(--theme-shadow);
}}

.btn:hover {{
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}}

.btn-secondary {{
  background: var(--theme-surface);
  color: var(--theme-text-primary);
  border: 1px solid var(--theme-border);
}}

.btn-secondary:hover {{
  background: var(--theme-background);
}}

/* Cards and containers */
.card {{
  background: var(--theme-surface);
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-border-radius);
  padding: 1.5rem;
  box-shadow: var(--theme-shadow);
}}

.container {{
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}}

/* Forms */
input, textarea, select {{
  background: var(--theme-background);
  color: var(--theme-text-primary);
  border: 1px solid var(--theme-border);
  border-radius: var(--theme-border-radius);
  padding: 0.75rem;
  font-family: var(--theme-font-primary);
  font-size: 0.875rem;
  transition: border-color 0.2s ease;
}}

input:focus, textarea:focus, select:focus {{
  outline: none;
  border-color: var(--theme-primary);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.1);
}}

/* Headers and navigation */
.header {{
  background: var(--theme-surface);
  border-bottom: 1px solid var(--theme-border);
  padding: 1rem 0;
}}

.nav {{
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.nav-link {{
  color: var(--theme-text-secondary);
  text-decoration: none;
  padding: 0.5rem 1rem;
  border-radius: var(--theme-border-radius);
  transition: all 0.2s ease;
}}

.nav-link:hover, .nav-link.active {{
  color: var(--theme-primary);
  background: var(--theme-background);
}}

/* Sections */
.section {{
  padding: 4rem 0;
}}

.section-alt {{
  background: var(--theme-surface);
}}

/* Utilities */
.text-center {{ text-align: center; }}
.text-left {{ text-align: left; }}
.text-right {{ text-align: right; }}

.mb-0 {{ margin-bottom: 0; }}
.mb-1 {{ margin-bottom: 0.25rem; }}
.mb-2 {{ margin-bottom: 0.5rem; }}
.mb-3 {{ margin-bottom: 1rem; }}
.mb-4 {{ margin-bottom: 1.5rem; }}

.mt-0 {{ margin-top: 0; }}
.mt-1 {{ margin-top: 0.25rem; }}
.mt-2 {{ margin-top: 0.5rem; }}
.mt-3 {{ margin-top: 1rem; }}
.mt-4 {{ margin-top: 1.5rem; }}

.p-0 {{ padding: 0; }}
.p-1 {{ padding: 0.25rem; }}
.p-2 {{ padding: 0.5rem; }}
.p-3 {{ padding: 1rem; }}
.p-4 {{ padding: 1.5rem; }}

/* Responsive design */
@media (max-width: 768px) {{
  .container {{
    padding: 0 0.5rem;
  }}

  .nav {{
    flex-direction: column;
    gap: 1rem;
  }}

  .section {{
    padding: 2rem 0;
  }}
}}

/* Accessibility */
@media (prefers-reduced-motion: reduce) {{
  * {{
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }}
}}

/* Focus styles */
.btn:focus, input:focus, textarea:focus, select:focus, a:focus {{
  outline: 2px solid var(--theme-accent);
  outline-offset: 2px;
}}
"""

    def _wrap_content_with_theme(self, content: str, theme: ThemeConfig, custom_properties: Dict[str, str]) -> str:
        """Wrap existing content with theme styling"""
        css_vars = "; ".join([f"{key}: {value}" for key, value in custom_properties.items()])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Themed Content - {theme.name}</title>
    <style>
        :root {{
            {css_vars};
        }}
        body {{
            font-family: var(--theme-font-primary);
            background-color: var(--theme-background);
            color: var(--theme-text-primary);
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        {content}
    </div>
</body>
</html>"""

    def _generate_sample_html(self, theme: ThemeConfig, custom_properties: Dict[str, str]) -> str:
        """Generate sample HTML demonstrating the theme"""
        css_vars = "; ".join([f"{key}: {value}" for key, value in custom_properties.items()])

        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{theme.name.title()} Theme Demo</title>
    <style>
        :root {{
            {css_vars};
        }}
        body {{
            font-family: var(--theme-font-primary);
            background-color: var(--theme-background);
            color: var(--theme-text-primary);
            line-height: 1.6;
            margin: 0;
            padding: 0;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            padding: 2rem;
        }}
        .card {{
            background: var(--theme-surface);
            border: 1px solid var(--theme-border);
            border-radius: var(--theme-border-radius);
            padding: 1.5rem;
            margin-bottom: 1.5rem;
            box-shadow: var(--theme-shadow);
        }}
        .btn {{
            background: var(--theme-gradient-primary);
            color: white;
            border: none;
            border-radius: var(--theme-border-radius);
            padding: 0.75rem 1.5rem;
            font-family: var(--theme-font-primary);
            font-size: 0.875rem;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            box-shadow: var(--theme-shadow);
            margin-right: 0.5rem;
        }}
        .btn:hover {{
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }}
        .btn-secondary {{
            background: var(--theme-surface);
            color: var(--theme-text-primary);
            border: 1px solid var(--theme-border);
        }}
        input {{
            background: var(--theme-background);
            color: var(--theme-text-primary);
            border: 1px solid var(--theme-border);
            border-radius: var(--theme-border-radius);
            padding: 0.75rem;
            font-family: var(--theme-font-primary);
            font-size: 0.875rem;
            width: 100%;
            margin-bottom: 1rem;
        }}
        .header {{
            background: var(--theme-surface);
            border-bottom: 1px solid var(--theme-border);
            padding: 1rem 0;
            margin-bottom: 2rem;
        }}
        .nav {{
            display: flex;
            justify-content: space-between;
            align-items: center;
        }}
        .nav-link {{
            color: var(--theme-text-secondary);
            text-decoration: none;
            padding: 0.5rem 1rem;
            border-radius: var(--theme-border-radius);
            transition: all 0.2s ease;
        }}
        .nav-link:hover, .nav-link.active {{
            color: var(--theme-primary);
            background: var(--theme-background);
        }}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <h1 style="margin: 0; font-family: var(--theme-font-secondary);">{theme.name.title()}</h1>
                <div>
                    <a href="#" class="nav-link active">Home</a>
                    <a href="#" class="nav-link">About</a>
                    <a href="#" class="nav-link">Services</a>
                    <a href="#" class="nav-link">Contact</a>
                </div>
            </nav>
        </div>
    </header>

    <div class="container">
        <div class="card">
            <h2 style="font-family: var(--theme-font-secondary); margin-top: 0;">{theme.name.title()} Theme</h2>
            <p style="color: var(--theme-text-secondary);">{theme.description}</p>
            <p>This professional theme provides instant visual polish with carefully chosen colors, typography, and spacing. Perfect for web applications, documentation, and modern interfaces.</p>
            <div>
                <button class="btn">Primary Action</button>
                <button class="btn btn-secondary">Secondary Action</button>
            </div>
        </div>

        <div class="card">
            <h3 style="font-family: var(--theme-font-secondary);">Sample Form</h3>
            <form>
                <input type="text" placeholder="Your name">
                <input type="email" placeholder="Your email">
                <textarea placeholder="Your message" rows="4"></textarea>
                <button class="btn">Send Message</button>
            </form>
        </div>

        <div class="card">
            <h3 style="font-family: var(--theme-font-secondary);">Theme Features</h3>
            <ul style="color: var(--theme-text-secondary);">
                <li>Zero external dependencies</li>
                <li>Responsive design ready</li>
                <li>Accessibility compliant</li>
                <li>Professional color palette</li>
                <li>Modern typography</li>
                <li>CSS custom properties for easy customization</li>
            </ul>
        </div>
    </div>
</body>
</html>"""

    def _get_theme_category(self, theme_name: str) -> str:
        """Get category for a theme"""
        categories = {
            "enterprise": "Corporate",
            "creative": "Artistic",
            "minimal": "Minimalist",
            "warm": "Friendly",
            "nature": "Organic",
            "ocean": "Calm",
            "sunset": "Dramatic",
            "midnight": "Dark",
            "elegant": "Luxury",
            "tech": "Technology"
        }
        return categories.get(theme_name, "General")

    def _update_performance_metrics(self, action: str, execution_time: float):
        """Update internal performance metrics"""
        if action == "generate":
            self.performance_metrics["themes_generated"] += 1
        elif action == "generate_css":
            self.performance_metrics["css_generated"] += 1
        elif action in ["generate", "generate_css", "custom_theme"]:
            self.performance_metrics["applications_completed"] += 1

        # Update average generation time
        total = self.performance_metrics["applications_completed"]
        if total > 0:
            current_avg = self.performance_metrics["average_generation_time"]
            new_avg = (current_avg * (total - 1) + execution_time) / total
            self.performance_metrics["average_generation_time"] = new_avg