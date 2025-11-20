"""
Tailwind CSS Performance Optimization Module

Comprehensive performance analysis, optimization strategies, and
bundle management for Tailwind CSS applications.
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any

from ..quality_assurance.validators.zero_hallucination_validator import ZeroHallucinationValidator


class PerformanceLevel(Enum):
    """Performance impact levels."""

    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    NEGLIGIBLE = "negligible"


@dataclass
class CSSClass:
    """Represents a Tailwind CSS class with performance data."""

    class_name: str
    category: str
    file_size_impact: int  # bytes
    render_cost: PerformanceLevel
    unused_probability: float  # 0.0 to 1.0
    alternatives: list[str]


@dataclass
class BundleAnalysis:
    """Analysis of CSS bundle performance."""

    total_size: int  # bytes
    gzipped_size: int  # bytes
    unused_classes: list[str]
    duplicate_classes: list[str]
    heavy_classes: list[CSSClass]
    optimization_potential: float  # percentage
    purge_efficiency: float  # percentage


@dataclass
class PerformanceMetrics:
    """Performance metrics for Tailwind CSS usage."""

    bundle_size_impact: int
    unused_classes_count: int
    render_performance_score: int  # 0-100
    critical_render_path: list[str]
    optimization_recommendations: list[str]
    estimated_improvements: dict[str, float]


class TailwindPerformanceOptimizer:
    """
    Comprehensive Tailwind CSS performance optimization system.

    Features:
    - Bundle size analysis and optimization
    - JIT compilation optimization
    - PurgeCSS configuration tuning
    - Runtime performance analysis
    - Critical CSS extraction
    - Rendering performance monitoring
    """

    def __init__(self):
        self.validator = ZeroHallucinationValidator(strict_mode=True)

        # Initialize performance data
        self._init_class_performance_data()
        self._init_optimization_strategies()
        self._init_performance_patterns()

        # Performance tracking
        self.optimization_history = []
        self.benchmark_data = {}

    def _init_class_performance_data(self):
        """Initialize performance data for common Tailwind classes."""
        self.class_performance = {
            # Heavy classes (high bundle impact)
            "custom_animation": CSSClass(
                class_name="custom_animation",
                category="animation",
                file_size_impact=200,
                render_cost=PerformanceLevel.HIGH,
                unused_probability=0.3,
                alternatives=["transition", "transform"],
            ),
            "backdrop_filter": CSSClass(
                class_name="backdrop-filter",
                category="effects",
                file_size_impact=150,
                render_cost=PerformanceLevel.HIGH,
                unused_probability=0.4,
                alternatives=["opacity", "background"],
            ),
            "grid_complex": CSSClass(
                class_name="grid-cols-12",
                category="layout",
                file_size_impact=120,
                render_cost=PerformanceLevel.MEDIUM,
                unused_probability=0.2,
                alternatives=["grid-cols-6", "flex"],
            ),
            # Medium impact classes
            "transform_complex": CSSClass(
                class_name="transform-gpu",
                category="transform",
                file_size_impact=80,
                render_cost=PerformanceLevel.MEDIUM,
                unused_probability=0.15,
                alternatives=["transform"],
            ),
            "filter_complex": CSSClass(
                class_name="filter",
                category="effects",
                file_size_impact=90,
                render_cost=PerformanceLevel.MEDIUM,
                unused_probability=0.25,
                alternatives=["opacity", "brightness"],
            ),
            # Low impact classes
            "spacing_basic": CSSClass(
                class_name="p-4",
                category="spacing",
                file_size_impact=20,
                render_cost=PerformanceLevel.NEGLIGIBLE,
                unused_probability=0.1,
                alternatives=[],
            ),
            "color_basic": CSSClass(
                class_name="text-blue-500",
                category="color",
                file_size_impact=25,
                render_cost=PerformanceLevel.NEGLIGIBLE,
                unused_probability=0.1,
                alternatives=[],
            ),
        }

        # Performance cost categories
        self.performance_costs = {
            PerformanceLevel.CRITICAL: {
                "description": "Significant performance impact",
                "recommendation": "Replace or remove immediately",
            },
            PerformanceLevel.HIGH: {
                "description": "Notable performance impact",
                "recommendation": "Optimize or find alternatives",
            },
            PerformanceLevel.MEDIUM: {
                "description": "Moderate performance impact",
                "recommendation": "Consider optimization",
            },
            PerformanceLevel.LOW: {"description": "Minimal performance impact", "recommendation": "Monitor usage"},
            PerformanceLevel.NEGLIGIBLE: {"description": "No performance impact", "recommendation": "No action needed"},
        }

    def _init_optimization_strategies(self):
        """Initialize comprehensive optimization strategies."""
        self.optimization_strategies = {
            "bundle_size": {
                "jit_compilation": {
                    "description": "Just-In-Time compilation for 10x smaller bundles",
                    "implementation": "mode: 'jit' in tailwind.config.js",
                    "savings": "80-90%",
                    "priority": "critical",
                },
                "purge_configuration": {
                    "description": "Accurate content path configuration",
                    "implementation": "Configure all template paths in purge array",
                    "savings": "30-60%",
                    "priority": "critical",
                },
                "tree_shaking": {
                    "description": "Remove unused utilities and components",
                    "implementation": "Enable CSS tree shaking in build tools",
                    "savings": "20-40%",
                    "priority": "high",
                },
                "css_minification": {
                    "description": "Minify CSS in production builds",
                    "implementation": "Use PostCSS minification plugins",
                    "savings": "15-25%",
                    "priority": "medium",
                },
                "gzip_compression": {
                    "description": "Enable gzip/brotli compression",
                    "implementation": "Server-side compression configuration",
                    "savings": "70-85%",
                    "priority": "high",
                },
            },
            "render_performance": {
                "gpu_acceleration": {
                    "description": "Push animations to GPU",
                    "implementation": "Use transform/opacity for animations",
                    "savings": "50-70% animation time",
                    "priority": "high",
                },
                "css_containment": {
                    "description": "Isolate layout recalculations",
                    "implementation": "Apply contain property strategically",
                    "savings": "20-40% layout time",
                    "priority": "medium",
                },
                "will_change_optimization": {
                    "description": "Optimize complex animations",
                    "implementation": "Use will-change property sparingly",
                    "savings": "30-50% animation time",
                    "priority": "medium",
                },
                "critical_css": {
                    "description": "Inline critical CSS",
                    "implementation": "Extract and inline above-fold CSS",
                    "savings": "40-60% render time",
                    "priority": "high",
                },
            },
            "loading_performance": {
                "lazy_loading": {
                    "description": "Lazy load non-critical CSS",
                    "implementation": "Split CSS into chunks",
                    "savings": "30-50% initial load",
                    "priority": "high",
                },
                "font_optimization": {
                    "description": "Optimize web font loading",
                    "implementation": "font-display: swap, preload critical fonts",
                    "savings": "20-40% font load time",
                    "priority": "medium",
                },
                "resource_hints": {
                    "description": "Use preload/prefetch strategically",
                    "implementation": "Add resource hints to HTML head",
                    "savings": "10-20% resource load time",
                    "priority": "low",
                },
            },
        }

    def _init_performance_patterns(self):
        """Initialize performance monitoring patterns."""
        self.performance_patterns = {
            "critical_render_path": [
                "Above-the-fold content",
                "Hero sections",
                "Primary navigation",
                "Call-to-action buttons",
            ],
            "heavy_selectors": [
                "Complex nth-child selectors",
                "Universal selectors",
                "Deep descendant selectors",
                "Attribute selectors with regex",
            ],
            "expensive_properties": [
                "box-shadow (large/blurry)",
                "filter (blur, grayscale)",
                "border-radius (large values)",
                "transform (complex 3d)",
                "animation (keyframes)",
                "backdrop-filter",
            ],
            "layout_triggers": [
                "Width/height changes",
                "Padding/margin changes",
                "Border changes",
                "Font size changes",
            ],
        }

    def analyze_css_bundle(self, css_content: str, project_path: str) -> BundleAnalysis:
        """
        Analyze CSS bundle for performance issues.

        Args:
            css_content: CSS content to analyze
            project_path: Path to project for context

        Returns:
            Comprehensive bundle analysis
        """
        # Extract class names from CSS
        class_pattern = r"\.([a-zA-Z0-9_-]+)"
        found_classes = re.findall(class_pattern, css_content)

        # Analyze class usage and performance
        total_size = len(css_content.encode("utf-8"))

        # Simulate gzipped size (rough estimate)
        gzipped_size = int(total_size * 0.3)

        # Identify potentially unused classes (simplified)
        all_tailwind_classes = set()
        for class_info in self.class_performance.values():
            all_tailwind_classes.add(class_info.class_name)

        # Check for duplicates
        class_counts = {}
        for cls in found_classes:
            class_counts[cls] = class_counts.get(cls, 0) + 1

        duplicate_classes = [cls for cls, count in class_counts.items() if count > 1]

        # Identify heavy classes
        heavy_classes = []
        for cls in found_classes:
            if cls in [c.class_name for c in self.class_performance.values()]:
                class_info = next(c for c in self.class_performance.values() if c.class_name == cls)
                if class_info.file_size_impact > 50:
                    heavy_classes.append(class_info)

        # Calculate optimization potential
        optimization_potential = 0
        if heavy_classes:
            heavy_impact = sum(c.file_size_impact for c in heavy_classes)
            optimization_potential = (heavy_impact / total_size) * 100

        # Estimate purge efficiency
        purge_efficiency = max(0, 85 - (len(found_classes) / 1000 * 10))

        return BundleAnalysis(
            total_size=total_size,
            gzipped_size=gzipped_size,
            unused_classes=self._identify_unused_classes(found_classes, project_path),
            duplicate_classes=duplicate_classes,
            heavy_classes=heavy_classes,
            optimization_potential=optimization_potential,
            purge_efficiency=purge_efficiency,
        )

    def _identify_unused_classes(self, found_classes: list[str], project_path: str) -> list[str]:
        """Identify potentially unused CSS classes."""
        # This is a simplified implementation
        # In practice, you'd scan the project files for actual usage
        unused_classes = []

        # Common patterns that might indicate unused classes
        for cls in found_classes:
            # Check for classes that might be dynamically generated
            if any(pattern in cls for pattern in ["-", "_", "\\d"]):
                # More complex analysis needed here
                pass

        return unused_classes

    def optimize_tailwind_config(self, current_config: dict[str, Any]) -> dict[str, Any]:
        """
        Optimize Tailwind CSS configuration for better performance.

        Args:
            current_config: Current tailwind.config.js content

        Returns:
            Optimized configuration
        """
        optimized_config = current_config.copy()

        # Ensure JIT mode is enabled
        if optimized_config.get("mode") != "jit":
            optimized_config["mode"] = "jit"

        # Optimize purge configuration
        if "purge" not in optimized_config:
            optimized_config["purge"] = {
                "enabled": True,
                "content": ["./src/**/*.{html,js,jsx,ts,tsx,vue,svelte}", "./public/**/*.html"],
            }
        else:
            # Ensure enabled: true for production
            if isinstance(optimized_config["purge"], dict):
                optimized_config["purge"]["enabled"] = True
            elif isinstance(optimized_config["purge"], list):
                optimized_config["purge"] = {"enabled": True, "content": optimized_config["purge"]}

        # Add performance optimizations
        if "theme" not in optimized_config:
            optimized_config["theme"] = {}

        if "extend" not in optimized_config["theme"]:
            optimized_config["theme"]["extend"] = {}

        # Add performance-focused theme extensions
        optimized_config["theme"]["extend"].update(
            {
                # Optimize for faster transitions
                "transitionDuration": {"75": "75ms", "150": "150ms"},
                # Optimize animation performance
                "animation": {"fade-in": "fadeIn 0.15s ease-in-out", "slide-up": "slideUp 0.2s ease-out"},
                # Optimize keyframes for GPU acceleration
                "keyframes": {
                    "fadeIn": {"0%": {"opacity": "0"}, "100%": {"opacity": "1"}},
                    "slideUp": {
                        "0%": {"transform": "translateY(10px)", "opacity": "0"},
                        "100%": {"transform": "translateY(0)", "opacity": "1"},
                    },
                },
            }
        )

        # Add plugins for optimization
        if "plugins" not in optimized_config:
            optimized_config["plugins"] = []

        return optimized_config

    def generate_critical_css(self, html_content: str, css_content: str) -> str:
        """
        Generate critical CSS for above-the-fold content.

        Args:
            html_content: HTML content to analyze
            css_content: CSS content to extract from

        Returns:
            Critical CSS for above-the-fold content
        """
        # Extract classes used in above-the-fold content
        above_fold_pattern = r"<[^>]*>(.*?)</[^>]*>"

        # This is a simplified implementation
        # In practice, you'd use a proper critical CSS extractor

        # Find all classes in the HTML
        html_classes = re.findall(r'class="([^"]*)"', html_content)
        all_classes = set()
        for class_list in html_classes:
            all_classes.update(class_list.split())

        # Extract relevant CSS rules
        critical_css_lines = []
        for line in css_content.split("\n"):
            for cls in all_classes:
                if f".{cls}" in line:
                    critical_css_lines.append(line)
                    break

        return "\n".join(critical_css_lines)

    def optimize_render_performance(self, css_content: str) -> dict[str, Any]:
        """
        Analyze and optimize CSS render performance.

        Args:
            css_content: CSS content to analyze

        Returns:
            Performance optimization recommendations
        """
        optimization_result = {
            "issues_found": [],
            "recommendations": [],
            "performance_score": 100,
            "estimated_improvements": {},
        }

        # Check for expensive properties
        expensive_properties = self.performance_patterns["expensive_properties"]
        for prop in expensive_properties:
            if prop.lower().replace(" ", "-") in css_content.lower():
                optimization_result["issues_found"].append(f"Expensive property detected: {prop}")
                optimization_result["performance_score"] -= 10

        # Check for heavy selectors
        if ":nth-child(" in css_content:
            optimization_result["issues_found"].append("Complex nth-child selectors found")
            optimization_result["performance_score"] -= 5
            optimization_result["recommendations"].append("Consider simplifying nth-child selectors")

        # Check for box-shadow performance
        box_shadow_count = css_content.count("box-shadow")
        if box_shadow_count > 10:
            optimization_result["issues_found"].append(f"Many box-shadows found ({box_shadow_count})")
            optimization_result["performance_score"] -= 8
            optimization_result["recommendations"].append("Consider using CSS containment for shadows")

        # Generate specific recommendations
        if "transform:" in css_content and "translateZ(0)" not in css_content:
            optimization_result["recommendations"].append(
                "Add transform: translateZ(0) or will-change: transform for GPU acceleration"
            )
            optimization_result["estimated_improvements"]["gpu_acceleration"] = 50

        if "animation:" in css_content and "transform" not in css_content:
            optimization_result["recommendations"].append("Use transform/opacity for animations to leverage GPU")
            optimization_result["estimated_improvements"]["animation_performance"] = 40

        # Calculate overall score
        optimization_result["performance_score"] = max(0, optimization_result["performance_score"])

        return optimization_result

    def generate_performance_report(self, project_path: str) -> dict[str, Any]:
        """
        Generate comprehensive performance report for a Tailwind CSS project.

        Args:
            project_path: Path to the project to analyze

        Returns:
            Complete performance report
        """
        report = {
            "project_path": project_path,
            "analysis_date": self._get_timestamp(),
            "bundle_analysis": None,
            "render_performance": None,
            "optimization_recommendations": [],
            "estimated_improvements": {},
            "priority_actions": [],
        }

        # Read CSS files
        css_files = self._find_css_files(project_path)
        total_css_content = ""

        for css_file in css_files:
            try:
                with open(css_file) as f:
                    total_css_content += f.read() + "\n"
            except Exception as e:
                report["optimization_recommendations"].append(f"Could not read {css_file}: {e}")

        if total_css_content:
            # Analyze bundle
            report["bundle_analysis"] = self.analyze_css_bundle(total_css_content, project_path)

            # Analyze render performance
            report["render_performance"] = self.optimize_render_performance(total_css_content)

            # Generate optimization recommendations
            report["optimization_recommendations"] = self._generate_optimization_recommendations(
                report["bundle_analysis"], report["render_performance"]
            )

            # Calculate estimated improvements
            report["estimated_improvements"] = self._calculate_improvements(report)

            # Generate priority actions
            report["priority_actions"] = self._generate_priority_actions(report)

        return report

    def _find_css_files(self, project_path: str) -> list[Path]:
        """Find all CSS files in the project."""
        project_dir = Path(project_path)
        css_files = []

        # Look for common CSS file patterns
        patterns = ["**/*.css", "**/output.css", "**/tailwind.css", "**/styles.css"]

        for pattern in patterns:
            css_files.extend(project_dir.glob(pattern))

        return css_files

    def _generate_optimization_recommendations(
        self, bundle_analysis: BundleAnalysis, render_performance: dict[str, Any]
    ) -> list[str]:
        """Generate specific optimization recommendations."""
        recommendations = []

        # Bundle size recommendations
        if bundle_analysis.optimization_potential > 20:
            recommendations.append(
                f"🔥 High optimization potential: {bundle_analysis.optimization_potential:.1f}% bundle size reduction possible"
            )

        if bundle_analysis.total_size > 50000:  # 50KB
            recommendations.append("📦 Large CSS bundle detected. Consider implementing:")
            recommendations.append("  - Enable JIT compilation mode")
            recommendations.append("  - Optimize PurgeCSS configuration")
            recommendations.append("  - Remove unused classes")

        if bundle_analysis.purge_efficiency < 70:
            recommendations.append(
                f"🧹 Low purge efficiency ({bundle_analysis.purge_efficiency:.1f}%). Review content paths configuration."
            )

        # Render performance recommendations
        if render_performance["performance_score"] < 80:
            recommendations.append("⚡ Render performance issues detected. Consider:")
            recommendations.extend([f"  - {rec}" for rec in render_performance["recommendations"]])

        # Heavy classes recommendations
        if bundle_analysis.heavy_classes:
            recommendations.append("🎨 Heavy CSS classes found:")
            for heavy_class in bundle_analysis.heavy_classes:
                if heavy_class.alternatives:
                    recommendations.append(
                        f"  - '{heavy_class.class_name}' → consider alternatives: {', '.join(heavy_class.alternatives)}"
                    )

        return recommendations

    def _calculate_improvements(self, report: dict[str, Any]) -> dict[str, float]:
        """Calculate estimated performance improvements."""
        improvements = {"bundle_size_reduction": 0, "render_time_improvement": 0, "load_time_improvement": 0}

        if report["bundle_analysis"]:
            # Bundle size improvements
            if report["bundle_analysis"].optimization_potential > 0:
                improvements["bundle_size_reduction"] = report["bundle_analysis"].optimization_potential

            # Critical CSS improvements
            improvements["load_time_improvement"] = min(50, report["bundle_analysis"].purge_efficiency * 0.5)

        if report["render_performance"]:
            # Render time improvements
            performance_score = report["render_performance"]["performance_score"]
            if performance_score < 100:
                improvements["render_time_improvement"] = (100 - performance_score) * 0.6

        return improvements

    def _generate_priority_actions(self, report: dict[str, Any]) -> list[dict[str, str]]:
        """Generate priority action items."""
        actions = []

        # Critical actions
        if report["bundle_analysis"] and report["bundle_analysis"].optimization_potential > 30:
            actions.append(
                {
                    "priority": "critical",
                    "action": "Enable JIT compilation mode",
                    "impact": f"Up to {report['bundle_analysis'].optimization_potential:.0f}% bundle size reduction",
                    "effort": "Low - Simple configuration change",
                }
            )

        if report["bundle_analysis"] and report["bundle_analysis"].total_size > 100000:  # 100KB
            actions.append(
                {
                    "priority": "critical",
                    "action": "Optimize PurgeCSS configuration",
                    "impact": "Significant bundle size reduction",
                    "effort": "Medium - Requires content path analysis",
                }
            )

        # High priority actions
        if report["render_performance"] and report["render_performance"]["performance_score"] < 70:
            actions.append(
                {
                    "priority": "high",
                    "action": "Optimize render performance",
                    "impact": "Improved animation and transition performance",
                    "effort": "Medium - Requires CSS refactoring",
                }
            )

        if report["estimated_improvements"].get("load_time_improvement", 0) > 20:
            actions.append(
                {
                    "priority": "high",
                    "action": "Implement critical CSS extraction",
                    "impact": f"{report['estimated_improvements']['load_time_improvement']:.0f}% faster page load",
                    "effort": "High - Requires build process changes",
                }
            )

        # Medium priority actions
        if report["bundle_analysis"] and report["bundle_analysis"].duplicate_classes:
            actions.append(
                {
                    "priority": "medium",
                    "action": "Remove duplicate CSS classes",
                    "impact": f"Clean up {len(report['bundle_analysis'].duplicate_classes)} duplicates",
                    "effort": "Low - Simple cleanup",
                }
            )

        return actions

    def create_optimized_postcss_config(self) -> str:
        """Create optimized PostCSS configuration."""
        config = """
module.exports = {
  plugins: {
    // Tailwind CSS (must be first)
    tailwindcss: {},

    // Autoprefixer for vendor prefixes
    autoprefixer: {
      grid: true,  // Enable grid autoprefixing
      flexbox: 'no-2009',  // Use modern flexbox syntax
    },

    // CSS optimization plugins (only in production)
    ...(process.env.NODE_ENV === 'production' ? {
      // PurgeCSS for removing unused CSS (only if not using JIT)
      '@fullhuman/postcss-purgecss': process.env.TAILWIND_MODE !== 'jit' ? {
        content: [
          './src/**/*.{html,js,jsx,ts,tsx,vue,svelte}',
          './public/**/*.html'
        ],
        defaultExtractor: content => {
          const broadMatches = content.match(/[^<>"'\\s]*[^<>"'\\s:]/g) || []
          const innerMatches = content.match(/[^<>"'\\s.()]*[^<>"'\\s.():]/g) || []
          return broadMatches.concat(innerMatches)
        },
        safelist: [
          // Always keep these classes
          'transition-all',
          'duration-300',
          'ease-in-out',
          // Add any dynamic classes that shouldn't be purged
        ]
      } : false,

      // CSS nano for minification
      'cssnano': {
        preset: 'default',
        plugins: [
          // Merge longhand properties into shorthand
          'cssnano-preset-advanced',
          // Optimize z-index values
          'postcss-merge-longhand',
          // Remove unused CSS rules
          'postcss-discard-unused',
          // Reduce calc() expressions
          'postcss-calc',
          // Optimize transform values
          'postcss-convert-values',
          // Minify font weights
          'postcss-minify-font-weight',
          // Remove duplicate rules
          'postcss-merge-rules'
        ]
      }
    } : {})
  }
}
"""
        return config.strip()

    def _get_timestamp(self) -> str:
        """Get current timestamp."""
        from datetime import datetime

        return datetime.now().isoformat()

    def generate_performance_monitoring_script(self) -> str:
        """Generate JavaScript for performance monitoring."""
        script = """
// Tailwind CSS Performance Monitor
class TailwindPerformanceMonitor {
  constructor() {
    this.metrics = {
      cssLoadTime: 0,
      renderTime: 0,
      bundleSize: 0,
      unusedClasses: 0
    };

    this.init();
  }

  init() {
    // Monitor CSS loading performance
    this.measureCSSLoadTime();

    // Monitor render performance
    this.measureRenderPerformance();

    // Monitor bundle size
    this.measureBundleSize();

    // Report metrics
    this.reportMetrics();
  }

  measureCSSLoadTime() {
    const observer = new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (entry.name.includes('.css')) {
          this.metrics.cssLoadTime += entry.duration;
        }
      }
    });

    observer.observe({ entryTypes: ['resource'] });
  }

  measureRenderPerformance() {
    // Measure First Contentful Paint
    const fcpEntry = performance.getEntriesByType('paint')
      .find(entry => entry.name === 'first-contentful-paint');

    if (fcpEntry) {
      this.metrics.renderTime = fcpEntry.startTime;
    }

    // Measure layout shifts
    let clsScore = 0;
    new PerformanceObserver((list) => {
      for (const entry of list.getEntries()) {
        if (!entry.hadRecentInput) {
          clsScore += entry.value;
        }
      }
    }).observe({ entryTypes: ['layout-shift'] });

    this.metrics.clsScore = clsScore;
  }

  measureBundleSize() {
    const stylesheets = document.querySelectorAll('link[rel="stylesheet"]');
    stylesheets.forEach(sheet => {
      if (sheet.href) {
        fetch(sheet.href, { method: 'HEAD' })
          .then(response => {
            const contentLength = response.headers.get('content-length');
            if (contentLength) {
              this.metrics.bundleSize += parseInt(contentLength);
            }
          })
          .catch(() => {
            // Fallback estimation
            this.metrics.bundleSize += 25000; // 25KB estimate
          });
      }
    });
  }

  reportMetrics() {
    // Wait for all measurements to complete
    setTimeout(() => {
      const report = {
        cssLoadTime: Math.round(this.metrics.cssLoadTime),
        renderTime: Math.round(this.metrics.renderTime),
        bundleSize: Math.round(this.metrics.bundleSize / 1024), // KB
        clsScore: Math.round(this.metrics.clsScore * 1000) / 1000
      };

      console.log('Tailwind CSS Performance Metrics:', report);

      // Send to analytics if available
      if (typeof gtag !== 'undefined') {
        gtag('event', 'tailwind_performance', {
          custom_map: {
            css_load_time: report.cssLoadTime,
            render_time: report.renderTime,
            bundle_size_kb: report.bundleSize,
            cls_score: report.clsScore
          }
        });
      }

      // Show performance warnings
      if (report.cssLoadTime > 500) {
        console.warn('⚠️ Slow CSS load time detected:', report.cssLoadTime + 'ms');
      }

      if (report.renderTime > 2000) {
        console.warn('⚠️ Slow render time detected:', report.renderTime + 'ms');
      }

      if (report.bundleSize > 50) {
        console.warn('⚠️ Large CSS bundle detected:', report.bundleSize + 'KB');
      }
    }, 3000);
  }
}

// Initialize monitor when DOM is loaded
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    new TailwindPerformanceMonitor();
  });
} else {
  new TailwindPerformanceMonitor();
}
"""
        return script.strip()

    def create_performance_audit_checklist(self) -> list[dict[str, Any]]:
        """Create comprehensive performance audit checklist."""
        return [
            {
                "category": "Bundle Size",
                "items": [
                    {
                        "check": "JIT compilation enabled",
                        "description": "Ensure mode: 'jit' is set in tailwind.config.js",
                        "priority": "critical",
                        "impact": "80-90% bundle size reduction",
                    },
                    {
                        "check": "PurgeCSS configuration accurate",
                        "description": "All template paths included in purge/content array",
                        "priority": "critical",
                        "impact": "30-60% bundle size reduction",
                    },
                    {
                        "check": "CSS minification enabled",
                        "description": "Use PostCSS minification in production",
                        "priority": "high",
                        "impact": "15-25% bundle size reduction",
                    },
                    {
                        "check": "Gzip/brotli compression enabled",
                        "description": "Server compression configured for CSS files",
                        "priority": "high",
                        "impact": "70-85% transfer size reduction",
                    },
                ],
            },
            {
                "category": "Render Performance",
                "items": [
                    {
                        "check": "GPU acceleration for animations",
                        "description": "Use transform/opacity for smooth animations",
                        "priority": "high",
                        "impact": "50-70% faster animations",
                    },
                    {
                        "check": "CSS containment used",
                        "description": "Apply contain property strategically",
                        "priority": "medium",
                        "impact": "20-40% layout performance",
                    },
                    {
                        "check": "Expensive properties optimized",
                        "description": "Minimize use of box-shadow, filter, blur",
                        "priority": "medium",
                        "impact": "10-30% render performance",
                    },
                    {
                        "check": "will-change used sparingly",
                        "description": "Only use will-change for complex animations",
                        "priority": "medium",
                        "impact": "Memory usage optimization",
                    },
                ],
            },
            {
                "category": "Loading Performance",
                "items": [
                    {
                        "check": "Critical CSS inlined",
                        "description": "Extract and inline above-fold CSS",
                        "priority": "high",
                        "impact": "40-60% faster render",
                        "effort": "High",
                    },
                    {
                        "check": "Non-critical CSS lazy loaded",
                        "description": "Split CSS into chunks and load on demand",
                        "priority": "high",
                        "impact": "30-50% faster initial load",
                    },
                    {
                        "check": "Font loading optimized",
                        "description": "font-display: swap, preload critical fonts",
                        "priority": "medium",
                        "impact": "20-40% faster font display",
                    },
                ],
            },
            {
                "category": "Development Workflow",
                "items": [
                    {
                        "check": "Performance monitoring in place",
                        "description": "Track CSS metrics in production",
                        "priority": "medium",
                        "impact": "Continuous optimization",
                    },
                    {
                        "check": "Bundle analysis tools configured",
                        "description": "webpack-bundle-analyzer or similar",
                        "priority": "low",
                        "impact": "Better optimization insights",
                    },
                    {
                        "check": "Performance budgets set",
                        "description": "CSS bundle size budgets enforced",
                        "priority": "medium",
                        "impact": "Prevents performance regression",
                    },
                ],
            },
        ]
