"""
Priority-based Task Queue System

High-performance task distribution with priority handling,
batching, and efficient queue management.
"""

import asyncio
import heapq
import threading
import time
from dataclasses import dataclass
from dataclasses import field
from queue import Queue

from .work_stealing_scheduler import Task
from .work_stealing_scheduler import TaskPriority
from .work_stealing_scheduler import TaskStatus


@dataclass
class QueueConfig:
    """Configuration for task queue behavior"""

    max_size: int = 10000
    priority_levels: int = 4
    batch_size: int = 100
    batch_timeout: float = 0.1  # seconds
    enable_batching: bool = True
    enable_prioritization: bool = True
    enable_deadlines: bool = True
    enable_affinity: bool = True
    enable_sharding: bool = True
    num_shards: int = 16


@dataclass
class QueueStats:
    """Statistics for task queue performance"""

    total_enqueued: int = 0
    total_dequeued: int = 0
    queue_depth: int = 0
    avg_wait_time_ms: float = 0.0
    max_wait_time_ms: float = 0.0
    batch_operations: int = 0
    priority_distribution: dict[int, int] = field(default_factory=dict)
    throughput_tasks_per_sec: float = 0.0


class PriorityTask:
    """Wrapper for tasks with priority comparison"""

    def __init__(self, task: Task, enqueue_time: float):
        self.task = task
        self.enqueue_time = enqueue_time
        self.priority_value = self._calculate_priority_value()

    def _calculate_priority_value(self) -> int:
        """Calculate priority value for heap ordering"""
        # Lower value = higher priority
        base_priority = len(TaskPriority) - 1 - self.task.priority.value

        # Add tie-breaker based on enqueue time (FIFO within priority)
        time_factor = int(self.enqueue_time * 1000000) % 1000000

        return (base_priority << 20) | time_factor

    def __lt__(self, other):
        return self.priority_value < other.priority_value


class TaskQueue:
    """High-performance priority task queue"""

    def __init__(self, config: QueueConfig | None = None):
        self.config = config or QueueConfig()

        # Priority queues
        self._priority_queues: list[heapq] = [[] for _ in range(self.config.priority_levels)]
        self._queue_locks: list[threading.Lock] = [threading.Lock() for _ in range(self.config.priority_levels)]

        # Task tracking
        self._task_lookup: dict[str, PriorityTask] = {}
        self._wait_times: list[float] = []
        self._lookup_lock = threading.Lock()

        # Batching
        self._batch_buffer: list[Task] = []
        self._batch_buffer_lock = threading.Lock()
        self._batch_ready_event = asyncio.Event()

        # Sharding for concurrent access
        if self.config.enable_sharding:
            self._shards: list[Queue] = [
                Queue(maxsize=self.config.max_size // self.config.num_shards) for _ in range(self.config.num_shards)
            ]
            self._shard_locks = [threading.Lock() for _ in range(self.config.num_shards)]

        # Statistics
        self._stats = QueueStats()
        self._stats_lock = threading.Lock()
        self._start_time = time.time()

        # Background processing
        self._processing = False
        self._batch_processor_task: asyncio.Task | None = None

    async def start(self):
        """Start the task queue"""
        if self._processing:
            return

        self._processing = True

        if self.config.enable_batching:
            self._batch_processor_task = asyncio.create_task(self._batch_processor_loop())

    async def stop(self):
        """Stop the task queue"""
        self._processing = False

        if self._batch_processor_task:
            self._batch_processor_task.cancel()
            try:
                await self._batch_processor_task
            except asyncio.CancelledError:
                pass

    async def enqueue(self, task: Task) -> bool:
        """Enqueue a task for processing"""
        current_time = time.time()

        # Check queue capacity
        if self.get_size() >= self.config.max_size:
            return False

        # Create priority task wrapper
        priority_task = PriorityTask(task, current_time)

        if self.config.enable_sharding:
            # Use sharding for concurrent access
            shard_id = hash(task.id) % self.config.num_shards
            shard = self._shards[shard_id]

            try:
                shard.put_nowait(priority_task)
            except:
                return False
        else:
            # Use priority queues
            priority = task.priority.value
            if priority >= len(self._priority_queues):
                priority = len(self._priority_queues) - 1

            queue = self._priority_queues[priority]
            lock = self._queue_locks[priority]

            with lock:
                heapq.heappush(queue, priority_task)

        # Track task
        with self._lookup_lock:
            self._task_lookup[task.id] = priority_task

        # Update statistics
        with self._stats_lock:
            self._stats.total_enqueued += 1
            self._stats.queue_depth += 1

            # Update priority distribution
            priority = task.priority.value
            self._stats.priority_distribution[priority] = self._stats.priority_distribution.get(priority, 0) + 1

        return True

    async def dequeue(self, timeout: float | None = None) -> Task | None:
        """Dequeue the highest priority task"""
        start_time = time.time()

        # Try to get from priority queues first
        for priority in range(len(self._priority_queues)):
            queue = self._priority_queues[priority]
            lock = self._queue_locks[priority]

            with lock:
                if queue:
                    priority_task = heapq.heappop(queue)
                    return self._finalize_dequeue(priority_task, start_time)

        if self.config.enable_sharding:
            # Try sharded queues
            for shard in self._shards:
                try:
                    priority_task = shard.get_nowait()
                    return self._finalize_dequeue(priority_task, start_time)
                except:
                    continue

        # Wait for task if timeout specified
        if timeout is not None:
            elapsed = time.time() - start_time
            remaining_timeout = timeout - elapsed

            if remaining_timeout > 0:
                await asyncio.sleep(remaining_timeout)

                # Try again after waiting
                for priority in range(len(self._priority_queues)):
                    queue = self._priority_queues[priority]
                    lock = self._queue_locks[priority]

                    with lock:
                        if queue:
                            priority_task = heapq.heappop(queue)
                            return self._finalize_dequeue(priority_task, start_time)

        return None

    def _finalize_dequeue(self, priority_task: PriorityTask, start_time: float) -> Task:
        """Finalize task dequeue with statistics"""
        task = priority_task.task
        current_time = time.time()
        wait_time = (current_time - start_time) * 1000  # Convert to ms

        # Remove from lookup
        with self._lookup_lock:
            self._task_lookup.pop(task.id, None)

        # Update task
        task.status = TaskStatus.RUNNING
        task.started_time = current_time

        # Track wait time
        self._wait_times.append(wait_time)
        if len(self._wait_times) > 1000:  # Keep last 1000 wait times
            self._wait_times.pop(0)

        # Update statistics
        with self._stats_lock:
            self._stats.total_dequeued += 1
            self._stats.queue_depth -= 1
            self._stats.max_wait_time_ms = max(self._stats.max_wait_time_ms, wait_time)

            # Update average wait time
            if self._wait_times:
                self._stats.avg_wait_time_ms = sum(self._wait_times) / len(self._wait_times)

        return task

    async def enqueue_batch(self, tasks: list[Task]) -> int:
        """Enqueue multiple tasks efficiently"""
        if not self.config.enable_batching:
            # Fallback to individual enqueues
            success_count = 0
            for task in tasks:
                if await self.enqueue(task):
                    success_count += 1
            return success_count

        # Add to batch buffer
        with self._batch_buffer_lock:
            self._batch_buffer.extend(tasks)

            # Trigger batch processing if buffer is full
            if len(self._batch_buffer) >= self.config.batch_size:
                self._batch_ready_event.set()

        return len(tasks)

    async def _batch_processor_loop(self):
        """Background loop for processing batched tasks"""
        while self._processing:
            try:
                # Wait for batch or timeout
                await asyncio.wait_for(self._batch_ready_event.wait(), timeout=self.config.batch_timeout)

                # Process batch
                await self._process_batch()
                self._batch_ready_event.clear()

            except TimeoutError:
                # Timeout - process whatever is in buffer
                with self._batch_buffer_lock:
                    if self._batch_buffer:
                        await self._process_batch()

            except Exception as e:
                print(f"Batch processor error: {e}")
                await asyncio.sleep(0.01)

    async def _process_batch(self):
        """Process a batch of tasks"""
        with self._batch_buffer_lock:
            if not self._batch_buffer:
                return

            batch = self._batch_buffer[:]
            self._batch_buffer.clear()

        # Sort batch by priority
        if self.config.enable_prioritization:
            batch.sort(key=lambda t: t.priority.value, reverse=True)

        # Enqueue batch
        success_count = 0
        for task in batch:
            if await self.enqueue(task):
                success_count += 1

        # Update statistics
        with self._stats_lock:
            self._stats.batch_operations += 1

    def get_size(self) -> int:
        """Get total queue size"""
        size = sum(len(queue) for queue in self._priority_queues)

        if self.config.enable_sharding:
            size += sum(shard.qsize() for shard in self._shards)

        return size

    def is_empty(self) -> bool:
        """Check if queue is empty"""
        if self.config.enable_sharding:
            return all(len(queue) == 0 for queue in self._priority_queues) and all(
                shard.empty() for shard in self._shards
            )
        return all(len(queue) == 0 for queue in self._priority_queues)

    def peek(self) -> Task | None:
        """Peek at the next task without removing it"""
        # Check priority queues first
        for priority in range(len(self._priority_queues)):
            queue = self._priority_queues[priority]
            lock = self._queue_locks[priority]

            with lock:
                if queue:
                    return queue[0].task

        if self.config.enable_sharding:
            # Check sharded queues
            for shard in self._shards:
                try:
                    priority_task = shard.queue[0]
                    return priority_task.task
                except (IndexError, AttributeError):
                    continue

        return None

    def remove_task(self, task_id: str) -> bool:
        """Remove a specific task from the queue"""
        with self._lookup_lock:
            priority_task = self._task_lookup.get(task_id)
            if not priority_task:
                return False

        # Remove from appropriate queue
        task = priority_task.task
        priority = task.priority.value

        if priority >= len(self._priority_queues):
            priority = len(self._priority_queues) - 1

        queue = self._priority_queues[priority]
        lock = self._queue_locks[priority]

        with lock:
            try:
                queue.remove(priority_task)
                heapq.heapify(queue)  # Rebuild heap

                # Remove from lookup
                with self._lookup_lock:
                    del self._task_lookup[task_id]

                # Update statistics
                with self._stats_lock:
                    self._stats.queue_depth -= 1

                return True
            except ValueError:
                # Task not in queue
                pass

        return False

    def get_task_priority_distribution(self) -> dict[str, int]:
        """Get distribution of tasks by priority"""
        distribution = {}

        for priority_value, count in self._stats.priority_distribution.items():
            priority_name = TaskPriority(priority_value).name
            distribution[priority_name] = count

        return distribution

    def get_stats(self) -> QueueStats:
        """Get current queue statistics"""
        current_time = time.time()
        runtime = current_time - self._start_time

        with self._stats_lock:
            # Calculate throughput
            throughput = self._stats.total_dequeued / runtime if runtime > 0 else 0.0

            return QueueStats(
                total_enqueued=self._stats.total_enqueued,
                total_dequeued=self._stats.total_dequeued,
                queue_depth=self.get_size(),
                avg_wait_time_ms=self._stats.avg_wait_time_ms,
                max_wait_time_ms=self._stats.max_wait_time_ms,
                batch_operations=self._stats.batch_operations,
                priority_distribution=self._stats.priority_distribution.copy(),
                throughput_tasks_per_sec=throughput,
            )

    def get_performance_metrics(self) -> dict[str, float]:
        """Get detailed performance metrics"""
        stats = self.get_stats()

        # Calculate additional metrics
        success_rate = stats.total_dequeued / stats.total_enqueued if stats.total_enqueued > 0 else 0.0

        queue_utilization = stats.queue_depth / self.config.max_size if self.config.max_size > 0 else 0.0

        # Calculate 95th percentile wait time
        wait_times_sorted = sorted(self._wait_times)
        p95_index = int(len(wait_times_sorted) * 0.95)
        p95_wait_time = wait_times_sorted[p95_index] if wait_times_sorted else 0.0

        return {
            "success_rate": success_rate,
            "queue_utilization": queue_utilization,
            "p95_wait_time_ms": p95_wait_time,
            "throughput_tasks_per_sec": stats.throughput_tasks_per_sec,
            "avg_wait_time_ms": stats.avg_wait_time_ms,
            "batch_efficiency": (stats.batch_operations / stats.total_dequeued if stats.total_dequeued > 0 else 0.0),
        }


# Global task queue instance
_global_task_queue: TaskQueue | None = None


def get_task_queue(**kwargs) -> TaskQueue:
    """Get or create the global task queue"""
    global _global_task_queue
    if _global_task_queue is None:
        _global_task_queue = TaskQueue(**kwargs)
        # Note: queue.start() must be called explicitly
    return _global_task_queue
