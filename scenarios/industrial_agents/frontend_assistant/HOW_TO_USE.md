# How to Use Industrial Frontend Assistant

**Generate factory-ready industrial interfaces with minimal configuration.**

## Quick Start

### 1. Generate Your First Industrial Interface

```bash
# Generate a pump monitoring dashboard
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=react \
  TEMPLATE=pump-monitoring \
  OUTPUT=factory_dashboard/
```

### 2. Explore Available Templates

```bash
# List all available templates
make industrial-ui-list
```

### 3. Try the Example

```bash
# Generate a complete example with all features
make industrial-ui-example
```

## Complete Usage Guide

### Basic Interface Generation

#### Dashboards

**Pump Monitoring Dashboard:**
```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=react \
  TEMPLATE=pump-monitoring \
  OUTPUT=pump_dashboard/ \
  FACTORY_OPTS="touch-friendly high-contrast" \
  THEME=factory-dark
```

**System Overview Dashboard:**
```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=vue \
  TEMPLATE=system-overview \
  OUTPUT=system_dashboard/ \
  FACTORY_OPTS="touch-friendly offline-first"
```

#### Control Panels

**Equipment Control Interface:**
```bash
make industrial-ui \
  TYPE=control-panel \
  FRAMEWORK=react \
  TEMPLATE=equipment-control \
  OUTPUT=control_panel/ \
  FACTORY_OPTS="touch-friendly high-contrast" \
  DATA_SOURCE=mqtt
```

#### Engineering Calculators

**Pipe Sizing Calculator:**
```bash
make industrial-ui \
  TYPE=calculator \
  FRAMEWORK=react \
  TEMPLATE=pipe-sizing \
  OUTPUT=pipe_calculator/ \
  FACTORY_OPTS="touch-friendly"
```

#### Technical Documentation

**Interactive Technical Manual:**
```bash
make industrial-ui \
  TYPE=documentation \
  FRAMEWORK=react \
  TEMPLATE=technical-manual \
  OUTPUT=tech_manual/ \
  FACTORY_OPTS="high-contrast accessibility"
```

### Advanced Configuration

#### Complete Feature Set

```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=react \
  TEMPLATE=pump-monitoring \
  OUTPUT=advanced_dashboard/ \
  FACTORY_OPTS="touch-friendly high-contrast offline-first ruggedized" \
  THEME=factory-dark \
  DATA_SOURCE=mqtt \
  FEATURES="alerts export authentication"
```

#### Streamlit Prototypes

```bash
make industrial-ui \
  TYPE=dashboard \
  FRAMEWORK=streamlit \
  TEMPLATE=system-overview \
  OUTPUT=prototype_dashboard/ \
  DATA_SOURCE=mock
```

### Factory Environment Options

#### Touch-Friendly Interface
```bash
FACTORY_OPTS="touch-friendly"
```
- Minimum 44px touch targets
- Large buttons for gloved hands
- Gesture support (swipe, tap, pinch)
- Haptic feedback for confirmations

#### High Contrast Display
```bash
FACTORY_OPTS="high-contrast"
```
- Enhanced visibility in bright lighting
- WCAG 2.1 AA compliant contrast ratios
- Clear visual status indicators
- Color blindness support

#### Offline-First Design
```bash
FACTORY_OPTS="offline-first"
```
- Local data caching
- Graceful degradation when offline
- Queue operations until reconnection
- Service worker for offline functionality

#### Ruggedized Error Handling
```bash
FACTORY_OPTS="ruggedized"
```
- Robust error recovery
- Automatic reconnection
- Data buffering during interruptions
- Comprehensive logging

#### Accessibility Features
```bash
FACTORY_OPTS="accessibility"
```
- Screen reader support
- Keyboard navigation
- ARIA labels and landmarks
- Focus indicators

### Data Source Configuration

#### MQTT Integration
```bash
DATA_SOURCE=mqtt
```
Configures MQTT broker connection for real-time data.

#### REST API Integration
```bash
DATA_SOURCE=rest-api
```
Configures REST API endpoints for data retrieval.

#### WebSocket Integration
```bash
DATA_SOURCE=websocket
```
Configures WebSocket connections for real-time updates.

#### Mock Data (Development)
```bash
DATA_SOURCE=mock
```
Uses simulated data for development and testing.

### Theme Selection

#### Factory Dark Theme
```bash
THEME=factory-dark
```
- Dark background for reduced eye strain
- Orange industrial accents (#FF6B35)
- Blue status indicators (#004E89)

#### Factory Light Theme
```bash
THEME=factory-light
```
- Light background for bright environments
- High contrast elements
- Professional appearance

#### High Contrast Theme
```bash
THEME=high-contrast
```
- Maximum contrast ratios
- Black background with bright accents
- Optimal for variable lighting

### Feature Flags

#### Alert System
```bash
FEATURES="alerts"
```
- Real-time alert notifications
- Multiple alert levels (info, warning, critical)
- Alert acknowledgment and history

#### Data Export
```bash
FEATURES="export"
```
- Export metrics to CSV/PDF
- Report generation
- Data backup capabilities

#### Authentication
```bash
FEATURES="authentication"
```
- User login/logout
- Role-based access control
- Session management

#### Real-time Updates
```bash
FEATURES="real-time"
```
- Live data streaming
- Auto-refresh capabilities
- Connection status monitoring

## Post-Generation Setup

### 1. Navigate to Generated Project
```bash
cd your_generated_directory/
```

### 2. Install Dependencies
```bash
# For React/Vue projects
npm install

# For Streamlit projects
pip install -r requirements.txt
```

### 3. Configure Data Sources
Edit configuration files:
- React/Vue: `src/config/index.ts`
- Streamlit: `config/config.py`

### 4. Start Development Server
```bash
# React/Vue
npm run dev

# Streamlit
streamlit run app.py
```

### 5. Build for Production
```bash
# React/Vue
npm run build

# Streamlit (no build needed)
# Ready for deployment with Streamlit server
```

## Deployment Options

### Docker Deployment
```bash
# Build Docker image
docker build -t industrial-interface .

# Run with Docker Compose
docker-compose up -d
```

### Static Hosting
```bash
# Build static files
npm run build

# Deploy dist/ folder to any static hosting service
# - Netlify
# - Vercel
# - AWS S3 + CloudFront
# - GitHub Pages
```

### Factory Network Deployment
```bash
# Configure for factory network
# 1. Set appropriate CORS headers
# 2. Configure firewall rules
# 3. Set up MQTT broker if needed
# 4. Test network connectivity
```

## Troubleshooting

### Common Issues

#### "Template not found" Error
```bash
# Check available templates
make industrial-ui-list

# Verify template name spelling
# Template names use hyphens, not underscores
```

#### "Framework not supported" Error
```bash
# Supported frameworks: react, vue, streamlit
# Check spelling and case sensitivity
```

#### Connection Issues
```bash
# Check data source configuration
# Verify network connectivity
# Test MQTT/WebSocket endpoints
```

#### Performance Issues
```bash
# Reduce update frequency in config
# Enable data compression
# Check browser console for errors
# Monitor memory usage
```

### Getting Help

#### Validation Reports
After generation, check the `VALIDATION_REPORT.md` file in your output directory for detailed analysis of factory compliance.

#### Debug Mode
```bash
# Enable verbose logging
python -m scenarios.industrial_agents.frontend_assistant \
  --type dashboard \
  --framework react \
  --template pump-monitoring \
  --output debug_dashboard/ \
  --verbose
```

#### Factory Environment Testing
```bash
# Test on actual factory hardware
# Verify touch responsiveness
# Test in various lighting conditions
# Check network reliability
```

## Best Practices

### Development Workflow
1. **Start Simple**: Begin with mock data source
2. **Iterative Enhancement**: Add features incrementally
3. **Factory Testing**: Test on actual factory hardware early
4. **Performance Monitoring**: Monitor resource usage
5. **User Feedback**: Collect feedback from factory workers

### Interface Design
1. **Touch Targets**: Maintain minimum 44px touch targets
2. **Visual Hierarchy**: Use size and color for importance
3. **Status Indicators**: Clear visual states for equipment
4. **Error Prevention**: Confirmation dialogs for critical actions
5. **Accessibility**: Ensure keyboard navigation support

### Data Integration
1. **Error Handling**: Graceful degradation when data unavailable
2. **Caching**: Local storage for offline periods
3. **Update Rates**: Balance real-time needs with performance
4. **Security**: Secure MQTT/WebSocket connections
5. **Monitoring**: Log connection issues and data quality

### Performance Optimization
1. **Bundle Size**: Minimize JavaScript bundle size
2. **Image Optimization**: Compress industrial diagrams
3. **Caching**: Enable browser caching for static assets
4. **Lazy Loading**: Load charts and heavy components on demand
5. **Memory Management**: Prevent memory leaks in real-time updates

## Integration Examples

### MQTT Integration
```typescript
// src/config/index.ts
export const mqttConfig = {
  broker: 'mqtt://factory-broker:1883',
  topics: ['factory/equipment/pump01/data'],
  clientId: 'industrial-dashboard',
  options: {
    username: process.env.VITE_MQTT_USERNAME,
    password: process.env.VITE_MQTT_PASSWORD,
    keepalive: 60,
  }
}
```

### REST API Integration
```typescript
// src/config/index.ts
export const apiConfig = {
  baseUrl: process.env.VITE_API_BASE_URL || 'https://api.factory.local',
  endpoints: {
    metrics: '/api/v1/metrics',
    equipment: '/api/v1/equipment',
    alerts: '/api/v1/alerts',
  },
  timeout: 5000,
  retryAttempts: 3,
}
```

### Custom Industrial Components
```typescript
// src/components/IndustrialGauge.tsx
import React from 'react';

interface IndustrialGaugeProps {
  value: number;
  min: number;
  max: number;
  unit: string;
  status: 'normal' | 'warning' | 'critical';
}

export const IndustrialGauge: React.FC<IndustrialGaugeProps> = ({
  value,
  min,
  max,
  unit,
  status
}) => {
  const percentage = ((value - min) / (max - min)) * 100;

  return (
    <div className={`industrial-gauge status-${status}`}>
      <div className="gauge-value">{value.toFixed(1)}</div>
      <div className="gauge-unit">{unit}</div>
      <div className="gauge-bar">
        <div
          className="gauge-fill"
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
};
```

---

This guide covers all essential aspects of using the Industrial Frontend Assistant. For specific technical implementation details, refer to the generated project's README.md file and the validation report.