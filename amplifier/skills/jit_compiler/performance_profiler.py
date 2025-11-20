"""
Performance Profiler for JIT Optimization

Real-time performance monitoring and analysis system
for measuring JIT compilation effectiveness.
"""

import asyncio
import threading
import time
from collections import defaultdict
from collections import deque
from dataclasses import dataclass
from dataclasses import field

from .jit_optimizer import CompilationTier
from .jit_optimizer import OptimizationResult


@dataclass
class ProfilerStats:
    """Statistics for performance profiler"""

    total_functions: int = 0
    optimized_functions: int = 0
    total_executions: int = 0
    total_jit_time_ms: float = 0.0
    avg_speedup: float = 0.0
    max_speedup: float = 0.0
    tier_distribution: dict[str, int] = field(default_factory=dict)


@dataclass
class ExecutionRecord:
    """Record of function execution"""

    func_key: str
    execution_time: float
    optimized: bool
    tier: CompilationTier | None
    timestamp: float


class PerformanceProfiler:
    """Real-time performance profiler for JIT optimization"""

    def __init__(self, sample_size: int = 1000):
        self.sample_size = sample_size

        # Execution tracking
        self._execution_records: deque = deque(maxlen=sample_size * 10)
        self._records_lock = threading.Lock()

        # Performance metrics
        self._function_metrics: dict[str, dict] = {}
        self._metrics_lock = threading.Lock()

        # JIT compilation tracking
        self._compilation_results: dict[str, list[OptimizationResult]] = {}
        self._results_lock = threading.Lock()

        # Background analysis
        self._analyzing = False
        self._analysis_task: asyncio.Task | None = None

    async def start(self):
        """Start performance profiling"""
        if self._analyzing:
            return

        self._analyzing = True
        self._analysis_task = asyncio.create_task(self._analysis_loop())

    async def stop(self):
        """Stop performance profiling"""
        self._analyzing = False

        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass

    def record_execution(
        self, func_key: str, execution_time: float, optimized: bool = False, tier: CompilationTier | None = None
    ):
        """Record a function execution"""
        record = ExecutionRecord(
            func_key=func_key, execution_time=execution_time, optimized=optimized, tier=tier, timestamp=time.time()
        )

        with self._records_lock:
            self._execution_records.append(record)

        # Update function metrics
        with self._metrics_lock:
            if func_key not in self._function_metrics:
                self._function_metrics[func_key] = {
                    "total_executions": 0,
                    "total_time": 0.0,
                    "optimized_executions": 0,
                    "optimized_time": 0.0,
                    "avg_time": 0.0,
                    "optimized_avg_time": 0.0,
                    "speedup": 0.0,
                }

            metrics = self._function_metrics[func_key]
            metrics["total_executions"] += 1
            metrics["total_time"] += execution_time
            metrics["avg_time"] = metrics["total_time"] / metrics["total_executions"]

            if optimized:
                metrics["optimized_executions"] += 1
                metrics["optimized_time"] += execution_time
                metrics["optimized_avg_time"] = metrics["optimized_time"] / metrics["optimized_executions"]

                # Calculate speedup
                if metrics["optimized_executions"] > 0 and metrics["avg_time"] > 0:
                    metrics["speedup"] = metrics["avg_time"] / metrics["optimized_avg_time"]

    def record_compilation(self, func_key: str, result: OptimizationResult):
        """Record JIT compilation result"""
        with self._results_lock:
            if func_key not in self._compilation_results:
                self._compilation_results[func_key] = []
            self._compilation_results[func_key].append(result)

    async def _analysis_loop(self):
        """Background loop for performance analysis"""
        while self._analyzing:
            try:
                await self._analyze_performance()
                await asyncio.sleep(5.0)  # Analyze every 5 seconds
            except Exception as e:
                print(f"Performance analysis error: {e}")
                await asyncio.sleep(1.0)

    async def _analyze_performance(self):
        """Analyze performance data"""
        # This would perform more sophisticated analysis
        # For now, just ensure data consistency
        pass

    def get_function_performance(self, func_key: str) -> dict | None:
        """Get performance metrics for a specific function"""
        with self._metrics_lock:
            return self._function_metrics.get(func_key)

    def get_compilation_history(self, func_key: str) -> list[OptimizationResult]:
        """Get compilation history for a function"""
        with self._results_lock:
            return self._compilation_results.get(func_key, [])

    def get_stats(self) -> ProfilerStats:
        """Get overall performance statistics"""
        with self._metrics_lock:
            total_functions = len(self._function_metrics)
            optimized_functions = len([f for f, m in self._function_metrics.items() if m["optimized_executions"] > 0])

            total_executions = sum(m["total_executions"] for m in self._function_metrics.values())
            total_jit_time = sum(
                result.compilation_time_ms for results in self._compilation_results.values() for result in results
            )

            # Calculate speedups
            speedups = [m["speedup"] for m in self._function_metrics.values() if m["speedup"] > 0]
            avg_speedup = sum(speedups) / len(speedups) if speedups else 0.0
            max_speedup = max(speedups) if speedups else 0.0

            # Tier distribution
            tier_distribution = defaultdict(int)
            for results in self._compilation_results.values():
                for result in results:
                    tier_distribution[result.tier.name] += 1

            return ProfilerStats(
                total_functions=total_functions,
                optimized_functions=optimized_functions,
                total_executions=total_executions,
                total_jit_time_ms=total_jit_time,
                avg_speedup=avg_speedup,
                max_speedup=max_speedup,
                tier_distribution=dict(tier_distribution),
            )

    def get_top_functions(self, metric: str = "total_executions", limit: int = 10) -> list[tuple[str, float]]:
        """Get top functions by specified metric"""
        with self._metrics_lock:
            functions = [
                (func_key, metrics[metric]) for func_key, metrics in self._function_metrics.items() if metric in metrics
            ]
            functions.sort(key=lambda x: x[1], reverse=True)
            return functions[:limit]

    def get_execution_timeline(self, duration_seconds: float = 60.0) -> dict[str, list[tuple[float, float]]]:
        """Get execution timeline for recent executions"""
        current_time = time.time()
        cutoff_time = current_time - duration_seconds

        timeline = defaultdict(list)

        with self._records_lock:
            for record in self._execution_records:
                if record.timestamp >= cutoff_time:
                    timeline[record.func_key].append((record.timestamp, record.execution_time))

        return dict(timeline)


# Global performance profiler instance
_global_performance_profiler: PerformanceProfiler | None = None


def get_performance_profiler(**kwargs) -> PerformanceProfiler:
    """Get or create the global performance profiler"""
    global _global_performance_profiler
    if _global_performance_profiler is None:
        _global_performance_profiler = PerformanceProfiler(**kwargs)
        # Note: profiler.start() must be called explicitly
    return _global_performance_profiler
