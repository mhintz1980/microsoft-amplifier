#!/usr/bin/env python3
"""
Deployment Configuration - Production deployment setup for AI Assistant
Includes Docker, Kubernetes, and monitoring configurations
"""

import os
import yaml
from pathlib import Path
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any


@dataclass
class DeploymentConfig:
    """Production deployment configuration"""

    app_name: str = "component-library-assistant"
    version: str = "1.0.0"
    environment: str = "production"
    replicas: int = 3

    # Container configuration
    image_name: str = "component-library-assistant"
    image_tag: str = "latest"
    port: int = 8000

    # Resource limits
    cpu_limit: str = "500m"
    memory_limit: str = "512Mi"
    cpu_request: str = "100m"
    memory_request: str = "128Mi"

    # Environment variables
    env_vars: Dict[str, str] = field(default_factory=dict)
    secrets: List[str] = field(default_factory=list)

    # Health checks
    health_check_path: str = "/health"
    readiness_path: str = "/ready"

    # Monitoring
    enable_metrics: bool = True
    metrics_port: int = 9090

    # Scaling
    enable_hpa: bool = True
    min_replicas: int = 2
    max_replicas: int = 10
    target_cpu_utilization: int = 70

    # Storage
    enable_persistence: bool = True
    storage_size: str = "1Gi"
    storage_class: str = "standard"


class DockerConfigGenerator:
    """Generate Docker configurations"""

    @staticmethod
    def create_dockerfile(config: DeploymentConfig) -> str:
        """Create optimized Dockerfile"""
        return f"""# Multi-stage build for production optimization
FROM python:3.11-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PIP_NO_CACHE_DIR=1 \\
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    build-essential \\
    curl \\
    git \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.11-slim as production

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \\
    PYTHONUNBUFFERED=1 \\
    PATH="/home/app/.local/bin:$PATH"

# Install runtime dependencies only
RUN apt-get update && apt-get install -y \\
    curl \\
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd --create-home --shell /bin/bash app

# Set work directory
WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY . .

# Change ownership to app user
RUN chown -R app:app /app
USER app

# Create necessary directories
RUN mkdir -p /app/data /app/logs /app/cache

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:{config.port}{config.health_check_path} || exit 1

# Expose port
EXPOSE {config.port}

# Run the application
CMD ["python", "-m", "ai_assistant.main", "--host", "0.0.0.0", "--port", "{config.port}"]
"""

    @staticmethod
    def create_docker_compose(config: DeploymentConfig) -> str:
        """Create Docker Compose configuration"""
        return f"""version: '3.8'

services:
  {config.app_name}:
    build:
      context: .
      dockerfile: Dockerfile
    image: {config.image_name}:{config.image_tag}
    container_name: {config.app_name}
    restart: unless-stopped
    ports:
      - "{config.port}:{config.port}"
    environment:
      - ENVIRONMENT={config.environment}
      - LOG_LEVEL=INFO
      - REDIS_URL=redis://redis:6379
      - DATABASE_URL=postgresql://postgres:password@postgres:5432/component_library
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
      - ./cache:/app/cache
    depends_on:
      - redis
      - postgres
    deploy:
      resources:
        limits:
          cpus: '{config.cpu_limit}'
          memory: {config.memory_limit}
        reservations:
          cpus: '{config.cpu_request}'
          memory: {config.memory_request}
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:{config.port}{config.health_check_path}"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

  redis:
    image: redis:7-alpine
    container_name: {config.app_name}-redis
    restart: unless-stopped
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    deploy:
      resources:
        limits:
          cpus: '200m'
          memory: 256Mi
        reservations:
          cpus: '100m'
          memory: 128Mi
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  postgres:
    image: postgres:15-alpine
    container_name: {config.app_name}-postgres
    restart: unless-stopped
    ports:
      - "5432:5432"
    environment:
      - POSTGRES_DB=component_library
      - POSTGRES_USER=postgres
      - POSTGRES_PASSWORD=password
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./scripts/init_db.sql:/docker-entrypoint-initdb.d/init_db.sql
    deploy:
      resources:
        limits:
          cpus: '500m'
          memory: 512Mi
        reservations:
          cpus: '200m'
          memory: 256Mi
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  nginx:
    image: nginx:alpine
    container_name: {config.app_name}-nginx
    restart: unless-stopped
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
    depends_on:
      - {config.app_name}
    deploy:
      resources:
        limits:
          cpus: '200m'
          memory: 128Mi
        reservations:
          cpus: '100m'
          memory: 64Mi

volumes:
  redis_data:
    driver: local
  postgres_data:
    driver: local

networks:
  default:
    driver: bridge
"""


class KubernetesConfigGenerator:
    """Generate Kubernetes configurations"""

    @staticmethod
    def create_namespace(config: DeploymentConfig) -> Dict[str, Any]:
        """Create namespace configuration"""
        return {
            "apiVersion": "v1",
            "kind": "Namespace",
            "metadata": {
                "name": config.app_name,
                "labels": {"app": config.app_name, "environment": config.environment},
            },
        }

    @staticmethod
    def create_deployment(config: DeploymentConfig) -> Dict[str, Any]:
        """Create deployment configuration"""
        return {
            "apiVersion": "apps/v1",
            "kind": "Deployment",
            "metadata": {
                "name": config.app_name,
                "namespace": config.app_name,
                "labels": {"app": config.app_name, "version": config.version},
            },
            "spec": {
                "replicas": config.replicas,
                "selector": {"matchLabels": {"app": config.app_name}},
                "template": {
                    "metadata": {"labels": {"app": config.app_name, "version": config.version}},
                    "spec": {
                        "containers": [
                            {
                                "name": config.app_name,
                                "image": f"{config.image_name}:{config.image_tag}",
                                "ports": [{"containerPort": config.port, "protocol": "TCP"}],
                                "env": [
                                    {"name": "ENVIRONMENT", "value": config.environment},
                                    {"name": "LOG_LEVEL", "value": "INFO"},
                                    {"name": "REDIS_URL", "value": "redis://redis-service:6379"},
                                    {
                                        "name": "DATABASE_URL",
                                        "value": "postgresql://postgres:password@postgres-service:5432/component_library",
                                    },
                                ]
                                + [{"name": key, "value": value} for key, value in config.env_vars.items()],
                                "resources": {
                                    "limits": {"cpu": config.cpu_limit, "memory": config.memory_limit},
                                    "requests": {"cpu": config.cpu_request, "memory": config.memory_request},
                                },
                                "livenessProbe": {
                                    "httpGet": {"path": config.health_check_path, "port": config.port},
                                    "initialDelaySeconds": 30,
                                    "periodSeconds": 10,
                                    "timeoutSeconds": 5,
                                    "failureThreshold": 3,
                                },
                                "readinessProbe": {
                                    "httpGet": {"path": config.readiness_path, "port": config.port},
                                    "initialDelaySeconds": 5,
                                    "periodSeconds": 5,
                                    "timeoutSeconds": 3,
                                    "failureThreshold": 3,
                                },
                                "volumeMounts": [
                                    {"name": "data-volume", "mountPath": "/app/data"},
                                    {"name": "cache-volume", "mountPath": "/app/cache"},
                                ],
                            }
                        ],
                        "volumes": [
                            {
                                "name": "data-volume",
                                "persistentVolumeClaim": {"claimName": f"{config.app_name}-data-pvc"},
                            },
                            {"name": "cache-volume", "emptyDir": {}},
                        ],
                    },
                },
            },
        }

    @staticmethod
    def create_service(config: DeploymentConfig) -> Dict[str, Any]:
        """Create service configuration"""
        return {
            "apiVersion": "v1",
            "kind": "Service",
            "metadata": {
                "name": f"{config.app_name}-service",
                "namespace": config.app_name,
                "labels": {"app": config.app_name},
            },
            "spec": {
                "selector": {"app": config.app_name},
                "ports": [{"port": 80, "targetPort": config.port, "protocol": "TCP", "name": "http"}],
                "type": "ClusterIP",
            },
        }

    @staticmethod
    def create_hpa(config: DeploymentConfig) -> Dict[str, Any]:
        """Create horizontal pod autoscaler configuration"""
        if not config.enable_hpa:
            return None

        return {
            "apiVersion": "autoscaling/v2",
            "kind": "HorizontalPodAutoscaler",
            "metadata": {"name": f"{config.app_name}-hpa", "namespace": config.app_name},
            "spec": {
                "scaleTargetRef": {"apiVersion": "apps/v1", "kind": "Deployment", "name": config.app_name},
                "minReplicas": config.min_replicas,
                "maxReplicas": config.max_replicas,
                "metrics": [
                    {
                        "type": "Resource",
                        "resource": {
                            "name": "cpu",
                            "target": {"type": "Utilization", "averageUtilization": config.target_cpu_utilization},
                        },
                    }
                ],
            },
        }

    @staticmethod
    def create_pvc(config: DeploymentConfig) -> Dict[str, Any]:
        """Create persistent volume claim configuration"""
        if not config.enable_persistence:
            return None

        return {
            "apiVersion": "v1",
            "kind": "PersistentVolumeClaim",
            "metadata": {
                "name": f"{config.app_name}-data-pvc",
                "namespace": config.app_name,
                "labels": {"app": config.app_name},
            },
            "spec": {
                "accessModes": ["ReadWriteOnce"],
                "resources": {"requests": {"storage": config.storage_size}},
                "storageClassName": config.storage_class,
            },
        }

    @staticmethod
    def create_ingress(config: DeploymentConfig) -> Dict[str, Any]:
        """Create ingress configuration"""
        return {
            "apiVersion": "networking.k8s.io/v1",
            "kind": "Ingress",
            "metadata": {
                "name": f"{config.app_name}-ingress",
                "namespace": config.app_name,
                "annotations": {
                    "kubernetes.io/ingress.class": "nginx",
                    "cert-manager.io/cluster-issuer": "letsencrypt-prod",
                    "nginx.ingress.kubernetes.io/rate-limit": "100",
                    "nginx.ingress.kubernetes.io/rate-limit-window": "1m",
                },
            },
            "spec": {
                "tls": [{"hosts": [f"{config.app_name}.yourdomain.com"], "secretName": f"{config.app_name}-tls"}],
                "rules": [
                    {
                        "host": f"{config.app_name}.yourdomain.com",
                        "http": {
                            "paths": [
                                {
                                    "path": "/",
                                    "pathType": "Prefix",
                                    "backend": {
                                        "service": {"name": f"{config.app_name}-service", "port": {"number": 80}}
                                    },
                                }
                            ]
                        },
                    }
                ],
            },
        }


class MonitoringConfigGenerator:
    """Generate monitoring configurations"""

    @staticmethod
    def create_service_monitor(config: DeploymentConfig) -> Dict[str, Any]:
        """Create Prometheus ServiceMonitor configuration"""
        return {
            "apiVersion": "monitoring.coreos.com/v1",
            "kind": "ServiceMonitor",
            "metadata": {
                "name": f"{config.app_name}-monitor",
                "namespace": config.app_name,
                "labels": {"app": config.app_name, "monitoring": "prometheus"},
            },
            "spec": {
                "selector": {"matchLabels": {"app": config.app_name}},
                "endpoints": [{"port": "metrics", "path": "/metrics", "interval": "30s", "scrapeTimeout": "10s"}],
            },
        }

    @staticmethod
    def create_grafana_dashboard(config: DeploymentConfig) -> Dict[str, Any]:
        """Create Grafana dashboard configuration"""
        return {
            "apiVersion": "v1",
            "kind": "ConfigMap",
            "metadata": {
                "name": f"{config.app_name}-dashboard",
                "namespace": config.app_name,
                "labels": {"grafana_dashboard": "1", "app": config.app_name},
            },
            "data": {
                "dashboard.json": json.dumps(
                    {
                        "dashboard": {
                            "title": f"{config.app_name} Dashboard",
                            "panels": [
                                {
                                    "title": "Request Rate",
                                    "type": "graph",
                                    "targets": [{"expr": f'rate(http_requests_total{{app="{config.app_name}"}}[5m])'}],
                                },
                                {
                                    "title": "Response Time",
                                    "type": "graph",
                                    "targets": [
                                        {
                                            "expr": f'histogram_quantile(0.95, rate(http_request_duration_seconds_bucket{{app="{config.app_name}"}}[5m]))'
                                        }
                                    ],
                                },
                                {
                                    "title": "Error Rate",
                                    "type": "graph",
                                    "targets": [
                                        {
                                            "expr": f'rate(http_requests_total{{app="{config.app_name}",status=~"5.."}}[5m])'
                                        }
                                    ],
                                },
                                {
                                    "title": "LLM Token Usage",
                                    "type": "graph",
                                    "targets": [{"expr": f'rate(llm_tokens_total{{app="{config.app_name}"}}[5m])'}],
                                },
                            ],
                            "refresh": "30s",
                        }
                    },
                    indent=2,
                )
            },
        }


def generate_all_configs(config: DeploymentConfig, output_dir: Path = Path("deployment")):
    """Generate all deployment configurations"""
    output_dir.mkdir(exist_ok=True)

    # Docker configurations
    dockerfile = DockerConfigGenerator.create_dockerfile(config)
    (output_dir / "Dockerfile").write_text(dockerfile)

    docker_compose = DockerConfigGenerator.create_docker_compose(config)
    (output_dir / "docker-compose.yml").write_text(docker_compose)

    # Kubernetes configurations
    k8s_dir = output_dir / "k8s"
    k8s_dir.mkdir(exist_ok=True)

    configs = {
        "namespace.yaml": KubernetesConfigGenerator.create_namespace(config),
        "deployment.yaml": KubernetesConfigGenerator.create_deployment(config),
        "service.yaml": KubernetesConfigGenerator.create_service(config),
        "ingress.yaml": KubernetesConfigGenerator.create_ingress(config),
        "pvc.yaml": KubernetesConfigGenerator.create_pvc(config),
        "hpa.yaml": KubernetesConfigGenerator.create_hpa(config),
        "service-monitor.yaml": MonitoringConfigGenerator.create_service_monitor(config),
        "grafana-dashboard.yaml": MonitoringConfigGenerator.create_grafana_dashboard(config),
    }

    for filename, k8s_config in configs.items():
        if k8s_config is not None:
            (k8s_dir / filename).write_text(yaml.dump(k8s_config, default_flow_style=False))

    print(f"✅ Generated deployment configurations in {output_dir}")
    print(f"   📁 Docker files: Dockerfile, docker-compose.yml")
    print(f"   📁 Kubernetes files: k8s/*.yaml")
    print(f"   📊 Monitoring: ServiceMonitor, Grafana dashboard")


if __name__ == "__main__":
    import json

    config = DeploymentConfig(
        app_name="component-library-assistant",
        version="1.0.0",
        environment="production",
        replicas=3,
        enable_hpa=True,
        enable_persistence=True,
    )

    generate_all_configs(config)
