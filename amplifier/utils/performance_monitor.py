"""
Performance Monitoring and Optimization Analysis

Provides comprehensive performance tracking, bottleneck identification,
and optimization impact measurement for the Amplifier system.  # type: ignore

Key Features:  # type: ignore
- Real-time performance metrics collection
- Bottleneck identification and analysis
- Before/after comparison capabilities
- Automated performance regression detection
- Resource utilization monitoring
"""

import json
import threading
import time
from collections import deque
from collections.abc import Callable
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from typing import Any

import psutil

from .logger import get_logger

logger = get_logger(__name__)  # type: ignore


class MetricType(Enum):  # type: ignore
    """Types of performance metrics."""  # type: ignore

    THROUGHPUT = "throughput"  # Operations per second  # type: ignore
    LATENCY = "latency"  # Response time  # type: ignore
    MEMORY = "memory"  # Memory usage  # type: ignore
    CPU = "cpu"  # CPU utilization  # type: ignore
    ERROR_RATE = "error_rate"  # Error percentage  # type: ignore
    PARALLEL_EFFICIENCY = "parallel_efficiency"  # Speedup ratio  # type: ignore


@dataclass
class PerformanceMetric:  # type: ignore
    """A single performance metric measurement."""  # type: ignore

    metric_type: MetricType  # type: ignore
    value: float  # type: ignore
    unit: str  # type: ignore
    timestamp: datetime  # type: ignore
    context: dict[str, Any] = field(default_factory=dict)  # type: ignore
    tags: list[str] = field(default_factory=list)  # type: ignore


@dataclass
class PerformanceSnapshot:  # type: ignore
    """A snapshot of system performance at a point in time."""  # type: ignore

    timestamp: datetime  # type: ignore
    cpu_percent: float  # type: ignore
    memory_percent: float  # type: ignore
    memory_available_gb: float  # type: ignore
    active_threads: int  # type: ignore
    open_files: int  # type: ignore
    network_io: dict[str, int]  # type: ignore
    disk_io: dict[str, int]  # type: ignore
    custom_metrics: list[PerformanceMetric] = field(default_factory=list)  # type: ignore


@dataclass
class BenchmarkResult:  # type: ignore
    """Results of a performance benchmark."""  # type: ignore

    test_name: str  # type: ignore
    start_time: datetime  # type: ignore
    end_time: datetime  # type: ignore
    duration_seconds: float  # type: ignore
    operations_completed: int  # type: ignore
    operations_per_second: float  # type: ignore
    average_latency: float  # type: ignore
    p95_latency: float  # type: ignore
    p99_latency: float  # type: ignore
    error_count: int  # type: ignore
    success_rate: float  # type: ignore
    memory_peak_mb: float  # type: ignore
    cpu_average: float  # type: ignore
    metadata: dict[str, Any] = field(default_factory=dict)  # type: ignore


class PerformanceMonitor:  # type: ignore
    """Comprehensive performance monitoring system."""  # type: ignore

    def __init__(self, max_history: int = 1000):  # type: ignore
        self.max_history = max_history  # type: ignore
        self.snapshots: deque = deque(maxlen=max_history)  # type: ignore
        self.metrics: deque = deque(maxlen=max_history)  # type: ignore
        self.benchmarks: list[BenchmarkResult] = []  # type: ignore
        self.is_monitoring = False  # type: ignore
        self.monitor_thread: threading.Thread | None = None  # type: ignore
        self.monitor_interval = 1.0  # seconds  # type: ignore
        self.baseline_metrics: dict[str, float] = {}  # type: ignore

    def start_monitoring(self, interval: float = 1.0):  # type: ignore
        """Start continuous performance monitoring."""  # type: ignore
        if self.is_monitoring:  # type: ignore
            logger.warning("Performance monitoring already running")  # type: ignore
            return  # type: ignore

        self.monitor_interval = interval  # type: ignore
        self.is_monitoring = True  # type: ignore
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)  # type: ignore
        self.monitor_thread.start()  # type: ignore
        logger.info(f"Performance monitoring started with {interval}s interval")  # type: ignore

    def stop_monitoring(self):  # type: ignore
        """Stop continuous performance monitoring."""  # type: ignore
        if not self.is_monitoring:  # type: ignore
            return  # type: ignore

        self.is_monitoring = False  # type: ignore
        if self.monitor_thread:  # type: ignore
            self.monitor_thread.join(timeout=5.0)  # type: ignore
        logger.info("Performance monitoring stopped")  # type: ignore

    def _monitor_loop(self):  # type: ignore
        """Main monitoring loop."""  # type: ignore
        while self.is_monitoring:  # type: ignore
            try:  # type: ignore
                snapshot = self._collect_snapshot()  # type: ignore
                self.snapshots.append(snapshot)  # type: ignore
                time.sleep(self.monitor_interval)  # type: ignore
            except Exception as e:  # type: ignore
                logger.error(f"Error in performance monitoring: {e}")  # type: ignore
                time.sleep(self.monitor_interval)  # type: ignore

    def _collect_snapshot(self) -> PerformanceSnapshot:  # type: ignore
        """Collect a performance snapshot."""  # type: ignore
        # CPU and memory
        cpu_percent = psutil.cpu_percent()  # type: ignore
        memory = psutil.virtual_memory()  # type: ignore

        # Process information
        process = psutil.Process()  # type: ignore
        active_threads = process.num_threads()  # type: ignore
        open_files = len(process.open_files())  # type: ignore

        # I/O statistics
        network_io = psutil.net_io_counters()._asdict()  # type: ignore
        disk_io = psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {}  # type: ignore

        return PerformanceSnapshot(  # type: ignore
            timestamp=datetime.now(),  # type: ignore
            cpu_percent=cpu_percent,  # type: ignore
            memory_percent=memory.percent,  # type: ignore
            memory_available_gb=memory.available / (1024**3),  # type: ignore
            active_threads=active_threads,  # type: ignore
            open_files=open_files,  # type: ignore
            network_io=network_io,  # type: ignore
            disk_io=disk_io,  # type: ignore
        )

    def record_metric(
        self,
        metric_type: MetricType,  # type: ignore
        value: float,  # type: ignore
        unit: str,  # type: ignore
        context: dict[str, Any] | None = None,  # type: ignore
        tags: list[str] | None = None,  # type: ignore
    ):  # type: ignore
        """Record a custom performance metric."""  # type: ignore
        metric = PerformanceMetric(  # type: ignore
            metric_type=metric_type,  # type: ignore
            value=value,  # type: ignore
            unit=unit,  # type: ignore
            timestamp=datetime.now(),  # type: ignore
            context=context or {},  # type: ignore
            tags=tags or [],  # type: ignore
        )
        self.metrics.append(metric)  # type: ignore

    def record_throughput(self, operations: float, time_seconds: float, context: dict[str, Any] | None = None):  # type: ignore
        """Record throughput metric."""  # type: ignore
        throughput = operations / time_seconds if time_seconds > 0 else 0  # type: ignore
        self.record_metric(MetricType.THROUGHPUT, throughput, "ops/sec", context=context)  # type: ignore

    def record_latency(self, latency_ms: float, context: dict[str, Any] | None = None):  # type: ignore
        """Record latency metric."""  # type: ignore
        self.record_metric(MetricType.LATENCY, latency_ms, "ms", context=context)  # type: ignore

    def start_benchmark(self, test_name: str) -> str:  # type: ignore
        """Start a new benchmark and return benchmark ID."""  # type: ignore
        benchmark_id = f"{test_name}_{int(time.time())}"  # type: ignore

        # Store start time in a temporary structure
        if not hasattr(self, "_benchmark_starts"):  # type: ignore
            self._benchmark_starts = {}  # type: ignore

        self._benchmark_starts[benchmark_id] = {  # type: ignore
            "test_name": test_name,  # type: ignore
            "start_time": datetime.now(),  # type: ignore
            "operations": 0,  # type: ignore
            "errors": 0,  # type: ignore
            "latencies": [],  # type: ignore
            "memory_samples": [],  # type: ignore
            "cpu_samples": [],  # type: ignore
        }

        return benchmark_id  # type: ignore

    def record_benchmark_operation(self, benchmark_id: str, latency_ms: float, success: bool = True):  # type: ignore
        """Record a single benchmark operation."""  # type: ignore
        if not hasattr(self, "_benchmark_starts") or benchmark_id not in self._benchmark_starts:  # type: ignore
            logger.warning(f"Benchmark {benchmark_id} not found")  # type: ignore
            return  # type: ignore

        benchmark = self._benchmark_starts[benchmark_id]  # type: ignore
        benchmark["operations"] += 1  # type: ignore

        if success:  # type: ignore
            benchmark["latencies"].append(latency_ms)  # type: ignore
        else:  # type: ignore
            benchmark["errors"] += 1  # type: ignore

        # Sample memory and CPU
        memory = psutil.virtual_memory()  # type: ignore
        benchmark["memory_samples"].append(memory.percent)  # type: ignore
        benchmark["cpu_samples"].append(psutil.cpu_percent())  # type: ignore

    def end_benchmark(self, benchmark_id: str) -> BenchmarkResult | None:  # type: ignore
        """End a benchmark and return results."""  # type: ignore
        if not hasattr(self, "_benchmark_starts") or benchmark_id not in self._benchmark_starts:  # type: ignore
            logger.warning(f"Benchmark {benchmark_id} not found")  # type: ignore
            return None  # type: ignore

        benchmark_data = self._benchmark_starts.pop(benchmark_id)  # type: ignore
        end_time = datetime.now()  # type: ignore
        start_time = benchmark_data["start_time"]  # type: ignore
        duration = (end_time - start_time).total_seconds()  # type: ignore

        # Calculate metrics
        operations = benchmark_data["operations"]  # type: ignore
        errors = benchmark_data["errors"]  # type: ignore
        latencies = benchmark_data["latencies"]  # type: ignore

        if operations == 0:  # type: ignore
            logger.warning(f"No operations recorded for benchmark {benchmark_id}")  # type: ignore
            return None  # type: ignore

        operations_per_second = operations / duration if duration > 0 else 0  # type: ignore
        success_rate = (operations - errors) / operations * 100  # type: ignore

        # Calculate latency percentiles
        if latencies:  # type: ignore
            average_latency = sum(latencies) / len(latencies)  # type: ignore
            sorted_latencies = sorted(latencies)  # type: ignore
            p95_index = int(len(sorted_latencies) * 0.95)  # type: ignore
            p99_index = int(len(sorted_latencies) * 0.99)  # type: ignore
            p95_latency = sorted_latencies[min(p95_index, len(sorted_latencies) - 1)]  # type: ignore
            p99_latency = sorted_latencies[min(p99_index, len(sorted_latencies) - 1)]  # type: ignore
        else:  # type: ignore
            average_latency = p95_latency = p99_latency = 0  # type: ignore

        # Memory and CPU averages
        memory_peak = max(benchmark_data["memory_samples"]) if benchmark_data["memory_samples"] else 0  # type: ignore
        cpu_average = (  # type: ignore
            sum(benchmark_data["cpu_samples"]) / len(benchmark_data["cpu_samples"])
            if benchmark_data["cpu_samples"]
            else 0
        )

        result = BenchmarkResult(  # type: ignore
            test_name=benchmark_data["test_name"],  # type: ignore
            start_time=start_time,  # type: ignore
            end_time=end_time,  # type: ignore
            duration_seconds=duration,  # type: ignore
            operations_completed=operations,  # type: ignore
            operations_per_second=operations_per_second,  # type: ignore
            average_latency=average_latency,  # type: ignore
            p95_latency=p95_latency,  # type: ignore
            p99_latency=p99_latency,  # type: ignore
            error_count=errors,  # type: ignore
            success_rate=success_rate,  # type: ignore
            memory_peak_mb=memory_peak,  # type: ignore
            cpu_average=cpu_average,  # type: ignore
            metadata={"benchmark_id": benchmark_id},  # type: ignore
        )

        self.benchmarks.append(result)  # type: ignore
        logger.info(  # type: ignore
            f"Benchmark completed: {operations} ops in {duration:.2f}s, "  # type: ignore
            f"{operations_per_second:.2f} ops/sec, {success_rate:.1f}% success"  # type: ignore
        )

        return result  # type: ignore

    def get_recent_metrics(
        self,
        metric_type: MetricType | None = None,
        minutes: int = 5,
        tags: list[str] | None = None,  # type: ignore
    ) -> list[PerformanceMetric]:  # type: ignore
        """Get recent metrics filtered by type and time."""  # type: ignore
        cutoff_time = datetime.now() - timedelta(minutes=minutes)  # type: ignore

        filtered_metrics = []  # type: ignore
        for metric in self.metrics:  # type: ignore
            if metric.timestamp < cutoff_time:  # type: ignore
                continue
            if metric_type and metric.metric_type != metric_type:  # type: ignore
                continue
            if tags and not any(tag in metric.tags for tag in tags):  # type: ignore
                continue
            filtered_metrics.append(metric)  # type: ignore

        return filtered_metrics  # type: ignore

    def get_performance_summary(self, minutes: int = 5) -> dict[str, Any]:  # type: ignore
        """Get a summary of recent performance."""  # type: ignore
        recent_snapshots = [s for s in self.snapshots if s.timestamp > datetime.now() - timedelta(minutes=minutes)]  # type: ignore

        if not recent_snapshots:  # type: ignore
            return {"message": "No recent data available"}  # type: ignore

        # Calculate averages
        avg_cpu = sum(s.cpu_percent for s in recent_snapshots) / len(recent_snapshots)  # type: ignore
        avg_memory = sum(s.memory_percent for s in recent_snapshots) / len(recent_snapshots)  # type: ignore

        # Calculate throughput metrics
        throughput_metrics = self.get_recent_metrics(MetricType.THROUGHPUT, minutes)  # type: ignore
        avg_throughput = sum(m.value for m in throughput_metrics) / len(throughput_metrics) if throughput_metrics else 0  # type: ignore

        # Calculate latency metrics
        latency_metrics = self.get_recent_metrics(MetricType.LATENCY, minutes)  # type: ignore
        avg_latency = sum(m.value for m in latency_metrics) / len(latency_metrics) if latency_metrics else 0  # type: ignore

        return {  # type: ignore
            "time_period_minutes": minutes,  # type: ignore
            "snapshot_count": len(recent_snapshots),  # type: ignore
            "cpu": {  # type: ignore
                "average_percent": avg_cpu,  # type: ignore
                "peak_percent": max(s.cpu_percent for s in recent_snapshots),  # type: ignore
                "current_percent": recent_snapshots[-1].cpu_percent if recent_snapshots else 0,  # type: ignore
            },
            "memory": {  # type: ignore
                "average_percent": avg_memory,  # type: ignore
                "peak_percent": max(s.memory_percent for s in recent_snapshots),  # type: ignore
                "current_percent": recent_snapshots[-1].memory_percent if recent_snapshots else 0,  # type: ignore
                "available_gb": recent_snapshots[-1].memory_available_gb if recent_snapshots else 0,  # type: ignore
            },
            "performance": {  # type: ignore
                "average_throughput_ops_per_sec": avg_throughput,  # type: ignore
                "average_latency_ms": avg_latency,  # type: ignore
                "throughput_samples": len(throughput_metrics),  # type: ignore
                "latency_samples": len(latency_metrics),  # type: ignore
            },
        }

    def compare_benchmarks(self, test_name: str) -> dict[str, Any]:  # type: ignore
        """Compare benchmarks for the same test over time."""  # type: ignore
        test_benchmarks = [b for b in self.benchmarks if b.test_name == test_name]  # type: ignore

        if len(test_benchmarks) < 2:  # type: ignore
            return {"message": f"Need at least 2 benchmarks for {test_name}"}  # type: ignore

        # Sort by start time
        test_benchmarks.sort(key=lambda b: b.start_time)  # type: ignore

        latest = test_benchmarks[-1]  # type: ignore
        previous = test_benchmarks[-2]  # type: ignore

        # Calculate improvements
        throughput_improvement = (  # type: ignore
            ((latest.operations_per_second - previous.operations_per_second) / previous.operations_per_second * 100)  # type: ignore
            if previous.operations_per_second > 0  # type: ignore
            else 0
        )

        latency_improvement = (  # type: ignore
            ((previous.average_latency - latest.average_latency) / previous.average_latency * 100)  # type: ignore
            if previous.average_latency > 0  # type: ignore
            else 0
        )

        return {  # type: ignore
            "test_name": test_name,  # type: ignore
            "comparison_period": {"previous": previous.start_time.isoformat(), "latest": latest.start_time.isoformat()},  # type: ignore
            "throughput": {  # type: ignore
                "previous_ops_per_sec": previous.operations_per_second,  # type: ignore
                "latest_ops_per_sec": latest.operations_per_second,  # type: ignore
                "improvement_percent": throughput_improvement,  # type: ignore
            },
            "latency": {  # type: ignore
                "previous_avg_ms": previous.average_latency,  # type: ignore
                "latest_avg_ms": latest.average_latency,  # type: ignore
                "improvement_percent": latency_improvement,  # type: ignore
            },
            "success_rate": {  # type: ignore
                "previous_percent": previous.success_rate,  # type: ignore
                "latest_percent": latest.success_rate,  # type: ignore
                "change_percent": latest.success_rate - previous.success_rate,  # type: ignore
            },
        }

    def identify_bottlenecks(self, minutes: int = 5) -> list[dict[str, Any]]:  # type: ignore
        """Identify performance bottlenecks from recent data."""  # type: ignore
        bottlenecks = []  # type: ignore
        summary = self.get_performance_summary(minutes)  # type: ignore

        # High CPU usage
        if summary["cpu"]["average_percent"] > 80:  # type: ignore
            bottlenecks.append(  # type: ignore
                {
                    "type": "high_cpu",  # type: ignore
                    "severity": "high" if summary["cpu"]["average_percent"] > 90 else "medium",  # type: ignore
                    "value": summary["cpu"]["average_percent"],  # type: ignore
                    "description": f"CPU usage at {summary['cpu']['average_percent']:.1f}%",  # type: ignore
                    "recommendation": "Consider optimizing CPU-intensive operations or adding more workers",  # type: ignore
                }
            )

        # High memory usage
        if summary["memory"]["average_percent"] > 85:  # type: ignore
            bottlenecks.append(  # type: ignore
                {
                    "type": "high_memory",  # type: ignore
                    "severity": "high" if summary["memory"]["average_percent"] > 95 else "medium",  # type: ignore
                    "value": summary["memory"]["average_percent"],  # type: ignore
                    "description": f"Memory usage at {summary['memory']['average_percent']:.1f}%",  # type: ignore
                    "recommendation": "Check for memory leaks or optimize data structures",  # type: ignore
                }
            )

        # Low throughput
        if summary["performance"]["average_throughput_ops_per_sec"] < 1.0:  # type: ignore
            bottlenecks.append(  # type: ignore
                {
                    "type": "low_throughput",  # type: ignore
                    "severity": "medium",  # type: ignore
                    "value": summary["performance"]["average_throughput_ops_per_sec"],  # type: ignore
                    "description": f"Low throughput at {summary['performance']['average_throughput_ops_per_sec']:.2f} ops/sec",  # type: ignore
                    "recommendation": "Consider parallel processing or optimizing algorithms",  # type: ignore
                }
            )

        # High latency
        if summary["performance"]["average_latency_ms"] > 1000:  # type: ignore
            bottlenecks.append(  # type: ignore
                {
                    "type": "high_latency",  # type: ignore
                    "severity": "high" if summary["performance"]["average_latency_ms"] > 5000 else "medium",  # type: ignore
                    "value": summary["performance"]["average_latency_ms"],  # type: ignore
                    "description": f"High latency at {summary['performance']['average_latency_ms']:.1f}ms",  # type: ignore
                    "recommendation": "Investigate slow operations and consider caching or optimization",  # type: ignore
                }
            )

        return bottlenecks  # type: ignore

    def export_metrics(self, filename: str, format: str = "json"):  # type: ignore
        """Export performance metrics to file."""  # type: ignore
        data = {  # type: ignore
            "export_timestamp": datetime.now().isoformat(),  # type: ignore
            "benchmarks": [  # type: ignore
                {
                    "test_name": b.test_name,  # type: ignore
                    "start_time": b.start_time.isoformat(),  # type: ignore
                    "duration_seconds": b.duration_seconds,  # type: ignore
                    "operations_per_second": b.operations_per_second,  # type: ignore
                    "average_latency_ms": b.average_latency,  # type: ignore
                    "success_rate": b.success_rate,  # type: ignore
                    "memory_peak_mb": b.memory_peak_mb,  # type: ignore
                    "cpu_average": b.cpu_average,  # type: ignore
                }
                for b in self.benchmarks  # type: ignore
            ],
            "recent_summary": self.get_performance_summary(60),  # Last hour  # type: ignore
        }

        if format.lower() == "json":  # type: ignore
            with open(filename, "w") as f:  # type: ignore
                json.dump(data, f, indent=2)  # type: ignore
        else:  # type: ignore
            raise ValueError(f"Unsupported export format: {format}")  # type: ignore

        logger.info(f"Performance metrics exported to {filename}")  # type: ignore

    def set_baseline(self, metric_name: str, value: float):  # type: ignore
        """Set a baseline metric for comparison."""  # type: ignore
        self.baseline_metrics[metric_name] = value  # type: ignore
        logger.info(f"Baseline set: {metric_name} = {value}")  # type: ignore

    def compare_to_baseline(self, metric_name: str, current_value: float) -> dict[str, Any]:  # type: ignore
        """Compare current metric to baseline."""  # type: ignore
        if metric_name not in self.baseline_metrics:  # type: ignore
            return {"error": f"No baseline found for {metric_name}"}  # type: ignore

        baseline = self.baseline_metrics[metric_name]  # type: ignore
        change = current_value - baseline  # type: ignore
        change_percent = (change / baseline) * 100 if baseline != 0 else 0  # type: ignore

        return {  # type: ignore
            "metric": metric_name,  # type: ignore
            "baseline": baseline,  # type: ignore
            "current": current_value,  # type: ignore
            "change": change,  # type: ignore
            "change_percent": change_percent,  # type: ignore
            "improvement": change_percent < 0  # type: ignore
            if "latency" in metric_name or "memory" in metric_name
            else change_percent > 0,
        }


# Global performance monitor instance
_performance_monitor = None  # type: ignore


def get_performance_monitor() -> PerformanceMonitor:  # type: ignore
    """Get the global performance monitor instance."""  # type: ignore
    global _performance_monitor
    if _performance_monitor is None:  # type: ignore
        _performance_monitor = PerformanceMonitor()  # type: ignore
    return _performance_monitor  # type: ignore


def benchmark_function(test_name: str, func: Callable, *args, **kwargs) -> BenchmarkResult:  # type: ignore
    """Convenience function to benchmark a function call."""  # type: ignore
    monitor = get_performance_monitor()  # type: ignore
    benchmark_id = monitor.start_benchmark(test_name)  # type: ignore

    start_time = time.time()  # type: ignore
    try:  # type: ignore
        func(*args, **kwargs)
        end_time = time.time()  # type: ignore

        # Record as single operation
        latency_ms = (end_time - start_time) * 1000  # type: ignore
        monitor.record_benchmark_operation(benchmark_id, latency_ms, success=True)  # type: ignore

    except Exception:  # type: ignore
        end_time = time.time()  # type: ignore
        latency_ms = (end_time - start_time) * 1000  # type: ignore
        monitor.record_benchmark_operation(benchmark_id, latency_ms, success=False)  # type: ignore
        raise
    finally:  # type: ignore
        benchmark_result = monitor.end_benchmark(benchmark_id)  # type: ignore

    return benchmark_result  # type: ignore


async def benchmark_async_function(test_name: str, func: Callable, *args, **kwargs) -> BenchmarkResult:  # type: ignore
    """Convenience function to benchmark an async function call."""  # type: ignore
    monitor = get_performance_monitor()  # type: ignore
    benchmark_id = monitor.start_benchmark(test_name)  # type: ignore

    start_time = time.time()  # type: ignore
    try:  # type: ignore
        await func(*args, **kwargs)  # type: ignore
        end_time = time.time()  # type: ignore

        # Record as single operation
        latency_ms = (end_time - start_time) * 1000  # type: ignore
        monitor.record_benchmark_operation(benchmark_id, latency_ms, success=True)  # type: ignore

    except Exception:  # type: ignore
        end_time = time.time()  # type: ignore
        latency_ms = (end_time - start_time) * 1000  # type: ignore
        monitor.record_benchmark_operation(benchmark_id, latency_ms, success=False)  # type: ignore
        raise
    finally:  # type: ignore
        benchmark_result = monitor.end_benchmark(benchmark_id)  # type: ignore

    return benchmark_result  # type: ignore
