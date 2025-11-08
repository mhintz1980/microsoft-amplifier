"""
Project Builder for Industrial Frontend Interfaces

Builds complete projects from templates and configurations.
"""

from pathlib import Path
from typing import Any

from amplifier.utils.logger import get_logger

from ..generators.base_generator import BaseGenerator

logger = get_logger(__name__)


class ProjectBuilder:
    """Builds industrial frontend projects from templates."""

    def __init__(self, output_dir: Path):
        """Initialize project builder.

        Args:
            output_dir: Directory where project will be built
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def build_project(
        self,
        template_config: dict[str, Any],
        project_config: dict[str, Any],
        generator: BaseGenerator,
    ) -> bool:
        """Build the complete project.

        Args:
            template_config: Template configuration
            project_config: Project configuration
            generator: Framework-specific generator

        Returns:
            True if successful, False otherwise
        """
        try:
            logger.info(f"🏗️ Building {project_config['framework']} project...")

            # Validate configuration
            errors = generator.validate_config(project_config)
            if errors:
                logger.error("Configuration validation failed:")
                for error in errors:
                    logger.error(f"  • {error}")
                return False

            # Generate project structure
            files = generator.generate_project_structure(template_config, project_config)

            # Write files to disk
            for file_path, content in files.items():
                self._write_file(file_path, content)

            # Create additional project files
            self._create_additional_files(project_config)

            logger.info(f"✅ Project built successfully in: {self.output_dir}")
            return True

        except Exception as e:
            logger.error(f"Project build failed: {e}")
            return False

    def _write_file(self, file_path: str, content: str) -> None:
        """Write a file to the output directory.

        Args:
            file_path: Relative file path from project root
            content: File content to write
        """
        full_path = self.output_dir / file_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_text(content, encoding="utf-8")

    def _create_additional_files(self, project_config: dict[str, Any]) -> None:
        """Create additional project files."""
        # Create .gitignore
        self._create_gitignore(project_config["framework"])

        # Create Docker files if requested
        if "docker" in project_config.get("features", []):
            self._create_docker_files(project_config)

        # Create environment files
        self._create_environment_files(project_config)

        # Create test files
        self._create_test_files(project_config)

    def _create_gitignore(self, framework: str) -> None:
        """Create .gitignore file."""
        gitignore_content = """
# Dependencies
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# Build outputs
dist/
build/
.output/

# Environment variables
.env
.env.local
.env.development.local
.env.test.local
.env.production.local

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Logs
logs/
*.log

# Runtime data
pids/
*.pid
*.seed

# Coverage directory used by tools like istanbul
coverage/

# TypeScript cache
*.tsbuildinfo

# Optional npm cache directory
.npm

# Optional eslint cache
.eslintcache

# Microbundle cache
.rpt2_cache/
.rts2_cache_cjs/
.rts2_cache_es/
.rts2_cache_umd/

# Optional REPL history
.node_repl_history

# Output of 'npm pack'
*.tgz

# Yarn Integrity file
.yarn-integrity

# dotenv environment variables file
.env

# parcel-bundler cache (https://parceljs.org/)
.cache
.parcel-cache

# Next.js build output
.next

# Nuxt.js build / generate output
.nuxt

# Gatsby files
.cache/
public

# Storybook build outputs
.out
.storybook-out

# Temporary folders
tmp/
temp/

# Editor directories and files
.vscode/*
!.vscode/extensions.json
.idea
*.suo
*.ntvs*
*.njsproj
*.sln
*.sw?
"""

        self._write_file(".gitignore", gitignore_content.strip())

    def _create_docker_files(self, project_config: dict[str, Any]) -> None:
        """Create Docker configuration files."""
        framework = project_config["framework"]

        if framework == "react":
            self._create_react_dockerfile()
        elif framework == "vue":
            self._create_vue_dockerfile()
        elif framework == "streamlit":
            self._create_streamlit_dockerfile()

        # Create docker-compose.yml
        docker_compose = """
version: '3.8'

services:
  industrial-frontend:
    build: .
    ports:
      - "3000:3000"
    environment:
      - NODE_ENV=production
    volumes:
      - ./config:/app/config
    restart: unless-stopped

  # Optional: MQTT broker for real-time data
  mosquitto:
    image: eclipse-mosquitto:2.0
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto.conf:/mosquitto/config/mosquitto.conf
    restart: unless-stopped
"""

        self._write_file("docker-compose.yml", docker_compose.strip())

    def _create_react_dockerfile(self) -> None:
        """Create Dockerfile for React applications."""
        dockerfile = """
# Multi-stage build for React applications
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

        self._write_file("Dockerfile", dockerfile.strip())

        # nginx.conf
        nginx_config = """
events {
    worker_connections 1024;
}

http {
    include       /etc/nginx/mime.types;
    default_type  application/octet-stream;

    server {
        listen 80;
        server_name localhost;
        root /usr/share/nginx/html;
        index index.html;

        # Enable gzip compression
        gzip on;
        gzip_vary on;
        gzip_min_length 1024;
        gzip_types text/plain text/css text/xml text/javascript application/javascript application/xml+rss application/json;

        # Handle client-side routing
        location / {
            try_files $uri $uri/ /index.html;
        }

        # Cache static assets
        location ~* \\.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }

        # Security headers
        add_header X-Frame-Options "SAMEORIGIN" always;
        add_header X-Content-Type-Options "nosniff" always;
        add_header X-XSS-Protection "1; mode=block" always;
    }
}
"""

        self._write_file("nginx.conf", nginx_config.strip())

    def _create_vue_dockerfile(self) -> None:
        """Create Dockerfile for Vue applications."""
        dockerfile = """
# Multi-stage build for Vue applications
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built application
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Expose port
EXPOSE 80

# Start nginx
CMD ["nginx", "-g", "daemon off;"]
"""

        self._write_file("Dockerfile", dockerfile.strip())

    def _create_streamlit_dockerfile(self) -> None:
        """Create Dockerfile for Streamlit applications."""
        dockerfile = """
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    gcc \\
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \\
    CMD curl -f http://localhost:8501/_stcore/health || exit 1

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
"""

        self._write_file("Dockerfile", dockerfile.strip())

    def _create_environment_files(self, project_config: dict[str, Any]) -> None:
        """Create environment configuration files."""
        framework = project_config["framework"]

        if framework in ["react", "vue"]:
            # .env.example
            env_example = f"""
# Industrial Frontend Environment Configuration

# Data source configuration
VITE_DATA_SOURCE={project_config.get("data_source", "mock")}
VITE_MQTT_BROKER_URL=mqtt://localhost:1883
VITE_API_BASE_URL=https://api.factory.local

# Update intervals (milliseconds)
VITE_UPDATE_INTERVAL=1000
VITE_CHART_UPDATE_INTERVAL=5000

# Feature flags
VITE_ENABLE_ALERTS={"true" if "alerts" in project_config.get("features", []) else "false"}
VITE_ENABLE_EXPORT={"true" if "export" in project_config.get("features", []) else "false"}
VITE_ENABLE_OFFLINE={"true" if "offline-support" in project_config.get("features", []) else "false"}

# Theme configuration
VITE_THEME={project_config.get("theme", "factory-dark")}

# Debug settings
VITE_DEBUG=false
VITE_LOG_LEVEL=info
"""

            self._write_file(".env.example", env_example.strip())

            # .env.local
            env_local = """
# Local development environment (git ignored)
VITE_DEBUG=true
VITE_LOG_LEVEL=debug
VITE_DATA_SOURCE=mock
"""

            self._write_file(".env.local", env_local.strip())

        elif framework == "streamlit":
            # .streamlit/secrets.toml.example
            secrets_example = """
# Industrial Streamlit Secrets Configuration

# Data source connections
mqtt_broker_url = "mqtt://localhost:1883"
mqtt_username = "your_username"
mqtt_password = "your_password"

# API credentials
api_base_url = "https://api.factory.local"
api_key = "your_api_key"

# Database connections (if needed)
database_url = "postgresql://user:password@localhost:5432/industrial_db"
"""

            secrets_dir = self.output_dir / ".streamlit"
            secrets_dir.mkdir(exist_ok=True)
            (secrets_dir / "secrets.toml.example").write_text(secrets_example.strip())

    def _create_test_files(self, project_config: dict[str, Any]) -> None:
        """Create test configuration and sample tests."""
        framework = project_config["framework"]

        if framework == "react":
            self._create_react_tests()
        elif framework == "vue":
            self._create_vue_tests()
        elif framework == "streamlit":
            self._create_streamlit_tests()

    def _create_react_tests(self) -> None:
        """Create React test files."""
        # Setup test
        setup_test = """
import '@testing-library/jest-dom'
"""

        self._write_file("src/setupTests.ts", setup_test.strip())

        # Sample component test
        component_test = """
import { render, screen } from '@testing-library/react'
import App from '../App'

// Mock industrial data
jest.mock('../hooks/useIndustrialData', () => ({
  useIndustrialData: () => ({
    data: {
      pressure: 100,
      temperature: 150,
      flowRate: 80,
      vibration: 2.0
    },
    isLoading: false,
    error: null
  })
}))

test('renders industrial dashboard', () => {
  render(<App />)

  // Check for main title
  expect(screen.getByText(/Pump Monitoring Dashboard/i)).toBeInTheDocument()

  // Check for key metrics
  expect(screen.getByText(/Pressure/i)).toBeInTheDocument()
  expect(screen.getByText(/Temperature/i)).toBeInTheDocument()
  expect(screen.getByText(/Flow Rate/i)).toBeInTheDocument()
})
"""

        tests_dir = self.output_dir / "src" / "components" / "__tests__"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "App.test.tsx").write_text(component_test.strip())

    def _create_vue_tests(self) -> None:
        """Create Vue test files."""
        # Sample component test
        component_test = """
import { mount } from '@vue/test-utils'
import { describe, it, expect } from 'vitest'
import App from '../App.vue'

describe('App', () => {
  it('renders industrial interface', () => {
    const wrapper = mount(App)

    // Check for main title
    expect(wrapper.text()).toContain('Industrial Dashboard')

    // Check for connection status
    expect(wrapper.find('.connection-status').exists()).toBe(true)
  })
})
"""

        tests_dir = self.output_dir / "src" / "components" / "__tests__"
        tests_dir.mkdir(parents=True, exist_ok=True)
        (tests_dir / "App.test.ts").write_text(component_test.strip())

    def _create_streamlit_tests(self) -> None:
        """Create Streamlit test files."""
        # Test utilities


import os
import sys
from unittest.mock import patch

# Add the app directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import main

from utils.data_simulator import DataSimulator
from utils.industrial_components import industrial_metric_card


def test_data_simulator():
    """Test the data simulator."""
    simulator = DataSimulator()

    # Test pump data generation
    pump_data = simulator.get_pump_data()
    assert "pressure" in pump_data
    assert "temperature" in pump_data
    assert "flowRate" in pump_data
    assert "vibration" in pump_data

    # Test data types
    assert isinstance(pump_data["pressure"], int | float)
    assert isinstance(pump_data["temperature"], int | float)
    assert isinstance(pump_data["flowRate"], int | float)
    assert isinstance(pump_data["vibration"], int | float)


def test_industrial_components():
    """Test industrial components."""
    # This would require streamlit testing framework
    # For now, just test that the functions can be imported
    assert callable(industrial_metric_card)


@patch("streamlit.markdown")
def test_main_function(mock_markdown):
    """Test the main app function."""
    # This is a basic test structure
    # Full Streamlit app testing requires special setup
    try:
        main()
    except Exception as e:
        # Expected in test environment without full Streamlit context
        assert "streamlit" in str(e).lower() or "session_state" in str(e).lower()
