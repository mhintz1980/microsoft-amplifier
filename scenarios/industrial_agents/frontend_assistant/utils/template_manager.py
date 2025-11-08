"""
Template Manager for Industrial UI Templates

Manages templates for different interface types, frameworks, and industrial use cases.
"""

from dataclasses import dataclass
from typing import Any


@dataclass
class TemplateConfig:
    """Configuration for a template."""

    name: str
    description: str
    interface_type: str
    framework: str
    files: dict[str, str]  # file_path -> template_content
    dependencies: dict[str, list[str]]  # framework -> dependencies
    config: dict[str, Any]  # additional configuration


class TemplateManager:
    """Manages industrial UI templates."""

    def __init__(self):
        """Initialize template manager with built-in templates."""
        self.templates = self._load_builtin_templates()

    def _load_builtin_templates(self) -> dict[str, dict[str, TemplateConfig]]:
        """Load built-in industrial templates."""
        templates = {
            "dashboard": {
                "react": {
                    "pump-monitoring": self._pump_monitoring_react(),
                    "system-overview": self._system_overview_react(),
                    "quality-control": self._quality_control_react(),
                    "energy-monitoring": self._energy_monitoring_react(),
                },
                "vue": {
                    "pump-monitoring": self._pump_monitoring_vue(),
                    "system-overview": self._system_overview_vue(),
                    "quality-control": self._quality_control_vue(),
                },
                "streamlit": {
                    "pump-monitoring": self._pump_monitoring_streamlit(),
                    "system-overview": self._system_overview_streamlit(),
                },
            },
            "control-panel": {
                "react": {
                    "equipment-control": self._equipment_control_react(),
                    "valve-control": self._valve_control_react(),
                    "motor-control": self._motor_control_react(),
                    "hmi-interface": self._hmi_interface_react(),
                },
                "vue": {
                    "equipment-control": self._equipment_control_vue(),
                    "valve-control": self._valve_control_vue(),
                },
            },
            "calculator": {
                "react": {
                    "pipe-sizing": self._pipe_sizing_react(),
                    "flow-calculator": self._flow_calculator_react(),
                    "energy-calculator": self._energy_calculator_react(),
                    "conversion-tools": self._conversion_tools_react(),
                },
                "vue": {
                    "pipe-sizing": self._pipe_sizing_vue(),
                    "flow-calculator": self._flow_calculator_vue(),
                },
            },
            "documentation": {
                "react": {
                    "technical-manual": self._technical_manual_react(),
                    "maintenance-guide": self._maintenance_guide_react(),
                    "safety-procedures": self._safety_procedures_react(),
                },
                "streamlit": {
                    "technical-manual": self._technical_manual_streamlit(),
                    "training-materials": self._training_materials_streamlit(),
                },
            },
        }
        return templates

    def get_template(self, interface_type: str, framework: str, template_name: str) -> TemplateConfig | None:
        """Get template configuration.

        Args:
            interface_type: Type of interface (dashboard, control-panel, etc.)
            framework: Target framework (react, vue, streamlit)
            template_name: Name of the template

        Returns:
            TemplateConfig or None if not found
        """
        return self.templates.get(interface_type, {}).get(framework, {}).get(template_name)

    def list_templates(self) -> dict[str, dict[str, dict[str, str]]]:
        """List all available templates.

        Returns:
            Dictionary of available templates by type and framework
        """
        result = {}
        for interface_type, frameworks in self.templates.items():
            result[interface_type] = {}
            for framework, templates in frameworks.items():
                result[interface_type][framework] = {name: template.description for name, template in templates.items()}
        return result

    # Dashboard Templates

    def _pump_monitoring_react(self) -> TemplateConfig:
        """React pump monitoring dashboard template."""
        return TemplateConfig(
            name="pump-monitoring",
            description="Real-time pump performance monitoring dashboard",
            interface_type="dashboard",
            framework="react",
            files={
                "src/App.tsx": self._get_pump_monitoring_app_react(),
                "src/components/PumpMetrics.tsx": self._get_pump_metrics_component(),
                "src/components/PumpChart.tsx": self._get_pump_chart_component(),
                "src/hooks/usePumpData.ts": self._get_pump_data_hook(),
                "src/styles/industrial.css": self._get_industrial_styles(),
            },
            dependencies={
                "react": ["react", "react-dom", "typescript"],
                "charts": ["recharts", "chart.js"],
                "real-time": ["socket.io-client", "mqtt-react-hooks"],
                "ui": ["@mui/material", "@emotion/react", "@emotion/styled"],
            },
            config={
                "real_time": True,
                "data_points": ["pressure", "flow_rate", "temperature", "vibration"],
                "alerts": ["high_pressure", "low_flow", "overheating", "excessive_vibration"],
                "refresh_rate": 1000,  # ms
            },
        )

    def _system_overview_react(self) -> TemplateConfig:
        """React system overview dashboard template."""
        return TemplateConfig(
            name="system-overview",
            description="Factory system status overview dashboard",
            interface_type="dashboard",
            framework="react",
            files={
                "src/App.tsx": self._get_system_overview_app_react(),
                "src/components/SystemStatus.tsx": self._get_system_status_component(),
                "src/components/AlertPanel.tsx": self._get_alert_panel_component(),
                "src/styles/industrial.css": self._get_industrial_styles(),
            },
            dependencies={
                "react": ["react", "react-dom", "typescript"],
                "ui": ["@mui/material", "@emotion/react"],
                "real-time": ["mqtt-react-hooks"],
            },
            config={
                "grid_layout": True,
                "system_components": ["pumps", "valves", "tanks", "sensors"],
                "alert_levels": ["info", "warning", "critical"],
            },
        )

    # Control Panel Templates

    def _equipment_control_react(self) -> TemplateConfig:
        """React equipment control panel template."""
        return TemplateConfig(
            name="equipment-control",
            description="Touch-friendly equipment control interface",
            interface_type="control-panel",
            framework="react",
            files={
                "src/App.tsx": self._get_equipment_control_app_react(),
                "src/components/ControlButton.tsx": self._get_control_button_component(),
                "src/components/StatusIndicator.tsx": self._get_status_indicator_component(),
                "src/styles/touch-friendly.css": self._get_touch_friendly_styles(),
            },
            dependencies={
                "react": ["react", "react-dom", "typescript"],
                "ui": ["@mui/material", "@emotion/react"],
                "touch": ["hammerjs"],
            },
            config={
                "touch_targets": True,
                "min_button_size": "44px",
                "haptic_feedback": True,
                "confirmation_dialogs": True,
            },
        )

    # Calculator Templates

    def _pipe_sizing_react(self) -> TemplateConfig:
        """React pipe sizing calculator template."""
        return TemplateConfig(
            name="pipe-sizing",
            description="Industrial pipe sizing calculation tool",
            interface_type="calculator",
            framework="react",
            files={
                "src/App.tsx": self._get_pipe_sizing_app_react(),
                "src/components/CalculatorForm.tsx": self._get_calculator_form_component(),
                "src/utils/pipeCalculations.ts": self._get_pipe_calculations(),
                "src/styles/calculator.css": self._get_calculator_styles(),
            },
            dependencies={
                "react": ["react", "react-dom", "typescript"],
                "validation": ["yup"],
                "ui": ["@mui/material"],
            },
            config={
                "calculations": ["flow_rate", "pressure_drop", "velocity", "reynolds_number"],
                "units": ["metric", "imperial"],
                "export_formats": ["pdf", "csv"],
            },
        )

    # Template content methods (simplified for brevity)

    def _get_pump_monitoring_app_react(self) -> str:
        """Get React pump monitoring app component."""
        return """
import React from 'react';
import { ThemeProvider, createTheme } from '@mui/material/styles';
import CssBaseline from '@mui/material/CssBaseline';
import { Container, Grid, Paper, Typography } from '@mui/material';
import PumpMetrics from './components/PumpMetrics';
import PumpChart from './components/PumpChart';
import { usePumpData } from './hooks/usePumpData';

// Industrial theme optimized for factory environments
const industrialTheme = createTheme({
  palette: {
    mode: 'dark',
    primary: {
      main: '#FF6B35', // Orange for industrial equipment
    },
    secondary: {
      main: '#004E89', // Blue for status indicators
    },
    error: {
      main: '#D32F2F', // Red for alarms
    },
    warning: {
      main: '#F57C00', // Amber for warnings
    },
    background: {
      default: '#1A1A1A', // Dark background for contrast
      paper: '#2A2A2A',
    },
  },
  typography: {
    fontFamily: '"Roboto Mono", monospace',
    h4: {
      fontSize: '1.8rem',
      fontWeight: 600,
    },
  },
});

function App() {
  const { pumpData, isLoading, error } = usePumpData();

  if (error) {
    return (
      <ThemeProvider theme={industrialTheme}>
        <CssBaseline />
        <Container maxWidth="xl">
          <Typography color="error" variant="h4">
            Connection Error: {error}
          </Typography>
        </Container>
      </ThemeProvider>
    );
  }

  return (
    <ThemeProvider theme={industrialTheme}>
      <CssBaseline />
      <Container maxWidth="xl" sx={{ py: 3 }}>
        <Typography variant="h4" gutterBottom sx={{ textAlign: 'center', mb: 4 }}>
          🏭 Pump Monitoring Dashboard
        </Typography>

        <Grid container spacing={3}>
          {/* Key Metrics */}
          <Grid item xs={12} md={4}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 300 }}>
              <Typography variant="h6" gutterBottom>
                Real-time Metrics
              </Typography>
              <PumpMetrics data={pumpData} isLoading={isLoading} />
            </Paper>
          </Grid>

          {/* Pressure Chart */}
          <Grid item xs={12} md={8}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 300 }}>
              <Typography variant="h6" gutterBottom>
                Pressure Trends
              </Typography>
              <PumpChart
                data={pumpData?.historical || []}
                metric="pressure"
                unit="PSI"
                color="#004E89"
              />
            </Paper>
          </Grid>

          {/* Flow Rate Chart */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 250 }}>
              <Typography variant="h6" gutterBottom>
                Flow Rate
              </Typography>
              <PumpChart
                data={pumpData?.historical || []}
                metric="flowRate"
                unit="GPM"
                color="#FF6B35"
              />
            </Paper>
          </Grid>

          {/* Temperature Chart */}
          <Grid item xs={12} md={6}>
            <Paper elevation={3} sx={{ p: 3, minHeight: 250 }}>
              <Typography variant="h6" gutterBottom>
                Temperature
              </Typography>
              <PumpChart
                data={pumpData?.historical || []}
                metric="temperature"
                unit="°F"
                color="#F57C00"
              />
            </Paper>
          </Grid>
        </Grid>
      </Container>
    </ThemeProvider>
  );
}

export default App;
"""

    def _get_pump_metrics_component(self) -> str:
        """Get pump metrics React component."""
        return """
import React from 'react';
import { Grid, Typography, Box, CircularProgress } from '@mui/material';
import {
  Speed as PressureIcon,
  Waves as FlowIcon,
  Thermostat as TempIcon,
  Vibration as VibrationIcon
} from '@mui/icons-material';

interface PumpData {
  pressure: number;
  flowRate: number;
  temperature: number;
  vibration: number;
  status: 'normal' | 'warning' | 'critical';
  lastUpdate: string;
}

interface PumpMetricsProps {
  data: PumpData | null;
  isLoading: boolean;
}

const MetricCard: React.FC<{
  title: string;
  value: number;
  unit: string;
  icon: React.ReactNode;
  status: 'normal' | 'warning' | 'critical';
}> = ({ title, value, unit, icon, status }) => {
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
        p: 2,
        border: `2px solid ${getStatusColor(status)}`,
        borderRadius: 2,
        textAlign: 'center',
        minHeight: 100,
        display: 'flex',
        flexDirection: 'column',
        justifyContent: 'center',
      }}
    >
      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', mb: 1 }}>
        {icon}
      </Box>
      <Typography variant="body2" sx={{ fontWeight: 'bold', mb: 0.5 }}>
        {title}
      </Typography>
      <Typography
        variant="h4"
        sx={{
          fontWeight: 'bold',
          color: getStatusColor(status),
          fontSize: '2rem',
        }}
      >
        {value.toFixed(1)}
      </Typography>
      <Typography variant="body2" color="text.secondary">
        {unit}
      </Typography>
    </Box>
  );
};

const PumpMetrics: React.FC<PumpMetricsProps> = ({ data, isLoading }) => {
  if (isLoading || !data) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight={200}>
        <CircularProgress size={60} />
      </Box>
    );
  }

  const metrics = [
    {
      title: 'Pressure',
      value: data.pressure,
      unit: 'PSI',
      icon: <PressureIcon sx={{ fontSize: 32 }} />,
      status: data.pressure > 150 ? 'critical' : data.pressure > 120 ? 'warning' : 'normal',
    },
    {
      title: 'Flow Rate',
      value: data.flowRate,
      unit: 'GPM',
      icon: <FlowIcon sx={{ fontSize: 32 }} />,
      status: data.flowRate < 50 ? 'critical' : data.flowRate < 75 ? 'warning' : 'normal',
    },
    {
      title: 'Temperature',
      value: data.temperature,
      unit: '°F',
      icon: <TempIcon sx={{ fontSize: 32 }} />,
      status: data.temperature > 200 ? 'critical' : data.temperature > 180 ? 'warning' : 'normal',
    },
    {
      title: 'Vibration',
      value: data.vibration,
      unit: 'mm/s',
      icon: <VibrationIcon sx={{ fontSize: 32 }} />,
      status: data.vibration > 5 ? 'critical' : data.vibration > 3 ? 'warning' : 'normal',
    },
  ];

  return (
    <Grid container spacing={2}>
      {metrics.map((metric, index) => (
        <Grid item xs={6} key={index}>
          <MetricCard {...metric} />
        </Grid>
      ))}
    </Grid>
  );
};

export default PumpMetrics;
"""

    def _get_pump_chart_component(self) -> str:
        """Get pump chart React component."""
        return """
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine
} from 'recharts';

interface DataPoint {
  timestamp: string;
  value: number;
}

interface PumpChartProps {
  data: DataPoint[];
  metric: string;
  unit: string;
  color: string;
}

const PumpChart: React.FC<PumpChartProps> = ({ data, metric, unit, color }) => {
  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString();
  };

  const getThresholds = (metric: string) => {
    switch (metric) {
      case 'pressure':
        return { warning: 120, critical: 150 };
      case 'flowRate':
        return { warning: 75, critical: 50 };
      case 'temperature':
        return { warning: 180, critical: 200 };
      case 'vibration':
        return { warning: 3, critical: 5 };
      default:
        return { warning: null, critical: null };
    }
  };

  const thresholds = getThresholds(metric);

  return (
    <ResponsiveContainer width="100%" height={200}>
      <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#444" />
        <XAxis
          dataKey="timestamp"
          tickFormatter={formatTime}
          stroke="#888"
          tick={{ fontSize: 12 }}
        />
        <YAxis
          stroke="#888"
          tick={{ fontSize: 12 }}
          label={{ value: unit, angle: -90, position: 'insideLeft' }}
        />
        <Tooltip
          contentStyle={{
            backgroundColor: '#2A2A2A',
            border: '1px solid #444',
            borderRadius: '4px'
          }}
          labelFormatter={(value) => formatTime(value as string)}
          formatter={(value: number) => [`${value.toFixed(2)} ${unit}`, metric]}
        />

        {thresholds.warning && (
          <ReferenceLine
            y={thresholds.warning}
            stroke="#F57C00"
            strokeDasharray="5 5"
            label={{ value: "Warning", position: "right" }}
          />
        )}

        {thresholds.critical && (
          <ReferenceLine
            y={thresholds.critical}
            stroke="#D32F2F"
            strokeDasharray="5 5"
            label={{ value: "Critical", position: "right" }}
          />
        )}

        <Line
          type="monotone"
          dataKey="value"
          stroke={color}
          strokeWidth={2}
          dot={false}
          activeDot={{ r: 6 }}
        />
      </LineChart>
    </ResponsiveContainer>
  );
};

export default PumpChart;
"""

    def _get_pump_data_hook(self) -> str:
        """Get pump data React hook."""
        return """
import { useState, useEffect, useCallback } from 'react';
import useMqtt from 'mqtt-react-hooks';

interface PumpData {
  pressure: number;
  flowRate: number;
  temperature: number;
  vibration: number;
  status: 'normal' | 'warning' | 'critical';
  lastUpdate: string;
  historical: Array<{
    timestamp: string;
    pressure: number;
    flowRate: number;
    temperature: number;
    vibration: number;
  }>;
}

const generateMockData = (): PumpData => {
  const now = new Date();
  const historical = Array.from({ length: 50 }, (_, i) => {
    const timestamp = new Date(now.getTime() - (49 - i) * 1000);
    return {
      timestamp: timestamp.toISOString(),
      pressure: 100 + Math.random() * 60,
      flowRate: 60 + Math.random() * 40,
      temperature: 150 + Math.random() * 50,
      vibration: Math.random() * 6,
    };
  });

  const current = historical[historical.length - 1];

  const getStatus = (data: typeof current): 'normal' | 'warning' | 'critical' => {
    if (data.pressure > 150 || data.flowRate < 50 || data.temperature > 200 || data.vibration > 5) {
      return 'critical';
    }
    if (data.pressure > 120 || data.flowRate < 75 || data.temperature > 180 || data.vibration > 3) {
      return 'warning';
    }
    return 'normal';
  };

  return {
    pressure: current.pressure,
    flowRate: current.flowRate,
    temperature: current.temperature,
    vibration: current.vibration,
    status: getStatus(current),
    lastUpdate: now.toISOString(),
    historical,
  };
};

export const usePumpData = () => {
  const [pumpData, setPumpData] = useState<PumpData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // MQTT connection (commented out for demo, uncomment for real MQTT)
  // const { connectionStatus, message } = useMqtt('mqtt://localhost:1883', [
  //   'factory/pumps/pump01/data'
  // ]);

  useEffect(() => {
    // Initialize with mock data
    const initialData = generateMockData();
    setPumpData(initialData);
    setIsLoading(false);

    // Set up real-time updates (mock for demo)
    const interval = setInterval(() => {
      const newData = generateMockData();
      setPumpData(prevData => {
        if (!prevData) return newData;

        // Keep only last 50 data points
        const historical = [...prevData.historical, ...newData.historical.slice(-1)].slice(-50);

        return {
          ...newData,
          historical,
        };
      });
    }, 1000); // Update every second

    return () => clearInterval(interval);
  }, []);

  // MQTT message handling (uncomment for real MQTT)
  /*
  useEffect(() => {
    if (message) {
      try {
        const data = JSON.parse(message.message.toString());
        setPumpData(prevData => ({
          ...data,
          historical: [...(prevData?.historical || []), data].slice(-50),
        }));
      } catch (err) {
        console.error('Error parsing MQTT message:', err);
      }
    }
  }, [message]);

  useEffect(() => {
    if (connectionStatus === 'Disconnected') {
      setError('MQTT connection lost');
    } else {
      setError(null);
    }
  }, [connectionStatus]);
  */

  return {
    pumpData,
    isLoading,
    error,
  };
};
"""

    def _get_industrial_styles(self) -> str:
        """Get industrial CSS styles."""
        return """
/* Industrial UI Styles - Optimized for Factory Environments */

:root {
  --industrial-primary: #FF6B35;
  --industrial-secondary: #004E89;
  --industrial-warning: #F57C00;
  --industrial-error: #D32F2F;
  --industrial-success: #4CAF50;
  --industrial-background: #1A1A1A;
  --industrial-surface: #2A2A2A;
  --industrial-text: #FFFFFF;
  --industrial-text-secondary: #B0B0B0;
}

body {
  font-family: 'Roboto Mono', monospace;
  background-color: var(--industrial-background);
  color: var(--industrial-text);
  margin: 0;
  padding: 0;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

/* High contrast for factory lighting */
.high-contrast {
  --industrial-primary: #FF8C42;
  --industrial-secondary: #0066CC;
  --industrial-background: #000000;
  --industrial-surface: #1A1A1A;
}

/* Touch-friendly targets (minimum 44px for gloved hands) */
.touch-target {
  min-width: 44px !important;
  min-height: 44px !important;
  padding: 12px !important;
}

/* Large buttons for industrial use */
.industrial-button {
  min-width: 60px;
  min-height: 60px;
  font-size: 1.2rem;
  font-weight: 600;
  text-transform: uppercase;
  border-radius: 8px;
  border: 2px solid var(--industrial-primary);
  background-color: var(--industrial-surface);
  color: var(--industrial-text);
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
  -webkit-tap-highlight-color: transparent;
}

.industrial-button:hover {
  background-color: var(--industrial-primary);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}

.industrial-button:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(255, 107, 53, 0.2);
}

/* Status indicators with clear visual states */
.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  border: 2px solid var(--industrial-text);
  position: relative;
}

.status-indicator.normal {
  background-color: var(--industrial-success);
  box-shadow: 0 0 10px rgba(76, 175, 80, 0.5);
}

.status-indicator.warning {
  background-color: var(--industrial-warning);
  box-shadow: 0 0 10px rgba(245, 124, 0, 0.5);
  animation: pulse-warning 2s infinite;
}

.status-indicator.critical {
  background-color: var(--industrial-error);
  box-shadow: 0 0 15px rgba(211, 47, 47, 0.7);
  animation: pulse-critical 1s infinite;
}

@keyframes pulse-warning {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.7; }
}

@keyframes pulse-critical {
  0%, 100% { opacity: 1; transform: scale(1); }
  50% { opacity: 0.8; transform: scale(1.1); }
}

/* Industrial data display */
.data-display {
  font-family: 'Roboto Mono', monospace;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: 0.05em;
  text-align: center;
  padding: 8px;
  background-color: var(--industrial-surface);
  border: 2px solid var(--industrial-secondary);
  border-radius: 4px;
  min-width: 120px;
}

.data-display.large {
  font-size: 2rem;
  min-width: 150px;
}

/* Alert panels */
.alert-panel {
  background-color: var(--industrial-surface);
  border-left: 6px solid var(--industrial-warning);
  padding: 16px;
  margin: 8px 0;
  border-radius: 4px;
}

.alert-panel.critical {
  border-left-color: var(--industrial-error);
  background-color: rgba(211, 47, 47, 0.1);
}

.alert-panel.warning {
  border-left-color: var(--industrial-warning);
  background-color: rgba(245, 124, 0, 0.1);
}

.alert-panel.info {
  border-left-color: var(--industrial-secondary);
  background-color: rgba(0, 78, 137, 0.1);
}

/* Responsive design for different factory screens */
@media (max-width: 768px) {
  .industrial-button {
    min-width: 50px;
    min-height: 50px;
    font-size: 1rem;
  }

  .data-display {
    font-size: 1.2rem;
  }

  .data-display.large {
    font-size: 1.5rem;
  }
}

@media (min-width: 1920px) {
  .industrial-button {
    min-width: 80px;
    min-height: 80px;
    font-size: 1.4rem;
  }

  .data-display.large {
    font-size: 2.5rem;
  }
}

/* Print styles for factory reports */
@media print {
  .industrial-button {
    display: none;
  }

  body {
    background: white;
    color: black;
  }

  .data-display {
    border: 2px solid black;
    background: white;
  }
}

/* Accessibility improvements */
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}

/* Focus indicators for keyboard navigation */
.industrial-button:focus,
.data-display:focus {
  outline: 3px solid var(--industrial-primary);
  outline-offset: 2px;
}
"""

    def _get_system_overview_app_react(self) -> str:
        """Get React system overview app component."""
        return """// Simplified system overview app
export const SYSTEM_OVERVIEW_REACT = "System overview React app content";"""

    def _get_system_status_component(self) -> str:
        """Get system status React component."""
        return """// System status component
export const SYSTEM_STATUS_COMPONENT = "System status component content";"""

    def _get_alert_panel_component(self) -> str:
        """Get alert panel React component."""
        return """// Alert panel component
export const ALERT_PANEL_COMPONENT = "Alert panel component content";"""

    def _get_equipment_control_app_react(self) -> str:
        """Get React equipment control app component."""
        return """// Equipment control app
export const EQUIPMENT_CONTROL_REACT = "Equipment control app content";"""

    def _get_control_button_component(self) -> str:
        """Get control button React component."""
        return """// Control button component
export const CONTROL_BUTTON_COMPONENT = "Control button component content";"""

    def _get_status_indicator_component(self) -> str:
        """Get status indicator React component."""
        return """// Status indicator component
export const STATUS_INDICATOR_COMPONENT = "Status indicator component content";"""

    def _get_touch_friendly_styles(self) -> str:
        """Get touch-friendly CSS styles."""
        return """/* Touch-friendly styles for factory environments */
.touch-button {
  min-width: 44px;
  min-height: 44px;
  /* Additional touch styles */
}"""

    def _get_pipe_sizing_app_react(self) -> str:
        """Get React pipe sizing calculator app component."""
        return """// Pipe sizing calculator app
export const PIPE_SIZING_REACT = "Pipe sizing calculator app content";"""

    def _get_calculator_form_component(self) -> str:
        """Get calculator form React component."""
        return """// Calculator form component
export const CALCULATOR_FORM_COMPONENT = "Calculator form component content";"""

    def _get_pipe_calculations(self) -> str:
        """Get pipe calculation utilities."""
        return """// Pipe calculation utilities
export const PIPE_CALCULATIONS = "Pipe calculation utilities content";"""

    def _get_calculator_styles(self) -> str:
        """Get calculator CSS styles."""
        return """/* Calculator styles */
.calculator-form {
  /* Calculator-specific styles */
}"""

    # Vue templates (simplified)
    def _pump_monitoring_vue(self) -> TemplateConfig:
        """Vue pump monitoring dashboard template."""
        return TemplateConfig(
            name="pump-monitoring",
            description="Real-time pump monitoring with Vue.js",
            interface_type="dashboard",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    def _system_overview_vue(self) -> TemplateConfig:
        """Vue system overview dashboard template."""
        return TemplateConfig(
            name="system-overview",
            description="Factory system overview with Vue.js",
            interface_type="dashboard",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    def _quality_control_vue(self) -> TemplateConfig:
        """Vue quality control dashboard template."""
        return TemplateConfig(
            name="quality-control",
            description="Quality metrics dashboard with Vue.js",
            interface_type="dashboard",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    def _equipment_control_vue(self) -> TemplateConfig:
        """Vue equipment control panel template."""
        return TemplateConfig(
            name="equipment-control",
            description="Equipment control with Vue.js",
            interface_type="control-panel",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    def _valve_control_vue(self) -> TemplateConfig:
        """Vue valve control panel template."""
        return TemplateConfig(
            name="valve-control",
            description="Valve control interface with Vue.js",
            interface_type="control-panel",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    def _pipe_sizing_vue(self) -> TemplateConfig:
        """Vue pipe sizing calculator template."""
        return TemplateConfig(
            name="pipe-sizing",
            description="Pipe sizing calculator with Vue.js",
            interface_type="calculator",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    def _flow_calculator_vue(self) -> TemplateConfig:
        """Vue flow calculator template."""
        return TemplateConfig(
            name="flow-calculator",
            description="Flow rate calculator with Vue.js",
            interface_type="calculator",
            framework="vue",
            files={},
            dependencies={},
            config={},
        )

    # Streamlit templates (simplified)
    def _pump_monitoring_streamlit(self) -> TemplateConfig:
        """Streamlit pump monitoring dashboard template."""
        return TemplateConfig(
            name="pump-monitoring",
            description="Quick pump monitoring prototype with Streamlit",
            interface_type="dashboard",
            framework="streamlit",
            files={},
            dependencies={},
            config={},
        )

    def _system_overview_streamlit(self) -> TemplateConfig:
        """Streamlit system overview dashboard template."""
        return TemplateConfig(
            name="system-overview",
            description="System overview prototype with Streamlit",
            interface_type="dashboard",
            framework="streamlit",
            files={},
            dependencies={},
            config={},
        )

    def _technical_manual_streamlit(self) -> TemplateConfig:
        """Streamlit technical documentation template."""
        return TemplateConfig(
            name="technical-manual",
            description="Interactive technical manual with Streamlit",
            interface_type="documentation",
            framework="streamlit",
            files={},
            dependencies={},
            config={},
        )

    def _training_materials_streamlit(self) -> TemplateConfig:
        """Streamlit training materials template."""
        return TemplateConfig(
            name="training-materials",
            description="Interactive training materials with Streamlit",
            interface_type="documentation",
            framework="streamlit",
            files={},
            dependencies={},
            config={},
        )

    # Documentation templates (simplified)
    def _technical_manual_react(self) -> TemplateConfig:
        """React technical documentation template."""
        return TemplateConfig(
            name="technical-manual",
            description="Interactive technical documentation with React",
            interface_type="documentation",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _maintenance_guide_react(self) -> TemplateConfig:
        """React maintenance guide template."""
        return TemplateConfig(
            name="maintenance-guide",
            description="Equipment maintenance guide with React",
            interface_type="documentation",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _safety_procedures_react(self) -> TemplateConfig:
        """React safety procedures template."""
        return TemplateConfig(
            name="safety-procedures",
            description="Safety procedures documentation with React",
            interface_type="documentation",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    # Additional dashboard templates
    def _quality_control_react(self) -> TemplateConfig:
        """React quality control dashboard template."""
        return TemplateConfig(
            name="quality-control",
            description="Quality metrics and control dashboard",
            interface_type="dashboard",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _energy_monitoring_react(self) -> TemplateConfig:
        """React energy monitoring dashboard template."""
        return TemplateConfig(
            name="energy-monitoring",
            description="Energy consumption and efficiency monitoring",
            interface_type="dashboard",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    # Additional control panel templates
    def _valve_control_react(self) -> TemplateConfig:
        """React valve control panel template."""
        return TemplateConfig(
            name="valve-control",
            description="Valve positioning and monitoring interface",
            interface_type="control-panel",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _motor_control_react(self) -> TemplateConfig:
        """React motor control panel template."""
        return TemplateConfig(
            name="motor-control",
            description="Motor speed and direction controls",
            interface_type="control-panel",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _hmi_interface_react(self) -> TemplateConfig:
        """React HMI interface template."""
        return TemplateConfig(
            name="hmi-interface",
            description="Human-machine interface panel",
            interface_type="control-panel",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    # Additional calculator templates
    def _flow_calculator_react(self) -> TemplateConfig:
        """React flow calculator template."""
        return TemplateConfig(
            name="flow-calculator",
            description="Flow rate and pressure calculations",
            interface_type="calculator",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _energy_calculator_react(self) -> TemplateConfig:
        """React energy calculator template."""
        return TemplateConfig(
            name="energy-calculator",
            description="Energy consumption and efficiency calculations",
            interface_type="calculator",
            framework="react",
            files={},
            dependencies={},
            config={},
        )

    def _conversion_tools_react(self) -> TemplateConfig:
        """React conversion tools template."""
        return TemplateConfig(
            name="conversion-tools",
            description="Unit conversion utilities",
            interface_type="calculator",
            framework="react",
            files={},
            dependencies={},
            config={},
        )
