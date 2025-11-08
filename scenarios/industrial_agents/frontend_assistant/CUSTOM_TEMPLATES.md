# Creating Custom Templates

**Guide to creating and customizing industrial interface templates.**

## Template Architecture

### Template Structure
```
templates/
├── dashboard/
│   ├── custom-dashboard/
│   │   ├── metadata.json
│   │   ├── components/
│   │   ├── styles/
│   │   └── config/
├── control-panel/
├── calculator/
└── documentation/
```

### Template Components
1. **Metadata**: Template configuration and description
2. **Components**: Framework-specific component implementations
3. **Styles**: CSS/styling files
4. **Configuration**: Default configuration values
5. **Assets**: Images, icons, and other static assets

## Creating a New Template

### Step 1: Define Template Metadata

Create `templates/dashboard/custom-dashboard/metadata.json`:

```json
{
  "name": "custom-dashboard",
  "description": "Custom industrial dashboard for specific equipment",
  "interface_type": "dashboard",
  "category": "monitoring",
  "supported_frameworks": ["react", "vue", "streamlit"],
  "factory_requirements": ["touch-friendly", "high-contrast"],
  "data_sources": ["mqtt", "rest-api", "websocket"],
  "features": ["real-time", "alerts", "export"],
  "components": {
    "react": ["DashboardLayout", "MetricCard", "ChartPanel", "AlertPanel"],
    "vue": ["DashboardLayout.vue", "MetricCard.vue", "ChartPanel.vue"],
    "streamlit": ["dashboard_layout", "metric_card", "chart_panel"]
  },
  "config_schema": {
    "update_interval": {
      "type": "number",
      "default": 5000,
      "min": 1000,
      "max": 60000,
      "description": "Data update interval in milliseconds"
    },
    "max_alerts": {
      "type": "number",
      "default": 50,
      "min": 10,
      "max": 200,
      "description": "Maximum number of alerts to display"
    }
  }
}
```

### Step 2: Create React Components

#### Main Dashboard Component
`templates/dashboard/custom-dashboard/components/react/DashboardLayout.tsx`:

```typescript
import React from 'react';
import { Grid, Paper, Typography, Box } from '@mui/material';
import { MetricCard } from './MetricCard';
import { ChartPanel } from './ChartPanel';
import { AlertPanel } from './AlertPanel';
import { useCustomData } from '../../hooks/useCustomData';

interface CustomDashboardProps {
  config: {
    updateInterval: number;
    maxAlerts: number;
    equipmentIds: string[];
  };
}

export const DashboardLayout: React.FC<CustomDashboardProps> = ({ config }) => {
  const { data, isLoading, error } = useCustomData(config);

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Typography color="error" variant="h5">
          Connection Error: {error}
        </Typography>
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 4 }}>
        🏭 Custom Equipment Dashboard
      </Typography>

      <Grid container spacing={3}>
        {/* Metrics Row */}
        <Grid item xs={12}>
          <Paper elevation={3} sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Real-time Metrics
            </Typography>
            <Grid container spacing={2}>
              {data.equipment.map((equipment) => (
                <Grid item xs={12} md={6} lg={3} key={equipment.id}>
                  <MetricCard equipment={equipment} />
                </Grid>
              ))}
            </Grid>
          </Paper>
        </Grid>

        {/* Charts Row */}
        <Grid item xs={12} md={8}>
          <Paper elevation={3} sx={{ p: 3, minHeight: 400 }}>
            <ChartPanel
              data={data.historical}
              config={config}
            />
          </Paper>
        </Grid>

        {/* Alerts Panel */}
        <Grid item xs={12} md={4}>
          <Paper elevation={3} sx={{ p: 3, minHeight: 400 }}>
            <AlertPanel
              alerts={data.alerts.slice(0, config.maxAlerts)}
            />
          </Paper>
        </Grid>
      </Grid>
    </Box>
  );
};
```

#### Metric Card Component
`templates/dashboard/custom-dashboard/components/react/MetricCard.tsx`:

```typescript
import React from 'react';
import { Box, Typography, LinearProgress } from '@mui/material';

interface MetricCardProps {
  equipment: {
    id: string;
    name: string;
    metrics: {
      pressure: number;
      temperature: number;
      efficiency: number;
      status: 'normal' | 'warning' | 'critical';
    };
  };
}

export const MetricCard: React.FC<MetricCardProps> = ({ equipment }) => {
  const { metrics } = equipment;

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'critical': return '#D32F2F';
      case 'warning': return '#F57C00';
      default: return '#4CAF50';
    }
  };

  return (
    <Box
      sx={{
        border: `2px solid ${getStatusColor(metrics.status)}`,
        borderRadius: 2,
        p: 2,
        minHeight: 200,
        backgroundColor: '#2A2A2A',
      }}
    >
      <Typography variant="h6" gutterBottom sx={{ textAlign: 'center' }}>
        {equipment.name}
      </Typography>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Pressure
        </Typography>
        <Typography variant="h5" color={getStatusColor(metrics.status)}>
          {metrics.pressure.toFixed(1)} PSI
        </Typography>
      </Box>

      <Box sx={{ mb: 2 }}>
        <Typography variant="body2" color="text.secondary">
          Temperature
        </Typography>
        <Typography variant="h5" color="text.primary">
          {metrics.temperature.toFixed(1)}°F
        </Typography>
      </Box>

      <Box>
        <Typography variant="body2" color="text.secondary">
          Efficiency
        </Typography>
        <LinearProgress
          variant="determinate"
          value={metrics.efficiency}
          sx={{
            height: 8,
            borderRadius: 4,
            backgroundColor: '#444',
            '& .MuiLinearProgress-bar': {
              backgroundColor: metrics.efficiency > 80 ? '#4CAF50' : '#F57C00',
            },
          }}
        />
        <Typography variant="body2" sx={{ mt: 1 }}>
          {metrics.efficiency.toFixed(1)}%
        </Typography>
      </Box>
    </Box>
  );
};
```

### Step 3: Create Vue Components

#### Vue Dashboard Component
`templates/dashboard/custom-dashboard/components/vue/DashboardLayout.vue`:

```vue
<template>
  <div class="custom-dashboard">
    <header class="dashboard-header">
      <h1>🏭 Custom Equipment Dashboard</h1>
      <div class="connection-status" :class="statusClass">
        {{ connectionStatus }}
      </div>
    </header>

    <main class="dashboard-main">
      <!-- Metrics Section -->
      <section class="metrics-section">
        <h2>Real-time Metrics</h2>
        <div class="metrics-grid">
          <MetricCard
            v-for="equipment in equipmentData"
            :key="equipment.id"
            :equipment="equipment"
          />
        </div>
      </section>

      <!-- Charts Section -->
      <section class="charts-section">
        <ChartPanel
          :data="historicalData"
          :config="chartConfig"
        />
      </section>

      <!-- Alerts Section -->
      <section class="alerts-section">
        <AlertPanel
          :alerts="alertsData"
          :max-alerts="maxAlerts"
        />
      </section>
    </main>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useCustomData } from '../../composables/useCustomData'
import MetricCard from './MetricCard.vue'
import ChartPanel from './ChartPanel.vue'
import AlertPanel from './AlertPanel.vue'

interface Props {
  config: {
    updateInterval: number
    maxAlerts: number
    equipmentIds: string[]
  }
}

const props = defineProps<Props>()

// Data composable
const { data, isLoading, error } = useCustomData(props.config)

// Reactive state
const updateInterval = ref<NodeJS.Timeout>()

// Computed properties
const connectionStatus = computed(() => {
  if (error.value) return 'Connection Error'
  if (isLoading.value) return 'Connecting...'
  return 'Connected'
})

const statusClass = computed(() => {
  if (error.value) return 'error'
  return 'connected'
})

const equipmentData = computed(() => data.value?.equipment || [])
const historicalData = computed(() => data.value?.historical || [])
const alertsData = computed(() => data.value?.alerts || [])
const chartConfig = computed(() => ({
  updateInterval: props.config.updateInterval,
  maxDataPoints: 50,
}))

// Lifecycle
onMounted(() => {
  // Start real-time updates
  updateInterval.value = setInterval(() => {
    // Data updates handled by composable
  }, props.config.updateInterval)
})

onUnmounted(() => {
  if (updateInterval.value) {
    clearInterval(updateInterval.value)
  }
})
</script>

<style scoped>
.custom-dashboard {
  min-height: 100vh;
  background-color: #1A1A1A;
  color: #FFFFFF;
  font-family: 'Roboto Mono', monospace;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 2rem;
  background-color: #2A2A2A;
  border-bottom: 2px solid #FF6B35;
}

.dashboard-header h1 {
  font-size: 1.5rem;
  font-weight: 600;
  color: #FF6B35;
  margin: 0;
}

.connection-status {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}

.connection-status.connected {
  background-color: #4CAF50;
  color: white;
}

.connection-status.error {
  background-color: #D32F2F;
  color: white;
}

.dashboard-main {
  padding: 2rem;
}

.metrics-section,
.charts-section,
.alerts-section {
  margin-bottom: 2rem;
}

.metrics-section h2 {
  font-size: 1.2rem;
  margin-bottom: 1rem;
  color: #FF6B35;
}

.metrics-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
}
</style>
```

### Step 4: Create Streamlit Components

#### Streamlit Dashboard
`templates/dashboard/custom-dashboard/components/streamlit/dashboard_layout.py`:

```python
import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, timedelta

def render_dashboard(config):
    """Render the custom dashboard layout."""

    # Header
    st.title("🏭 Custom Equipment Dashboard")

    # Connection status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**System Status:**")
    with col2:
        st.success("Connected")
    with col3:
        st.markdown(f"Last Update: {datetime.now().strftime('%H:%M:%S')}")

    # Get data (this would come from your data source)
    data = get_equipment_data(config)

    # Metrics section
    st.subheader("📊 Real-time Metrics")
    render_metrics_grid(data['equipment'])

    # Charts section
    st.subheader("📈 Historical Trends")
    render_charts(data['historical'], config)

    # Alerts section
    st.subheader("🚨 Active Alerts")
    render_alerts(data['alerts'], config['max_alerts'])

def render_metrics_grid(equipment_list):
    """Render equipment metrics in a grid layout."""
    cols = st.columns(4)

    for i, equipment in enumerate(equipment_list):
        with cols[i % 4]:
            render_metric_card(equipment)

def render_metric_card(equipment):
    """Render a single equipment metric card."""
    status_color = {
        'normal': '#4CAF50',
        'warning': '#F57C00',
        'critical': '#D32F2F'
    }.get(equipment['status'], '#757575')

    st.markdown(f"""
    <div style="
        background-color: #2A2A2A;
        border: 2px solid {status_color};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    ">
        <div style="font-size: 1rem; color: #B0B0B0; margin-bottom: 0.5rem;">
            {equipment['name']}
        </div>
        <div style="font-size: 1.5rem; font-weight: bold; color: {status_color};">
            {equipment['metrics']['pressure']:.1f} PSI
        </div>
        <div style="font-size: 0.9rem; color: #B0B0B0;">
            {equipment['metrics']['temperature']:.1f}°F
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_charts(historical_data, config):
    """Render historical data charts."""
    if not historical_data:
        st.info("No historical data available")
        return

    df = pd.DataFrame(historical_data)

    # Create chart
    fig = px.line(
        df,
        x='timestamp',
        y=['pressure', 'temperature'],
        title="Equipment Metrics Over Time",
        labels={
            'timestamp': 'Time',
            'value': 'Value',
            'variable': 'Metric'
        }
    )

    fig.update_layout(
        template="plotly_dark",
        height=400,
        showlegend=True
    )

    st.plotly_chart(fig, use_container_width=True)

def render_alerts(alerts, max_alerts):
    """Render alerts panel."""
    if not alerts:
        st.success("No active alerts")
        return

    limited_alerts = alerts[:max_alerts]

    for alert in limited_alerts:
        level_color = {
            'info': '#2196F3',
            'warning': '#F57C00',
            'critical': '#D32F2F'
        }.get(alert['level'], '#757575')

        level_icon = {
            'info': 'ℹ️',
            'warning': '⚠️',
            'critical': '🚨'
        }.get(alert['level'], 'ℹ️')

        st.markdown(f"""
        <div style="
            background-color: {level_color}20;
            border-left: 6px solid {level_color};
            padding: 1rem;
            margin: 0.5rem 0;
            border-radius: 4px;
        ">
            <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
                <span style="font-size: 1.2rem; margin-right: 8px;">{level_icon}</span>
                <strong style="color: {level_color}; text-transform: uppercase;">
                    {alert['level']}
                </strong>
                <span style="margin-left: auto; color: #B0B0B0; font-size: 0.9rem;">
                    {alert['timestamp']}
                </span>
            </div>
            <div>{alert['message']}</div>
        </div>
        """, unsafe_allow_html=True)

def get_equipment_data(config):
    """Get equipment data (mock implementation)."""
    # This would connect to your actual data source
    import random

    return {
        'equipment': [
            {
                'id': 'pump-01',
                'name': 'Pump 1',
                'status': 'normal',
                'metrics': {
                    'pressure': 100 + random.uniform(-20, 30),
                    'temperature': 150 + random.uniform(-10, 20),
                }
            },
            {
                'id': 'pump-02',
                'name': 'Pump 2',
                'status': 'warning',
                'metrics': {
                    'pressure': 130 + random.uniform(-10, 20),
                    'temperature': 180 + random.uniform(-5, 15),
                }
            }
        ],
        'historical': [
            {
                'timestamp': (datetime.now() - timedelta(minutes=i)).isoformat(),
                'pressure': 100 + random.uniform(-20, 30),
                'temperature': 150 + random.uniform(-10, 20),
            }
            for i in range(50, 0, -1)
        ],
        'alerts': [
            {
                'level': 'warning',
                'message': 'Elevated pressure detected on Pump 2',
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        ]
    }
```

### Step 5: Create Styles and Configuration

#### CSS Styles
`templates/dashboard/custom-dashboard/styles/industrial.css`:

```css
/* Custom Industrial Dashboard Styles */

:root {
  --primary-color: #FF6B35;
  --secondary-color: #004E89;
  --success-color: #4CAF50;
  --warning-color: #F57C00;
  --error-color: #D32F2F;
  --background-color: #1A1A1A;
  --surface-color: #2A2A2A;
  --text-color: #FFFFFF;
}

/* Custom metric card styles */
.custom-metric-card {
  background-color: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  padding: 1rem;
  transition: all 0.2s ease;
}

.custom-metric-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

/* Custom chart styles */
.custom-chart {
  background-color: var(--surface-color);
  border-radius: 8px;
  padding: 1rem;
  min-height: 400px;
}

/* Custom alert styles */
.custom-alert {
  border-left: 6px solid var(--warning-color);
  background-color: var(--warning-color)20;
  padding: 1rem;
  margin: 0.5rem 0;
  border-radius: 4px;
}

.custom-alert.critical {
  border-left-color: var(--error-color);
  background-color: var(--error-color)20;
}

/* Touch-friendly styles */
.touch-button {
  min-width: 60px;
  min-height: 60px;
  padding: 15px;
  font-size: 18px;
  font-weight: 600;
  border: 3px solid var(--primary-color);
  border-radius: 8px;
  background-color: var(--surface-color);
  color: var(--text-color);
  cursor: pointer;
  transition: all 0.2s ease;
}

.touch-button:hover {
  background-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
}

/* High contrast styles */
.high-contrast {
  --primary-color: #FF8C42;
  --secondary-color: #0066CC;
  --background-color: #000000;
  --surface-color: #1A1A1A;
}

/* Responsive design */
@media (max-width: 768px) {
  .custom-metric-card {
    margin: 0.25rem 0;
    padding: 0.75rem;
  }

  .touch-button {
    min-width: 50px;
    min-height: 50px;
    font-size: 16px;
  }
}
```

#### Default Configuration
`templates/dashboard/custom-dashboard/config/defaults.json`:

```json
{
  "update_interval": 5000,
  "max_alerts": 50,
  "equipment_ids": ["pump-01", "pump-02", "pump-03"],
  "thresholds": {
    "pressure": {
      "warning": 120,
      "critical": 150
    },
    "temperature": {
      "warning": 180,
      "critical": 200
    },
    "efficiency": {
      "warning": 70,
      "critical": 50
    }
  },
  "chart_config": {
    "max_data_points": 50,
    "refresh_interval": 1000,
    "animation_duration": 300
  },
  "theme": {
    "primary_color": "#FF6B35",
    "secondary_color": "#004E89",
    "background_color": "#1A1A1A",
    "surface_color": "#2A2A2A"
  },
  "factory_options": {
    "touch_friendly": true,
    "high_contrast": false,
    "offline_first": true,
    "ruggedized": true
  }
}
```

## Template Registration

### Register Template with Generator Factory

Update `generators/generator_factory.py` to include custom templates:

```python
def load_custom_templates(self):
    """Load custom templates from templates directory."""
    custom_templates = {}

    template_dir = Path(__file__).parent.parent / "templates"

    for interface_type in template_dir.iterdir():
        if interface_type.is_dir():
            custom_templates[interface_type.name] = {}
            for template_dir in interface_type.iterdir():
                if template_dir.is_dir():
                    metadata_file = template_dir / "metadata.json"
                    if metadata_file.exists():
                        with open(metadata_file) as f:
                            metadata = json.load(f)
                            custom_templates[interface_type.name][metadata["name"]] = metadata

    return custom_templates
```

## Testing Custom Templates

### Unit Tests
Create tests for your custom components:

```typescript
// tests/components/DashboardLayout.test.tsx
import { render, screen } from '@testing-library/react'
import { DashboardLayout } from '../components/DashboardLayout'

describe('DashboardLayout', () => {
  const mockConfig = {
    updateInterval: 5000,
    maxAlerts: 50,
    equipmentIds: ['pump-01', 'pump-02']
  }

  test('renders dashboard header', () => {
    render(<DashboardLayout config={mockConfig} />)

    expect(screen.getByText('Custom Equipment Dashboard')).toBeInTheDocument()
  })

  test('displays connection status', () => {
    render(<DashboardLayout config={mockConfig} />)

    expect(screen.getByText(/Connected|Connecting|Connection Error/)).toBeInTheDocument()
  })
})
```

### Integration Tests
Test the complete template with data:

```python
# tests/test_custom_template.py
import pytest
from templates.dashboard.custom_dashboard.components.streamlit.dashboard_layout import render_dashboard

def test_custom_dashboard_render():
    """Test that custom dashboard renders correctly."""
    config = {
        'update_interval': 5000,
        'max_alerts': 10,
        'equipment_ids': ['test-pump']
    }

    # This would need a Streamlit testing framework
    # For now, just test that the function exists and doesn't error
    assert callable(render_dashboard)
    assert 'config' in render_dashboard.__code__.co_varnames
```

## Best Practices

### Template Design Principles
1. **Modularity**: Keep components small and focused
2. **Reusability**: Design components for reuse across templates
3. **Configuration**: Make templates configurable through JSON
4. **Factory First**: Prioritize factory environment requirements
5. **Accessibility**: Ensure WCAG compliance from the start

### Code Organization
1. **Separation of Concerns**: Separate data, presentation, and business logic
2. **Type Safety**: Use TypeScript or proper type hints
3. **Error Handling**: Graceful error handling and user feedback
4. **Performance**: Optimize for real-time updates and large datasets
5. **Testing**: Comprehensive unit and integration tests

### Documentation
1. **README**: Clear setup and usage instructions
2. **API Documentation**: Complete API documentation for components
3. **Examples**: Working examples for common use cases
4. **Configuration Guide**: Detailed configuration options
5. **Troubleshooting**: Common issues and solutions

---

By following these guidelines, you can create robust, reusable industrial interface templates that meet factory environment requirements and can be easily customized for specific use cases.