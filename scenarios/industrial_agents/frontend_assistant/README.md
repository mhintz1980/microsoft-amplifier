# Industrial Frontend Assistant

**Generate industrial-grade dashboards, control panels, and engineering interfaces optimized for factory environments.**

## The Problem

Industrial frontend development has unique challenges that standard web tools don't address:

- **Factory environment constraints** - Touch screens, high-noise environments, variable lighting
- **Real-time requirements** - Monitoring dashboards need efficient data streaming
- **Engineering workflows** - Calculators, technical documentation, control interfaces
- **Accessibility needs** - Large touch targets for gloved hands, high contrast displays
- **Offline capability** - Network connectivity can be unreliable in industrial settings

## The Solution

Industrial Frontend Assistant generates production-ready interfaces with:

1. **Factory-optimized components** - Touch-friendly controls, high contrast themes, rugged design
2. **Multi-framework support** - React, Vue, and Streamlit templates for different use cases
3. **Real-time data handling** - Efficient streaming for monitoring dashboards
4. **Engineering tools** - Calculators, configuration panels, technical documentation
5. **Environment validation** - Ensures interfaces work in factory conditions
6. **Offline-first design** - Graceful degradation when network unavailable

## Quick Start

**Prerequisites**: Complete the [Amplifier setup instructions](../../../README.md#-step-by-step-setup) first.

### Basic Usage

```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=react \
  OUTPUT=my_dashboard/
```

### Available Interface Types

- **dashboard** - Real-time monitoring dashboards
- **control-panel** - Touch-friendly control interfaces
- **calculator** - Engineering calculation tools
- **documentation** - Interactive technical documentation

### Supported Frameworks

- **react** - Modern React applications with TypeScript
- **vue** - Vue.js applications with Composition API
- **streamlit** - Python-based data apps for quick prototypes

## Usage Examples

### Generate a Pump Monitoring Dashboard

```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=react \
  TEMPLATE=pump-monitoring \
  OUTPUT=factory_dashboard/
```

**Creates**: Complete React dashboard with real-time pump metrics, alerts, and controls.

### Create Engineering Calculator

```bash
make industrial-ui \
  TYPE=calculator \
  FRAMEWORK=vue \
  TEMPLATE=pipe-sizing \
  OUTPUT=engineering_tools/
```

**Creates**: Vue-based calculator for pipe sizing with industrial validation.

### Build Control Panel for Factory Equipment

```bash
make industrial-ui \
  TYPE=control-panel \
  FRAMEWORK=react \
  TEMPLATE=equipment-control \
  OUTPUT=control_interface/ \
  FACTORY_OPTS=touch-friendly,high-contrast
```

**Creates**: Touch-optimized control panel with large buttons and clear visual feedback.

### Quick Streamlit Prototype

```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=streamlit \
  TEMPLATE=system-monitoring \
  OUTPUT=prototype/
```

**Creates**: Fast Streamlit prototype for data visualization and testing.

## Factory Environment Features

### Touch Interface Optimization
- **Large touch targets** - Minimum 44px for gloved hands
- **Gesture support** - Swipe, pinch, and tap interactions
- **Haptic feedback** - Vibration responses for confirmations
- **Error prevention** - Confirmation dialogs for critical actions

### High Contrast Themes
- **Factory lighting** - Optimized for bright, variable conditions
- **Color blindness support** - High contrast patterns
- **Status indicators** - Clear visual states (normal/warning/critical)
- **Accessibility** - Screen reader and keyboard navigation

### Real-time Data Streaming
- **WebSocket connections** - Efficient real-time updates
- **Offline caching** - Local storage for network interruptions
- **Data buffering** - Smooth UI during connectivity issues
- **Error recovery** - Automatic reconnection with state preservation

### Engineering Calculations
- **Unit conversions** - Built-in support for metric/imperial
- **Technical validation** - Industry-standard calculation checks
- **Formula library** - Common engineering calculations
- **Export capabilities** - Results in CSV, PDF formats

## Configuration

### Command-Line Options

```bash
# Required
--type TYPE              # Interface type (dashboard, control-panel, calculator, documentation)
--framework FRAMEWORK    # Target framework (react, vue, streamlit)
--template TEMPLATE      # Specific template (pump-monitoring, pipe-sizing, etc.)
--output PATH            # Output directory for generated code

# Optional
--factory-opts OPTS      # Factory optimizations (touch-friendly, high-contrast, offline-first)
--theme THEME           # Color theme (factory-dark, factory-light, high-contrast)
--data-source SOURCE    # Data source configuration (mqtt, rest-api, websocket)
--features FEATURES      # Additional features (alerts, export, authentication)
--responsive            # Enable responsive design for different screen sizes
--offline-support       # Add offline capabilities
```

### Factory Environment Options

- **touch-friendly** - Large touch targets, gesture support
- **high-contrast** - Enhanced visibility in bright lighting
- **offline-first** - Local storage and graceful degradation
- **ruggedized** - Error handling for harsh environments
- **accessibility** - Screen reader and keyboard navigation

## Generated Code Structure

```
output_directory/
├── README.md                 # Setup and usage instructions
├── package.json             # Dependencies and scripts
├── src/
│   ├── components/          # Industrial-grade components
│   ├── hooks/              # Custom hooks for real-time data
│   ├── utils/              # Engineering utilities
│   ├── styles/             # Factory-optimized styles
│   └── types/              # TypeScript definitions
├── public/                 # Static assets
├── tests/                  # Component tests
└── docs/                   # Component documentation
```

## Templates

### Dashboard Templates
- **pump-monitoring** - Industrial pump performance dashboard
- **system-overview** - Factory system status overview
- **quality-control** - Quality metrics and trending
- **energy-monitoring** - Power consumption and efficiency

### Control Panel Templates
- **equipment-control** - Generic equipment control interface
- **valve-control** - Valve positioning and monitoring
- **motor-control** - Motor speed and direction controls
- **hmi-interface** - Human-machine interface panels

### Calculator Templates
- **pipe-sizing** - Industrial pipe sizing calculations
- **flow-calculator** - Flow rate and pressure calculations
- **energy-calculator** - Energy consumption and efficiency
- **conversion-tools** - Unit conversion utilities

### Documentation Templates
- **technical-manual** - Interactive technical documentation
- **maintenance-guide** - Equipment maintenance procedures
- **safety-procedures** - Safety protocol documentation
- **training-materials** - Interactive training content

## Validation Tools

The assistant includes built-in validation for factory environments:

- **Touch target validation** - Ensures buttons meet minimum size requirements
- **Contrast ratio checking** - Verifies text visibility in factory lighting
- **Performance testing** - Validates real-time data handling
- **Accessibility compliance** - WCAG 2.1 AA standard checking
- **Offline functionality** - Tests graceful degradation scenarios

## Architecture

### Generation Pipeline

```
Interface Requirements
         ↓
   [Template Selection]
         ↓
   [Factory Optimization]
         ↓
   [Code Generation]
         ↓
   [Validation & Testing]
         ↓
    Production-Ready Interface
```

### Key Components

- **Template Engine** - Converts specifications to framework-specific code
- **Factory Optimizer** - Applies industrial environment constraints
- **Component Generator** - Creates reusable industrial components
- **Validation Suite** - Ensures factory-ready quality standards
- **Theme System** - Manages industrial color schemes and typography

## Learn More

- **[TROUBLESHOOTING.md](./TROUBLESHOOTING.md)** - Common issues and solutions
- **[CUSTOM_TEMPLATES.md](./CUSTOM_TEMPLATES.md)** - Creating your own templates
- **[FACTORY_GUIDELINES.md](./FACTORY_GUIDELINES.md)** - Industrial design guidelines
- **[Amplifier](https://github.com/microsoft/amplifier)** - The framework that powers this tool

## What's Next?

This tool demonstrates amplifier's capability to generate specialized industrial interfaces:

1. **Use it** - Generate factory-ready interfaces for your projects
2. **Extend it** - Add custom templates for your specific industry
3. **Learn from it** - Study the template system and validation approach
4. **Build your own** - Create specialized generators for other domains

---

**Built with minimal input using Amplifier** - Generated from requirements and industrial best practices.