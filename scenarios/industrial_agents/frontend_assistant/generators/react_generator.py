"""
React Generator for Industrial Frontend Components

Generates React applications optimized for industrial environments.
"""

import json
from typing import Any

from .base_generator import BaseGenerator


class ReactGenerator(BaseGenerator):
    """Generator for React-based industrial interfaces."""

    def generate_project_structure(
        self, template_config: dict[str, Any], project_config: dict[str, Any]
    ) -> dict[str, str]:
        """Generate complete React project structure."""
        files = {}

        # Generate package.json
        files["package.json"] = self.generate_package_json(project_config)

        # Generate main application files
        files["src/App.tsx"] = template_config["files"].get("src/App.tsx", "")
        files["src/index.tsx"] = self._generate_index_tsx()
        files["src/App.css"] = self.generate_styles(project_config["theme"], project_config["factory_options"])

        # Generate components
        for file_path, content in template_config["files"].items():
            if file_path.startswith("src/components/") or file_path.startswith("src/hooks/"):
                files[file_path] = content

        # Generate types
        files["src/types/index.ts"] = self._generate_types(project_config)

        # Generate config
        files["src/config/index.ts"] = self._generate_config(project_config)

        # Generate utilities
        files["src/utils/index.ts"] = self._generate_utils(project_config)

        # Generate additional files
        files["tsconfig.json"] = self._generate_tsconfig()
        files["vite.config.ts"] = self._generate_vite_config()
        files[".eslintrc.json"] = self._generate_eslint_config()
        files["README.md"] = self.generate_readme(project_config)

        return files

    def generate_package_json(self, project_config: dict[str, Any]) -> str:
        """Generate package.json for React project."""
        dependencies = {
            "react": "^18.2.0",
            "react-dom": "^18.2.0",
            "typescript": "^5.0.0",
            "@types/react": "^18.2.0",
            "@types/react-dom": "^18.2.0",
        }

        # Add template-specific dependencies
        template_deps = project_config.get("template_dependencies", {})
        for _category, deps in template_deps.items():
            if isinstance(deps, list):
                dependencies.update(dict.fromkeys(deps, "latest"))

        # Add industrial-specific dependencies
        if "real-time" in project_config.get("features", []):
            dependencies.update(
                {
                    "socket.io-client": "^4.7.0",
                    "mqtt-react-hooks": "^5.0.0",
                }
            )

        if "charts" in project_config.get("features", []):
            dependencies.update(
                {
                    "recharts": "^2.8.0",
                    "chart.js": "^4.4.0",
                    "react-chartjs-2": "^5.2.0",
                }
            )

        if "touch" in project_config.get("factory_options", []):
            dependencies.update(
                {
                    "hammerjs": "^2.0.8",
                    "@types/hammerjs": "^2.0.41",
                }
            )

        dev_dependencies = {
            "@vitejs/plugin-react": "^4.0.0",
            "vite": "^4.4.0",
            "eslint": "^8.45.0",
            "@typescript-eslint/eslint-plugin": "^6.0.0",
            "@typescript-eslint/parser": "^6.0.0",
            "eslint-plugin-react-hooks": "^4.6.0",
            "eslint-plugin-react-refresh": "^0.4.0",
        }

        package_json = {
            "name": f"industrial-{project_config['type']}-{project_config['template']}",
            "version": "1.0.0",
            "description": f"Industrial {project_config['type']} generated with React",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
                "preview": "vite preview",
                "type-check": "tsc --noEmit",
                "format": "prettier --write 'src/**/*.{ts,tsx,css,md}'",
            },
            "dependencies": dependencies,
            "devDependencies": dev_dependencies,
            "keywords": [
                "industrial",
                "factory",
                project_config["framework"],
                project_config["type"],
                "iot",
                "monitoring",
            ],
        }

        return json.dumps(package_json, indent=2)

    def generate_component(self, component_type: str, config: dict[str, Any]) -> str:
        """Generate a React component."""
        components = {
            "metrics": self._generate_metrics_component(config),
            "chart": self._generate_chart_component(config),
            "control": self._generate_control_component(config),
            "status": self._generate_status_component(config),
            "alert": self._generate_alert_component(config),
        }

        return components.get(component_type, "// Component not implemented")

    def generate_styles(self, theme: str, factory_options: list[str]) -> str:
        """Generate CSS styles for React application."""
        return f"""
/* Industrial React Styles - {theme.title()} Theme */

:root {{
  --primary-color: {self._get_theme_colors(theme)["primary"]};
  --secondary-color: {self._get_theme_colors(theme)["secondary"]};
  --background-color: {self._get_theme_colors(theme)["background"]};
  --surface-color: {self._get_theme_colors(theme)["surface"]};
  --text-color: {self._get_theme_colors(theme)["text"]};
  --error-color: #D32F2F;
  --warning-color: #F57C00;
  --success-color: #4CAF50;
}}

* {{
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}}

body {{
  font-family: 'Roboto Mono', monospace;
  background-color: var(--background-color);
  color: var(--text-color);
  line-height: 1.6;
}}

#root {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}}

/* Touch-friendly styles */
{"body { --touch-target-size: 44px; }" if "touch-friendly" in factory_options else ""}

.touch-button {{
  min-width: var(--touch-target-size, 44px);
  min-height: var(--touch-target-size, 44px);
  padding: 12px 24px;
  font-size: 1.1rem;
  font-weight: 600;
  border: 2px solid var(--primary-color);
  background-color: var(--surface-color);
  color: var(--text-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  user-select: none;
}}

.touch-button:hover {{
  background-color: var(--primary-color);
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
}}

.touch-button:active {{
  transform: translateY(0);
}}

/* High contrast styles */
{"body { --contrast-ratio: 7; }" if "high-contrast" in factory_options else ""}

.high-contrast {{
  --primary-color: #FF8C42;
  --secondary-color: #0066CC;
  --background-color: #000000;
  --surface-color: #1A1A1A;
}}

/* Industrial components */
.industrial-card {{
  background-color: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  padding: 16px;
  margin: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
}}

.metric-display {{
  font-family: 'Roboto Mono', monospace;
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  color: var(--primary-color);
  margin: 8px 0;
}}

.status-indicator {{
  width: 16px;
  height: 16px;
  border-radius: 50%;
  display: inline-block;
  margin-right: 8px;
}}

.status-indicator.normal {{
  background-color: var(--success-color);
  box-shadow: 0 0 8px rgba(76, 175, 80, 0.5);
}}

.status-indicator.warning {{
  background-color: var(--warning-color);
  box-shadow: 0 0 8px rgba(245, 124, 0, 0.5);
  animation: pulse-warning 2s infinite;
}}

.status-indicator.critical {{
  background-color: var(--error-color);
  box-shadow: 0 0 12px rgba(211, 47, 47, 0.7);
  animation: pulse-critical 1s infinite;
}}

@keyframes pulse-warning {{
  0%, 100% {{ opacity: 1; }}
  50% {{ opacity: 0.6; }}
}}

@keyframes pulse-critical {{
  0%, 100% {{ opacity: 1; transform: scale(1); }}
  50% {{ opacity: 0.7; transform: scale(1.1); }}
}}

/* Responsive design */
@media (max-width: 768px) {{
  .industrial-card {{
    margin: 4px;
    padding: 12px;
  }}

  .metric-display {{
    font-size: 1.5rem;
  }}

  {"body { --touch-target-size: 48px; }" if "touch-friendly" in factory_options else ""}
}}

@media (min-width: 1920px) {{
  .metric-display {{
    font-size: 2.5rem;
  }}

  {"body { --touch-target-size: 48px; }" if "touch-friendly" in factory_options else ""}
}}

/* Offline styles */
.offline-indicator {{
  position: fixed;
  top: 16px;
  right: 16px;
  background-color: var(--warning-color);
  color: white;
  padding: 8px 16px;
  border-radius: 4px;
  font-weight: 600;
  z-index: 1000;
}}

/* Loading states */
.loading-spinner {{
  width: 40px;
  height: 40px;
  border: 4px solid var(--surface-color);
  border-top: 4px solid var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 20px auto;
}}

@keyframes spin {{
  0% {{ transform: rotate(0deg); }}
  100% {{ transform: rotate(360deg); }}
}}
"""

    def generate_hooks(self, data_source: str, features: list[str]) -> dict[str, str]:
        """Generate custom React hooks."""
        hooks = {}

        # Data connection hook
        if "real-time" in features:
            hooks["useDataConnection.ts"] = self._generate_data_connection_hook(data_source)

        # Offline support hook
        if "offline-support" in features:
            hooks["useOfflineSupport.ts"] = self._generate_offline_hook()

        # Touch interaction hook
        hooks["useTouchInteraction.ts"] = self._generate_touch_hook()

        return hooks

    def _get_theme_colors(self, theme: str) -> dict[str, str]:
        """Get color palette for theme."""
        themes = {
            "factory-dark": {
                "primary": "#FF6B35",
                "secondary": "#004E89",
                "background": "#1A1A1A",
                "surface": "#2A2A2A",
                "text": "#FFFFFF",
            },
            "factory-light": {
                "primary": "#E65100",
                "secondary": "#1565C0",
                "background": "#F5F5F5",
                "surface": "#FFFFFF",
                "text": "#212121",
            },
            "high-contrast": {
                "primary": "#FF8C42",
                "secondary": "#0066CC",
                "background": "#000000",
                "surface": "#1A1A1A",
                "text": "#FFFFFF",
            },
        }
        return themes.get(theme, themes["factory-dark"])

    def _generate_index_tsx(self) -> str:
        """Generate React index.tsx file."""
        return """
import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './index.css';
import './App.css';

ReactDOM.createRoot(document.getElementById('root')!).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>
);
"""

    def _generate_types(self, project_config: dict[str, Any]) -> str:
        """Generate TypeScript type definitions."""
        interface_type = project_config["type"]

        base_types = """
// Base industrial data types
export interface BaseMetric {
  value: number;
  unit: string;
  timestamp: string;
  status: 'normal' | 'warning' | 'critical';
}

export interface Alert {
  id: string;
  level: 'info' | 'warning' | 'critical';
  message: string;
  timestamp: string;
  acknowledged: boolean;
}

export interface EquipmentStatus {
  id: string;
  name: string;
  online: boolean;
  lastUpdate: string;
  metrics: Record<string, BaseMetric>;
}
"""

        type_extensions = {
            "dashboard": """
// Dashboard-specific types
export interface DashboardData {
  equipment: EquipmentStatus[];
  alerts: Alert[];
  systemHealth: {
    overall: 'healthy' | 'degraded' | 'critical';
    uptime: number;
    performance: number;
  };
}

export interface ChartDataPoint {
  timestamp: string;
  value: number;
  [key: string]: any;
}
""",
            "control-panel": """
// Control panel specific types
export interface ControlCommand {
  equipmentId: string;
  action: string;
  parameters: Record<string, any>;
  timestamp: string;
}

export interface ControlState {
  equipmentId: string;
  mode: 'auto' | 'manual' | 'maintenance';
  permissions: string[];
  safetyInterlocks: string[];
}
""",
            "calculator": """
// Calculator specific types
export interface CalculationInput {
  [key: string]: number | string;
}

export interface CalculationResult {
  inputs: CalculationInput;
  results: Record<string, number>;
  units: Record<string, string>;
  warnings: string[];
  timestamp: string;
}
""",
        }

        return base_types + type_extensions.get(interface_type, "")

    def _generate_config(self, project_config: dict[str, Any]) -> str:
        """Generate configuration file."""
        data_source = project_config.get("data_source", "mock")
        theme = project_config.get("theme", "factory-dark")

        return f"""
// Industrial Frontend Configuration
export const config = {{
  // Data source configuration
  dataSource: {{
    type: '{data_source}',
    endpoint: {self._get_data_source_config(data_source)},
    updateInterval: 1000, // ms
    retryAttempts: 3,
    retryDelay: 2000, // ms
  }},

  // Theme configuration
  theme: '{theme}',

  // Factory optimizations
  factoryOptions: {project_config.get("factory_options", [])},

  // Features
  features: {project_config.get("features", [])},

  // Alert thresholds
  thresholds: {{
    pressure: {{ warning: 120, critical: 150 }},
    temperature: {{ warning: 180, critical: 200 }},
    flowRate: {{ warning: 75, critical: 50 }},
    vibration: {{ warning: 3, critical: 5 }},
  }},

  // UI configuration
  ui: {{
    chartHistoryPoints: 50,
    maxAlerts: 100,
    autoRefresh: true,
    animationsEnabled: !window.matchMedia('(prefers-reduced-motion: reduce)').matches,
  }},
}};

// Environment-specific overrides
if (import.meta.env.DEV) {{
  config.dataSource.type = 'mock';
  config.dataSource.updateInterval = 500;
}}
"""

    def _generate_utils(self, project_config: dict[str, Any]) -> str:
        """Generate utility functions."""
        return """
// Industrial utility functions

export const formatMetricValue = (value: number, unit: string, decimals: number = 1): string => {
  return `${value.toFixed(decimals)} ${unit}`;
};

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'critical': return '#D32F2F';
    case 'warning': return '#F57C00';
    case 'normal': return '#4CAF50';
    default: return '#757575';
  }
};

export const calculateStatus = (
  value: number,
  thresholds: { warning: number; critical: number }
): 'normal' | 'warning' | 'critical' => {
  if (value >= thresholds.critical) return 'critical';
  if (value >= thresholds.warning) return 'warning';
  return 'normal';
};

export const formatTimestamp = (timestamp: string): string => {
  return new Date(timestamp).toLocaleTimeString();
};

export const debounce = <T extends (...args: any[]) => void>(
  func: T,
  wait: number
): ((...args: Parameters<T>) => void) => {
  let timeout: NodeJS.Timeout;
  return (...args: Parameters<T>) => {
    clearTimeout(timeout);
    timeout = setTimeout(() => func(...args), wait);
  };
};

// Offline storage utilities
export const saveToLocalStorage = (key: string, data: any): void => {
  try {
    localStorage.setItem(key, JSON.stringify(data));
  } catch (error) {
    console.warn('Failed to save to localStorage:', error);
  }
};

export const loadFromLocalStorage = <T>(key: string, defaultValue: T): T => {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : defaultValue;
  } catch (error) {
    console.warn('Failed to load from localStorage:', error);
    return defaultValue;
  }
};
"""

    def _generate_tsconfig(self) -> str:
        """Generate TypeScript configuration."""
        return """
{
  "compilerOptions": {
    "target": "ES2020",
    "useDefineForClassFields": true,
    "lib": ["ES2020", "DOM", "DOM.Iterable"],
    "module": "ESNext",
    "skipLibCheck": true,
    "moduleResolution": "bundler",
    "allowImportingTsExtensions": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx",
    "strict": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true,
    "noFallthroughCasesInSwitch": true
  },
  "include": ["src"],
  "references": [{ "path": "./tsconfig.node.json" }]
}
"""

    def _generate_vite_config(self) -> str:
        """Generate Vite configuration."""
        return """
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  server: {
    port: 3000,
    host: true, // Allow external connections for factory networks
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom'],
          charts: ['recharts', 'chart.js'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['react', 'react-dom'],
  },
});
"""

    def _generate_eslint_config(self) -> str:
        """Generate ESLint configuration."""
        return """
{
  "env": {
    "browser": true,
    "es2020": true
  },
  "extends": [
    "eslint:recommended",
    "@typescript-eslint/recommended",
    "plugin:react-hooks/recommended"
  ],
  "ignorePatterns": ["dist", ".eslintrc.cjs"],
  "parser": "@typescript-eslint/parser",
  "plugins": ["react-refresh"],
  "rules": {
    "react-refresh/only-export-components": [
      "warn",
      { "allowConstantExport": true }
    ],
    "@typescript-eslint/no-unused-vars": "warn",
    "@typescript-eslint/no-explicit-any": "warn"
  }
}
"""

    def _generate_data_connection_hook(self, data_source: str) -> str:
        """Generate data connection hook."""
        if data_source == "mqtt":
            return """
import { useState, useEffect, useCallback } from 'react';

interface DataConnectionState {
  connected: boolean;
  data: any;
  error: string | null;
}

export const useDataConnection = (broker: string, topics: string[]) => {
  const [state, setState] = useState<DataConnectionState>({
    connected: false,
    data: null,
    error: null,
  });

  const connect = useCallback(() => {
    // MQTT connection logic
    setState(prev => ({ ...prev, connected: true, error: null }));
  }, []);

  const disconnect = useCallback(() => {
    // MQTT disconnect logic
    setState(prev => ({ ...prev, connected: false }));
  }, []);

  useEffect(() => {
    connect();
    return () => disconnect();
  }, [connect, disconnect]);

  return { ...state, connect, disconnect };
};
"""
        return """
import { useState, useEffect } from 'react';

export const useDataConnection = (endpoint: string) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Mock data connection
    const mockData = {
      pressure: 100 + Math.random() * 50,
      temperature: 150 + Math.random() * 30,
      flowRate: 60 + Math.random() * 20,
    };

    setTimeout(() => {
      setData(mockData);
      setLoading(false);
    }, 1000);
  }, [endpoint]);

  return { data, loading, error };
};
"""

    def _generate_offline_hook(self) -> str:
        """Generate offline support hook."""
        return """
import { useState, useEffect } from 'react';

export const useOfflineSupport = () => {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return { isOnline };
};
"""

    def _generate_touch_hook(self) -> str:
        """Generate touch interaction hook."""
        return """
import { useRef, useEffect } from 'react';

export const useTouchInteraction = (onTap?: () => void, onLongPress?: () => void) => {
  const elementRef = useRef<HTMLElement>(null);
  const timeoutRef = useRef<NodeJS.Timeout>();

  useEffect(() => {
    const element = elementRef.current;
    if (!element) return;

    let touchStartTime: number;

    const handleTouchStart = (e: TouchEvent) => {
      touchStartTime = Date.now();

      if (onLongPress) {
        timeoutRef.current = setTimeout(() => {
          onLongPress();
        }, 500);
      }
    };

    const handleTouchEnd = (e: TouchEvent) => {
      const touchDuration = Date.now() - touchStartTime;

      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }

      if (touchDuration < 500 && onTap) {
        onTap();
      }
    };

    element.addEventListener('touchstart', handleTouchStart);
    element.addEventListener('touchend', handleTouchEnd);

    return () => {
      element.removeEventListener('touchstart', handleTouchStart);
      element.removeEventListener('touchend', handleTouchEnd);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [onTap, onLongPress]);

  return elementRef;
};
"""

    def _get_data_source_config(self, data_source: str) -> str:
        """Get data source configuration."""
        configs = {
            "mqtt": "'mqtt://localhost:1883'",
            "rest-api": "'https://api.factory.local'",
            "websocket": "'ws://localhost:8080'",
            "mock": "null",
        }
        return configs.get(data_source, "null")

    def _generate_metrics_component(self, config: dict[str, Any]) -> str:
        """Generate metrics display component."""
        return """
// Metrics display component
export const METRICS_COMPONENT = "Metrics component implementation";
"""

    def _generate_chart_component(self, config: dict[str, Any]) -> str:
        """Generate chart component."""
        return """
// Chart component
export const CHART_COMPONENT = "Chart component implementation";
"""

    def _generate_control_component(self, config: dict[str, Any]) -> str:
        """Generate control component."""
        return """
// Control component
export const CONTROL_COMPONENT = "Control component implementation";
"""

    def _generate_status_component(self, config: dict[str, Any]) -> str:
        """Generate status component."""
        return """
// Status component
export const STATUS_COMPONENT = "Status component implementation";
"""

    def _generate_alert_component(self, config: dict[str, Any]) -> str:
        """Generate alert component."""
        return """
// Alert component
export const ALERT_COMPONENT = "Alert component implementation";
"""
