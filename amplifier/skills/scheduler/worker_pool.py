"""
Dynamic Worker Pool Management

Efficient worker thread management with auto-scaling,
health monitoring, and resource-aware task assignment.
"""

import asyncio
import os
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from enum import Enum

import psutil


class WorkerStatus(Enum):
    """Worker thread status"""

    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    STOPPED = "stopped"


@dataclass
class WorkerConfig:
    """Configuration for worker pool behavior"""

    min_workers: int = 2
    max_workers: int = os.cpu_count() * 2
    initial_workers: int | None = None
    worker_timeout: float = 300.0  # 5 minutes
    health_check_interval: float = 10.0
    auto_scale: bool = True
    scale_up_threshold: float = 0.8
    scale_down_threshold: float = 0.3
    max_idle_time: float = 60.0
    worker_memory_limit_mb: float = 512.0


@dataclass
class WorkerStats:
    """Statistics for a worker thread"""

    worker_id: str
    status: WorkerStatus
    tasks_completed: int = 0
    tasks_failed: int = 0
    total_execution_time: float = 0.0
    memory_usage_mb: float = 0.0
    cpu_usage: float = 0.0
    last_activity: float = field(default_factory=time.time)
    error_count: int = 0
    last_error: str | None = None


class WorkerPool:
    """Dynamic worker pool with auto-scaling and health monitoring"""

    def __init__(self, config: WorkerConfig | None = None):
        self.config = config or WorkerConfig()
        self.initial_workers = self.config.initial_workers or min(
            self.config.max_workers, max(self.config.min_workers, os.cpu_count())
        )

        # Worker management
        self._workers: dict[str, ThreadPoolExecutor] = {}
        self._worker_stats: dict[str, WorkerStats] = {}
        self._worker_tasks: dict[str, set[int]] = {}  # Track active tasks per worker

        # Pool state
        self._running = False
        self._pool_lock = threading.Lock()

        # Auto-scaling
        self._last_scale_time = 0.0
        self._scale_cooldown = 30.0  # 30 seconds between scaling

        # Health monitoring
        self._process = psutil.Process()
        self._health_check_task: asyncio.Task | None = None

        # Task execution tracking
        self._total_tasks = 0
        self._completed_tasks = 0
        self._failed_tasks = 0

    async def start(self):
        """Start the worker pool"""
        if self._running:
            return

        self._running = True

        # Create initial workers
        await self._create_initial_workers()

        # Start health monitoring
        self._health_check_task = asyncio.create_task(self._health_monitoring_loop())

    async def stop(self):
        """Stop the worker pool"""
        if not self._running:
            return

        self._running = False

        # Cancel health monitoring
        if self._health_check_task:
            self._health_check_task.cancel()
            try:
                await self._health_check_task
            except asyncio.CancelledError:
                pass

        # Shutdown all workers
        with self._pool_lock:
            for executor in self._workers.values():
                executor.shutdown(wait=True)

            self._workers.clear()
            self._worker_stats.clear()
            self._worker_tasks.clear()

    async def _create_initial_workers(self):
        """Create the initial set of workers"""
        for i in range(self.initial_workers):
            worker_id = f"worker_{i}"
            await self._create_worker(worker_id)

    async def _create_worker(self, worker_id: str) -> bool:
        """Create a new worker thread"""
        try:
            # Create thread pool executor for this worker
            executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix=worker_id)

            with self._pool_lock:
                self._workers[worker_id] = executor
                self._worker_stats[worker_id] = WorkerStats(worker_id=worker_id, status=WorkerStatus.IDLE)
                self._worker_tasks[worker_id] = set()

            return True

        except Exception as e:
            print(f"Failed to create worker {worker_id}: {e}")
            return False

    async def submit_to_worker(self, worker_id: str, func, *args, **kwargs):
        """Submit a task to a specific worker"""
        if worker_id not in self._workers:
            raise ValueError(f"Worker {worker_id} not found")

        executor = self._workers[worker_id]

        # Update worker status
        with self._pool_lock:
            if worker_id in self._worker_stats:
                self._worker_stats[worker_id].status = WorkerStatus.BUSY
                self._worker_stats[worker_id].last_activity = time.time()

        self._total_tasks += 1

        try:
            # Execute task
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(executor, func, *args, **kwargs)

            # Update statistics
            with self._pool_lock:
                if worker_id in self._worker_stats:
                    stats = self._worker_stats[worker_id]
                    stats.tasks_completed += 1
                    stats.status = WorkerStatus.IDLE
                    stats.last_activity = time.time()

            self._completed_tasks += 1
            return result

        except Exception as e:
            # Update error statistics
            with self._pool_lock:
                if worker_id in self._worker_stats:
                    stats = self._worker_stats[worker_id]
                    stats.tasks_failed += 1
                    stats.error_count += 1
                    stats.last_error = str(e)
                    stats.status = WorkerStatus.ERROR if stats.error_count > 3 else WorkerStatus.IDLE

            self._failed_tasks += 1
            raise

    def get_available_worker(self) -> str | None:
        """Get an available worker for task assignment"""
        with self._pool_lock:
            # Prefer idle workers
            idle_workers = [
                worker_id for worker_id, stats in self._worker_stats.items() if stats.status == WorkerStatus.IDLE
            ]

            if idle_workers:
                # Choose worker with lowest task completion count (load balancing)
                return min(idle_workers, key=lambda w: self._worker_stats[w].tasks_completed)

            # If no idle workers, choose least busy
            busy_workers = [
                worker_id for worker_id, stats in self._worker_stats.items() if stats.status == WorkerStatus.BUSY
            ]

            if busy_workers:
                return min(busy_workers, key=lambda w: self._worker_stats[w].tasks_completed)

        return None

    async def _health_monitoring_loop(self):
        """Monitor worker health and performance"""
        while self._running:
            try:
                await self._perform_health_check()
                await self._update_worker_stats()
                await self._auto_scale_if_needed()
                await asyncio.sleep(self.config.health_check_interval)
            except Exception as e:
                print(f"Health monitoring error: {e}")
                await asyncio.sleep(1.0)

    async def _perform_health_check(self):
        """Perform health check on all workers"""
        current_time = time.time()
        unhealthy_workers = []

        with self._pool_lock:
            for worker_id, stats in self._worker_stats.items():
                # Check for stuck workers
                if (
                    stats.status == WorkerStatus.BUSY
                    and current_time - stats.last_activity > self.config.worker_timeout
                ):
                    unhealthy_workers.append(worker_id)

                # Check for excessive errors
                if stats.error_count > 5:
                    unhealthy_workers.append(worker_id)

                # Check memory usage
                if stats.memory_usage_mb > self.config.worker_memory_limit_mb:
                    unhealthy_workers.append(worker_id)

        # Replace unhealthy workers
        for worker_id in unhealthy_workers:
            await self._replace_worker(worker_id)

    async def _replace_worker(self, worker_id: str):
        """Replace an unhealthy worker"""
        print(f"Replacing unhealthy worker: {worker_id}")

        # Shutdown old worker
        if worker_id in self._workers:
            self._workers[worker_id].shutdown(wait=True)

        # Remove from tracking
        with self._pool_lock:
            self._workers.pop(worker_id, None)
            self._worker_stats.pop(worker_id, None)
            self._worker_tasks.pop(worker_id, None)

        # Create new worker
        new_worker_id = f"{worker_id}_new_{int(time.time())}"
        await self._create_worker(new_worker_id)

    async def _update_worker_stats(self):
        """Update worker statistics"""
        try:
            # Get system stats
            memory_info = self._process.memory_info()
            cpu_percent = self._process.cpu_percent()

            with self._pool_lock:
                for worker_id, stats in self._worker_stats.items():
                    # Update memory usage (distributed evenly)
                    if self._workers:
                        stats.memory_usage_mb = memory_info.rss / (1024 * 1024) / len(self._workers)

                    # Update CPU usage (distributed evenly)
                    if self._workers:
                        stats.cpu_usage = cpu_percent / len(self._workers)

        except Exception as e:
            print(f"Failed to update worker stats: {e}")

    async def _auto_scale_if_needed(self):
        """Auto-scale worker pool based on load"""
        if not self.config.auto_scale:
            return

        current_time = time.time()
        if current_time - self._last_scale_time < self._scale_cooldown:
            return

        with self._pool_lock:
            num_workers = len(self._workers)
            busy_workers = sum(1 for stats in self._worker_stats.values() if stats.status == WorkerStatus.BUSY)

            if num_workers == 0:
                return

            busy_ratio = busy_workers / num_workers

            # Scale up if too busy
            if busy_ratio > self.config.scale_up_threshold and num_workers < self.config.max_workers:
                await self._scale_up()

            # Scale down if too idle
            elif busy_ratio < self.config.scale_down_threshold and num_workers > self.config.min_workers:
                await self._scale_down()

        self._last_scale_time = current_time

    async def _scale_up(self):
        """Scale up worker pool by adding workers"""
        current_time = time.time()
        add_count = min(2, self.config.max_workers - len(self._workers))

        for i in range(add_count):
            worker_id = f"worker_scale_up_{int(current_time)}_{i}"
            success = await self._create_worker(worker_id)
            if success:
                print(f"Scaled up: Added worker {worker_id}")

    async def _scale_down(self):
        """Scale down worker pool by removing idle workers"""
        with self._pool_lock:
            # Find idle workers with least tasks
            idle_workers = [
                (worker_id, stats.tasks_completed)
                for worker_id, stats in self._worker_stats.items()
                if stats.status == WorkerStatus.IDLE
            ]

            if len(idle_workers) <= self.config.min_workers:
                return

            # Sort by task completion (remove least used workers)
            idle_workers.sort(key=lambda x: x[1])

            remove_count = min(2, len(idle_workers) - self.config.min_workers)

            for i in range(remove_count):
                if i < len(idle_workers):
                    worker_id = idle_workers[i][0]
                    await self._remove_worker(worker_id)

    async def _remove_worker(self, worker_id: str):
        """Remove a worker from the pool"""
        print(f"Scaled down: Removing worker {worker_id}")

        # Shutdown worker
        if worker_id in self._workers:
            self._workers[worker_id].shutdown(wait=True)

        # Remove from tracking
        with self._pool_lock:
            self._workers.pop(worker_id, None)
            self._worker_stats.pop(worker_id, None)
            self._worker_tasks.pop(worker_id, None)

    def get_stats(self) -> dict:
        """Get worker pool statistics"""
        with self._pool_lock:
            return {
                "total_workers": len(self._workers),
                "busy_workers": sum(1 for stats in self._worker_stats.values() if stats.status == WorkerStatus.BUSY),
                "idle_workers": sum(1 for stats in self._worker_stats.values() if stats.status == WorkerStatus.IDLE),
                "error_workers": sum(1 for stats in self._worker_stats.values() if stats.status == WorkerStatus.ERROR),
                "total_tasks": self._total_tasks,
                "completed_tasks": self._completed_tasks,
                "failed_tasks": self._failed_tasks,
                "success_rate": (self._completed_tasks / self._total_tasks if self._total_tasks > 0 else 0.0),
                "worker_details": {
                    worker_id: {
                        "status": stats.status.value,
                        "tasks_completed": stats.tasks_completed,
                        "tasks_failed": stats.tasks_failed,
                        "error_count": stats.error_count,
                        "memory_usage_mb": stats.memory_usage_mb,
                        "cpu_usage": stats.cpu_usage,
                        "last_activity": stats.last_activity,
                    }
                    for worker_id, stats in self._worker_stats.items()
                },
            }

    def get_efficiency_metrics(self) -> dict[str, float]:
        """Calculate worker pool efficiency metrics"""
        with self._pool_lock:
            total_tasks = self._completed_tasks + self._failed_tasks
            if total_tasks == 0:
                return {"success_rate": 0.0, "error_rate": 0.0, "worker_utilization": 0.0, "throughput_per_worker": 0.0}

            success_rate = self._completed_tasks / total_tasks
            error_rate = self._failed_tasks / total_tasks

            # Worker utilization
            busy_workers = sum(1 for stats in self._worker_stats.values() if stats.status == WorkerStatus.BUSY)
            worker_utilization = busy_workers / len(self._workers) if self._workers else 0.0

            # Throughput per worker
            runtime = time.time() - (
                self._worker_stats[next(iter(self._worker_stats))].last_activity if self._worker_stats else time.time()
            )
            throughput_per_worker = (
                self._completed_tasks / len(self._workers) / runtime if self._workers and runtime > 0 else 0.0
            )

            return {
                "success_rate": success_rate,
                "error_rate": error_rate,
                "worker_utilization": worker_utilization,
                "throughput_per_worker": throughput_per_worker,
            }


# Global worker pool instance
_global_worker_pool: WorkerPool | None = None


def get_worker_pool(**kwargs) -> WorkerPool:
    """Get or create the global worker pool"""
    global _global_worker_pool
    if _global_worker_pool is None:
        _global_worker_pool = WorkerPool(**kwargs)
    return _global_worker_pool
