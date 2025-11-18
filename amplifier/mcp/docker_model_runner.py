from typing import Any

"""
Docker Model Runner - Local LLM Serving with OpenAI-Compatible API

Implements ruthlessly simple local LLM model serving using Docker containers.
Provides OpenAI-compatible endpoints for seamless integration with existing agents.

Key Features:
- Pull models from Docker Hub ai/ namespace
- OpenAI-compatible /v1/chat/completions endpoint
- Model management (pull, list, status, remove)
- Cost reduction through local models
- Privacy and offline capability
- Integration with existing MCP infrastructure
"""

import asyncio
import json
import subprocess
import uuid
from contextlib import asynccontextmanager
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path

try:
    import uvicorn
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware
except ImportError:
    FastAPI = None
    uvicorn = None

from ..utils.logger import get_logger

logger = get_logger(__name__)


class ModelStatus(Enum):
    """Model lifecycle status."""

    PULLING = "pulling"
    READY = "ready"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"
    NOT_FOUND = "not_found"


@dataclass
class ModelInfo:
    """Information about a model."""

    name: str
    docker_image: str
    status: ModelStatus
    size_mb: int = 0
    pulled_at: datetime | None = None
    last_used: datetime | None = None
    usage_count: int = 0
    port: int | None = None
    container_id: str | None = None
    capabilities: list[str] = None

    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = []


@dataclass
class ChatMessage:
    """Chat message for OpenAI-compatible API."""

    role: str  # system, user, assistant
    content: str

    def to_dict(self) -> dict[str, Any]:
        return {"role": self.role, "content": self.content}


@dataclass
class ChatCompletionRequest:
    """OpenAI-compatible chat completion request."""

    model: str
    messages: list[ChatMessage]
    max_tokens: int = 1000
    temperature: float = 0.7
    stream: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [msg.to_dict() for msg in self.messages],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "stream": self.stream,
        }


@dataclass
class ChatCompletionChoice:
    """Chat completion choice for OpenAI-compatible response."""

    index: int
    message: ChatMessage
    finish_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "index": self.index,
            "message": self.message.to_dict(),
            "finish_reason": self.finish_reason,
        }


@dataclass
class ChatCompletionResponse:
    """OpenAI-compatible chat completion response."""

    id: str
    object: str = "chat.completion"
    created: int = 0
    model: str = ""
    choices: list[ChatCompletionChoice] = None

    def __post_init__(self):
        if self.choices is None:
            self.choices = []
        if self.created == 0:
            self.created = int(datetime.now().timestamp())

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "object": self.object,
            "created": self.created,
            "model": self.model,
            "choices": [choice.to_dict() for choice in self.choices],
        }


class DockerModelManager:
    """Manages Docker models with ruthless simplicity."""

    def __init__(self):  # type: ignore[assignment]
        self.models: dict[str, ModelInfo] = {}
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        self.active_containers: dict[str, str] = {}  # model_name -> container_id
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        self.base_port = 8080
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        self.storage_dir = Path.home() / ".amplifier" / "models"
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        self.storage_dir.mkdir(parents=True, exist_ok=True)

        # Popular models from ai/ namespace
        self.predefined_models = {  # type: ignore[definition]
            "llama3.2-3b": ModelInfo(
                name="llama3.2-3b",
                docker_image="ai/llama3.2:3b",
                status=ModelStatus.NOT_FOUND,
                capabilities=["chat", "completion"],
            ),
            "llama3.2-1b": ModelInfo(
                name="llama3.2-1b",
                docker_image="ai/llama3.2:1b",
                status=ModelStatus.NOT_FOUND,
                capabilities=["chat", "completion"],
            ),
            "qwen2.5-1.5b": ModelInfo(
                name="qwen2.5-1.5b",
                docker_image="ai/qwen2.5:1.5b",
                status=ModelStatus.NOT_FOUND,
                capabilities=["chat", "completion", "code"],
            ),
            "phi3-mini": ModelInfo(
                name="phi3-mini",
                docker_image="ai/phi3:mini",
                status=ModelStatus.NOT_FOUND,
                capabilities=["chat", "completion", "code"],
            ),
        }

        # Load existing models
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        # type: ignore[name-defined]
        self._load_existing_models()

    def _load_existing_models(self):
        """Load existing Docker models."""
        try:
            # List Docker images with ai/ prefix
            result = subprocess.run(
                ["docker", "images", "--format", "json", "ai/*"],
                capture_output=True,
                text=True,
                check=True,
            )

            for line in result.stdout.strip().split("\n"):
                if line:
                    try:
                        image_info = json.loads(line)
                        repo_tags = image_info.get("RepositoryTags", [])
                        for tag in repo_tags:
                            if tag.startswith("ai/"):
                                model_name = self._image_to_model_name(tag)
                                if model_name in self.predefined_models:
                                    model = self.predefined_models[model_name]
                                    model.status = ModelStatus.READY
                                    model.size_mb = image_info.get("Size", 0)
                                    logger.info(f"Found existing model: {model_name}")
                    except json.JSONDecodeError:
                        continue

        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to list Docker images: {e}")

    def _image_to_model_name(self, image_tag: str) -> str:
        """Convert Docker image tag to model name."""
        # Remove 'ai/' prefix and version tag
        name = image_tag.replace("ai/", "").split(":")[0]
        return name

    def _get_next_port(self) -> int:
        """Get next available port."""
        import socket

        for port in range(self.base_port, self.base_port + 100):
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.bind(("localhost", port))
                    return port
            except OSError:
                continue
        raise RuntimeError("No available ports found")

    async def pull_model(self, model_name: str) -> bool:
        """Pull a model from Docker Hub."""
        if model_name not in self.predefined_models:
            logger.error(f"Unknown model: {model_name}")
            return False

        model = self.predefined_models[model_name]

        if model.status in [ModelStatus.PULLING, ModelStatus.READY]:
            logger.info(f"Model {model_name} already available")
            return True

        try:
            model.status = ModelStatus.PULLING
            logger.info(f"Pulling model: {model.docker_image}")

            # Pull Docker image
            process = await asyncio.create_subprocess_exec(
                "docker",
                "pull",
                model.docker_image,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                model.status = ModelStatus.READY
                model.pulled_at = datetime.now()
                logger.info(f"Successfully pulled model: {model_name}")
                return True
            model.status = ModelStatus.ERROR
            logger.error(f"Failed to pull model {model_name}: {stderr.decode()}")
            return False

        except Exception as e:
            model.status = ModelStatus.ERROR
            logger.error(f"Error pulling model {model_name}: {e}")
            return False

    async def start_model(self, model_name: str) -> bool:
        """Start a model container."""
        if model_name not in self.predefined_models:
            return False

        model = self.predefined_models[model_name]

        if model.status != ModelStatus.READY and not await self.pull_model(model_name):
            return False

        # Stop existing container if running
        if model_name in self.active_containers:
            await self.stop_model(model_name)

        try:
            port = self._get_next_port()

            # Start Docker container
            cmd = [
                "docker",
                "run",
                "-d",
                "--name",
                f"amplifier-{model_name}",
                "-p",
                f"{port}:8080",
                "--gpus",
                "all",  # Use GPU if available
                model.docker_image,
            ]

            # Remove --gpus if not available
            try:
                result = subprocess.run(["docker", "version"], capture_output=True)
                if "--gpus" not in result.stdout.decode():
                    cmd.remove("--gpus")
                    cmd.remove("all")
            except Exception:
                if "--gpus" in cmd:
                    cmd.remove("--gpus")
                    cmd.remove("all")

            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            stdout, stderr = await process.communicate()

            if process.returncode == 0:
                container_id = stdout.decode().strip()
                model.status = ModelStatus.RUNNING
                model.port = port
                model.container_id = container_id
                self.active_containers[model_name] = container_id

                logger.info(f"Started model {model_name} on port {port}")
                return True
            logger.error(f"Failed to start model {model_name}: {stderr.decode()}")
            return False

        except Exception as e:
            logger.error(f"Error starting model {model_name}: {e}")
            return False

    async def stop_model(self, model_name: str) -> bool:
        """Stop a model container."""
        if model_name not in self.predefined_models:
            return False

        model = self.predefined_models[model_name]

        if model.container_id:
            try:
                # Stop and remove container
                await asyncio.create_subprocess_exec(
                    "docker",
                    "stop",
                    model.container_id,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )

                await asyncio.create_subprocess_exec(
                    "docker",
                    "rm",
                    model.container_id,
                    stdout=asyncio.subprocess.DEVNULL,
                    stderr=asyncio.subprocess.DEVNULL,
                )

                model.status = ModelStatus.READY
                model.port = None
                model.container_id = None

                if model_name in self.active_containers:
                    del self.active_containers[model_name]

                logger.info(f"Stopped model: {model_name}")
                return True

            except Exception as e:
                logger.error(f"Error stopping model {model_name}: {e}")
                return False

        return True

    async def list_models(self) -> list[ModelInfo]:
        """List all available models."""
        return list(self.predefined_models.values())

    async def get_model(self, model_name: str) -> ModelInfo | None:
        """Get model information."""
        return self.predefined_models.get(model_name)

    async def remove_model(self, model_name: str) -> bool:
        """Remove a model from Docker."""
        if model_name not in self.predefined_models:
            return False

        # Stop if running
        await self.stop_model(model_name)

        model = self.predefined_models[model_name]

        try:
            # Remove Docker image
            await asyncio.create_subprocess_exec(
                "docker",
                "rmi",
                model.docker_image,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL,
            )

            model.status = ModelStatus.NOT_FOUND
            model.pulled_at = None

            logger.info(f"Removed model: {model_name}")
            return True

        except Exception as e:
            logger.error(f"Error removing model {model_name}: {e}")
            return False


class DockerModelRunner:
    """Main Docker Model Runner with OpenAI-compatible API."""

    def __init__(self):  # type: ignore[assignment]
        self.model_manager = DockerModelManager()
        self.app = None

        if FastAPI is not None:
            self.app = self._create_app()

    def _create_app(self) -> FastAPI:
        """Create FastAPI application."""

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            """Application lifespan manager."""
            logger.info("Starting Docker Model Runner")
            yield
            logger.info("Shutting down Docker Model Runner")
            # Stop all running models
            for model_name in list(self.model_manager.active_containers.keys()):
                await self.model_manager.stop_model(model_name)

        app = FastAPI(
            title="Docker Model Runner",
            description="Local LLM serving with OpenAI-compatible API",
            version="1.0.0",
            lifespan=lifespan,
        )

        # Add CORS
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        # Register routes
        self._register_routes(app)

        return app

    def _register_routes(self, app: FastAPI):
        """Register API routes."""

        @app.get("/")
        async def root():
            return {"message": "Docker Model Runner - Local LLM Serving", "version": "1.0.0"}

        @app.get("/health")
        async def health():
            return {"status": "healthy", "models_running": len(self.model_manager.active_containers)}

        @app.get("/v1/models")
        async def list_models():
            """List available models (OpenAI-compatible)."""
            models = await self.model_manager.list_models()
            return {
                "object": "list",
                "data": [
                    {
                        "id": model.name,
                        "object": "model",
                        "created": int(model.pulled_at.timestamp()) if model.pulled_at else 0,
                        "owned_by": "amplifier",
                    }
                    for model in models
                ],
            }

        @app.post("/v1/chat/completions")
        async def chat_completions(request: dict[str, Any]):
            """OpenAI-compatible chat completions endpoint."""
            try:
                # Parse request
                model_name = request.get("model")
                messages = request.get("messages", [])
                max_tokens = request.get("max_tokens", 1000)
                temperature = request.get("temperature", 0.7)
                stream = request.get("stream", False)

                if not model_name:
                    return {"error": "model parameter is required"}

                # Get model
                model = await self.model_manager.get_model(model_name)
                if not model:
                    return {"error": f"Model not found: {model_name}"}

                # Start model if not running
                if model.status != ModelStatus.RUNNING and not await self.model_manager.start_model(model_name):
                    return {"error": f"Failed to start model: {model_name}"}

                # Prepare request for model
                model_request = {
                    "messages": messages,
                    "max_tokens": max_tokens,
                    "temperature": temperature,
                    "stream": stream,
                }

                # Call model API
                response = await self._call_model_api(model, model_request)

                # Update usage
                model.usage_count += 1
                model.last_used = datetime.now()

                return response

            except Exception as e:
                logger.error(f"Chat completion error: {e}")
                return {"error": str(e)}

        @app.get("/admin/models")
        async def admin_list_models():
            """Admin endpoint for detailed model information."""
            models = await self.model_manager.list_models()
            return {
                "models": [
                    {
                        "name": model.name,
                        "docker_image": model.docker_image,
                        "status": model.status.value,
                        "size_mb": model.size_mb,
                        "pulled_at": model.pulled_at.isoformat() if model.pulled_at else None,
                        "last_used": model.last_used.isoformat() if model.last_used else None,
                        "usage_count": model.usage_count,
                        "port": model.port,
                        "container_id": model.container_id,
                        "capabilities": model.capabilities,
                    }
                    for model in models
                ]
            }

        @app.post("/admin/models/{model_name}/pull")
        async def pull_model(model_name: str):
            """Pull a model from Docker Hub."""
            success = await self.model_manager.pull_model(model_name)
            return {"success": success, "model": model_name}

        @app.post("/admin/models/{model_name}/start")
        async def start_model(model_name: str):
            """Start a model container."""
            success = await self.model_manager.start_model(model_name)
            return {"success": success, "model": model_name}

        @app.post("/admin/models/{model_name}/stop")
        async def stop_model(model_name: str):
            """Stop a model container."""
            success = await self.model_manager.stop_model(model_name)
            return {"success": success, "model": model_name}

        @app.delete("/admin/models/{model_name}")
        async def remove_model(model_name: str):
            """Remove a model."""
            success = await self.model_manager.remove_model(model_name)
            return {"success": success, "model": model_name}

    async def _call_model_api(self, model: ModelInfo, request: dict[str, Any]) -> dict[str, Any]:
        """Call the model's API."""
        import aiohttp

        if not model.port:
            raise Exception(f"Model {model.name} is not running")

        url = f"http://localhost:{model.port}/v1/chat/completions"

        # type: ignore[arg-type]
        # type: ignore[arg-type]
        async with aiohttp.ClientSession() as session, session.post(url, json=request, timeout=30) as response:
            if response.status == 200:
                result = await response.json()

                # Transform to OpenAI format
                return {
                    "id": f"chatcmpl-{uuid.uuid4().hex[:8]}",
                    "object": "chat.completion",
                    "created": int(datetime.now().timestamp()),
                    "model": model.name,
                    "choices": result.get("choices", []),
                    "usage": result.get(
                        "usage",
                        {
                            "prompt_tokens": 0,
                            "completion_tokens": 0,
                            "total_tokens": 0,
                        },
                    ),
                }
            error_text = await response.text()
            raise Exception(f"Model API error: {response.status} - {error_text}")

    async def run(self, host: str = "0.0.0.0", port: int = 8000):
        """Run the API server."""
        if not self.app:
            raise RuntimeError("FastAPI not available - install with: pip install fastapi uvicorn")

        config = uvicorn.Config(self.app, host=host, port=port)
        server = uvicorn.Server(config)
        await server.serve()


# Global instance
_docker_model_runner = DockerModelRunner()


def get_model_runner() -> DockerModelRunner:
    """Get the global Docker Model Runner instance."""
    return _docker_model_runner


async def start_local_llm(model_name: str = "llama3.2-1b") -> bool:
    """Convenient function to start a local LLM."""
    runner = get_model_runner()
    return await runner.model_manager.start_model(model_name)


async def chat_with_local_llm(
    model_name: str,
    messages: list[dict[str, str]],
    max_tokens: int = 1000,
    temperature: float = 0.7,
) -> dict[str, Any]:
    """Convenient function to chat with a local LLM."""
    runner = get_model_runner()

    request = {
        "model": model_name,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": False,
    }

    response = await runner._call_model_api(
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        await runner.model_manager.get_model(model_name),
        request,
    )

    return response


if __name__ == "__main__":
    # Run standalone server
    import asyncio

    async def main():
        runner = get_model_runner()
        await runner.run()

    asyncio.run(main())  # type: ignore  # type: ignore  # type: ignore  # type: ignore
