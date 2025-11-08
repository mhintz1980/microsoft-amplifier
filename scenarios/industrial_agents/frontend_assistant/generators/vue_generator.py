"""
Vue Generator for Industrial Frontend Components

Generates Vue.js applications optimized for industrial environments.
"""

import json
from typing import Any

from .base_generator import BaseGenerator


class VueGenerator(BaseGenerator):
    """Generator for Vue-based industrial interfaces."""

    def generate_project_structure(
        self, template_config: dict[str, Any], project_config: dict[str, Any]
    ) -> dict[str, str]:
        """Generate complete Vue project structure."""
        files = {}

        # Generate package.json
        files["package.json"] = self.generate_package_json(project_config)

        # Generate main application files
        files["src/App.vue"] = self._generate_app_vue(project_config)
        files["src/main.ts"] = self._generate_main_ts()
        files["src/assets/main.css"] = self.generate_styles(project_config["theme"], project_config["factory_options"])

        # Generate components
        for file_path, content in template_config["files"].items():
            if file_path.startswith("src/components/"):
                files[file_path] = content

        # Generate composables
        files["src/composables/useIndustrialData.ts"] = self._generate_data_composable(project_config)

        # Generate types
        files["src/types/index.ts"] = self._generate_types(project_config)

        # Generate config
        files["src/config/index.ts"] = self._generate_config(project_config)

        # Generate additional files
        files["vite.config.ts"] = self._generate_vite_config()
        files["tsconfig.json"] = self._generate_tsconfig()
        files["README.md"] = self.generate_readme(project_config)

        return files

    def generate_package_json(self, project_config: dict[str, Any]) -> str:
        """Generate package.json for Vue project."""
        dependencies = {
            "vue": "^3.3.0",
            "typescript": "^5.0.0",
            "vue-router": "^4.2.0",
            "pinia": "^2.1.0",
        }

        # Add industrial-specific dependencies
        if "real-time" in project_config.get("features", []):
            dependencies.update(
                {
                    "mqtt": "^5.0.0",
                    "socket.io-client": "^4.7.0",
                }
            )

        if "charts" in project_config.get("features", []):
            dependencies.update(
                {
                    "chart.js": "^4.4.0",
                    "vue-chartjs": "^5.2.0",
                }
            )

        dev_dependencies = {
            "@vitejs/plugin-vue": "^4.2.0",
            "vite": "^4.4.0",
            "@vue/tsconfig": "^0.4.0",
            "eslint": "^8.45.0",
            "@typescript-eslint/eslint-plugin": "^6.0.0",
            "@typescript-eslint/parser": "^6.0.0",
            "eslint-plugin-vue": "^9.15.0",
        }

        package_json = {
            "name": f"industrial-{project_config['type']}-{project_config['template']}",
            "version": "1.0.0",
            "description": f"Industrial {project_config['type']} generated with Vue.js",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "vue-tsc && vite build",
                "preview": "vite preview",
                "lint": "eslint . --ext .vue,.js,.jsx,.cjs,.mjs,.ts,.tsx,.cts,.mts --fix --ignore-path .gitignore",
                "type-check": "vue-tsc --noEmit",
            },
            "dependencies": dependencies,
            "devDependencies": dev_dependencies,
        }

        return json.dumps(package_json, indent=2)

    def generate_component(self, component_type: str, config: dict[str, Any]) -> str:
        """Generate a Vue component."""
        components = {
            "metrics": self._generate_metrics_component_vue(config),
            "chart": self._generate_chart_component_vue(config),
            "control": self._generate_control_component_vue(config),
        }

        return components.get(component_type, "<!-- Component not implemented -->")

    def generate_styles(self, theme: str, factory_options: list[str]) -> str:
        """Generate CSS styles for Vue application."""
        return f"""
/* Industrial Vue Styles - {theme.title()} Theme */

:root {{
  --primary-color: {self._get_theme_colors(theme)["primary"]};
  --secondary-color: {self._get_theme_colors(theme)["secondary"]};
  --background-color: {self._get_theme_colors(theme)["background"]};
  --surface-color: {self._get_theme_colors(theme)["surface"]};
  --text-color: {self._get_theme_colors(theme)["text"]};
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

#app {{
  min-height: 100vh;
}}

/* Industrial Vue components */
.industrial-card {{
  background-color: var(--surface-color);
  border: 2px solid var(--primary-color);
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem;
}}

.metric-display {{
  font-family: 'Roboto Mono', monospace;
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  color: var(--primary-color);
}}
"""

    def generate_hooks(self, data_source: str, features: list[str]) -> dict[str, str]:
        """Generate Vue composables."""
        composables = {}

        if "real-time" in features:
            composables["useDataConnection.ts"] = self._generate_data_composable({"data_source": data_source})

        if "offline-support" in features:
            composables["useOfflineSupport.ts"] = self._generate_offline_composable()

        return composables

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
        }
        return themes.get(theme, themes["factory-dark"])

    def _generate_app_vue(self, project_config: dict[str, Any]) -> str:
        """Generate main Vue App component."""
        return f"""
<template>
  <div id="app" :class="['industrial-app', themeClass]">
    <header class="app-header">
      <h1>🏭 Industrial {project_config["type"].title()}</h1>
      <div class="connection-status" :class="statusClass">
        {{ connectionStatus }}
      </div>
    </header>

    <main class="app-main">
      <router-view />
    </main>

    <footer class="app-footer">
      <div class="system-info">
        Last Update: {{ lastUpdate }}
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import {{ ref, computed, onMounted }} from 'vue'
import {{ useIndustrialData }} from './composables/useIndustrialData'
import {{ useOfflineSupport }} from './composables/useOfflineSupport'

// Composables
const {{ data, isLoading, error }} = useIndustrialData()
const {{ isOnline }} = useOfflineSupport()

// Reactive state
const lastUpdate = ref(new Date().toLocaleTimeString())

// Computed properties
const connectionStatus = computed(() => {{
  if (error.value) return 'Connection Error'
  if (isLoading.value) return 'Connecting...'
  if (!isOnline.value) return 'Offline'
  return 'Connected'
}})

const statusClass = computed(() => {{
  if (error.value) return 'error'
  if (!isOnline.value) return 'offline'
  return 'connected'
}})

const themeClass = computed(() => `theme-{project_config.get("theme", "factory-dark")}`)

// Lifecycle
onMounted(() => {{
  setInterval(() => {{
    lastUpdate.value = new Date().toLocaleTimeString()
  }}, 1000)
}})
</script>

<style scoped>
.industrial-app {{
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}}

.app-header {{
  background-color: var(--surface-color);
  border-bottom: 2px solid var(--primary-color);
  padding: 1rem;
  display: flex;
  justify-content: space-between;
  align-items: center;
}}

.app-header h1 {{
  font-size: 1.5rem;
  font-weight: 600;
  color: var(--primary-color);
}}

.connection-status {{
  padding: 0.5rem 1rem;
  border-radius: 4px;
  font-weight: 600;
}}

.connection-status.connected {{
  background-color: var(--success-color, #4CAF50);
  color: white;
}}

.connection-status.error {{
  background-color: var(--error-color, #D32F2F);
  color: white;
}}

.connection-status.offline {{
  background-color: var(--warning-color, #F57C00);
  color: white;
}}

.app-main {{
  flex: 1;
  padding: 1rem;
}}

.app-footer {{
  background-color: var(--surface-color);
  border-top: 2px solid var(--primary-color);
  padding: 1rem;
  text-align: center;
  font-size: 0.9rem;
  color: var(--text-color);
  opacity: 0.8;
}}
</style>
"""

    def _generate_main_ts(self) -> str:
        """Generate Vue main.ts file."""
        return """
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
"""

    def _generate_data_composable(self, project_config: dict[str, Any]) -> str:
        """Generate Vue data composable."""
        return """
import { ref, reactive, onMounted, onUnmounted } from 'vue'

export function useIndustrialData() {
  const data = ref(null)
  const isLoading = ref(true)
  const error = ref(null)
  const updateInterval = ref(null)

  const mockData = {
    pressure: 100 + Math.random() * 50,
    temperature: 150 + Math.random() * 30,
    flowRate: 60 + Math.random() * 20,
    vibration: Math.random() * 4,
  }

  const fetchData = async () => {
    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 500))
      data.value = mockData
      error.value = null
    } catch (err) {
      error.value = 'Failed to fetch data'
    } finally {
      isLoading.value = false
    }
  }

  const startRealTimeUpdates = () => {
    updateInterval.value = setInterval(fetchData, 1000)
  }

  const stopRealTimeUpdates = () => {
    if (updateInterval.value) {
      clearInterval(updateInterval.value)
      updateInterval.value = null
    }
  }

  onMounted(() => {
    fetchData()
    startRealTimeUpdates()
  })

  onUnmounted(() => {
    stopRealTimeUpdates()
  })

  return {
    data,
    isLoading,
    error,
    refresh: fetchData,
    startRealTimeUpdates,
    stopRealTimeUpdates,
  }
}
"""

    def _generate_offline_composable(self) -> str:
        """Generate offline support composable."""
        return """
import { ref, onMounted, onUnmounted } from 'vue'

export function useOfflineSupport() {
  const isOnline = ref(navigator.onLine)
  const connectionType = ref('unknown')

  const updateConnectionStatus = () => {
    isOnline.value = navigator.onLine
    if ('connection' in navigator) {
      const connection = (navigator as any).connection
      connectionType.value = connection ? connection.effectiveType : 'unknown'
    }
  }

  onMounted(() => {
    window.addEventListener('online', updateConnectionStatus)
    window.addEventListener('offline', updateConnectionStatus)
    updateConnectionStatus()
  })

  onUnmounted(() => {
    window.removeEventListener('online', updateConnectionStatus)
    window.removeEventListener('offline', updateConnectionStatus)
  })

  return {
    isOnline,
    connectionType,
  }
}
"""

    def _generate_types(self, project_config: dict[str, Any]) -> str:
        """Generate TypeScript types for Vue."""
        return """
// Industrial data types
export interface IndustrialData {
  pressure: number
  temperature: number
  flowRate: number
  vibration: number
  timestamp: string
}

export interface Alert {
  id: string
  level: 'info' | 'warning' | 'critical'
  message: string
  timestamp: string
}
"""

    def _generate_config(self, project_config: dict[str, Any]) -> str:
        """Generate configuration for Vue."""
        return f"""
// Industrial Vue Configuration
export const config = {{
  theme: '{project_config.get("theme", "factory-dark")}',
  dataSource: '{project_config.get("data_source", "mock")}',
  updateInterval: 1000,
  factoryOptions: {project_config.get("factory_options", [])},
  features: {project_config.get("features", [])},
}}
"""

    def _generate_vite_config(self) -> str:
        """Generate Vite configuration for Vue."""
        return """
import { fileURLToPath, URL } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    host: true,
  }
})
"""

    def _generate_tsconfig(self) -> str:
        """Generate TypeScript configuration for Vue."""
        return """
{
  "extends": "@vue/tsconfig/tsconfig.dom.json",
  "include": ["env.d.ts", "src/**/*", "src/**/*.vue"],
  "exclude": ["src/**/__tests__/*"],
  "compilerOptions": {
    "composite": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["./src/*"]
    }
  }
}
"""

    def _generate_metrics_component_vue(self, config: dict[str, Any]) -> str:
        """Generate Vue metrics component."""
        return """
<template>
  <div class="metrics-panel">
    <div v-for="metric in metrics" :key="metric.name" class="metric-card">
      <h3>{{ metric.name }}</h3>
      <div class="metric-value" :class="metric.status">
        {{ metric.value.toFixed(1) }} {{ metric.unit }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface Metric {
  name: string
  value: number
  unit: string
  status: 'normal' | 'warning' | 'critical'
}

defineProps<{
  metrics: Metric[]
}>()
</script>
"""

    def _generate_chart_component_vue(self, config: dict[str, Any]) -> str:
        """Generate Vue chart component."""
        return """
<template>
  <div class="chart-container">
    <canvas ref="chartCanvas"></canvas>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'

const chartCanvas = ref<HTMLCanvasElement>()

onMounted(() => {
  // Chart.js implementation
})
</script>
"""

    def _generate_control_component_vue(self, config: dict[str, Any]) -> str:
        """Generate Vue control component."""
        return """
<template>
  <div class="control-panel">
    <button
      v-for="control in controls"
      :key="control.id"
      @click="handleControl(control)"
      class="control-button"
      :disabled="control.disabled"
    >
      {{ control.label }}
    </button>
  </div>
</template>

<script setup lang="ts">
interface Control {
  id: string
  label: string
  disabled: boolean
}

const emit = defineEmits<{
  control: [control: Control]
}>()

const handleControl = (control: Control) => {
  emit('control', control)
}

defineProps<{
  controls: Control[]
}>()
</script>
"""
