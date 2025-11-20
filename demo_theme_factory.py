#!/usr/bin/env python3
"""
Theme Factory Demonstration

Showcases the Theme Factory skill with all 10 professional themes.
Generates sample HTML files for manual review and testing.
"""

import tempfile
import os
import json
from pathlib import Path


# Theme definitions (all 10 professional themes)
THEMES = {
    "enterprise": {
        "name": "enterprise",
        "description": "Professional corporate theme with blue accents and clean design",
        "primary_color": "#1e40af",
        "secondary_color": "#3b82f6",
        "accent_color": "#60a5fa",
        "background_color": "#ffffff",
        "surface_color": "#f8fafc",
        "text_primary": "#1e293b",
        "text_secondary": "#64748b",
        "border_color": "#e2e8f0",
        "font_family_primary": "Inter, system-ui, sans-serif",
        "font_family_secondary": "Inter, system-ui, sans-serif",
        "border_radius": "6px",
        "shadow_style": "0 1px 3px rgba(0,0,0,0.12), 0 1px 2px rgba(0,0,0,0.24)",
        "gradient_primary": "linear-gradient(135deg, #1e40af 0%, #3b82f6 100%)",
        "gradient_secondary": "linear-gradient(135deg, #3b82f6 0%, #60a5fa 100%)"
    },
    "creative": {
        "name": "creative",
        "description": "Vibrant artistic theme with purple gradients and bold typography",
        "primary_color": "#7c3aed",
        "secondary_color": "#a78bfa",
        "accent_color": "#c4b5fd",
        "background_color": "#fefefe",
        "surface_color": "#faf5ff",
        "text_primary": "#1f1f1f",
        "text_secondary": "#6b7280",
        "border_color": "#e9d5ff",
        "font_family_primary": "Calistoga, Georgia, serif",
        "font_family_secondary": "Inter, system-ui, sans-serif",
        "border_radius": "12px",
        "shadow_style": "0 4px 12px rgba(124,58,237,0.15)",
        "gradient_primary": "linear-gradient(135deg, #7c3aed 0%, #a78bfa 100%)",
        "gradient_secondary": "linear-gradient(135deg, #a78bfa 0%, #c4b5fd 100%)"
    },
    "minimal": {
        "name": "minimal",
        "description": "Clean minimalist theme with subtle grays and sharp typography",
        "primary_color": "#171717",
        "secondary_color": "#404040",
        "accent_color": "#737373",
        "background_color": "#ffffff",
        "surface_color": "#fafafa",
        "text_primary": "#171717",
        "text_secondary": "#737373",
        "border_color": "#e5e5e5",
        "font_family_primary": "system-ui, -apple-system, sans-serif",
        "font_family_secondary": "system-ui, -apple-system, sans-serif",
        "border_radius": "4px",
        "shadow_style": "0 1px 2px rgba(0,0,0,0.05)",
        "gradient_primary": "linear-gradient(135deg, #171717 0%, #404040 100%)",
        "gradient_secondary": "linear-gradient(135deg, #404040 0%, #737373 100%)"
    },
    "warm": {
        "name": "warm",
        "description": "Cozy warm theme with orange accents and friendly colors",
        "primary_color": "#ea580c",
        "secondary_color": "#fb923c",
        "accent_color": "#fed7aa",
        "background_color": "#fff7ed",
        "surface_color": "#fed7aa",
        "text_primary": "#1c1917",
        "text_secondary": "#78716c",
        "border_color": "#fdba74",
        "font_family_primary": "system-ui, sans-serif",
        "font_family_secondary": "Georgia, serif",
        "border_radius": "8px",
        "shadow_style": "0 2px 8px rgba(234,88,12,0.15)",
        "gradient_primary": "linear-gradient(135deg, #ea580c 0%, #fb923c 100%)",
        "gradient_secondary": "linear-gradient(135deg, #fb923c 0%, #fed7aa 100%)"
    },
    "nature": {
        "name": "nature",
        "description": "Fresh nature-inspired theme with green tones and organic feel",
        "primary_color": "#059669",
        "secondary_color": "#10b981",
        "accent_color": "#34d399",
        "background_color": "#ecfdf5",
        "surface_color": "#d1fae5",
        "text_primary": "#064e3b",
        "text_secondary": "#6b7280",
        "border_color": "#a7f3d0",
        "font_family_primary": "system-ui, sans-serif",
        "font_family_secondary": "Georgia, serif",
        "border_radius": "6px",
        "shadow_style": "0 2px 8px rgba(5,150,105,0.1)",
        "gradient_primary": "linear-gradient(135deg, #059669 0%, #10b981 100%)",
        "gradient_secondary": "linear-gradient(135deg, #10b981 0%, #34d399 100%)"
    },
    "ocean": {
        "name": "ocean",
        "description": "Calm ocean theme with blue gradients and serene atmosphere",
        "primary_color": "#0c4a6e",
        "secondary_color": "#0284c7",
        "accent_color": "#0ea5e9",
        "background_color": "#f0f9ff",
        "surface_color": "#e0f2fe",
        "text_primary": "#0c4a6e",
        "text_secondary": "#64748b",
        "border_color": "#bae6fd",
        "font_family_primary": "system-ui, sans-serif",
        "font_family_secondary": "Inter, system-ui, sans-serif",
        "border_radius": "8px",
        "shadow_style": "0 2px 8px rgba(12,74,110,0.1)",
        "gradient_primary": "linear-gradient(135deg, #0c4a6e 0%, #0284c7 100%)",
        "gradient_secondary": "linear-gradient(135deg, #0284c7 0%, #0ea5e9 100%)"
    },
    "sunset": {
        "name": "sunset",
        "description": "Dramatic sunset theme with warm gradients and romantic colors",
        "primary_color": "#dc2626",
        "secondary_color": "#f97316",
        "accent_color": "#fb923c",
        "background_color": "#fff7ed",
        "surface_color": "#fed7aa",
        "text_primary": "#7c2d12",
        "text_secondary": "#92400e",
        "border_color": "#fdba74",
        "font_family_primary": "Georgia, serif",
        "font_family_secondary": "system-ui, sans-serif",
        "border_radius": "12px",
        "shadow_style": "0 4px 12px rgba(220,38,38,0.15)",
        "gradient_primary": "linear-gradient(135deg, #dc2626 0%, #f97316 100%)",
        "gradient_secondary": "linear-gradient(135deg, #f97316 0%, #fb923c 100%)"
    },
    "midnight": {
        "name": "midnight",
        "description": "Dark professional theme with deep blues and subtle accents",
        "primary_color": "#1e293b",
        "secondary_color": "#334155",
        "accent_color": "#64748b",
        "background_color": "#0f172a",
        "surface_color": "#1e293b",
        "text_primary": "#f1f5f9",
        "text_secondary": "#cbd5e1",
        "border_color": "#334155",
        "font_family_primary": "Inter, system-ui, sans-serif",
        "font_family_secondary": "system-ui, sans-serif",
        "border_radius": "8px",
        "shadow_style": "0 2px 8px rgba(0,0,0,0.3)",
        "gradient_primary": "linear-gradient(135deg, #1e293b 0%, #334155 100%)",
        "gradient_secondary": "linear-gradient(135deg, #334155 0%, #64748b 100%)"
    },
    "elegant": {
        "name": "elegant",
        "description": "Sophisticated theme with gold accents and luxury feel",
        "primary_color": "#b45309",
        "secondary_color": "#f59e0b",
        "accent_color": "#fbbf24",
        "background_color": "#fffbeb",
        "surface_color": "#fef3c7",
        "text_primary": "#451a03",
        "text_secondary": "#78350f",
        "border_color": "#fde68a",
        "font_family_primary": "Playfair Display, Georgia, serif",
        "font_family_secondary": "Inter, system-ui, sans-serif",
        "border_radius": "4px",
        "shadow_style": "0 2px 8px rgba(180,83,9,0.1)",
        "gradient_primary": "linear-gradient(135deg, #b45309 0%, #f59e0b 100%)",
        "gradient_secondary": "linear-gradient(135deg, #f59e0b 0%, #fbbf24 100%)"
    },
    "tech": {
        "name": "tech",
        "description": "Modern tech theme with vibrant colors and digital aesthetic",
        "primary_color": "#7c2d12",
        "secondary_color": "#dc2626",
        "accent_color": "#ef4444",
        "background_color": "#0a0a0a",
        "surface_color": "#171717",
        "text_primary": "#fafafa",
        "text_secondary": "#d4d4d4",
        "border_color": "#404040",
        "font_family_primary": "JetBrains Mono, Consolas, monospace",
        "font_family_secondary": "system-ui, sans-serif",
        "border_radius": "2px",
        "shadow_style": "0 0 20px rgba(239,68,68,0.3), inset 0 0 0 1px rgba(239,68,68,0.1)",
        "gradient_primary": "linear-gradient(135deg, #7c2d12 0%, #dc2626 100%)",
        "gradient_secondary": "linear-gradient(135deg, #dc2626 0%, #ef4444 100%)"
    }
}


def generate_css(theme_data):
    """Generate CSS for a theme"""
    custom_props = {
        "--theme-primary": theme_data["primary_color"],
        "--theme-secondary": theme_data["secondary_color"],
        "--theme-accent": theme_data["accent_color"],
        "--theme-background": theme_data["background_color"],
        "--theme-surface": theme_data["surface_color"],
        "--theme-text-primary": theme_data["text_primary"],
        "--theme-text-secondary": theme_data["text_secondary"],
        "--theme-border": theme_data["border_color"],
        "--theme-font-primary": theme_data["font_family_primary"],
        "--theme-font-secondary": theme_data["font_family_secondary"],
        "--theme-border-radius": theme_data["border_radius"],
        "--theme-shadow": theme_data["shadow_style"],
        "--theme-gradient-primary": theme_data["gradient_primary"],
        "--theme-gradient-secondary": theme_data["gradient_secondary"],
    }

    css_vars = "\n".join([f"  {key}: {value};" for key, value in custom_props.items()])

    return f"""/* Theme: {theme_data['name']} - {theme_data['description']} */

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
  margin-bottom: 1.5rem;
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
  width: 100%;
  margin-bottom: 1rem;
}}

input:focus, textarea:focus, select:focus {{
  outline: none;
  border-color: var(--theme-primary);
  box-shadow: 0 0 0 3px rgba(124,58,237,0.1);
}}

/* Header and navigation */
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

/* Grid layout */
.grid {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-bottom: 2rem;
}}

/* Badges */
.badge {{
  display: inline-block;
  padding: 0.25rem 0.5rem;
  background: var(--theme-primary);
  color: white;
  border-radius: var(--theme-border-radius);
  font-size: 0.75rem;
  font-weight: 500;
  margin-right: 0.5rem;
}}

/* Code */
code {{
  background: var(--theme-surface);
  padding: 0.2rem 0.4rem;
  border-radius: var(--theme-border-radius);
  font-family: monospace;
  font-size: 0.875rem;
}}

/* Responsive design */
@media (max-width: 768px) {{
  .container {{
    padding: 0 0.5rem;
  }}

  .nav {{
    flex-direction: column;
    gap: 1rem;
  }}

  .grid {{
    grid-template-columns: 1fr;
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


def generate_demo_html(theme_name, theme_data, css_content):
    """Generate demo HTML for a theme"""
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{theme_name.title()} Theme Demo</title>
    <style>
{css_content}
    </style>
</head>
<body>
    <header class="header">
        <div class="container">
            <nav class="nav">
                <h1 style="margin: 0; font-family: var(--theme-font-secondary);">{theme_name.title()}</h1>
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
            <h2>{theme_name.title()} Theme</h2>
            <p><strong>{theme_data['description']}</strong></p>
            <p>This professional theme provides instant visual polish with carefully chosen colors, typography, and spacing. Perfect for web applications, documentation, and modern interfaces.</p>
            <div style="margin-bottom: 1rem;">
                <span class="badge">Primary: {theme_data['primary_color']}</span>
                <span class="badge">Secondary: {theme_data['secondary_color']}</span>
                <span class="badge">Font: {theme_data['font_family_primary'].split(',')[0]}</span>
            </div>
            <div>
                <button class="btn">Primary Action</button>
                <button class="btn btn-secondary">Secondary Action</button>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <h3>Sample Form</h3>
                <form>
                    <input type="text" placeholder="Your name">
                    <input type="email" placeholder="Your email">
                    <textarea placeholder="Your message" rows="4"></textarea>
                    <button class="btn">Send Message</button>
                </form>
            </div>

            <div class="card">
                <h3>Typography</h3>
                <p><strong>Heading:</strong> <h4 style="margin: 0.5rem 0;">This is a heading</h4></p>
                <p><strong>Paragraph:</strong> This is a paragraph with <code>inline code</code> and <a href="#">links</a>.</p>
                <p><strong>Badges:</strong></p>
                <div>
                    <span class="badge">Success</span>
                    <span class="badge">Warning</span>
                    <span class="badge">Error</span>
                </div>
            </div>

            <div class="card">
                <h3>Theme Features</h3>
                <ul style="color: var(--theme-text-secondary);">
                    <li>Zero external dependencies</li>
                    <li>Responsive design ready</li>
                    <li>Accessibility compliant</li>
                    <li>Professional color palette</li>
                    <li>Modern typography</li>
                    <li>CSS custom properties for easy customization</li>
                </ul>
            </div>

            <div class="card">
                <h3>Technical Details</h3>
                <p style="color: var(--theme-text-secondary);">
                    <strong>Background:</strong> {theme_data['background_color']}<br>
                    <strong>Surface:</strong> {theme_data['surface_color']}<br>
                    <strong>Border Radius:</strong> {theme_data['border_radius']}<br>
                    <strong>Shadow:</strong> {theme_data['shadow_style']}
                </p>
            </div>
        </div>

        <div class="card">
            <h3>Color Palette</h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(150px, 1fr)); gap: 1rem;">
                <div style="padding: 1rem; background: var(--theme-primary); color: white; border-radius: var(--theme-border-radius); text-align: center;">
                    <strong>Primary</strong><br>
                    {theme_data['primary_color']}
                </div>
                <div style="padding: 1rem; background: var(--theme-secondary); color: white; border-radius: var(--theme-border-radius); text-align: center;">
                    <strong>Secondary</strong><br>
                    {theme_data['secondary_color']}
                </div>
                <div style="padding: 1rem; background: var(--theme-accent); color: white; border-radius: var(--theme-border-radius); text-align: center;">
                    <strong>Accent</strong><br>
                    {theme_data['accent_color']}
                </div>
                <div style="padding: 1rem; background: var(--theme-surface); color: var(--theme-text-primary); border-radius: var(--theme-border-radius); text-align: center; border: 1px solid var(--theme-border);">
                    <strong>Surface</strong><br>
                    {theme_data['surface_color']}
                </div>
            </div>
        </div>
    </div>
</body>
</html>"""


def create_theme_gallery():
    """Create a gallery page showing all themes"""
    gallery_html = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Theme Factory Gallery - 10 Professional Themes</title>
    <style>
        body {
            font-family: system-ui, -apple-system, sans-serif;
            background: #f8fafc;
            color: #1e293b;
            line-height: 1.6;
            margin: 0;
            padding: 2rem;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        h1 {
            text-align: center;
            margin-bottom: 3rem;
            font-size: 2.5rem;
            color: #1e40af;
        }
        .grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 2rem;
            margin-bottom: 3rem;
        }
        .theme-card {
            background: white;
            border-radius: 12px;
            padding: 2rem;
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            transition: transform 0.2s ease;
        }
        .theme-card:hover {
            transform: translateY(-4px);
        }
        .theme-name {
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.5rem;
            color: #1e293b;
        }
        .theme-description {
            color: #64748b;
            margin-bottom: 1.5rem;
        }
        .color-preview {
            display: flex;
            gap: 0.5rem;
            margin-bottom: 1.5rem;
        }
        .color-dot {
            width: 40px;
            height: 40px;
            border-radius: 8px;
            border: 2px solid #e2e8f0;
        }
        .demo-button {
            display: inline-block;
            background: linear-gradient(135deg, #3b82f6 0%, #1e40af 100%);
            color: white;
            text-decoration: none;
            padding: 0.75rem 1.5rem;
            border-radius: 8px;
            font-weight: 500;
            transition: all 0.2s ease;
        }
        .demo-button:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(59,130,246,0.4);
        }
        .features {
            display: flex;
            flex-wrap: wrap;
            gap: 0.5rem;
            margin-bottom: 1rem;
        }
        .feature-tag {
            background: #f1f5f9;
            color: #475569;
            padding: 0.25rem 0.5rem;
            border-radius: 4px;
            font-size: 0.75rem;
        }
        .footer {
            text-align: center;
            color: #64748b;
            margin-top: 3rem;
            padding-top: 2rem;
            border-top: 1px solid #e2e8f0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎨 Theme Factory Gallery</h1>
        <p style="text-align: center; color: #64748b; font-size: 1.25rem; margin-bottom: 3rem;">
            10 professional themes for immediate visual polish. Zero external dependencies.
        </p>

        <div class="grid">
"""

    # Add theme cards
    theme_files = []
    for theme_name, theme_data in THEMES.items():
        # Generate individual theme demo
        css_content = generate_css(theme_data)
        html_content = generate_demo_html(theme_name, theme_data, css_content)

        # Save individual theme file
        with tempfile.NamedTemporaryFile(mode='w', suffix=f'_{theme_name}.html', delete=False) as f:
            f.write(html_content)
            theme_files.append((theme_name, f.name))

        # Add to gallery
        colors = [
            theme_data["primary_color"],
            theme_data["secondary_color"],
            theme_data["accent_color"]
        ]

        color_dots = ""
        for color in colors:
            color_dots += f'<div class="color-dot" style="background: {color};" title="{color}"></div>'

        # Determine features
        features = []
        if "blue" in theme_data["description"].lower():
            features.append("Professional")
        if "dark" in theme_name or theme_data["background_color"] == "#0a0a0a":
            features.append("Dark Mode")
        if "gradient" in theme_data["description"].lower():
            features.append("Gradients")
        if "serif" in theme_data["font_family_primary"]:
            features.append("Typography")
        if "eco" in theme_name.lower() or "nature" in theme_name.lower():
            features.append("Eco-Friendly")

        feature_tags = ""
        for feature in features:
            feature_tags += f'<span class="feature-tag">{feature}</span>'

        gallery_html += f"""
            <div class="theme-card">
                <div class="theme-name">{theme_name.title()}</div>
                <div class="theme-description">{theme_data['description']}</div>
                <div class="color-preview">
                    {color_dots}
                </div>
                <div class="features">
                    {feature_tags}
                </div>
                <div>
                    <a href="{theme_files[-1][1]}" class="demo-button" target="_blank">View Demo</a>
                </div>
            </div>
        """

    gallery_html += f"""
        </div>

        <div class="footer">
            <p><strong>Theme Factory Skill</strong> - Professional theme generation and application system</p>
            <p>Zero dependencies • Accessible • Responsive • Production-ready</p>
            <p style="margin-top: 1rem;">
                <small>Generated {len(theme_files)} theme demos • Open each demo in a new tab to explore</small>
            </p>
        </div>
    </div>
</body>
</html>"""

    # Save gallery
    with tempfile.NamedTemporaryFile(mode='w', suffix='_gallery.html', delete=False) as f:
        f.write(gallery_html)
        gallery_file = f.name

    print(f"🎨 Theme Factory Gallery Generated!")
    print(f"📁 Gallery: {gallery_file}")
    print(f"📂 Individual themes:")
    for theme_name, file_path in theme_files:
        print(f"   - {theme_name.title()}: {file_path}")

    return gallery_file, theme_files


def main():
    """Main demonstration"""
    print("🎨 Theme Factory Demonstration")
    print("=" * 50)
    print("Generating 10 professional themes with zero dependencies...")

    # Create theme gallery
    gallery_file, theme_files = create_theme_gallery()

    print(f"\n✅ Generated {len(theme_files)} theme demos")
    print(f"\n🚀 Available themes:")
    for theme_name in THEMES:
        print(f"   - {theme_name.title()}: {THEMES[theme_name]['description']}")

    print(f"\n📋 Theme Categories:")
    categories = {
        "Corporate": ["enterprise"],
        "Creative": ["creative", "elegant"],
        "Minimalist": ["minimal"],
        "Friendly": ["warm", "nature"],
        "Dramatic": ["sunset"],
        "Professional": ["ocean"],
        "Dark Mode": ["midnight", "tech"]
    }

    for category, theme_list in categories.items():
        themes_str = ", ".join([t.title() for t in theme_list])
        print(f"   {category}: {themes_str}")

    print(f"\n🌟 Key Features:")
    print(f"   • Zero external dependencies")
    print(f"   • Professional color palettes")
    print(f"   • Responsive design ready")
    print(f"   • Accessibility compliant")
    print(f"   • CSS custom properties")
    print(f"   • Modern typography")

    print(f"\n📖 Usage:")
    print(f"   1. Open gallery to see all themes: {gallery_file}")
    print(f"   2. Click individual theme links to see demos")
    print(f"   3. Copy CSS from generated files")
    print(f"   4. Apply to your own projects")

    print(f"\n💡 Integration with Amplifier:")
    print(f"   The ThemeFactorySkill provides programmatic access to these themes")
    print(f"   Use 'amplifier.skills.ThemeFactorySkill' to integrate in your code")

    return gallery_file


if __name__ == "__main__":
    gallery_file = main()
    print(f"\n🎉 Theme Factory demonstration complete!")
    print(f"📊 View the gallery: {gallery_file}")