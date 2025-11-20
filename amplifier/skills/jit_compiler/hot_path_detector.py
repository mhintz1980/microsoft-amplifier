"""
Hot Path Detection System

Identifies frequently executed code paths for JIT optimization
with statistical analysis and pattern recognition.
"""

import asyncio
import threading
import time
from collections import deque
from dataclasses import dataclass
from dataclasses import field


@dataclass
class DetectionConfig:
    """Configuration for hot path detection"""

    sample_window_size: int = 1000
    hot_threshold_percentile: float = 90.0
    min_execution_count: int = 100
    analysis_interval: float = 10.0
    enable_profiling: bool = True


@dataclass
class FunctionStats:
    """Statistics for function execution"""

    func_key: str
    execution_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    max_time: float = 0.0
    min_time: float = float("inf")
    last_execution: float = 0.0
    execution_times: deque = field(default_factory=lambda: deque(maxlen=1000))


@dataclass
class HotPath:
    """Represents a hot execution path"""

    func_key: str
    execution_count: int
    avg_time: float
    total_time: float
    hot_score: float
    detected_time: float


class HotPathDetector:
    """Detects hot execution paths for JIT optimization"""

    def __init__(self, config: DetectionConfig | None = None):
        self.config = config or DetectionConfig()

        # Function tracking
        self._function_stats: dict[str, FunctionStats] = {}
        self._stats_lock = threading.Lock()

        # Hot path tracking
        self._hot_paths: dict[str, HotPath] = {}
        self._hot_paths_lock = threading.Lock()

        # Background analysis
        self._analyzing = False
        self._analysis_task: asyncio.Task | None = None

    async def start(self):
        """Start hot path detection"""
        if self._analyzing:
            return

        self._analyzing = True
        if self.config.enable_profiling:
            self._analysis_task = asyncio.create_task(self._analysis_loop())

    async def stop(self):
        """Stop hot path detection"""
        self._analyzing = False

        if self._analysis_task:
            self._analysis_task.cancel()
            try:
                await self._analysis_task
            except asyncio.CancelledError:
                pass

    def record_execution(self, func_key: str, execution_time: float):
        """Record a function execution"""
        with self._stats_lock:
            if func_key not in self._function_stats:
                self._function_stats[func_key] = FunctionStats(func_key=func_key)

            stats = self._function_stats[func_key]
            stats.execution_count += 1
            stats.total_time += execution_time
            stats.avg_time = stats.total_time / stats.execution_count
            stats.max_time = max(stats.max_time, execution_time)
            stats.min_time = min(stats.min_time, execution_time)
            stats.last_execution = time.time()
            stats.execution_times.append(execution_time)

    async def _analysis_loop(self):
        """Background loop for hot path analysis"""
        while self._analyzing:
            try:
                await self._analyze_hot_paths()
                await asyncio.sleep(self.config.analysis_interval)
            except Exception as e:
                print(f"Hot path analysis error: {e}")
                await asyncio.sleep(1.0)

    async def _analyze_hot_paths(self):
        """Analyze function statistics to identify hot paths"""
        with self._stats_lock:
            # Get functions with minimum execution count
            candidates = [
                stats
                for stats in self._function_stats.values()
                if stats.execution_count >= self.config.min_execution_count
            ]

        if not candidates:
            return

        # Calculate hot scores
        hot_candidates = []
        for stats in candidates:
            hot_score = self._calculate_hot_score(stats)
            if hot_score > 0:
                hot_candidates.append((stats, hot_score))

        # Sort by hot score
        hot_candidates.sort(key=lambda x: x[1], reverse=True)

        # Update hot paths
        with self._hot_paths_lock:
            current_time = time.time()
            for stats, hot_score in hot_candidates:
                hot_path = HotPath(
                    func_key=stats.func_key,
                    execution_count=stats.execution_count,
                    avg_time=stats.avg_time,
                    total_time=stats.total_time,
                    hot_score=hot_score,
                    detected_time=current_time,
                )
                self._hot_paths[stats.func_key] = hot_path

    def _calculate_hot_score(self, stats: FunctionStats) -> float:
        """Calculate hot score for a function"""
        # Score based on execution frequency and total time
        frequency_score = min(1.0, stats.execution_count / 1000.0)
        time_score = min(1.0, stats.total_time / 10.0)

        # Combine scores
        return frequency_score * 0.6 + time_score * 0.4

    def get_hot_paths(self, limit: int | None = None) -> list[HotPath]:
        """Get current hot paths"""
        with self._hot_paths_lock:
            hot_paths = list(self._hot_paths.values())
            hot_paths.sort(key=lambda hp: hp.hot_score, reverse=True)

            return hot_paths[:limit] if limit else hot_paths

    def get_function_stats(self, func_key: str) -> FunctionStats | None:
        """Get statistics for a specific function"""
        with self._stats_lock:
            return self._function_stats.get(func_key)

    def is_hot_path(self, func_key: str) -> bool:
        """Check if a function is identified as a hot path"""
        with self._hot_paths_lock:
            return func_key in self._hot_paths

    def get_stats(self) -> dict:
        """Get hot path detector statistics"""
        with self._stats_lock:
            total_functions = len(self._function_stats)
            total_executions = sum(stats.execution_count for stats in self._function_stats.values())

        with self._hot_paths_lock:
            hot_path_count = len(self._hot_paths)

        return {
            "total_functions_tracked": total_functions,
            "total_executions": total_executions,
            "hot_paths_detected": hot_path_count,
            "detection_config": {
                "min_execution_count": self.config.min_execution_count,
                "hot_threshold_percentile": self.config.hot_threshold_percentile,
            },
        }


# Global hot path detector instance
_global_hot_path_detector: HotPathDetector | None = None


def get_hot_path_detector(**kwargs) -> HotPathDetector:
    """Get or create the global hot path detector"""
    global _global_hot_path_detector
    if _global_hot_path_detector is None:
        _global_hot_path_detector = HotPathDetector(**kwargs)
        # Note: detector.start() must be called explicitly
    return _global_hot_path_detector
