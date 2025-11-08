"""
Base Generator for Industrial Frontend Components

Abstract base class for framework-specific generators.
"""

from abc import ABC
from abc import abstractmethod
from typing import Any


class BaseGenerator(ABC):
    """Abstract base class for industrial frontend generators."""

    @abstractmethod
    def generate_project_structure(
        self, template_config: dict[str, Any], project_config: dict[str, Any]
    ) -> dict[str, str]:
        """Generate the complete project structure.

        Args:
            template_config: Template configuration
            project_config: Project-specific configuration

        Returns:
            Dictionary mapping file paths to file contents
        """
        pass

    @abstractmethod
    def generate_package_json(self, project_config: dict[str, Any]) -> str:
        """Generate package.json file.

        Args:
            project_config: Project configuration

        Returns:
            package.json content as string
        """
        pass

    @abstractmethod
    def generate_component(self, component_type: str, config: dict[str, Any]) -> str:
        """Generate a component file.

        Args:
            component_type: Type of component to generate
            config: Component configuration

        Returns:
            Component code as string
        """
        pass

    @abstractmethod
    def generate_styles(self, theme: str, factory_options: list[str]) -> str:
        """Generate CSS styles for the interface.

        Args:
            theme: Color theme to use
            factory_options: Factory environment optimizations

        Returns:
            CSS content as string
        """
        pass

    @abstractmethod
    def generate_hooks(self, data_source: str, features: list[str]) -> dict[str, str]:
        """Generate custom hooks for the framework.

        Args:
            data_source: Data source configuration
            features: List of features to implement

        Returns:
            Dictionary mapping hook names to hook implementations
        """
        pass

    def generate_readme(self, project_config: dict[str, Any]) -> str:
        """Generate README.md file.

        Args:
            project_config: Project configuration

        Returns:
            README.md content as string
        """
        interface_type = project_config["type"]
        framework = project_config["framework"]
        template = project_config["template"]
        factory_options = project_config["factory_options"]
        features = project_config["features"]

        readme = f"""# Industrial {interface_type.title()} - {template.title()}

{self._get_interface_description(interface_type, template)}

Generated with Industrial Frontend Assistant for factory environments.

## Features

- **{framework.title()} Framework** - Modern {framework} application with TypeScript
- **Factory Optimized** - {" • ".join(factory_options)}
- **Real-time Data** - Live updates for monitoring and control
- **Touch Interface** - Large touch targets for industrial use
{self._format_features(features)}

## Quick Start

### Prerequisites

- Node.js 16+ and npm
- Modern web browser with WebSocket support

### Installation

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build
```

### Configuration

Edit `src/config.ts` to configure:
- Data source endpoints
- Update intervals
- Alert thresholds
- Theme settings

## Factory Environment Features

### Touch Interface
- Minimum 44px touch targets for gloved hands
- Gesture support for common operations
- Haptic feedback for confirmations

### High Contrast Display
- Optimized for bright factory lighting
- WCAG 2.1 AA compliant color contrasts
- Clear visual status indicators

### Real-time Updates
- WebSocket connections for live data
- Automatic reconnection on network issues
- Local caching for offline periods

### Offline Support
- Graceful degradation when network unavailable
- Local storage for critical data
- Queue operations until connection restored

## Data Integration

### MQTT Integration
```typescript
// Configure MQTT connection
const mqttConfig = {{
  broker: 'mqtt://factory-broker:1883',
  topics: ['factory/equipment/data'],
  clientId: 'frontend-{{template}}'
}};
```

### REST API Integration
```typescript
// Configure API endpoints
const apiConfig = {{
  baseUrl: 'https://factory-api.company.com',
  endpoints: {{
    metrics: '/api/v1/metrics',
    controls: '/api/v1/controls',
    alerts: '/api/v1/alerts'
  }}
}};
```

## Customization

### Adding New Metrics
1. Update data types in `src/types/`
2. Add chart configuration in `src/components/`
3. Update hooks to handle new data
4. Add UI components to display metrics

### Theme Customization
Edit `src/styles/theme.ts` to modify:
- Color schemes
- Typography
- Component styling
- Responsive breakpoints

### Factory Options
Enable/disable factory optimizations:
- `touch-friendly` - Large touch targets
- `high-contrast` - Enhanced visibility
- `offline-first` - Local storage support
- `ruggedized` - Error handling for harsh environments

## Deployment

### Docker Deployment
```bash
# Build Docker image
docker build -t factory-{interface_type} .

# Run container
docker run -p 3000:3000 factory-{interface_type}
```

### Static Hosting
```bash
# Build static files
npm run build

# Deploy dist/ folder to any static hosting service
```

## Troubleshooting

### Connection Issues
- Check MQTT broker connectivity
- Verify firewall settings
- Ensure WebSocket support

### Performance Issues
- Reduce update frequency in config
- Enable data compression
- Optimize chart rendering

### Display Issues
- Adjust browser zoom level
- Check monitor resolution
- Verify high contrast mode

## Development

### Component Development
```bash
# Run tests
npm test

# Type checking
npm run type-check

# Linting
npm run lint

# Formatting
npm run format
```

### Adding New Templates
1. Create template in `templates/`
2. Update generator configuration
3. Add tests for new template
4. Update documentation

## Support

For issues and feature requests:
- Check troubleshooting section
- Review template documentation
- Contact factory IT support

---

Generated with Industrial Frontend Assistant
Framework: {framework} | Template: {template} | Type: {interface_type}
"""
        return readme

    def _get_interface_description(self, interface_type: str, template: str) -> str:
        """Get description for the interface type and template."""
        descriptions = {
            "dashboard": {
                "pump-monitoring": "Real-time monitoring dashboard for industrial pump systems with performance metrics, alerts, and historical trends.",
                "system-overview": "Comprehensive factory system status dashboard showing equipment health, production metrics, and alert summaries.",
                "quality-control": "Quality metrics dashboard with statistical process control, trend analysis, and compliance monitoring.",
                "energy-monitoring": "Energy consumption and efficiency monitoring dashboard with cost analysis and optimization recommendations.",
            },
            "control-panel": {
                "equipment-control": "Touch-friendly control interface for industrial equipment with safety interlocks and status monitoring.",
                "valve-control": "Valve positioning and control interface with flow monitoring and automated sequencing capabilities.",
                "motor-control": "Motor speed and direction controls with load monitoring and protection features.",
                "hmi-interface": "Human-machine interface panel with configurable controls and real-time process visualization.",
            },
            "calculator": {
                "pipe-sizing": "Engineering calculator for industrial pipe sizing with flow rate, pressure drop, and velocity calculations.",
                "flow-calculator": "Flow rate and pressure calculations for fluid systems with unit conversions and validation.",
                "energy-calculator": "Energy consumption and efficiency calculations with cost analysis and carbon footprint tracking.",
                "conversion-tools": "Comprehensive unit conversion tools for industrial measurements and engineering calculations.",
            },
            "documentation": {
                "technical-manual": "Interactive technical documentation with search, bookmarks, and cross-reference capabilities.",
                "maintenance-guide": "Equipment maintenance procedures with step-by-step instructions and safety checklists.",
                "safety-procedures": "Safety protocol documentation with compliance tracking and emergency procedures.",
            },
        }
        return descriptions.get(interface_type, {}).get(
            template, f"Industrial {interface_type} for {template} applications."
        )

    def _format_features(self, features: list[str]) -> str:
        """Format features list for README."""
        if not features:
            return ""
        return "\n- **Additional Features** - " + " • ".join(features)

    def validate_config(self, project_config: dict[str, Any]) -> list[str]:
        """Validate project configuration.

        Args:
            project_config: Project configuration to validate

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        required_fields = ["type", "framework", "template", "factory_options", "theme"]
        for field in required_fields:
            if field not in project_config:
                errors.append(f"Missing required field: {field}")

        if "framework" in project_config and project_config["framework"] not in ["react", "vue", "streamlit"]:
            errors.append(f"Unsupported framework: {project_config['framework']}")

        if "type" in project_config:
            valid_types = ["dashboard", "control-panel", "calculator", "documentation"]
            if project_config["type"] not in valid_types:
                errors.append(f"Invalid interface type: {project_config['type']}")

        return errors
