"""
Factory Environment Validator

Validates industrial frontend interfaces against factory environment requirements.
"""

import re
from pathlib import Path
from typing import Any

from amplifier.utils.logger import get_logger

logger = get_logger(__name__)


class FactoryValidator:
    """Validates industrial interfaces for factory environment compliance."""

    def __init__(self):
        """Initialize factory validator."""
        self.validation_rules = self._load_validation_rules()

    def validate_requirements(self, factory_options: list[str]) -> bool:
        """Validate factory environment requirements.

        Args:
            factory_options: List of factory optimization options

        Returns:
            True if requirements are valid, False otherwise
        """
        valid_options = [
            "touch-friendly",
            "high-contrast",
            "offline-first",
            "ruggedized",
            "accessibility",
        ]

        for option in factory_options:
            if option not in valid_options:
                logger.error(f"Invalid factory option: {option}")
                return False

        return True

    def validate_generated_code(self, output_dir: Path) -> bool:
        """Validate generated code against factory requirements.

        Args:
            output_dir: Directory containing generated code

        Returns:
            True if validation passes, False otherwise
        """
        logger.info("🔍 Validating generated industrial interface...")

        validation_results = []

        # Validate project structure
        validation_results.append(self._validate_project_structure(output_dir))

        # Validate touch interface requirements
        validation_results.append(self._validate_touch_interface(output_dir))

        # Validate contrast and visibility
        validation_results.append(self._validate_contrast_requirements(output_dir))

        # Validate responsive design
        validation_results.append(self._validate_responsive_design(output_dir))

        # Validate accessibility
        validation_results.append(self._validate_accessibility(output_dir))

        # Validate offline capabilities
        validation_results.append(self._validate_offline_capabilities(output_dir))

        # Validate real-time data handling
        validation_results.append(self._validate_realtime_capabilities(output_dir))

        # Report results
        passed_count = sum(1 for result in validation_results if result["passed"])
        total_count = len(validation_results)

        logger.info(f"✅ Validation completed: {passed_count}/{total_count} checks passed")

        for result in validation_results:
            if not result["passed"]:
                logger.error(f"❌ {result['category']}: {result['message']}")
                for issue in result.get("issues", []):
                    logger.error(f"   • {issue}")

        return all(result["passed"] for result in validation_results)

    def _validate_project_structure(self, output_dir: Path) -> dict[str, Any]:
        """Validate project structure."""
        issues = []

        # Check for required files
        required_files = ["README.md", "package.json", "src/"]
        for file_path in required_files:
            if not (output_dir / file_path).exists():
                issues.append(f"Missing required file/directory: {file_path}")

        # Check for source code structure
        src_dir = output_dir / "src"
        if src_dir.exists():
            expected_dirs = ["components", "styles", "types"]
            for dir_name in expected_dirs:
                if not (src_dir / dir_name).exists():
                    issues.append(f"Missing source directory: src/{dir_name}")

        return {
            "category": "Project Structure",
            "passed": len(issues) == 0,
            "message": "Project structure validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _validate_touch_interface(self, output_dir: Path) -> dict[str, Any]:
        """Validate touch interface requirements."""
        issues = []

        # Check CSS files for touch-friendly styles
        css_files = list(output_dir.rglob("*.css"))
        for css_file in css_files:
            content = css_file.read_text()

            # Check for minimum touch target size
            if "min-width" not in content and "min-height" not in content:
                issues.append(f"{css_file.name}: Missing minimum touch target sizes")

            # Check for touch-friendly button styles
            if "button" in content.lower() and "padding" not in content:
                issues.append(f"{css_file.name}: Buttons may not have adequate padding for touch")

        # Check React/Vue components for touch interactions
        component_files = list(output_dir.rglob("*.tsx")) + list(output_dir.rglob("*.vue"))
        for component_file in component_files:
            content = component_file.read_text()

            # Look for onClick handlers
            if "onClick" in content or "@click" in content:
                # Check if there are any visual feedback styles
                if ":hover" not in content and ":active" not in content:
                    issues.append(f"{component_file.name}: Missing hover/active states for touch feedback")

        return {
            "category": "Touch Interface",
            "passed": len(issues) == 0,
            "message": "Touch interface validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _validate_contrast_requirements(self, output_dir: Path) -> dict[str, Any]:
        """Validate contrast and visibility requirements."""
        issues = []

        # Check CSS for high contrast colors
        css_files = list(output_dir.rglob("*.css"))
        for css_file in css_files:
            content = css_file.read_text()

            # Look for color definitions
            re.findall(r"color:\s*([^;]+)", content, re.IGNORECASE)
            re.findall(r"background[^:]*:\s*([^;]+)", content, re.IGNORECASE)

            # Check for dark theme support
            if "dark" not in content.lower() and "#000" not in content and "#1a" not in content.lower():
                issues.append(f"{css_file.name}: Missing dark theme support")

            # Check for industrial color schemes
            industrial_colors = ["#FF6B35", "#004E89", "#F57C00", "#D32F2F", "#4CAF50"]
            has_industrial_colors = any(color in content for color in industrial_colors)

            if not has_industrial_colors:
                issues.append(f"{css_file.name}: Missing industrial color scheme")

        return {
            "category": "Contrast & Visibility",
            "passed": len(issues) == 0,
            "message": "Contrast requirements validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _validate_responsive_design(self, output_dir: Path) -> dict[str, Any]:
        """Validate responsive design requirements."""
        issues = []

        # Check CSS for media queries
        css_files = list(output_dir.rglob("*.css"))
        has_media_queries = False

        for css_file in css_files:
            content = css_file.read_text()

            if "@media" in content:
                has_media_queries = True

                # Check for common breakpoints
                if "768px" not in content and "1024px" not in content:
                    issues.append(f"{css_file.name}: Missing common tablet breakpoint")

                if "1920px" not in content:
                    issues.append(f"{css_file.name}: Missing large desktop breakpoint")

        if not has_media_queries:
            issues.append("No responsive design (media queries) found")

        # Check for flexible layouts
        css_files = list(output_dir.rglob("*.css"))
        has_flexbox = any("display: flex" in f.read_text() for f in css_files)
        has_grid = any("display: grid" in f.read_text() for f in css_files)

        if not (has_flexbox or has_grid):
            issues.append("Missing flexible layout systems (Flexbox or Grid)")

        return {
            "category": "Responsive Design",
            "passed": len(issues) == 0,
            "message": "Responsive design validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _validate_accessibility(self, output_dir: Path) -> dict[str, Any]:
        """Validate accessibility requirements."""
        issues = []

        # Check HTML/JSX files for accessibility features
        html_files = (
            list(output_dir.rglob("*.html")) + list(output_dir.rglob("*.jsx")) + list(output_dir.rglob("*.tsx"))
        )

        for html_file in html_files:
            content = html_file.read_text()

            # Check for alt text on images
            if "<img" in content and "alt=" not in content:
                issues.append(f"{html_file.name}: Images missing alt text")

            # Check for ARIA labels
            if "button" in content.lower() and "aria-label" not in content:
                issues.append(f"{html_file.name}: Buttons may need ARIA labels")

            # Check for focus indicators
            css_files = list(output_dir.rglob("*.css"))
            has_focus_styles = any(":focus" in f.read_text() for f in css_files)

            if not has_focus_styles:
                issues.append("Missing focus indicators for keyboard navigation")

        # Check for semantic HTML
        jsx_files = list(output_dir.rglob("*.jsx")) + list(output_dir.rglob("*.tsx"))
        for jsx_file in jsx_files:
            content = jsx_file.read_text()

            # Look for div-heavy structures
            div_count = content.count("<div")
            if div_count > 20:
                issues.append(f"{jsx_file.name}: Consider using semantic HTML elements instead of excessive divs")

        return {
            "category": "Accessibility",
            "passed": len(issues) == 0,
            "message": "Accessibility validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _validate_offline_capabilities(self, output_dir: Path) -> dict[str, Any]:
        """Validate offline capabilities."""
        issues = []

        # Check for service worker registration
        js_files = list(output_dir.rglob("*.js")) + list(output_dir.rglob("*.ts")) + list(output_dir.rglob("*.tsx"))

        has_service_worker = any("serviceWorker" in f.read_text() for f in js_files)
        has_local_storage = any("localStorage" in f.read_text() for f in js_files)

        if not has_service_worker:
            issues.append("Missing service worker for offline functionality")

        if not has_local_storage:
            issues.append("Missing local storage for offline data caching")

        # Check for offline detection
        has_offline_detection = any("navigator.onLine" in f.read_text() for f in js_files)
        if not has_offline_detection:
            issues.append("Missing offline/online connection detection")

        # Check for error handling
        has_error_handling = any("catch" in f.read_text() and "network" in f.read_text().lower() for f in js_files)
        if not has_error_handling:
            issues.append("Missing network error handling for offline scenarios")

        return {
            "category": "Offline Capabilities",
            "passed": len(issues) == 0,
            "message": "Offline capabilities validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _validate_realtime_capabilities(self, output_dir: Path) -> dict[str, Any]:
        """Validate real-time data capabilities."""
        issues = []

        # Check for WebSocket/MQTT implementations
        js_files = list(output_dir.rglob("*.js")) + list(output_dir.rglob("*.ts")) + list(output_dir.rglob("*.tsx"))

        has_websocket = any("WebSocket" in f.read_text() for f in js_files)
        has_mqtt = any("mqtt" in f.read_text().lower() for f in js_files)
        has_sse = any("EventSource" in f.read_text() for f in js_files)

        if not (has_websocket or has_mqtt or has_sse):
            issues.append("Missing real-time data connection (WebSocket/MQTT/SSE)")

        # Check for reconnection logic
        has_reconnection = any("reconnect" in f.read_text().lower() for f in js_files)
        if not has_reconnection:
            issues.append("Missing automatic reconnection logic")

        # Check for data buffering
        has_buffering = any("buffer" in f.read_text().lower() or "queue" in f.read_text().lower() for f in js_files)
        if not has_buffering:
            issues.append("Missing data buffering for connection interruptions")

        # Check for update intervals/throttling
        has_throttling = any(
            "interval" in f.read_text().lower() or "throttle" in f.read_text().lower() for f in js_files
        )
        if not has_throttling:
            issues.append("Missing update rate throttling to prevent performance issues")

        return {
            "category": "Real-time Capabilities",
            "passed": len(issues) == 0,
            "message": "Real-time capabilities validation"
            + (" passed" if len(issues) == 0 else f" failed ({len(issues)} issues)"),
            "issues": issues,
        }

    def _load_validation_rules(self) -> dict[str, Any]:
        """Load validation rules for factory environments."""
        return {
            "touch_interface": {
                "min_touch_target": 44,  # pixels
                "min_button_size": 60,  # pixels for industrial use
                "required_feedback": ["hover", "active"],
            },
            "contrast": {
                "min_contrast_ratio": 4.5,  # WCAG AA standard
                "industrial_colors": ["#FF6B35", "#004E89", "#F57C00", "#D32F2F"],
                "dark_theme_required": True,
            },
            "responsive": {
                "breakpoints": ["768px", "1024px", "1920px"],
                "flexible_layout_required": True,
            },
            "accessibility": {
                "alt_text_required": True,
                "focus_indicators_required": True,
                "semantic_html_preferred": True,
            },
            "performance": {
                "max_update_frequency": 1000,  # ms
                "connection_timeout": 5000,  # ms
                "retry_attempts": 3,
            },
        }

    def generate_validation_report(self, output_dir: Path) -> str:
        """Generate detailed validation report.

        Args:
            output_dir: Directory containing generated code

        Returns:
            Validation report as markdown string
        """
        validation_results = []

        # Run all validations
        validation_results.append(self._validate_project_structure(output_dir))
        validation_results.append(self._validate_touch_interface(output_dir))
        validation_results.append(self._validate_contrast_requirements(output_dir))
        validation_results.append(self._validate_responsive_design(output_dir))
        validation_results.append(self._validate_accessibility(output_dir))
        validation_results.append(self._validate_offline_capabilities(output_dir))
        validation_results.append(self._validate_realtime_capabilities(output_dir))

        # Generate report
        report = "# Industrial Interface Validation Report\n\n"
        report += f"Generated for: `{output_dir.name}`\n"
        report += f"Validation Date: {Path.cwd()}\n\n"

        # Summary
        passed_count = sum(1 for result in validation_results if result["passed"])
        total_count = len(validation_results)

        report += "## Summary\n\n"
        report += f"- **Overall Status**: {'✅ PASSED' if passed_count == total_count else '❌ FAILED'}\n"
        report += f"- **Checks Passed**: {passed_count}/{total_count}\n"
        report += f"- **Success Rate**: {passed_count / total_count * 100:.1f}%\n\n"

        # Detailed results
        report += "## Detailed Results\n\n"

        for result in validation_results:
            status_icon = "✅" if result["passed"] else "❌"
            report += f"### {status_icon} {result['category']}\n\n"
            report += f"**Status**: {result['message']}\n\n"

            if not result["passed"] and result["issues"]:
                report += "**Issues Found:**\n\n"
                for issue in result["issues"]:
                    report += f"- ❌ {issue}\n"
                report += "\n"

        # Recommendations
        failed_results = [r for r in validation_results if not r["passed"]]
        if failed_results:
            report += "## Recommendations\n\n"
            report += "The following areas need attention to meet factory environment standards:\n\n"

            for result in failed_results:
                report += f"### {result['category']}\n\n"
                if result["category"] == "Touch Interface":
                    report += "- Ensure minimum touch target size of 44px\n"
                    report += "- Add hover and active states for touch feedback\n"
                    report += "- Consider larger buttons (60px+) for industrial use\n"
                elif result["category"] == "Contrast & Visibility":
                    report += "- Implement dark theme support\n"
                    report += "- Use industrial color schemes\n"
                    report += "- Ensure WCAG AA contrast ratios (4.5:1 minimum)\n"
                elif result["category"] == "Responsive Design":
                    report += "- Add media queries for different screen sizes\n"
                    report += "- Include tablet (768px) and large desktop (1920px) breakpoints\n"
                    report += "- Use flexible layout systems (Flexbox/Grid)\n"
                elif result["category"] == "Accessibility":
                    report += "- Add alt text to all images\n"
                    report += "- Include ARIA labels for interactive elements\n"
                    report += "- Add focus indicators for keyboard navigation\n"
                elif result["category"] == "Offline Capabilities":
                    report += "- Implement service worker for offline functionality\n"
                    report += "- Add local storage for data caching\n"
                    report += "- Include offline/online connection detection\n"
                elif result["category"] == "Real-time Capabilities":
                    report += "- Implement WebSocket/MQTT/SSE for real-time data\n"
                    report += "- Add automatic reconnection logic\n"
                    report += "- Include data buffering for connection interruptions\n"

                report += "\n"

        # Save report
        report_path = output_dir / "VALIDATION_REPORT.md"
        report_path.write_text(report)

        logger.info(f"📋 Validation report saved to: {report_path}")
        return report
