#!/usr/bin/env python3
"""
Monitoring Dashboard - Real-time monitoring for AI Assistant
Provides comprehensive monitoring of system performance, usage, and health
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
import statistics

try:
    from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    from fastapi.staticfiles import StaticFiles
    from fastapi.middleware.cors import CORSMiddleware
    import uvicorn
    import psutil
    from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST

    WEB_FRAMEWORK_AVAILABLE = True
except ImportError:
    WEB_FRAMEWORK_AVAILABLE = False
    print("⚠️ Web framework not installed - run: pip install fastapi uvicorn psutil prometheus-client")

logger = logging.getLogger(__name__)


@dataclass
class MetricValue:
    """Individual metric value with timestamp"""

    timestamp: datetime
    value: float
    labels: Dict[str, str] = field(default_factory=dict)


@dataclass
class SystemMetrics:
    """System performance metrics"""

    cpu_percent: float
    memory_percent: float
    disk_usage_percent: float
    active_connections: int
    timestamp: datetime


@dataclass
class ApplicationMetrics:
    """Application-specific metrics"""

    total_requests: int
    successful_requests: int
    failed_requests: int
    average_response_time: float
    llm_calls: int
    llm_tokens_used: int
    cache_hit_rate: float
    timestamp: datetime


@dataclass
class UserMetrics:
    """User interaction metrics"""

    active_users: int
    conversations_per_hour: float
    average_conversation_length: float
    user_satisfaction_score: float
    timestamp: datetime


class MetricsCollector:
    """Collects and stores metrics from various sources"""

    def __init__(self, max_history: int = 1000):
        self.max_history = max_history
        self.system_metrics: List[SystemMetrics] = []
        self.app_metrics: List[ApplicationMetrics] = []
        self.user_metrics: List[UserMetrics] = []
        self.custom_metrics: Dict[str, List[MetricValue]] = {}
        self.callbacks: List[Callable] = []

        # Prometheus metrics
        if WEB_FRAMEWORK_AVAILABLE:
            self.setup_prometheus_metrics()

    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        self.request_counter = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
        self.request_duration = Histogram("http_request_duration_seconds", "HTTP request duration")
        self.active_connections_gauge = Gauge("active_connections", "Number of active connections")
        self.llm_calls_counter = Counter("llm_calls_total", "Total LLM calls", ["provider", "model"])
        self.llm_tokens_counter = Counter("llm_tokens_total", "Total LLM tokens used", ["provider", "model"])
        self.cache_hit_rate_gauge = Gauge("cache_hit_rate", "Cache hit rate")

    async def collect_system_metrics(self):
        """Collect system performance metrics"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage("/")

            # Count network connections (simplified)
            connections = len(psutil.net_connections())

            metrics = SystemMetrics(
                cpu_percent=cpu_percent,
                memory_percent=memory.percent,
                disk_usage_percent=disk.percent,
                active_connections=connections,
                timestamp=datetime.now(),
            )

            self.system_metrics.append(metrics)
            if len(self.system_metrics) > self.max_history:
                self.system_metrics.pop(0)

        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")

    async def collect_application_metrics(self, app_instance=None):
        """Collect application-specific metrics"""
        try:
            # This would typically collect from your application
            # For demo purposes, we'll use mock data
            metrics = ApplicationMetrics(
                total_requests=1000,
                successful_requests=950,
                failed_requests=50,
                average_response_time=0.25,
                llm_calls=200,
                llm_tokens_used=50000,
                cache_hit_rate=0.85,
                timestamp=datetime.now(),
            )

            self.app_metrics.append(metrics)
            if len(self.app_metrics) > self.max_history:
                self.app_metrics.pop(0)

        except Exception as e:
            logger.error(f"Failed to collect application metrics: {e}")

    async def collect_user_metrics(self):
        """Collect user interaction metrics"""
        try:
            metrics = UserMetrics(
                active_users=45,
                conversations_per_hour=120.5,
                average_conversation_length=8.3,
                user_satisfaction_score=4.6,
                timestamp=datetime.now(),
            )

            self.user_metrics.append(metrics)
            if len(self.user_metrics) > self.max_history:
                self.user_metrics.pop(0)

        except Exception as e:
            logger.error(f"Failed to collect user metrics: {e}")

    def add_custom_metric(self, name: str, value: float, labels: Dict[str, str] = None):
        """Add a custom metric"""
        if name not in self.custom_metrics:
            self.custom_metrics[name] = []

        metric = MetricValue(timestamp=datetime.now(), value=value, labels=labels or {})

        self.custom_metrics[name].append(metric)
        if len(self.custom_metrics[name]) > self.max_history:
            self.custom_metrics[name].pop(0)

    def get_recent_metrics(self, metric_type: str, minutes: int = 60) -> List[Any]:
        """Get recent metrics within specified time window"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)

        if metric_type == "system":
            return [m for m in self.system_metrics if m.timestamp > cutoff_time]
        elif metric_type == "application":
            return [m for m in self.app_metrics if m.timestamp > cutoff_time]
        elif metric_type == "user":
            return [m for m in self.user_metrics if m.timestamp > cutoff_time]
        elif metric_type in self.custom_metrics:
            return [m for m in self.custom_metrics[metric_type] if m.timestamp > cutoff_time]

        return []

    def calculate_aggregates(self, metrics: List[Any], field: str) -> Dict[str, float]:
        """Calculate statistical aggregates for a metric field"""
        if not metrics:
            return {"min": 0, "max": 0, "avg": 0, "median": 0}

        values = [getattr(m, field) for m in metrics]
        return {
            "min": min(values),
            "max": max(values),
            "avg": statistics.mean(values),
            "median": statistics.median(values),
        }

    async def start_collection(self, interval: int = 30):
        """Start continuous metrics collection"""
        while True:
            try:
                await asyncio.gather(
                    self.collect_system_metrics(), self.collect_application_metrics(), self.collect_user_metrics()
                )

                # Notify callbacks
                for callback in self.callbacks:
                    try:
                        await callback()
                    except Exception as e:
                        logger.error(f"Callback error: {e}")

                await asyncio.sleep(interval)

            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(interval)


class MonitoringDashboard:
    """Web-based monitoring dashboard"""

    def __init__(self, metrics_collector: MetricsCollector, port: int = 8080):
        if not WEB_FRAMEWORK_AVAILABLE:
            raise ImportError("Web framework dependencies not installed")

        self.metrics_collector = metrics_collector
        self.port = port
        self.app = FastAPI(title="AI Assistant Monitoring Dashboard")
        self.websocket_connections: List[WebSocket] = []

        self.setup_routes()
        self.setup_middleware()

    def setup_middleware(self):
        """Setup FastAPI middleware"""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    def setup_routes(self):
        """Setup API routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            """Serve the monitoring dashboard"""
            return self.get_dashboard_html()

        @self.app.get("/metrics")
        async def prometheus_metrics():
            """Serve Prometheus metrics"""
            if not hasattr(self.metrics_collector, "request_counter"):
                return {"error": "Prometheus metrics not available"}

            return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)

        @self.app.get("/api/system-metrics")
        async def get_system_metrics(minutes: int = 60):
            """Get system metrics"""
            metrics = self.metrics_collector.get_recent_metrics("system", minutes)
            return {
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "cpu_percent": m.cpu_percent,
                        "memory_percent": m.memory_percent,
                        "disk_usage_percent": m.disk_usage_percent,
                        "active_connections": m.active_connections,
                    }
                    for m in metrics
                ],
                "aggregates": {
                    "cpu": self.metrics_collector.calculate_aggregates(metrics, "cpu_percent"),
                    "memory": self.metrics_collector.calculate_aggregates(metrics, "memory_percent"),
                    "disk": self.metrics_collector.calculate_aggregates(metrics, "disk_usage_percent"),
                },
            }

        @self.app.get("/api/application-metrics")
        async def get_application_metrics(minutes: int = 60):
            """Get application metrics"""
            metrics = self.metrics_collector.get_recent_metrics("application", minutes)
            return {
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "total_requests": m.total_requests,
                        "successful_requests": m.successful_requests,
                        "failed_requests": m.failed_requests,
                        "average_response_time": m.average_response_time,
                        "llm_calls": m.llm_calls,
                        "llm_tokens_used": m.llm_tokens_used,
                        "cache_hit_rate": m.cache_hit_rate,
                    }
                    for m in metrics
                ]
            }

        @self.app.get("/api/user-metrics")
        async def get_user_metrics(minutes: int = 60):
            """Get user metrics"""
            metrics = self.metrics_collector.get_recent_metrics("user", minutes)
            return {
                "metrics": [
                    {
                        "timestamp": m.timestamp.isoformat(),
                        "active_users": m.active_users,
                        "conversations_per_hour": m.conversations_per_hour,
                        "average_conversation_length": m.average_conversation_length,
                        "user_satisfaction_score": m.user_satisfaction_score,
                    }
                    for m in metrics
                ]
            }

        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            """WebSocket for real-time updates"""
            await websocket.accept()
            self.websocket_connections.append(websocket)

            try:
                while True:
                    # Send current metrics every 5 seconds
                    data = {
                        "timestamp": datetime.now().isoformat(),
                        "system": await self.get_system_metrics_dict(),
                        "application": await self.get_application_metrics_dict(),
                        "user": await self.get_user_metrics_dict(),
                    }

                    await websocket.send_text(json.dumps(data))
                    await asyncio.sleep(5)

            except WebSocketDisconnect:
                self.websocket_connections.remove(websocket)

        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": datetime.now().isoformat()}

    async def get_system_metrics_dict(self) -> Dict[str, Any]:
        """Get current system metrics as dict"""
        recent = self.metrics_collector.get_recent_metrics("system", 5)
        if recent:
            latest = recent[-1]
            return {
                "cpu_percent": latest.cpu_percent,
                "memory_percent": latest.memory_percent,
                "disk_usage_percent": latest.disk_usage_percent,
                "active_connections": latest.active_connections,
            }
        return {}

    async def get_application_metrics_dict(self) -> Dict[str, Any]:
        """Get current application metrics as dict"""
        recent = self.metrics_collector.get_recent_metrics("application", 5)
        if recent:
            latest = recent[-1]
            return {
                "total_requests": latest.total_requests,
                "successful_requests": latest.successful_requests,
                "failed_requests": latest.failed_requests,
                "average_response_time": latest.average_response_time,
                "llm_calls": latest.llm_calls,
                "llm_tokens_used": latest.llm_tokens_used,
                "cache_hit_rate": latest.cache_hit_rate,
            }
        return {}

    async def get_user_metrics_dict(self) -> Dict[str, Any]:
        """Get current user metrics as dict"""
        recent = self.metrics_collector.get_recent_metrics("user", 5)
        if recent:
            latest = recent[-1]
            return {
                "active_users": latest.active_users,
                "conversations_per_hour": latest.conversations_per_hour,
                "average_conversation_length": latest.average_conversation_length,
                "user_satisfaction_score": latest.user_satisfaction_score,
            }
        return {}

    def get_dashboard_html(self) -> str:
        """Generate the dashboard HTML"""
        return """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI Assistant Monitoring Dashboard</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: #1a1a1a;
            color: #ffffff;
            overflow-x: hidden;
        }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
            gap: 20px;
            padding: 20px;
            max-width: 1600px;
            margin: 0 auto;
        }

        .card {
            background: #2a2a2a;
            border-radius: 12px;
            padding: 20px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.3);
            border: 1px solid #3a3a3a;
        }

        .card h2 {
            margin-bottom: 20px;
            color: #00ff88;
            font-size: 1.2em;
            font-weight: 600;
        }

        .metric {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px 0;
            border-bottom: 1px solid #3a3a3a;
        }

        .metric:last-child {
            border-bottom: none;
        }

        .metric-label {
            color: #999;
            font-size: 0.9em;
        }

        .metric-value {
            font-size: 1.1em;
            font-weight: 600;
        }

        .metric-value.good {
            color: #00ff88;
        }

        .metric-value.warning {
            color: #ffaa00;
        }

        .metric-value.critical {
            color: #ff4444;
        }

        .chart-container {
            height: 200px;
            margin-top: 20px;
        }

        .header {
            background: linear-gradient(135deg, #00ff88, #00aaff);
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
        }

        .header h1 {
            font-size: 2.5em;
            font-weight: 700;
            text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
        }

        .status {
            display: inline-block;
            padding: 8px 16px;
            background: rgba(255, 255, 255, 0.2);
            border-radius: 20px;
            margin-top: 10px;
            font-weight: 500;
        }

        .last-update {
            text-align: center;
            color: #666;
            margin: 20px 0;
            font-size: 0.9em;
        }
    </style>
</head>
<body>
    <div class="header">
        <h1>🤖 AI Assistant Dashboard</h1>
        <div class="status">● System Operational</div>
    </div>

    <div class="dashboard">
        <!-- System Metrics -->
        <div class="card">
            <h2>🖥️ System Performance</h2>
            <div class="metric">
                <span class="metric-label">CPU Usage</span>
                <span class="metric-value" id="cpu-percent">--%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Memory Usage</span>
                <span class="metric-value" id="memory-percent">--%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Disk Usage</span>
                <span class="metric-value" id="disk-percent">--%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Active Connections</span>
                <span class="metric-value" id="connections">--</span>
            </div>
            <div class="chart-container">
                <canvas id="system-chart"></canvas>
            </div>
        </div>

        <!-- Application Metrics -->
        <div class="card">
            <h2>📊 Application Performance</h2>
            <div class="metric">
                <span class="metric-label">Total Requests</span>
                <span class="metric-value" id="total-requests">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Success Rate</span>
                <span class="metric-value" id="success-rate">--%</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Response Time</span>
                <span class="metric-value" id="avg-response">--ms</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cache Hit Rate</span>
                <span class="metric-value" id="cache-hit">--%</span>
            </div>
            <div class="chart-container">
                <canvas id="app-chart"></canvas>
            </div>
        </div>

        <!-- LLM Metrics -->
        <div class="card">
            <h2>🧠 LLM Usage</h2>
            <div class="metric">
                <span class="metric-label">Total LLM Calls</span>
                <span class="metric-value" id="llm-calls">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Tokens Used</span>
                <span class="metric-value" id="llm-tokens">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Tokens per Call</span>
                <span class="metric-value" id="avg-tokens">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Cost (Estimate)</span>
                <span class="metric-value" id="llm-cost">--$</span>
            </div>
            <div class="chart-container">
                <canvas id="llm-chart"></canvas>
            </div>
        </div>

        <!-- User Metrics -->
        <div class="card">
            <h2>👥 User Activity</h2>
            <div class="metric">
                <span class="metric-label">Active Users</span>
                <span class="metric-value" id="active-users">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Conversations/Hour</span>
                <span class="metric-value" id="conversations-per-hour">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">Avg Conversation Length</span>
                <span class="metric-value" id="avg-conversation-length">--</span>
            </div>
            <div class="metric">
                <span class="metric-label">User Satisfaction</span>
                <span class="metric-value" id="user-satisfaction">--/5</span>
            </div>
            <div class="chart-container">
                <canvas id="user-chart"></canvas>
            </div>
        </div>
    </div>

    <div class="last-update" id="last-update">Last updated: --</div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket(`ws://${window.location.host}/ws`);

        // Chart configuration
        const chartOptions = {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#3a3a3a'
                    },
                    ticks: {
                        color: '#666'
                    }
                },
                y: {
                    grid: {
                        color: '#3a3a3a'
                    },
                    ticks: {
                        color: '#666'
                    }
                }
            }
        };

        // Initialize charts
        const systemChart = new Chart(document.getElementById('system-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'CPU %',
                    data: [],
                    borderColor: '#00ff88',
                    backgroundColor: 'rgba(0, 255, 136, 0.1)',
                    tension: 0.4
                }]
            },
            options: chartOptions
        });

        const appChart = new Chart(document.getElementById('app-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Response Time (ms)',
                    data: [],
                    borderColor: '#00aaff',
                    backgroundColor: 'rgba(0, 170, 255, 0.1)',
                    tension: 0.4
                }]
            },
            options: chartOptions
        });

        const llmChart = new Chart(document.getElementById('llm-chart'), {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Tokens Used',
                    data: [],
                    backgroundColor: '#ff6b6b'
                }]
            },
            options: chartOptions
        });

        const userChart = new Chart(document.getElementById('user-chart'), {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Active Users',
                    data: [],
                    borderColor: '#ffd93d',
                    backgroundColor: 'rgba(255, 217, 61, 0.1)',
                    tension: 0.4
                }]
            },
            options: chartOptions
        });

        // Update dashboard with new data
        function updateDashboard(data) {
            // Update system metrics
            if (data.system) {
                document.getElementById('cpu-percent').textContent = data.system.cpu_percent.toFixed(1) + '%';
                document.getElementById('memory-percent').textContent = data.system.memory_percent.toFixed(1) + '%';
                document.getElementById('disk-percent').textContent = data.system.disk_usage_percent.toFixed(1) + '%';
                document.getElementById('connections').textContent = data.system.active_connections;

                // Update color coding
                updateMetricColor('cpu-percent', data.system.cpu_percent, 70, 90);
                updateMetricColor('memory-percent', data.system.memory_percent, 70, 90);
                updateMetricColor('disk-percent', data.system.disk_usage_percent, 80, 95);
            }

            // Update application metrics
            if (data.application) {
                document.getElementById('total-requests').textContent = data.application.total_requests.toLocaleString();
                const successRate = (data.application.successful_requests / data.application.total_requests * 100).toFixed(1);
                document.getElementById('success-rate').textContent = successRate + '%';
                document.getElementById('avg-response').textContent = (data.application.average_response_time * 1000).toFixed(0) + 'ms';
                document.getElementById('cache-hit').textContent = (data.application.cache_hit_rate * 100).toFixed(1) + '%';
                document.getElementById('llm-calls').textContent = data.application.llm_calls.toLocaleString();
                document.getElementById('llm-tokens').textContent = data.application.llm_tokens_used.toLocaleString();

                const avgTokens = Math.round(data.application.llm_tokens_used / data.application.llm_calls);
                document.getElementById('avg-tokens').textContent = avgTokens.toLocaleString();

                // Estimate cost (assuming $0.01 per 1K tokens)
                const cost = (data.application.llm_tokens_used / 1000 * 0.01).toFixed(2);
                document.getElementById('llm-cost').textContent = '$' + cost;

                // Update color coding
                updateMetricColor('success-rate', parseFloat(successRate), 95, 99);
                updateMetricColor('avg-response', data.application.average_response_time * 1000, 500, 1000, true);
                updateMetricColor('cache-hit', data.application.cache_hit_rate * 100, 70, 85);
            }

            // Update user metrics
            if (data.user) {
                document.getElementById('active-users').textContent = data.user.active_users.toLocaleString();
                document.getElementById('conversations-per-hour').textContent = data.user.conversations_per_hour.toFixed(1);
                document.getElementById('avg-conversation-length').textContent = data.user.average_conversation_length.toFixed(1);
                document.getElementById('user-satisfaction').textContent = data.user.user_satisfaction_score.toFixed(1) + '/5';
            }

            // Update last update time
            document.getElementById('last-update').textContent = 'Last updated: ' + new Date().toLocaleTimeString();

            // Update charts (keep last 20 data points)
            const timestamp = new Date().toLocaleTimeString();

            updateChart(systemChart, timestamp, [data.system ? data.system.cpu_percent : 0]);
            updateChart(appChart, timestamp, [data.application ? data.application.average_response_time * 1000 : 0]);
            updateChart(llmChart, timestamp, [data.application ? data.application.llm_tokens_used : 0]);
            updateChart(userChart, timestamp, [data.user ? data.user.active_users : 0]);
        }

        function updateMetricColor(elementId, value, warningThreshold, criticalThreshold, inverse = false) {
            const element = document.getElementById(elementId);
            element.classList.remove('good', 'warning', 'critical');

            if (inverse) {
                if (value <= warningThreshold) {
                    element.classList.add('good');
                } else if (value <= criticalThreshold) {
                    element.classList.add('warning');
                } else {
                    element.classList.add('critical');
                }
            } else {
                if (value <= warningThreshold) {
                    element.classList.add('good');
                } else if (value <= criticalThreshold) {
                    element.classList.add('warning');
                } else {
                    element.classList.add('critical');
                }
            }
        }

        function updateChart(chart, label, data) {
            chart.data.labels.push(label);
            chart.data.datasets[0].data.push(...data);

            // Keep only last 20 data points
            if (chart.data.labels.length > 20) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }

            chart.update('none'); // Update without animation for performance
        }

        // Handle WebSocket messages
        ws.onmessage = function(event) {
            const data = JSON.parse(event.data);
            updateDashboard(data);
        };

        ws.onopen = function() {
            console.log('Connected to monitoring dashboard');
        };

        ws.onclose = function() {
            console.log('Disconnected from monitoring dashboard');
            // Attempt to reconnect after 5 seconds
            setTimeout(() => {
                location.reload();
            }, 5000);
        };

        ws.onerror = function(error) {
            console.error('WebSocket error:', error);
        };
    </script>
</body>
</html>
        """

    async def start_server(self):
        """Start the monitoring dashboard server"""
        config = uvicorn.Config(self.app, host="0.0.0.0", port=self.port, log_level="info")

        server = uvicorn.Server(config)
        await server.serve()


# CLI interface for running the monitoring dashboard
async def main():
    """Run the monitoring dashboard"""
    import argparse

    parser = argparse.ArgumentParser(description="AI Assistant Monitoring Dashboard")
    parser.add_argument("--port", type=int, default=8080, help="Port to run the dashboard on")
    parser.add_argument("--metrics-interval", type=int, default=30, help="Metrics collection interval in seconds")

    args = parser.parse_args()

    if not WEB_FRAMEWORK_AVAILABLE:
        print("❌ Web framework dependencies not installed")
        print("   Run: pip install fastapi uvicorn psutil prometheus-client")
        return 1

    print("🚀 Starting AI Assistant Monitoring Dashboard")
    print(f"   📊 Dashboard: http://localhost:{args.port}")
    print(f"   📈 Metrics: http://localhost:{args.port}/metrics")
    print(f"   🔗 WebSocket: ws://localhost:{args.port}/ws")
    print()

    # Initialize metrics collector
    metrics_collector = MetricsCollector()

    # Start metrics collection
    collection_task = asyncio.create_task(metrics_collector.start_collection(args.metrics_interval))

    try:
        # Initialize and start dashboard
        dashboard = MonitoringDashboard(metrics_collector, args.port)
        await dashboard.start_server()

    except KeyboardInterrupt:
        print("\n🛑 Shutting down monitoring dashboard")
        collection_task.cancel()

    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        collection_task.cancel()
        return 1

    return 0


if __name__ == "__main__":
    import sys

    sys.exit(asyncio.run(main()))
