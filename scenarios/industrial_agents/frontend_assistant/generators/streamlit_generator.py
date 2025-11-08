"""
Streamlit Generator for Industrial Frontend Components

Generates Streamlit applications optimized for industrial environments.
"""

from typing import Any

from .base_generator import BaseGenerator


class StreamlitGenerator(BaseGenerator):
    """Generator for Streamlit-based industrial interfaces."""

    def generate_project_structure(
        self, template_config: dict[str, Any], project_config: dict[str, Any]
    ) -> dict[str, str]:
        """Generate complete Streamlit project structure."""
        files = {}

        # Generate requirements.txt
        files["requirements.txt"] = self.generate_requirements_txt(project_config)

        # Generate main application file
        files["app.py"] = self._generate_app_py(project_config, template_config)

        # Generate utility modules
        files["utils/data_simulator.py"] = self._generate_data_simulator()
        files["utils/industrial_components.py"] = self._generate_industrial_components()
        files["config/config.py"] = self._generate_config_py(project_config)

        # Generate additional files
        files["README.md"] = self.generate_readme(project_config)
        files[".streamlit/config.toml"] = self._generate_streamlit_config()

        return files

    def generate_package_json(self, project_config: dict[str, Any]) -> str:
        """Streamlit doesn't use package.json - return empty string."""
        return ""

    def generate_requirements_txt(self, project_config: dict[str, Any]) -> str:
        """Generate requirements.txt for Streamlit project."""
        requirements = [
            "streamlit>=1.28.0",
            "pandas>=2.0.0",
            "numpy>=1.24.0",
            "plotly>=5.15.0",
            "requests>=2.31.0",
        ]

        # Add industrial-specific dependencies
        if "real-time" in project_config.get("features", []):
            requirements.extend(
                [
                    "paho-mqtt>=1.6.0",
                    "websocket-client>=1.6.0",
                ]
            )

        if "charts" in project_config.get("features", []):
            requirements.extend(
                [
                    "matplotlib>=3.7.0",
                    "seaborn>=0.12.0",
                    "altair>=5.0.0",
                ]
            )

        if "alerts" in project_config.get("features", []):
            requirements.extend(
                [
                    "streamlit-extras>=0.3.0",
                    "streamlit-antd>=0.2.0",
                ]
            )

        return "\n".join(requirements)

    def generate_component(self, component_type: str, config: dict[str, Any]) -> str:
        """Generate a Streamlit component."""
        components = {
            "metrics": self._generate_metrics_component_st(config),
            "chart": self._generate_chart_component_st(config),
            "control": self._generate_control_component_st(config),
            "status": self._generate_status_component_st(config),
            "alert": self._generate_alert_component_st(config),
        }

        return components.get(component_type, "# Component not implemented")

    def generate_styles(self, theme: str, factory_options: list[str]) -> str:
        """Generate CSS styles for Streamlit."""
        return f"""
/* Industrial Streamlit Styles - {theme.title()} Theme */

.stApp {{
  background-color: {self._get_theme_colors(theme)["background"]};
  color: {self._get_theme_colors(theme)["text"]};
}}

.industrial-metric {{
  background-color: {self._get_theme_colors(theme)["surface"]};
  border: 2px solid {self._get_theme_colors(theme)["primary"]};
  border-radius: 8px;
  padding: 1rem;
  margin: 0.5rem;
  text-align: center;
}}

.metric-value {{
  font-size: 2rem;
  font-weight: bold;
  color: {self._get_theme_colors(theme)["primary"]};
}}

{"/* Touch-friendly styles */" if "touch-friendly" in factory_options else ""}
.stButton > button {{
  min-width: 44px;
  min-height: 44px;
  padding: 12px 24px;
  font-size: 1.1rem;
  font-weight: 600;
}}

{"/* High contrast styles */" if "high-contrast" in factory_options else ""}
.high-contrast {{
  --primary-color: #FF8C42;
  --secondary-color: #0066CC;
  --background-color: #000000;
  --surface-color: #1A1A1A;
}}
"""

    def generate_hooks(self, data_source: str, features: list[str]) -> dict[str, str]:
        """Generate Streamlit utilities."""
        utilities = {}

        if "real-time" in features:
            utilities["data_connection.py"] = self._generate_data_connection_util(data_source)

        if "offline-support" in features:
            utilities["offline_support.py"] = self._generate_offline_util()

        return utilities

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

    def _generate_app_py(self, project_config: dict[str, Any], template_config: dict[str, Any]) -> str:
        """Generate main Streamlit application."""
        interface_type = project_config["type"]
        template = project_config["template"]

        return f'''
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import time

from utils.data_simulator import DataSimulator
from utils.industrial_components import (
    industrial_metric_card,
    industrial_alert_panel,
    industrial_status_indicator,
)
from config.config import CONFIG

# Page configuration
st.set_page_config(
    page_title=f"Industrial {interface_type.title()} - {template.title()}",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
with open("styles/industrial.css") as f:
    st.markdown(f"<style>{{f.read()}}</style>", unsafe_allow_html=True)

# Initialize session state
if 'data_simulator' not in st.session_state:
    st.session_state.data_simulator = DataSimulator()
    st.session_state.last_update = datetime.now()
    st.session_state.alerts = []

def main():
    """Main application function."""
    # Header
    st.title(f"🏭 Industrial {interface_type.title()}")
    st.markdown(f"Template: {template.title()} | Framework: Streamlit")

    # Connection status
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        st.markdown("**System Status:**")
    with col2:
        industrial_status_indicator("Connected", "normal")
    with col3:
        st.markdown(f"Last Update: {{st.session_state.last_update.strftime('%H:%M:%S')}}")

    # Main content based on interface type
    {self._generate_interface_content(interface_type, template)}

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # Update interval
        update_interval = st.slider(
            "Update Interval (seconds)",
            min_value=1,
            max_value=60,
            value=CONFIG.get('update_interval', 5)
        )

        # Theme selection
        theme = st.selectbox(
            "Theme",
            ["factory-dark", "factory-light", "high-contrast"],
            index=0
        )

        # Factory options
        st.subheader("Factory Options")
        touch_friendly = st.checkbox("Touch Friendly", value=True)
        high_contrast = st.checkbox("High Contrast", value=False)
        offline_support = st.checkbox("Offline Support", value=True)

    # Auto-refresh
    if st.button("🔄 Refresh Data", type="primary"):
        st.session_state.last_update = datetime.now()
        st.rerun()

def {self._get_interface_function_name(interface_type, template)}():
    """Generate content for specific interface type and template."""
    {self._generate_template_implementation(interface_type, template)}

{self._generate_additional_functions(interface_type, template)}

if __name__ == "__main__":
    main()
'''

    def _generate_interface_content(self, interface_type: str, template: str) -> str:
        """Generate interface-specific content."""
        return f'''
    if "{interface_type}" == "dashboard":
        {self._get_interface_function_name(interface_type, template)}()
    elif "{interface_type}" == "control-panel":
        {self._get_interface_function_name(interface_type, template)}()
    elif "{interface_type}" == "calculator":
        {self._get_interface_function_name(interface_type, template)}()
    else:
        st.info("Interface type not implemented")
'''

    def _get_interface_function_name(self, interface_type: str, template: str) -> str:
        """Get function name for interface."""
        return f"render_{interface_type}_{template.replace('-', '_')}"

    def _generate_template_implementation(self, interface_type: str, template: str) -> str:
        """Generate specific template implementation."""
        implementations = {
            "dashboard": {
                "pump-monitoring": """
    # Get simulated data
    data = st.session_state.data_simulator.get_pump_data()

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        industrial_metric_card(
            "Pressure",
            f"{data['pressure']:.1f}",
            "PSI",
            status="normal" if data['pressure'] < 120 else "warning" if data['pressure'] < 150 else "critical"
        )

    with col2:
        industrial_metric_card(
            "Flow Rate",
            f"{data['flowRate']:.1f}",
            "GPM",
            status="normal" if data['flowRate'] > 75 else "warning" if data['flowRate'] > 50 else "critical"
        )

    with col3:
        industrial_metric_card(
            "Temperature",
            f"{data['temperature']:.1f}",
            "°F",
            status="normal" if data['temperature'] < 180 else "warning" if data['temperature'] < 200 else "critical"
        )

    with col4:
        industrial_metric_card(
            "Vibration",
            f"{data['vibration']:.2f}",
            "mm/s",
            status="normal" if data['vibration'] < 3 else "warning" if data['vibration'] < 5 else "critical"
        )

    # Historical data chart
    st.subheader("📊 Historical Trends")

    historical_data = st.session_state.data_simulator.get_historical_data()
    df = pd.DataFrame(historical_data)

    fig = px.line(
        df,
        x='timestamp',
        y=['pressure', 'flowRate', 'temperature', 'vibration'],
        title="Pump Metrics Over Time",
        labels={
            'timestamp': 'Time',
            'value': 'Value',
            'variable': 'Metric'
        }
    )

    fig.update_layout(
        template="plotly_dark",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # Alerts section
    st.subheader("🚨 Alerts")
    alerts = st.session_state.data_simulator.get_alerts()

    if alerts:
        for alert in alerts:
            industrial_alert_panel(alert['level'], alert['message'])
    else:
        st.success("No active alerts")
""",
                "system-overview": """
    # System overview implementation
    st.info("System overview template implementation")
""",
            },
            "control-panel": {
                "equipment-control": """
    # Equipment control interface
    st.subheader("🎛️ Equipment Control")

    # Control buttons
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("▶️ START", type="primary", use_container_width=True):
            st.success("Equipment started")

    with col2:
        if st.button("⏸️ STOP", type="secondary", use_container_width=True):
            st.warning("Equipment stopped")

    with col3:
        if st.button("🔄 RESET", use_container_width=True):
            st.info("Equipment reset")

    # Status indicators
    st.subheader("📊 Equipment Status")

    status_data = {
        "Equipment": ["Pump A", "Pump B", "Valve 1", "Valve 2"],
        "Status": ["Running", "Stopped", "Open", "Closed"],
        "Efficiency": [85, 0, 100, 100],
    }

    df_status = pd.DataFrame(status_data)
    st.dataframe(df_status, use_container_width=True)
""",
            },
            "calculator": {
                "pipe-sizing": """
    # Pipe sizing calculator
    st.subheader("🧮 Pipe Sizing Calculator")

    # Input parameters
    col1, col2 = st.columns(2)

    with col1:
        flow_rate = st.number_input("Flow Rate (GPM)", min_value=0.0, value=100.0)
        velocity = st.number_input("Velocity (ft/s)", min_value=0.0, value=5.0)

    with col2:
        pressure_drop = st.number_input("Pressure Drop (psi/100ft)", min_value=0.0, value=2.0)
        pipe_length = st.number_input("Pipe Length (ft)", min_value=0.0, value=100.0)

    # Calculate button
    if st.button("🧮 Calculate", type="primary"):
        # Simple pipe sizing calculation
        pipe_area = flow_rate / (velocity * 448.831)  # Convert GPM to ft³/s
        pipe_diameter = 2 * (pipe_area / 3.14159) ** 0.5
        pipe_diameter_inches = pipe_diameter * 12

        total_pressure_drop = pressure_drop * (pipe_length / 100)

        # Results
        st.subheader("📋 Results")

        col1, col2 = st.columns(2)

        with col1:
            industrial_metric_card(
                "Pipe Diameter",
                f"{pipe_diameter_inches:.2f}",
                "inches",
                status="normal"
            )

            industrial_metric_card(
                "Total Pressure Drop",
                f"{total_pressure_drop:.2f}",
                "psi",
                status="normal" if total_pressure_drop < 10 else "warning"
            )

        with col2:
            industrial_metric_card(
                "Flow Velocity",
                f"{velocity:.1f}",
                "ft/s",
                status="normal" if velocity < 10 else "warning"
            )

            industrial_metric_card(
                "Reynolds Number",
                f"{(velocity * pipe_diameter * 1000):.0f}",
                "",
                status="normal"
            )
""",
            },
        }

        return implementations.get(interface_type, {}).get(template, 'st.info("Template not implemented")')

    def _generate_additional_functions(self, interface_type: str, template: str) -> str:
        """Generate additional helper functions."""
        return '''
def render_sidebar_config():
    """Render sidebar configuration options."""
    pass

def handle_data_refresh():
    """Handle manual data refresh."""
    st.session_state.last_update = datetime.now()
    st.success("Data refreshed!")
'''

    def _generate_data_simulator(self) -> str:
        """Generate data simulator utility."""
        return '''
import random
import time
from datetime import datetime, timedelta
from typing import Dict, List, Any


class DataSimulator:
    """Simulates industrial data for testing purposes."""

    def __init__(self):
        """Initialize the data simulator."""
        self.base_values = {
            "pressure": 100.0,
            "flowRate": 80.0,
            "temperature": 160.0,
            "vibration": 2.0,
        }
        self.historical_data = []
        self._generate_initial_data()

    def _generate_initial_data(self):
        """Generate initial historical data."""
        now = datetime.now()
        for i in range(50):
            timestamp = now - timedelta(seconds=(49 - i))
            data_point = {
                "timestamp": timestamp.isoformat(),
                "pressure": self.base_values["pressure"] + random.uniform(-20, 30),
                "flowRate": self.base_values["flowRate"] + random.uniform(-10, 20),
                "temperature": self.base_values["temperature"] + random.uniform(-10, 20),
                "vibration": self.base_values["vibration"] + random.uniform(-1, 2),
            }
            self.historical_data.append(data_point)

    def get_pump_data(self) -> Dict[str, float]:
        """Get current pump data with realistic variations."""
        return {
            "pressure": self.base_values["pressure"] + random.uniform(-20, 30),
            "flowRate": self.base_values["flowRate"] + random.uniform(-10, 20),
            "temperature": self.base_values["temperature"] + random.uniform(-10, 20),
            "vibration": self.base_values["vibration"] + random.uniform(-1, 2),
        }

    def get_historical_data(self) -> List[Dict[str, Any]]:
        """Get historical data with new data point."""
        # Add new data point
        current_data = self.get_pump_data()
        current_data["timestamp"] = datetime.now().isoformat()

        self.historical_data.append(current_data)

        # Keep only last 50 data points
        if len(self.historical_data) > 50:
            self.historical_data = self.historical_data[-50:]

        return self.historical_data

    def get_alerts(self) -> List[Dict[str, str]]:
        """Get simulated alerts based on current conditions."""
        alerts = []
        data = self.get_pump_data()

        if data["pressure"] > 150:
            alerts.append({
                "level": "critical",
                "message": "High pressure detected! Check pump immediately."
            })
        elif data["pressure"] > 120:
            alerts.append({
                "level": "warning",
                "message": "Elevated pressure - monitor closely."
            })

        if data["flowRate"] < 50:
            alerts.append({
                "level": "critical",
                "message": "Low flow rate - potential blockage."
            })
        elif data["flowRate"] < 75:
            alerts.append({
                "level": "warning",
                "message": "Reduced flow rate detected."
            })

        if data["temperature"] > 200:
            alerts.append({
                "level": "critical",
                "message": "Overheating detected - immediate attention required."
            })
        elif data["temperature"] > 180:
            alerts.append({
                "level": "warning",
                "message": "High temperature - check cooling system."
            })

        return alerts
'''

    def _generate_industrial_components(self) -> str:
        """Generate industrial Streamlit components."""
        return '''
import streamlit as st


def industrial_metric_card(title: str, value: str, unit: str, status: str = "normal"):
    """Display an industrial-style metric card."""
    status_colors = {
        "normal": "#4CAF50",
        "warning": "#F57C00",
        "critical": "#D32F2F"
    }

    border_color = status_colors.get(status, "#757575")

    st.markdown(f"""
    <div style="
        background-color: #2A2A2A;
        border: 2px solid {border_color};
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
        text-align: center;
    ">
        <div style="font-size: 0.9rem; color: #B0B0B0; margin-bottom: 0.5rem;">{title}</div>
        <div style="font-size: 2rem; font-weight: bold; color: {border_color};">{value}</div>
        <div style="font-size: 0.9rem; color: #B0B0B0;">{unit}</div>
    </div>
    """, unsafe_allow_html=True)


def industrial_status_indicator(label: str, status: str):
    """Display an industrial status indicator."""
    status_colors = {
        "normal": "#4CAF50",
        "warning": "#F57C00",
        "critical": "#D32F2F",
        "connected": "#2196F3",
        "offline": "#757575"
    }

    color = status_colors.get(status, "#757575")

    st.markdown(f"""
    <div style="display: flex; align-items: center; margin: 0.5rem 0;">
        <div style="
            width: 16px;
            height: 16px;
            border-radius: 50%;
            background-color: {color};
            margin-right: 8px;
            box-shadow: 0 0 8px {color}40;
        "></div>
        <span>{label}</span>
    </div>
    """, unsafe_allow_html=True)


def industrial_alert_panel(level: str, message: str):
    """Display an industrial alert panel."""
    level_colors = {
        "info": "#2196F3",
        "warning": "#F57C00",
        "critical": "#D32F2F"
    }

    level_icons = {
        "info": "ℹ️",
        "warning": "⚠️",
        "critical": "🚨"
    }

    color = level_colors.get(level, "#757575")
    icon = level_icons.get(level, "ℹ️")

    st.markdown(f"""
    <div style="
        background-color: {color}20;
        border-left: 6px solid {color};
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    ">
        <div style="display: flex; align-items: center; margin-bottom: 0.5rem;">
            <span style="font-size: 1.2rem; margin-right: 8px;">{icon}</span>
            <strong style="color: {color}; text-transform: uppercase;">{level}</strong>
        </div>
        <div>{message}</div>
    </div>
    """, unsafe_allow_html=True)


def industrial_control_button(label: str, on_click=None, key=None):
    """Display an industrial-style control button."""
    button_style = """
    <style>
    .industrial-button {
        background-color: #FF6B35;
        color: white;
        border: none;
        padding: 12px 24px;
        font-size: 1.1rem;
        font-weight: 600;
        border-radius: 8px;
        cursor: pointer;
        min-width: 44px;
        min-height: 44px;
        text-transform: uppercase;
    }
    .industrial-button:hover {
        background-color: #FF8C42;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.3);
    }
    </style>
    """

    st.markdown(button_style, unsafe_allow_html=True)

    return st.button(label, key=key, on_click=on_click)
'''

    def _generate_config_py(self, project_config: dict[str, Any]) -> str:
        """Generate configuration file."""
        return f'''
# Industrial Streamlit Configuration

CONFIG = {{
    "theme": "{project_config.get("theme", "factory-dark")}",
    "data_source": "{project_config.get("data_source", "mock")}",
    "update_interval": {project_config.get("update_interval", 5)},
    "factory_options": {project_config.get("factory_options", [])},
    "features": {project_config.get("features", [])},
    "thresholds": {{
        "pressure": {{"warning": 120, "critical": 150}},
        "temperature": {{"warning": 180, "critical": 200}},
        "flowRate": {{"warning": 75, "critical": 50}},
        "vibration": {{"warning": 3, "critical": 5}},
    }}
}}
'''

    def _generate_streamlit_config(self) -> str:
        """Generate Streamlit configuration."""
        return """
[theme]
primaryColor = "#FF6B35"
backgroundColor = "#1A1A1A"
secondaryBackgroundColor = "#2A2A2A"
textColor = "#FFFFFF"
font = "monospace"

[server]
headless = true
port = 8501
enableCORS = false

[browser]
gatherUsageStats = false
"""

    def _generate_data_connection_util(self, data_source: str) -> str:
        """Generate data connection utility."""
        return f'''
# Data connection utilities for {data_source}

import time
from typing import Dict, Any, Optional

class DataConnection:
    """Handles data connection for {data_source}."""

    def __init__(self):
        self.connected = False
        self.last_data = None

    def connect(self) -> bool:
        """Establish connection."""
        try:
            # Connection logic for {data_source}
            self.connected = True
            return True
        except Exception as e:
            print(f"Connection failed: {{e}}")
            return False

    def get_data(self) -> Optional[Dict[str, Any]]:
        """Get latest data."""
        if not self.connected:
            return None

        # Data retrieval logic
        return {{"timestamp": time.time(), "value": 42}}
'''

    def _generate_offline_util(self) -> str:
        """Generate offline support utility."""
        return '''
# Offline support utilities

import json
import time
from typing import Dict, Any, List, Optional

class OfflineManager:
    """Manages offline data storage and synchronization."""

    def __init__(self):
        self.cache = {}
        self.queue = []

    def store_data(self, key: str, data: Any):
        """Store data locally."""
        self.cache[key] = {
            "data": data,
            "timestamp": time.time()
        }

    def get_data(self, key: str) -> Optional[Any]:
        """Retrieve cached data."""
        item = self.cache.get(key)
        if item:
            return item["data"]
        return None

    def queue_operation(self, operation: Dict[str, Any]):
        """Queue operation for when connection is restored."""
        self.queue.append(operation)

    def process_queue(self) -> List[Dict[str, Any]]:
        """Get queued operations."""
        operations = self.queue.copy()
        self.queue.clear()
        return operations
'''

    def _generate_metrics_component_st(self, config: dict[str, Any]) -> str:
        """Generate Streamlit metrics component."""
        return '''
def render_metrics_panel(data: Dict[str, Any]):
    """Render metrics panel in Streamlit."""
    for metric, value in data.items():
        industrial_metric_card(metric.title(), f"{value:.1f}", "units")
'''

    def _generate_chart_component_st(self, config: dict[str, Any]) -> str:
        """Generate Streamlit chart component."""
        return '''
def render_chart(data: List[Dict[str, Any]]):
    """Render chart in Streamlit."""
    import pandas as pd
    import plotly.express as px

    df = pd.DataFrame(data)
    fig = px.line(df, x='timestamp', y='value')
    st.plotly_chart(fig)
'''

    def _generate_control_component_st(self, config: dict[str, Any]) -> str:
        """Generate Streamlit control component."""
        return '''
def render_control_panel():
    """Render control panel in Streamlit."""
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("START", type="primary"):
            st.success("Started")

    with col2:
        if st.button("STOP", type="secondary"):
            st.warning("Stopped")

    with col3:
        if st.button("RESET"):
            st.info("Reset")
'''

    def _generate_status_component_st(self, config: dict[str, Any]) -> str:
        """Generate Streamlit status component."""
        return '''
def render_status_panel(status: Dict[str, str]):
    """Render status panel in Streamlit."""
    for item, state in status.items():
        industrial_status_indicator(item, state)
'''

    def _generate_alert_component_st(self, config: dict[str, Any]) -> str:
        """Generate Streamlit alert component."""
        return '''
def render_alert_panel(alerts: List[Dict[str, str]]):
    """Render alert panel in Streamlit."""
    for alert in alerts:
        industrial_alert_panel(alert["level"], alert["message"])
'''
