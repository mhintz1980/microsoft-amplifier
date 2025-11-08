"""
Tests for Template Manager
"""

from utils.template_manager import TemplateManager


class TestTemplateManager:
    """Test cases for TemplateManager."""

    def setup_method(self):
        """Set up test fixtures."""
        self.template_manager = TemplateManager()

    def test_get_pump_monitoring_react_template(self):
        """Test getting pump monitoring React template."""
        template = self.template_manager.get_template("dashboard", "react", "pump-monitoring")
        assert template is not None
        assert template.name == "pump-monitoring"
        assert template.interface_type == "dashboard"
        assert template.framework == "react"

    def test_get_equipment_control_vue_template(self):
        """Test getting equipment control Vue template."""
        template = self.template_manager.get_template("control-panel", "vue", "equipment-control")
        assert template is not None
        assert template.name == "equipment-control"
        assert template.interface_type == "control-panel"
        assert template.framework == "vue"

    def test_get_streamlit_template(self):
        """Test getting Streamlit template."""
        template = self.template_manager.get_template("dashboard", "streamlit", "pump-monitoring")
        assert template is not None
        assert template.name == "pump-monitoring"
        assert template.interface_type == "dashboard"
        assert template.framework == "streamlit"

    def test_get_nonexistent_template(self):
        """Test getting non-existent template returns None."""
        template = self.template_manager.get_template("dashboard", "react", "nonexistent")
        assert template is None

    def test_list_templates(self):
        """Test listing all available templates."""
        templates = self.template_manager.list_templates()
        assert "dashboard" in templates
        assert "react" in templates["dashboard"]
        assert "pump-monitoring" in templates["dashboard"]["react"]

    def test_template_file_structure(self):
        """Test template has required file structure."""
        template = self.template_manager.get_template("dashboard", "react", "pump-monitoring")
        assert template is not None

        # Check for required files
        assert "src/App.tsx" in template.files
        assert "src/components/" in str(template.files)

    def test_template_dependencies(self):
        """Test template dependencies are properly defined."""
        template = self.template_manager.get_template("dashboard", "react", "pump-monitoring")
        assert template is not None

        # Check for React dependencies
        assert "react" in template.dependencies
        assert "typescript" in template.dependencies["react"]

    def test_template_configuration(self):
        """Test template configuration is valid."""
        template = self.template_manager.get_template("dashboard", "react", "pump-monitoring")
        assert template is not None

        # Check for configuration
        assert template.config is not None
        assert isinstance(template.config, dict)

    def test_all_interface_types(self):
        """Test all interface types have templates."""
        interface_types = ["dashboard", "control-panel", "calculator", "documentation"]

        for interface_type in interface_types:
            templates = self.template_manager.list_templates()
            assert interface_type in templates
            assert len(templates[interface_type]) > 0

    def test_all_frameworks(self):
        """Test all frameworks have templates."""
        frameworks = ["react", "vue", "streamlit"]

        for framework in frameworks:
            templates = self.template_manager.list_templates()
            found_framework = False

            for _interface_type, framework_templates in templates.items():
                if framework in framework_templates:
                    found_framework = True
                    break

            assert found_framework, f"No templates found for framework: {framework}"
