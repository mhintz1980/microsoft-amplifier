"""
Dynamic Load Balancer

Intelligent workload distribution with multiple balancing strategies,
real-time load monitoring, and adaptive routing.
"""

import asyncio
import math
import time
from abc import ABC
from abc import abstractmethod
from dataclasses import dataclass
from dataclasses import field
from enum import Enum

from .work_stealing_scheduler import Task
from .worker_pool import get_worker_pool


class BalancerStrategy(Enum):
    """Load balancing strategies"""

    ROUND_ROBIN = "round_robin"
    LEAST_CONNECTIONS = "least_connections"
    WEIGHTED_ROUND_ROBIN = "weighted_round_robin"
    RESPONSE_TIME = "response_time"
    RESOURCE_BASED = "resource_based"
    PREDICTIVE = "predictive"


@dataclass
class WorkerLoad:
    """Load information for a worker"""

    worker_id: str
    current_tasks: int = 0
    completed_tasks: int = 0
    avg_response_time: float = 0.0
    error_rate: float = 0.0
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    queue_depth: int = 0
    weight: float = 1.0
    last_update: float = field(default_factory=time.time)


@dataclass
class BalancerStats:
    """Statistics for load balancer performance"""

    total_assignments: int = 0
    rebalancing_operations: int = 0
    strategy_changes: int = 0
    avg_load_imbalance: float = 0.0
    max_load_imbalance: float = 0.0
    assignment_success_rate: float = 0.0


class LoadBalancingStrategy(ABC):
    """Abstract base class for load balancing strategies"""

    @abstractmethod
    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        """Select the best worker for a task"""
        pass

    @abstractmethod
    def update_weights(self, workers: list[WorkerLoad]):
        """Update worker weights based on performance"""
        pass


class RoundRobinStrategy(LoadBalancingStrategy):
    """Round-robin load balancing"""

    def __init__(self):
        self._current_index = 0

    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        if not workers:
            return None

        # Simple round-robin
        worker = workers[self._current_index % len(workers)]
        self._current_index += 1

        return worker.worker_id

    def update_weights(self, workers: list[WorkerLoad]):
        # Round-robin doesn't use weights
        pass


class LeastConnectionsStrategy(LoadBalancingStrategy):
    """Least connections load balancing"""

    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        if not workers:
            return None

        # Select worker with minimum current tasks
        best_worker = min(workers, key=lambda w: w.current_tasks)
        return best_worker.worker_id

    def update_weights(self, workers: list[WorkerLoad]):
        # Update weights based on current load
        max_tasks = max((w.current_tasks for w in workers), default=1)
        for worker in workers:
            if max_tasks > 0:
                worker.weight = 1.0 - (worker.current_tasks / max_tasks)
            else:
                worker.weight = 1.0


class WeightedRoundRobinStrategy(LoadBalancingStrategy):
    """Weighted round-robin load balancing"""

    def __init__(self):
        self._current_index = 0
        self._current_weight = 0

    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        if not workers:
            return None

        # Calculate total weight
        total_weight = sum(w.weight for w in workers)
        if total_weight == 0:
            return workers[0].worker_id

        # Weighted round-robin selection
        while True:
            self._current_index = (self._current_index + 1) % len(workers)
            self._current_weight += workers[self._current_index].weight

            if self._current_weight >= total_weight:
                self._current_weight = 0
                return workers[self._current_index].worker_id

    def update_weights(self, workers: list[WorkerLoad]):
        # Weights should be updated externally
        pass


class ResponseTimeStrategy(LoadBalancingStrategy):
    """Response time based load balancing"""

    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        if not workers:
            return None

        # Select worker with best response time score
        def score_worker(worker: WorkerLoad) -> float:
            # Lower response time is better
            response_score = 1.0 / (1.0 + worker.avg_response_time)

            # Penalize high error rates
            error_penalty = 1.0 - worker.error_rate

            # Consider current load
            load_penalty = 1.0 / (1.0 + worker.current_tasks)

            return response_score * error_penalty * load_penalty * worker.weight

        best_worker = max(workers, key=score_worker)
        return best_worker.worker_id

    def update_weights(self, workers: list[WorkerLoad]):
        # Update weights based on response times
        max_response_time = max((w.avg_response_time for w in workers), default=1.0)

        for worker in workers:
            if max_response_time > 0:
                # Faster workers get higher weights
                performance_ratio = max_response_time / (worker.avg_response_time + 0.001)
                worker.weight = min(2.0, performance_ratio)  # Cap at 2.0
            else:
                worker.weight = 1.0


class ResourceBasedStrategy(LoadBalancingStrategy):
    """Resource-based load balancing"""

    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        if not workers:
            return None

        def score_worker(worker: WorkerLoad) -> float:
            # Calculate resource availability score
            cpu_availability = 1.0 - worker.cpu_usage
            memory_availability = 1.0 - worker.memory_usage

            # Consider current load
            load_availability = 1.0 / (1.0 + worker.current_tasks)

            # Composite score
            resource_score = (cpu_availability + memory_availability) / 2.0
            return resource_score * load_availability * worker.weight

        best_worker = max(workers, key=score_worker)
        return best_worker.worker_id

    def update_weights(self, workers: list[WorkerLoad]):
        # Update weights based on resource availability
        for worker in workers:
            resource_availability = (1.0 - worker.cpu_usage + 1.0 - worker.memory_usage) / 2.0
            worker.weight = max(0.1, resource_availability)


class PredictiveStrategy(LoadBalancingStrategy):
    """Predictive load balancing using historical data"""

    def __init__(self):
        self._task_history: dict[str, list[float]] = {}
        self._worker_performance: dict[str, list[float]] = {}

    async def select_worker(self, workers: list[WorkerLoad], task: Task | None = None) -> str | None:
        if not workers:
            return None

        if task is None:
            # Fallback to least connections if no task info
            return min(workers, key=lambda w: w.current_tasks).worker_id

        # Predict task execution time
        predicted_time = self._predict_task_time(task)

        # Score workers based on predicted performance
        def score_worker(worker: WorkerLoad) -> float:
            # Base score from current load
            load_score = 1.0 / (1.0 + worker.current_tasks)

            # Adjust for predicted task fit
            worker_avg_time = self._get_worker_avg_time(worker.worker_id)
            if worker_avg_time > 0:
                time_fit = worker_avg_time / (predicted_time + 0.001)
                time_score = min(2.0, time_fit)  # Cap the bonus
            else:
                time_score = 1.0

            return load_score * time_score * worker.weight

        best_worker = max(workers, key=score_worker)
        return best_worker.worker_id

    def update_weights(self, workers: list[WorkerLoad]):
        # Update weights based on historical performance
        for worker in workers:
            avg_performance = self._get_worker_avg_time(worker.worker_id)
            if avg_performance > 0:
                # Better performing workers get higher weights
                worker.weight = min(2.0, 10.0 / avg_performance)
            else:
                worker.weight = 1.0

    def _predict_task_time(self, task: Task) -> float:
        """Predict task execution time based on historical data"""
        task_type = type(task.func).__name__

        if task_type in self._task_history:
            history = self._task_history[task_type]
            if history:
                # Return average historical time
                return sum(history) / len(history)

        return 1.0  # Default prediction

    def _get_worker_avg_time(self, worker_id: str) -> float:
        """Get average execution time for a worker"""
        if worker_id in self._worker_performance:
            history = self._worker_performance[worker_id]
            if history:
                return sum(history) / len(history)

        return 0.0

    def record_task_completion(self, task: Task, execution_time: float):
        """Record task completion for learning"""
        task_type = type(task.func).__name__

        if task_type not in self._task_history:
            self._task_history[task_type] = []

        if task.worker_id not in self._worker_performance:
            self._worker_performance[task.worker_id] = []

        # Add to history (keep last 100 entries)
        self._task_history[task_type].append(execution_time)
        if len(self._task_history[task_type]) > 100:
            self._task_history[task_type].pop(0)

        self._worker_performance[task.worker_id].append(execution_time)
        if len(self._worker_performance[task.worker_id]) > 100:
            self._worker_performance[task.worker_id].pop(0)


class LoadBalancer:
    """Dynamic load balancer with multiple strategies"""

    def __init__(
        self,
        initial_strategy: BalancerStrategy = BalancerStrategy.LEAST_CONNECTIONS,
        rebalance_interval: float = 5.0,
        strategy_switch_threshold: float = 0.2,
        enable_auto_switching: bool = True,
    ):
        self.initial_strategy = initial_strategy
        self.rebalance_interval = rebalance_interval
        self.strategy_switch_threshold = strategy_switch_threshold
        self.enable_auto_switching = enable_auto_switching

        # Strategy implementations
        self._strategies: dict[BalancerStrategy, LoadBalancingStrategy] = {
            BalancerStrategy.ROUND_ROBIN: RoundRobinStrategy(),
            BalancerStrategy.LEAST_CONNECTIONS: LeastConnectionsStrategy(),
            BalancerStrategy.WEIGHTED_ROUND_ROBIN: WeightedRoundRobinStrategy(),
            BalancerStrategy.RESPONSE_TIME: ResponseTimeStrategy(),
            BalancerStrategy.RESOURCE_BASED: ResourceBasedStrategy(),
            BalancerStrategy.PREDICTIVE: PredictiveStrategy(),
        }

        self._current_strategy = self._strategies[initial_strategy]
        self._current_strategy_name = initial_strategy

        # Worker load tracking
        self._worker_loads: dict[str, WorkerLoad] = {}
        self._performance_history: dict[str, list[float]] = {}

        # Statistics
        self._stats = BalancerStats()
        self._stats_lock = None  # Will be created in async context

        # Background tasks
        self._balancing = False
        self._rebalance_task: asyncio.Task | None = None

        # Worker pool reference
        self._worker_pool = get_worker_pool()

    async def start(self):
        """Start the load balancer"""
        if self._balancing:
            return

        self._balancing = True
        self._stats_lock = asyncio.Lock()

        # Start rebalancing task
        self._rebalance_task = asyncio.create_task(self._rebalancing_loop())

    async def stop(self):
        """Stop the load balancer"""
        self._balancing = False

        if self._rebalance_task:
            self._rebalance_task.cancel()
            try:
                await self._rebalance_task
            except asyncio.CancelledError:
                pass

    async def assign_task(self, task: Task) -> str | None:
        """Assign a task to the best available worker"""
        # Get current worker loads
        current_loads = list(self._worker_loads.values())

        if not current_loads:
            # Initialize worker loads if empty
            await self._initialize_worker_loads()
            current_loads = list(self._worker_loads.values())

        # Select worker using current strategy
        worker_id = await self._current_strategy.select_worker(current_loads, task)

        if worker_id:
            # Update worker load
            if worker_id in self._worker_loads:
                self._worker_loads[worker_id].current_tasks += 1
                self._worker_loads[worker_id].last_update = time.time()

            # Record assignment
            async with self._stats_lock:
                self._stats.total_assignments += 1

        return worker_id

    def task_completed(self, worker_id: str, task: Task, execution_time: float):
        """Record task completion and update statistics"""
        if worker_id in self._worker_loads:
            load = self._worker_loads[worker_id]
            load.current_tasks = max(0, load.current_tasks - 1)
            load.completed_tasks += 1

            # Update average response time
            if load.completed_tasks > 0:
                total_time = load.avg_response_time * (load.completed_tasks - 1) + execution_time
                load.avg_response_time = total_time / load.completed_tasks

            load.last_update = time.time()

        # Record for predictive strategy
        if isinstance(self._current_strategy, PredictiveStrategy):
            self._current_strategy.record_task_completion(task, execution_time)

    def task_failed(self, worker_id: str, task: Task):
        """Record task failure"""
        if worker_id in self._worker_loads:
            load = self._worker_loads[worker_id]
            load.current_tasks = max(0, load.current_tasks - 1)

            # Update error rate (simplified)
            total_tasks = load.completed_tasks + 1
            if total_tasks > 0:
                load.error_rate = min(1.0, load.error_rate + (1.0 / total_tasks))

            load.last_update = time.time()

    async def _initialize_worker_loads(self):
        """Initialize worker load tracking"""
        worker_pool_stats = self._worker_pool.get_stats()

        if "worker_details" in worker_pool_stats:
            for worker_id, details in worker_pool_stats["worker_details"].items():
                if worker_id not in self._worker_loads:
                    self._worker_loads[worker_id] = WorkerLoad(
                        worker_id=worker_id, current_tasks=0, completed_tasks=details.get("tasks_completed", 0)
                    )

    async def _rebalancing_loop(self):
        """Background loop for periodic rebalancing"""
        while self._balancing:
            try:
                await self._update_worker_loads()
                await self._update_strategy_weights()
                await self._check_strategy_switch()
                await asyncio.sleep(self.rebalance_interval)
            except Exception as e:
                print(f"Load balancer rebalancing error: {e}")
                await asyncio.sleep(1.0)

    async def _update_worker_loads(self):
        """Update worker load information"""
        worker_pool_stats = self._worker_pool.get_stats()

        if "worker_details" not in worker_pool_stats:
            return

        for worker_id, details in worker_pool_stats["worker_details"].items():
            if worker_id not in self._worker_loads:
                self._worker_loads[worker_id] = WorkerLoad(worker_id=worker_id)

            load = self._worker_loads[worker_id]
            load.current_tasks = 1 if details.get("status") == "busy" else 0
            load.completed_tasks = details.get("tasks_completed", 0)
            load.cpu_usage = details.get("cpu_usage", 0.0)
            load.memory_usage = details.get("memory_usage_mb", 0.0) / 1024.0  # Convert to GB
            load.queue_depth = 0  # Would need access to queue information
            load.last_update = time.time()

    async def _update_strategy_weights(self):
        """Update weights for current strategy"""
        current_loads = list(self._worker_loads.values())
        self._current_strategy.update_weights(current_loads)

    async def _check_strategy_switch(self):
        """Check if strategy switching is needed"""
        if not self.enable_auto_switching:
            return

        # Evaluate current strategy performance
        current_performance = await self._evaluate_strategy(self._current_strategy_name)

        # Try other strategies
        best_strategy = self._current_strategy_name
        best_performance = current_performance

        for strategy_name in BalancerStrategy:
            if strategy_name == self._current_strategy_name:
                continue

            performance = await self._evaluate_strategy(strategy_name)
            if performance > best_performance + self.strategy_switch_threshold:
                best_strategy = strategy_name
                best_performance = performance

        # Switch if better strategy found
        if best_strategy != self._current_strategy_name:
            await self._switch_strategy(best_strategy)

    async def _evaluate_strategy(self, strategy_name: BalancerStrategy) -> float:
        """Evaluate a strategy's performance"""
        # For now, use simple load imbalance metric
        loads = list(self._worker_loads.values())

        if not loads:
            return 0.0

        current_tasks = [w.current_tasks for w in loads]
        if not current_tasks:
            return 1.0

        avg_tasks = sum(current_tasks) / len(current_tasks)
        max_tasks = max(current_tasks)
        min_tasks = min(current_tasks)

        # Load imbalance (lower is better)
        if avg_tasks > 0:
            imbalance = (max_tasks - min_tasks) / avg_tasks
        else:
            imbalance = 0.0

        # Convert to performance score (higher is better)
        return max(0.0, 1.0 - min(1.0, imbalance))

    async def _switch_strategy(self, new_strategy: BalancerStrategy):
        """Switch to a different load balancing strategy"""
        print(f"Switching load balancing strategy: {self._current_strategy_name.value} -> {new_strategy.value}")

        self._current_strategy = self._strategies[new_strategy]
        self._current_strategy_name = new_strategy

        async with self._stats_lock:
            self._stats.strategy_changes += 1

    def get_stats(self) -> BalancerStats:
        """Get load balancer statistics"""
        return BalancerStats(
            total_assignments=self._stats.total_assignments,
            rebalancing_operations=self._stats.rebalancing_operations,
            strategy_changes=self._stats.strategy_changes,
            avg_load_imbalance=self._calculate_load_imbalance(),
            max_load_imbalance=self._calculate_max_load_imbalance(),
            assignment_success_rate=1.0,  # Simplified
        )

    def _calculate_load_imbalance(self) -> float:
        """Calculate current load imbalance"""
        loads = list(self._worker_loads.values())
        if not loads:
            return 0.0

        current_tasks = [w.current_tasks for w in loads]
        if not current_tasks:
            return 0.0

        avg_tasks = sum(current_tasks) / len(current_tasks)
        if avg_tasks == 0:
            return 0.0

        variance = sum((tasks - avg_tasks) ** 2 for tasks in current_tasks) / len(current_tasks)
        return math.sqrt(variance) / avg_tasks

    def _calculate_max_load_imbalance(self) -> float:
        """Calculate maximum load imbalance seen"""
        # This would need tracking over time
        return self._calculate_load_imbalance()

    def get_worker_loads(self) -> dict[str, WorkerLoad]:
        """Get current worker load information"""
        return self._worker_loads.copy()

    def set_strategy(self, strategy: BalancerStrategy):
        """Manually set the load balancing strategy"""
        self._current_strategy = self._strategies[strategy]
        self._current_strategy_name = strategy

    def get_current_strategy(self) -> BalancerStrategy:
        """Get the current load balancing strategy"""
        return self._current_strategy_name


# Global load balancer instance
_global_load_balancer: LoadBalancer | None = None


def get_load_balancer(**kwargs) -> LoadBalancer:
    """Get or create the global load balancer"""
    global _global_load_balancer
    if _global_load_balancer is None:
        _global_load_balancer = LoadBalancer(**kwargs)
        # Note: balancer.start() must be called explicitly
    return _global_load_balancer
