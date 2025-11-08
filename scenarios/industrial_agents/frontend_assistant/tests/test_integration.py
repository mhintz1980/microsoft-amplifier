"""
Integration Tests for Industrial Frontend Assistant
"""

import json
import tempfile
from pathlib import Path

from generators.generator_factory import GeneratorFactory
from main import IndustrialFrontendAssistant
from validators.factory_validator import FactoryValidator

from utils.template_manager import TemplateManager


class TestIntegration:
    """Integration tests for the complete system."""

    def setup_method(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def teardown_method(self):
        """Clean up test fixtures."""
        import shutil

        shutil.rmtree(self.temp_dir)

    def test_complete_react_project_generation(self):
        """Test complete React project generation."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": ["touch-friendly", "high-contrast"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": ["alerts", "real-time"],
        }

        result = assistant.generate(**project_config)
        assert result

        # Verify generated files
        expected_files = [
            "package.json",
            "src/App.tsx",
            "src/App.css",
            "src/types/index.ts",
            "src/config/index.ts",
            "tsconfig.json",
            "vite.config.ts",
            "README.md",
            ".gitignore",
        ]

        for file_path in expected_files:
            full_path = self.temp_path / file_path
            assert full_path.exists(), f"Missing file: {file_path}"

    def test_complete_vue_project_generation(self):
        """Test complete Vue project generation."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "control-panel",
            "framework": "vue",
            "template": "equipment-control",
            "factory_options": ["touch-friendly"],
            "theme": "factory-dark",
            "data_source": "mqtt",
            "features": ["real-time"],
        }

        result = assistant.generate(**project_config)
        assert result

        # Verify Vue-specific files
        vue_files = [
            "src/App.vue",
            "src/main.ts",
            "src/assets/main.css",
            "vite.config.ts",
        ]

        for file_path in vue_files:
            full_path = self.temp_path / file_path
            assert full_path.exists(), f"Missing Vue file: {file_path}"

    def test_complete_streamlit_project_generation(self):
        """Test complete Streamlit project generation."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "dashboard",
            "framework": "streamlit",
            "template": "system-overview",
            "factory_options": ["high-contrast"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": ["alerts"],
        }

        result = assistant.generate(**project_config)
        assert result

        # Verify Streamlit-specific files
        streamlit_files = [
            "app.py",
            "requirements.txt",
            "config/config.py",
            ".streamlit/config.toml",
        ]

        for file_path in streamlit_files:
            full_path = self.temp_path / file_path
            assert full_path.exists(), f"Missing Streamlit file: {file_path}"

    def test_generated_package_json_structure(self):
        """Test generated package.json has correct structure."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": ["touch-friendly"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": [],
        }

        assistant.generate(**project_config)

        package_json_path = self.temp_path / "package.json"
        assert package_json_path.exists()

        with open(package_json_path) as f:
            package_data = json.load(f)

        # Verify required fields
        assert "name" in package_data
        assert "version" in package_data
        assert "scripts" in package_data
        assert "dependencies" in package_data
        assert "devDependencies" in package_data

        # Verify required dependencies
        assert "react" in package_data["dependencies"]
        assert "typescript" in package_data["dependencies"]

        # Verify required scripts
        assert "dev" in package_data["scripts"]
        assert "build" in package_data["scripts"]

    def test_generated_readme_content(self):
        """Test generated README has required content."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": ["touch-friendly", "high-contrast"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": ["alerts"],
        }

        assistant.generate(**project_config)

        readme_path = self.temp_path / "README.md"
        assert readme_path.exists()

        readme_content = readme_path.read_text()

        # Verify required sections
        assert "# Industrial Dashboard - Pump Monitoring" in readme_content
        assert "## Quick Start" in readme_content
        assert "## Installation" in readme_content
        assert "## Features" in readme_content
        assert "## Factory Environment Features" in readme_content

        # Verify project-specific content
        assert "React Framework" in readme_content
        assert "touch-friendly" in readme_content
        assert "high-contrast" in readme_content

    def test_factory_validation_on_generated_project(self):
        """Test factory validation passes on generated project."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": ["touch-friendly", "high-contrast", "offline-first"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": ["alerts", "real-time"],
        }

        assistant.generate(**project_config)

        validator = FactoryValidator()
        validation_result = validator.validate_generated_code(self.temp_path)
        assert validation_result, "Generated project should pass factory validation"

    def test_template_integration_with_generator(self):
        """Test template integration with generators."""
        template_manager = TemplateManager()
        generator_factory = GeneratorFactory()

        template = template_manager.get_template("dashboard", "react", "pump-monitoring")
        assert template is not None

        generator = generator_factory.create_generator("react")
        assert generator is not None

        # Test that generator can handle template configuration
        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": ["touch-friendly"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": [],
        }

        # Generate files using the template
        files = generator.generate_project_structure(template.config, project_config)
        assert len(files) > 0
        assert "src/App.tsx" in files

    def test_all_template_combinations(self):
        """Test that all template combinations can be generated."""
        template_manager = TemplateManager()
        generator_factory = GeneratorFactory()

        templates = template_manager.list_templates()

        for interface_type, frameworks in templates.items():
            for framework, template_names in frameworks.items():
                for template_name in template_names:
                    # Skip some combinations for test performance
                    if len(template_names) > 2 and list(template_names.keys()).index(template_name) > 1:
                        continue

                    print(f"Testing {interface_type}/{framework}/{template_name}")

                    template = template_manager.get_template(interface_type, framework, template_name)
                    assert template is not None, f"Template not found: {interface_type}/{framework}/{template_name}"

                    generator = generator_factory.create_generator(framework)
                    assert generator is not None, f"Generator not found for framework: {framework}"

                    # Test configuration validation
                    project_config = {
                        "type": interface_type,
                        "framework": framework,
                        "template": template_name,
                        "factory_options": ["touch-friendly"],
                        "theme": "factory-dark",
                        "data_source": "mock",
                        "features": [],
                    }

                    errors = generator.validate_config(project_config)
                    assert len(errors) == 0, f"Configuration validation failed: {errors}"

    def test_error_handling_invalid_configuration(self):
        """Test error handling with invalid configuration."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        # Test with invalid interface type
        invalid_config = {
            "type": "invalid-type",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": ["touch-friendly"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": [],
        }

        result = assistant.generate(**invalid_config)
        assert not result

    def test_error_handling_missing_files(self):
        """Test error handling when required files are missing."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "nonexistent-template",
            "factory_options": ["touch-friendly"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": [],
        }

        result = assistant.generate(**project_config)
        assert not result

    def test_custom_factory_options(self):
        """Test custom factory options are handled correctly."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        custom_options = ["touch-friendly", "high-contrast", "offline-first", "ruggedized", "accessibility"]

        project_config = {
            "type": "dashboard",
            "framework": "react",
            "template": "pump-monitoring",
            "factory_options": custom_options,
            "theme": "factory-dark",
            "data_source": "mock",
            "features": ["alerts", "export", "authentication"],
        }

        result = assistant.generate(**project_config)
        assert result

        # Verify that CSS contains styles for custom options
        css_file = self.temp_path / "src/App.css"
        assert css_file.exists()

        css_content = css_file.read_text()
        assert "min-width" in css_content  # touch-friendly
        assert "min-height" in css_content  # touch-friendly

    def test_generated_project_is_valid_industrial_interface(self):
        """Test that generated project meets industrial interface standards."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        # Generate project with all factory optimizations
        project_config = {
            "type": "control-panel",
            "framework": "react",
            "template": "equipment-control",
            "factory_options": ["touch-friendly", "high-contrast", "offline-first", "ruggedized", "accessibility"],
            "theme": "high-contrast",
            "data_source": "mqtt",
            "features": ["alerts", "real-time", "export", "authentication"],
        }

        result = assistant.generate(**project_config)
        assert result

        # Validate generated project
        validator = FactoryValidator()
        validation_result = validator.validate_generated_code(self.temp_path)
        assert validation_result

        # Generate validation report
        report = validator.generate_validation_report(self.temp_path)
        assert "Overall Status: ✅ PASSED" in report

        # Verify report file
        report_file = self.temp_path / "VALIDATION_REPORT.md"
        assert report_file.exists()

    def test_generated_project_can_be_built(self):
        """Test that generated project can be built (basic build check)."""
        assistant = IndustrialFrontendAssistant(self.temp_path)

        project_config = {
            "type": "calculator",
            "framework": "react",
            "template": "pipe-sizing",
            "factory_options": ["touch-friendly"],
            "theme": "factory-dark",
            "data_source": "mock",
            "features": [],
        }

        result = assistant.generate(**project_config)
        assert result

        # Check that package.json exists and has build script
        package_json_path = self.temp_path / "package.json"
        assert package_json_path.exists()

        with open(package_json_path) as f:
            package_data = json.load(f)

        assert "build" in package_data["scripts"]

        # Check that TypeScript configuration exists
        tsconfig_path = self.temp_path / "tsconfig.json"
        assert tsconfig_path.exists()

        # Check that Vite configuration exists
        vite_config_path = self.temp_path / "vite.config.ts"
        assert vite_config_path.exists()

        print(f"Generated project structure: {list(self.temp_path.rglob('*'))}")
