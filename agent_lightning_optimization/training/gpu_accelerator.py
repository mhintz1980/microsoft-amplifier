"""
GPU Acceleration and Multi-Process Training Infrastructure for Agent Lightning.

This module provides high-performance training capabilities using GPU acceleration
and multi-process parallel execution for large-scale RL training.
"""

import asyncio
import multiprocessing as mp
import os
import time
import uuid
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from enum import Enum
from typing import Any

import numpy as np
import psutil
import torch
import torch.distributed as dist
import torch.multiprocessing as torch_mp

try:
    from agent_lightning import LightningAgent
    from agent_lightning import TrainingConfig

    AGENT_LIGHTNING_AVAILABLE = True
except ImportError:
    AGENT_LIGHTNING_AVAILABLE = False

from ..store.sqlite_store import SQLiteLightningStore
from ..utils.logger import get_logger

logger = get_logger(__name__)


class GPUStatus(Enum):
    """GPU availability status."""

    AVAILABLE = "available"
    BUSY = "busy"
    ERROR = "error"
    NOT_AVAILABLE = "not_available"


class ProcessStatus(Enum):
    """Training process status."""

    INITIALIZING = "initializing"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    KILLED = "killed"


@dataclass
class GPUInfo:
    """Information about a GPU."""

    device_id: int
    name: str
    memory_total: int
    memory_used: int
    memory_free: int
    utilization: float
    temperature: float
    status: GPUStatus

    @property
    def memory_available_mb(self) -> float:
        """Get available memory in MB."""
        return self.memory_free / (1024 * 1024)

    @property
    def is_available_for_training(self) -> bool:
        """Check if GPU is available for training."""
        return (
            self.status == GPUStatus.AVAILABLE
            and self.memory_available_mb > 1000  # At least 1GB free
            and self.utilization < 0.8  # Less than 80% utilized
            and self.temperature < 85  # Less than 85°C
        )


@dataclass
class TrainingProcess:
    """Information about a training process."""

    process_id: str
    pid: int
    gpu_id: int | None
    status: ProcessStatus
    start_time: float
    end_time: float | None = None
    session_id: str | None = None
    config: dict[str, Any] | None = None
    metrics: dict[str, float] = field(default_factory=dict)
    error_message: str | None = None


@dataclass
class DistributedTrainingConfig:
    """Configuration for distributed training."""

    world_size: int = 1
    rank: int = 0
    local_rank: int = 0
    master_addr: str = "localhost"
    master_port: int = 12355
    backend: str = "nccl"  # nccl for GPU, gloo for CPU
    device_ids: list[int] | None = None


class GPUManager:
    """Manages GPU resources and allocation."""

    def __init__(self):
        self.gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        self.gpu_info: list[GPUInfo] = []
        self.allocated_gpus: dict[int, str] = {}  # gpu_id -> process_id

    def initialize(self):
        """Initialize GPU manager and detect available GPUs."""
        if not torch.cuda.is_available():
            logger.warning("CUDA not available, training will use CPU")
            return

        self.gpu_count = torch.cuda.device_count()
        logger.info(f"Detected {self.gpu_count} GPUs")

        for i in range(self.gpu_count):
            gpu_info = self._get_gpu_info(i)
            self.gpu_info.append(gpu_info)
            logger.info(f"GPU {i}: {gpu_info.name} - {gpu_info.memory_available_mb:.0f}MB available")

    def _get_gpu_info(self, device_id: int) -> GPUInfo:
        """Get information about a specific GPU."""
        try:
            torch.cuda.set_device(device_id)

            # Get memory info
            memory_info = torch.cuda.get_device_properties(device_id)
            memory_total = memory_info.total_memory
            memory_used = torch.cuda.memory_allocated(device_id)
            memory_free = memory_total - memory_used

            # Get utilization (simplified - in practice you'd use nvidia-ml-py)
            utilization = 0.0
            temperature = 0.0

            try:
                import pynvml

                pynvml.nvmlInit()
                handle = pynvml.nvmlDeviceGetHandleByIndex(device_id)
                util_info = pynvml.nvmlDeviceGetUtilizationRates(handle)
                utilization = util_info.gpu / 100.0
                temperature = pynvml.nvmlDeviceGetTemperature(handle, pynvml.NVML_TEMPERATURE_GPU)
            except ImportError:
                logger.debug("pynvml not available, using simplified GPU monitoring")

            return GPUInfo(
                device_id=device_id,
                name=torch.cuda.get_device_name(device_id),
                memory_total=memory_total,
                memory_used=memory_used,
                memory_free=memory_free,
                utilization=utilization,
                temperature=temperature,
                status=GPUStatus.AVAILABLE,
            )

        except Exception as e:
            logger.error(f"Error getting GPU info for device {device_id}: {e}")
            return GPUInfo(
                device_id=device_id,
                name="Unknown",
                memory_total=0,
                memory_used=0,
                memory_free=0,
                utilization=0.0,
                temperature=0.0,
                status=GPUStatus.ERROR,
            )

    def get_available_gpus(self, min_memory_mb: int = 1000) -> list[GPUInfo]:
        """Get list of available GPUs."""
        return [
            gpu for gpu in self.gpu_info if gpu.is_available_for_training and gpu.memory_available_mb >= min_memory_mb
        ]

    def allocate_gpu(self, process_id: str, requirements: dict[str, Any] | None = None) -> int | None:
        """Allocate a GPU for a training process."""
        if not torch.cuda.is_available():
            return None

        available_gpus = self.get_available_gpus()
        if not available_gpus:
            logger.warning("No GPUs available for allocation")
            return None

        # Select best GPU (most free memory)
        best_gpu = max(available_gpus, key=lambda gpu: gpu.memory_available_mb)

        self.allocated_gpus[best_gpu.device_id] = process_id
        logger.info(f"Allocated GPU {best_gpu.device_id} to process {process_id}")

        return best_gpu.device_id

    def release_gpu(self, process_id: str) -> bool:
        """Release a GPU allocated to a process."""
        for gpu_id, pid in list(self.allocated_gpus.items()):
            if pid == process_id:
                del self.allocated_gpus[gpu_id]
                logger.info(f"Released GPU {gpu_id} from process {process_id}")
                return True
        return False

    def update_gpu_status(self):
        """Update the status of all GPUs."""
        for i in range(len(self.gpu_info)):
            self.gpu_info[i] = self._get_gpu_info(i)

    def get_gpu_utilization_report(self) -> dict[str, Any]:
        """Get a report of GPU utilization."""
        self.update_gpu_status()

        total_memory = sum(gpu.memory_total for gpu in self.gpu_info)
        used_memory = sum(gpu.memory_used for gpu in self.gpu_info)
        allocated_count = len(self.allocated_gpus)

        return {
            "total_gpus": self.gpu_count,
            "allocated_gpus": allocated_count,
            "available_gpus": self.gpu_count - allocated_count,
            "total_memory_mb": total_memory / (1024 * 1024),
            "used_memory_mb": used_memory / (1024 * 1024),
            "utilization_pct": sum(gpu.utilization for gpu in self.gpu_info) / max(self.gpu_count, 1) * 100,
            "average_temperature": sum(gpu.temperature for gpu in self.gpu_info) / max(self.gpu_count, 1),
            "gpu_details": [
                {
                    "device_id": gpu.device_id,
                    "name": gpu.name,
                    "memory_available_mb": gpu.memory_available_mb,
                    "utilization": gpu.utilization,
                    "temperature": gpu.temperature,
                    "allocated": gpu.device_id in self.allocated_gpus,
                }
                for gpu in self.gpu_info
            ],
        }


class MultiProcessTrainer:
    """Manages multi-process training with GPU acceleration."""

    def __init__(self, gpu_manager: GPUManager, store: SQLiteLightningStore):
        self.gpu_manager = gpu_manager
        self.store = store
        self.processes: dict[str, TrainingProcess] = {}
        self.max_concurrent_processes = min(mp.cpu_count(), 8)  # Limit concurrent processes
        self.process_executor: ProcessPoolExecutor | None = None

    async def initialize(self):
        """Initialize the multi-process trainer."""
        self.process_executor = ProcessPoolExecutor(max_workers=self.max_concurrent_processes)
        logger.info(f"Multi-process trainer initialized with {self.max_concurrent_processes} workers")

    async def start_training_process(
        self,
        session_id: str,
        config: dict[str, Any],
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]],
    ) -> str:
        """Start a new training process."""
        process_id = str(uuid.uuid4())

        # Allocate GPU if available
        gpu_id = self.gpu_manager.allocate_gpu(process_id)

        # Create training process record
        process = TrainingProcess(
            process_id=process_id,
            pid=0,  # Will be set when process starts
            gpu_id=gpu_id,
            status=ProcessStatus.INITIALIZING,
            start_time=time.time(),
            session_id=session_id,
            config=config,
        )

        self.processes[process_id] = process

        try:
            # Start training in separate process
            if self.process_executor:
                future = self.process_executor.submit(
                    self._run_training_process, process_id, session_id, config, training_data, validation_data, gpu_id
                )

                # Update process with actual PID (this is approximate)
                # In practice, you'd get the actual PID from the process
                process.pid = os.getpid()  # This is a placeholder
                process.status = ProcessStatus.RUNNING

                logger.info(f"Started training process {process_id} on GPU {gpu_id if gpu_id is not None else 'CPU'}")

                # Start monitoring the process
                asyncio.create_task(self._monitor_process(process_id, future))

            else:
                raise RuntimeError("Process executor not initialized")

        except Exception as e:
            logger.error(f"Failed to start training process {process_id}: {e}")
            process.status = ProcessStatus.FAILED
            process.error_message = str(e)
            if gpu_id is not None:
                self.gpu_manager.release_gpu(process_id)

        return process_id

    async def _monitor_process(self, process_id: str, future):
        """Monitor a training process."""
        try:
            # Wait for process to complete
            result = await asyncio.wrap_future(future)

            if process_id in self.processes:
                process = self.processes[process_id]
                process.status = ProcessStatus.COMPLETED
                process.end_time = time.time()
                process.metrics = result.get("metrics", {})

                logger.info(f"Training process {process_id} completed successfully")

        except Exception as e:
            logger.error(f"Training process {process_id} failed: {e}")

            if process_id in self.processes:
                process = self.processes[process_id]
                process.status = ProcessStatus.FAILED
                process.end_time = time.time()
                process.error_message = str(e)

        finally:
            # Release GPU if allocated
            if process_id in self.processes:
                gpu_id = self.processes[process_id].gpu_id
                if gpu_id is not None:
                    self.gpu_manager.release_gpu(process_id)

    def _run_training_process(
        self,
        process_id: str,
        session_id: str,
        config: dict[str, Any],
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]],
        gpu_id: int | None,
    ) -> dict[str, Any]:
        """Run training in a separate process."""
        try:
            # Set up GPU if available
            if gpu_id is not None and torch.cuda.is_available():
                torch.cuda.set_device(gpu_id)
                device = f"cuda:{gpu_id}"
            else:
                device = "cpu"

            logger.info(f"Starting training on device: {device}")

            # Initialize Agent Lightning if available
            if AGENT_LIGHTNING_AVAILABLE:
                agent = LightningAgent(device=device)

                # Convert to training config
                training_config = TrainingConfig(
                    epochs=config.get("epochs", 100),
                    batch_size=config.get("batch_size", 32),
                    learning_rate=config.get("learning_rate", 0.001),
                    validation_split=config.get("validation_split", 0.2),
                )

                # Prepare data
                train_data = self._prepare_training_data(training_data)
                val_data = self._prepare_training_data(validation_data)

                # Train model
                model_path = f"models/{session_id}_{process_id}"
                result = asyncio.run(
                    agent.train(train_data=train_data, val_data=val_data, config=training_config, model_path=model_path)
                )

                return {"success": True, "metrics": result, "model_path": model_path, "device": device}

            # Mock training for development
            logger.warning("Agent Lightning not available, using mock training")
            return self._mock_training(config, training_data, validation_data, device)

        except Exception as e:
            logger.error(f"Training process error: {e}")
            return {"success": False, "error": str(e), "device": device if "device" in locals() else "unknown"}

    def _prepare_training_data(self, data: list[dict[str, Any]]) -> dict[str, Any]:
        """Prepare data for training."""
        if not data:
            return {"X": [], "y": []}

        # Extract features and labels
        X = []
        y = []

        for item in data:
            # Simple feature extraction - in practice, this would be more sophisticated
            features = []

            # Add basic features
            if "expert_rating" in item:
                features.append(float(item["expert_rating"]))
                y.append(float(item["expert_rating"]))
            else:
                features.append(0.0)
                y.append(0.0)

            # Add recommendation count
            if "expert_recommendations" in item:
                features.append(len(item["expert_recommendations"]))
            else:
                features.append(0)

            # Add more features as needed...
            while len(features) < 20:  # Ensure consistent feature length
                features.append(0.0)

            X.append(features[:20])  # Limit to 20 features

        return {"X": X, "y": y}

    def _mock_training(
        self,
        config: dict[str, Any],
        training_data: list[dict[str, Any]],
        validation_data: list[dict[str, Any]],
        device: str,
    ) -> dict[str, Any]:
        """Mock training for development."""
        epochs = config.get("epochs", 100)

        # Simulate training progress
        metrics = {
            "final_loss": 0.1 + np.random.random() * 0.2,
            "final_accuracy": 0.8 + np.random.random() * 0.15,
            "training_time": epochs * 0.1,  # Simulate training time
            "epochs_trained": epochs,
        }

        # Simulate training delay
        time.sleep(epochs * 0.01)  # Short delay for demonstration

        logger.info(f"Mock training completed on {device}: {metrics}")

        return {"success": True, "metrics": metrics, "model_path": f"mock_models/{uuid.uuid4()}.pt", "device": device}

    async def stop_training_process(self, process_id: str) -> bool:
        """Stop a training process."""
        if process_id not in self.processes:
            return False

        process = self.processes[process_id]

        if process.status in [ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.KILLED]:
            return True

        try:
            # In practice, you'd terminate the actual process
            # For now, we'll just mark it as killed
            process.status = ProcessStatus.KILLED
            process.end_time = time.time()

            # Release GPU
            if process.gpu_id is not None:
                self.gpu_manager.release_gpu(process_id)

            logger.info(f"Stopped training process {process_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to stop training process {process_id}: {e}")
            return False

    async def get_process_status(self, process_id: str) -> dict[str, Any] | None:
        """Get status of a training process."""
        if process_id not in self.processes:
            return None

        process = self.processes[process_id]

        return {
            "process_id": process.process_id,
            "pid": process.pid,
            "gpu_id": process.gpu_id,
            "status": process.status.value,
            "start_time": process.start_time,
            "end_time": process.end_time,
            "session_id": process.session_id,
            "metrics": process.metrics,
            "error_message": process.error_message,
            "runtime_seconds": (process.end_time or time.time()) - process.start_time,
        }

    async def list_processes(self, status_filter: ProcessStatus | None = None) -> list[dict[str, Any]]:
        """List all training processes."""
        processes = []

        for process in self.processes.values():
            if status_filter is None or process.status == status_filter:
                processes.append(
                    {
                        "process_id": process.process_id,
                        "pid": process.pid,
                        "gpu_id": process.gpu_id,
                        "status": process.status.value,
                        "start_time": process.start_time,
                        "session_id": process.session_id,
                    }
                )

        return processes

    async def cleanup_completed_processes(self, max_age_hours: int = 24) -> int:
        """Clean up old completed processes."""
        current_time = time.time()
        max_age_seconds = max_age_hours * 3600

        to_remove = []

        for process_id, process in self.processes.items():
            if process.status in [ProcessStatus.COMPLETED, ProcessStatus.FAILED, ProcessStatus.KILLED]:
                age = current_time - (process.end_time or process.start_time)
                if age > max_age_seconds:
                    to_remove.append(process_id)

        for process_id in to_remove:
            del self.processes[process_id]
            logger.info(f"Cleaned up old training process {process_id}")

        return len(to_remove)

    def get_system_resources_report(self) -> dict[str, Any]:
        """Get system resource utilization report."""
        # CPU info
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()

        # GPU info
        gpu_report = self.gpu_manager.get_gpu_utilization_report()

        # Process info
        running_processes = len([p for p in self.processes.values() if p.status == ProcessStatus.RUNNING])

        return {
            "cpu_percent": cpu_percent,
            "memory_percent": memory.percent,
            "memory_available_gb": memory.available / (1024**3),
            "active_processes": running_processes,
            "max_concurrent_processes": self.max_concurrent_processes,
            "gpu_utilization": gpu_report,
        }

    async def shutdown(self):
        """Shutdown the multi-process trainer."""
        logger.info("Shutting down multi-process trainer")

        # Stop all running processes
        for process_id in list(self.processes.keys()):
            if self.processes[process_id].status == ProcessStatus.RUNNING:
                await self.stop_training_process(process_id)

        # Shutdown process executor
        if self.process_executor:
            self.process_executor.shutdown(wait=True)
            self.process_executor = None

        logger.info("Multi-process trainer shutdown complete")


class DistributedTrainingManager:
    """Manages distributed training across multiple GPUs/nodes."""

    def __init__(self, gpu_manager: GPUManager):
        self.gpu_manager = gpu_manager
        self.active_distributed_jobs: dict[str, DistributedTrainingConfig] = {}

    async def launch_distributed_training(
        self,
        session_id: str,
        config: dict[str, Any],
        world_size: int,
        master_addr: str = "localhost",
        master_port: int = 12355,
    ) -> bool:
        """Launch distributed training across multiple processes."""
        try:
            # Initialize process group for distributed training
            os.environ["MASTER_ADDR"] = master_addr
            os.environ["MASTER_PORT"] = str(master_port)
            os.environ["WORLD_SIZE"] = str(world_size)

            # Launch processes for each rank
            processes = []
            available_gpus = self.gpu_manager.get_available_gpus()

            for rank in range(world_size):
                # Assign GPU if available
                gpu_id = available_gpus[rank % len(available_gpus)].device_id if available_gpus else None

                # Create distributed config
                dist_config = DistributedTrainingConfig(
                    world_size=world_size,
                    rank=rank,
                    local_rank=rank,
                    master_addr=master_addr,
                    master_port=master_port,
                    device_ids=[gpu_id] if gpu_id is not None else None,
                )

                # Launch process
                process = torch_mp.Process(
                    target=self._distributed_training_worker, args=(session_id, config, dist_config)
                )
                process.start()
                processes.append(process)

            # Store job info
            self.active_distributed_jobs[session_id] = dist_config

            # Wait for processes to complete
            for process in processes:
                process.join()

            return True

        except Exception as e:
            logger.error(f"Distributed training failed: {e}")
            return False

    def _distributed_training_worker(
        self, session_id: str, config: dict[str, Any], dist_config: DistributedTrainingConfig
    ):
        """Worker process for distributed training."""
        try:
            # Initialize distributed training
            dist.init_process_group(
                backend=dist_config.backend, rank=dist_config.rank, world_size=dist_config.world_size
            )

            # Set device
            if dist_config.device_ids:
                device = f"cuda:{dist_config.device_ids[0]}"
                torch.cuda.set_device(dist_config.device_ids[0])
            else:
                device = "cpu"

            logger.info(f"Started distributed training worker {dist_config.rank}/{dist_config.world_size} on {device}")

            # Training logic would go here
            # This is a placeholder for the actual training implementation

        except Exception as e:
            logger.error(f"Distributed training worker {dist_config.rank} failed: {e}")

        finally:
            # Clean up
            if dist.is_initialized():
                dist.destroy_process_group()
