"""
Tests for Factory Validator
"""

import tempfile
from pathlib import Path

from validators.factory_validator import FactoryValidator


class TestFactoryValidator:
    """Test cases for FactoryValidator."""

    def setup_method(self):
        """Set up test fixtures."""
        self.validator = FactoryValidator()
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_validate_valid_factory_options(self):
        """Test validating valid factory options."""
        valid_options = ["touch-friendly", "high-contrast", "offline-first"]
        assert self.validator.validate_requirements(valid_options)

    def test_validate_invalid_factory_options(self):
        """Test validating invalid factory options."""
        invalid_options = ["invalid-option", "another-invalid"]
        assert not self.validator.validate_requirements(invalid_options)

    def test_validate_empty_factory_options(self):
        """Test validating empty factory options."""
        empty_options = []
        assert self.validator.validate_requirements(empty_options)

    def test_validate_valid_project_structure(self):
        """Test validating valid project structure."""
        # Create required files
        (self.temp_path / "README.md").write_text("# Test Project")
        (self.temp_path / "package.json").write_text('{"name": "test"}')
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "components").mkdir()
        (self.temp_path / "src" / "styles").mkdir()

        result = self.validator._validate_project_structure(self.temp_path)
        assert result["passed"]

    def test_validate_missing_project_files(self):
        """Test validating project with missing files."""
        result = self.validator._validate_project_structure(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_touch_interface_requirements(self):
        """Test touch interface validation."""
        # Create CSS with touch-friendly styles
        css_content = """
        .touch-button {
            min-width: 44px;
            min-height: 44px;
            padding: 12px;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_touch_interface(self.temp_path)
        assert result["passed"]

    def test_validate_touch_interface_missing_styles(self):
        """Test touch interface validation with missing styles."""
        # Create CSS without touch-friendly styles
        css_content = """
        .button {
            width: 20px;
            height: 20px;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_touch_interface(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_contrast_requirements(self):
        """Test contrast requirements validation."""
        # Create CSS with industrial colors and dark theme
        css_content = """
        :root {
            --primary-color: #FF6B35;
            --background-color: #1A1A1A;
        }

        .dark-theme {
            background-color: #000000;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_contrast_requirements(self.temp_path)
        assert result["passed"]

    def test_validate_contrast_missing_theme(self):
        """Test contrast validation without dark theme."""
        css_content = """
        .light-theme {
            background-color: #FFFFFF;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_contrast_requirements(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_responsive_design(self):
        """Test responsive design validation."""
        # Create CSS with media queries
        css_content = """
        @media (max-width: 768px) {
            .container {
                width: 100%;
            }
        }

        .flex-container {
            display: flex;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_responsive_design(self.temp_path)
        assert result["passed"]

    def test_validate_responsive_design_missing_media_queries(self):
        """Test responsive design validation without media queries."""
        css_content = """
        .container {
            width: 1200px;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_responsive_design(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_accessibility_requirements(self):
        """Test accessibility validation."""
        # Create HTML with alt text and ARIA labels
        html_content = """
        <img src="test.jpg" alt="Test image" />
        <button aria-label="Start pump">Start</button>
        """
        html_file = self.temp_path / "index.html"
        html_file.write_text(html_content)

        # Create CSS with focus styles
        css_content = """
        button:focus {
            outline: 2px solid blue;
        }
        """
        css_file = self.temp_path / "styles.css"
        css_file.write_text(css_content)

        result = self.validator._validate_accessibility(self.temp_path)
        assert result["passed"]

    def test_validate_accessibility_missing_alt_text(self):
        """Test accessibility validation without alt text."""
        html_content = """
        <img src="test.jpg" />
        """
        html_file = self.temp_path / "index.html"
        html_file.write_text(html_content)

        result = self.validator._validate_accessibility(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_offline_capabilities(self):
        """Test offline capabilities validation."""
        # Create JS with service worker and local storage
        js_content = """
        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }

        localStorage.setItem('data', JSON.stringify({}));
        """
        js_file = self.temp_path / "app.js"
        js_file.write_text(js_content)

        result = self.validator._validate_offline_capabilities(self.temp_path)
        assert result["passed"]

    def test_validate_offline_capabilities_missing_support(self):
        """Test offline capabilities validation without support."""
        js_content = """
        console.log('app started');
        """
        js_file = self.temp_path / "app.js"
        js_file.write_text(js_content)

        result = self.validator._validate_offline_capabilities(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_realtime_capabilities(self):
        """Test real-time capabilities validation."""
        # Create JS with WebSocket and reconnection logic
        js_content = """
        const ws = new WebSocket('ws://localhost:8080');

        ws.onclose = () => {
            setTimeout(() => {
                ws.reconnect();
            }, 5000);
        };
        """
        js_file = self.temp_path / "app.js"
        js_file.write_text(js_content)

        result = self.validator._validate_realtime_capabilities(self.temp_path)
        assert result["passed"]

    def test_validate_realtime_capabilities_missing_websocket(self):
        """Test real-time capabilities validation without WebSocket."""
        js_content = """
        console.log('app started');
        """
        js_file = self.temp_path / "app.js"
        js_file.write_text(js_content)

        result = self.validator._validate_realtime_capabilities(self.temp_path)
        assert not result["passed"]
        assert len(result["issues"]) > 0

    def test_validate_generated_code_complete_project(self):
        """Test validating complete generated project."""
        # Create a complete project structure
        (self.temp_path / "README.md").write_text("# Test Project")
        (self.temp_path / "package.json").write_text('{"name": "test"}')
        (self.temp_path / "src").mkdir()
        (self.temp_path / "src" / "components").mkdir()
        (self.temp_path / "src" / "styles").mkdir()
        (self.temp_path / "src" / "App.tsx").write_text("export default function App() { return <div>Test</div>; }")

        # Create industrial CSS
        css_content = """
        .touch-button {
            min-width: 44px;
            min-height: 44px;
        }

        @media (max-width: 768px) {
            .container { width: 100%; }
        }

        button:focus { outline: 2px solid blue; }
        """
        (self.temp_path / "src" / "styles.css").write_text(css_content)

        # Create JS with real-time and offline support
        js_content = """
        const ws = new WebSocket('ws://localhost:8080');

        if ('serviceWorker' in navigator) {
            navigator.serviceWorker.register('/sw.js');
        }

        ws.onclose = () => {
            setTimeout(() => ws.reconnect(), 5000);
        };

        localStorage.setItem('config', '{}');
        """
        (self.temp_path / "src" / "app.js").write_text(js_content)

        result = self.validator.validate_generated_code(self.temp_path)
        assert result

    def test_generate_validation_report(self):
        """Test validation report generation."""
        # Create minimal project
        (self.temp_path / "README.md").write_text("# Test Project")

        report = self.validator.generate_validation_report(self.temp_path)
        assert isinstance(report, str)
        assert "Industrial Interface Validation Report" in report
        assert "Summary" in report
        assert "Detailed Results" in report

        # Check that report file was created
        report_file = self.temp_path / "VALIDATION_REPORT.md"
        assert report_file.exists()
        assert report_file.read_text() == report
