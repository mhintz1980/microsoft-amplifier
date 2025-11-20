"""
Real-time Memory Usage Monitoring

Comprehensive memory tracking and analysis system with pressure detection,
leak detection, and performance metrics collection.
"""

import asyncio
import sys
import threading
import time
from collections import defaultdict
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from enum import Enum

import psutil

from .arena_allocator import get_arena_allocator


class MemoryPressureLevel(Enum):
    """Memory pressure levels for adaptive behavior"""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class MemorySnapshot:
    """A snapshot of memory usage at a point in time"""

    timestamp: float
    total_mb: float
    available_mb: float
    used_mb: float
    percent: float
    arena_usage_mb: float
    arena_efficiency: float
    gc_pressure: float
    process_memory_mb: float
    system_load: float


@dataclass
class MemoryLeakInfo:
    """Information about potential memory leaks"""

    object_type: str
    growth_rate: float  # MB per minute
    current_size: float  # MB
    confidence: float
    first_detected: float
    last_detected: float


@dataclass
class MemoryStats:
    """Statistics for memory monitoring"""

    snapshots_count: int = 0
    avg_usage_percent: float = 0.0
    peak_usage_mb: float = 0.0
    peak_pressure: float = 0.0
    leak_detections: int = 0
    efficiency_score: float = 0.0
    allocation_rate: float = 0.0
    deallocation_rate: float = 0.0


class MemoryMonitor:
    """Real-time memory usage monitoring and analysis"""

    def __init__(
        self,
        snapshot_interval: float = 1.0,
        history_size: int = 300,  # 5 minutes of history at 1s intervals
        leak_detection_window: float = 300.0,  # 5 minutes
        pressure_thresholds: dict[str, float] | None = None,
    ):
        self.snapshot_interval = snapshot_interval
        self.history_size = history_size
        self.leak_detection_window = leak_detection_window

        # Pressure thresholds
        self.pressure_thresholds = pressure_thresholds or {"medium": 0.6, "high": 0.8, "critical": 0.95}

        # Memory tracking
        self._snapshots: deque = deque(maxlen=history_size)
        self._object_counts: dict[str, list[tuple[float, int]]] = defaultdict(list)
        self._allocation_events: deque = deque(maxlen=1000)
        self._deallocation_events: deque = deque(maxlen=1000)

        # Leak detection
        self._potential_leaks: dict[str, MemoryLeakInfo] = {}
        self._baseline_counts: dict[str, int] = {}

        # Statistics
        self._stats = MemoryStats()
        self._stats_lock = threading.Lock()

        # Monitoring state
        self._monitoring = False
        self._monitor_task: asyncio.Task | None = None
        self._monitor_lock = threading.Lock()

        # Process and system info
        self._process = psutil.Process()
        self._system_memory = psutil.virtual_memory()

        # Arena allocator reference
        self._arena = get_arena_allocator()

        # Thread pool for intensive operations
        self._executor = ThreadPoolExecutor(max_workers=2)

    def start_monitoring(self):
        """Start real-time memory monitoring"""
        with self._monitor_lock:
            if not self._monitoring:
                self._monitoring = True
                self._monitor_task = asyncio.create_task(self._monitoring_loop())

    def stop_monitoring(self):
        """Stop memory monitoring"""
        with self._monitor_lock:
            self._monitoring = False
            if self._monitor_task and not self._monitor_task.done():
                self._monitor_task.cancel()
                try:
                    asyncio.run(self._monitor_task)
                except asyncio.CancelledError:
                    pass

    async def _monitoring_loop(self):
        """Main monitoring loop"""
        while self._monitoring:
            try:
                snapshot = await self._take_snapshot()
                await self._process_snapshot(snapshot)
                await asyncio.sleep(self.snapshot_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Memory monitoring error: {e}")
                await asyncio.sleep(1.0)

    async def _take_snapshot(self) -> MemorySnapshot:
        """Take a memory usage snapshot"""
        current_time = time.time()

        # Get system memory info
        system_memory = psutil.virtual_memory()
        process_memory = self._process.memory_info()

        # Get arena info
        arena_stats = self._arena.get_stats()
        arena_usage_mb = arena_stats.bytes_allocated / (1024 * 1024)
        arena_efficiency = self._arena.get_hash_consing_efficiency()

        # Calculate GC pressure (simplified)
        gc_pressure = self._calculate_gc_pressure()

        # Get system load
        system_load = psutil.cpu_percent() / 100.0

        return MemorySnapshot(
            timestamp=current_time,
            total_mb=system_memory.total / (1024 * 1024),
            available_mb=system_memory.available / (1024 * 1024),
            used_mb=system_memory.used / (1024 * 1024),
            percent=system_memory.percent,
            arena_usage_mb=arena_usage_mb,
            arena_efficiency=arena_efficiency,
            gc_pressure=gc_pressure,
            process_memory_mb=process_memory.rss / (1024 * 1024),
            system_load=system_load,
        )

    async def _process_snapshot(self, snapshot: MemorySnapshot):
        """Process a memory snapshot and update statistics"""
        # Store snapshot
        self._snapshots.append(snapshot)

        # Track object counts (simplified - would need actual object tracking)
        await self._track_object_counts(snapshot.timestamp)

        # Update statistics
        await self._update_statistics(snapshot)

        # Check for memory leaks
        await self._detect_memory_leaks()

    async def _track_object_counts(self, timestamp: float):
        """Track object counts for leak detection"""
        # Get current object counts (simplified)
        try:
            # In a real implementation, this would track specific object types
            # For now, we'll track general Python object counts
            frame = sys._current_frames().values()
            total_objects = sum(len(f.f_locals) for f in frame)

            # Track general "objects" category
            self._object_counts["objects"].append((timestamp, total_objects))

            # Keep only recent history
            cutoff_time = timestamp - self.leak_detection_window
            self._object_counts["objects"] = [(t, c) for t, c in self._object_counts["objects"] if t >= cutoff_time]

        except Exception:
            pass  # Error in object counting is not critical

    def _calculate_gc_pressure(self) -> float:
        """Calculate garbage collection pressure"""
        try:
            # Get Python GC stats
            gc_stats = [
                {"count": stat[0], "collected": stat[2], "uncollectable": stat[3]}
                for stat in sys.getstats()[1:]  # Skip the first (internal) stat
            ]

            total_pressure = 0.0
            for gen_stat in gc_stats:
                if gen_stat["collected"] > 0:
                    # Pressure based on collection frequency
                    pressure = min(1.0, gen_stat["count"] / 100.0)  # Normalize by expected count
                    total_pressure += pressure

            return min(1.0, total_pressure / len(gc_stats)) if gc_stats else 0.0

        except:
            return 0.0

    async def _update_statistics(self, snapshot: MemorySnapshot):
        """Update monitoring statistics"""
        with self._stats_lock:
            self._stats.snapshots_count += 1

            # Update average usage
            total_usage = sum(s.percent for s in self._snapshots)
            self._stats.avg_usage_percent = total_usage / len(self._snapshots)

            # Update peak usage
            self._stats.peak_usage_mb = max(self._stats.peak_usage_mb, snapshot.used_mb)

            # Update peak pressure
            current_pressure = self.get_memory_pressure()
            self._stats.peak_pressure = max(self._stats.peak_pressure, current_pressure)

            # Calculate efficiency score
            if snapshot.arena_efficiency > 0:
                self._stats.efficiency_score = snapshot.arena_efficiency

    async def _detect_memory_leaks(self):
        """Detect potential memory leaks based on object count trends"""
        current_time = time.time()

        for obj_type, counts in self._object_counts.items():
            if len(counts) < 10:  # Need enough data points
                continue

            # Analyze growth trend
            times = [t for t, c in counts]
            values = [c for t, c in counts]

            # Simple linear regression to detect growth
            if len(times) >= 2:
                time_span = times[-1] - times[0]
                if time_span > 0:
                    growth_rate = (values[-1] - values[0]) / time_span

                    # Check if growth is significant
                    if growth_rate > 0.1:  # Growing
                        confidence = min(1.0, growth_rate / 10.0)

                        leak_info = MemoryLeakInfo(
                            object_type=obj_type,
                            growth_rate=growth_rate * 60,  # Convert to per minute
                            current_size=values[-1],
                            confidence=confidence,
                            first_detected=times[0],
                            last_detected=times[-1],
                        )

                        self._potential_leaks[obj_type] = leak_info

                        with self._stats_lock:
                            self._stats.leak_detections += 1

    def record_allocation(self, size_bytes: int, obj_type: str = "unknown"):
        """Record a memory allocation event"""
        event = (time.time(), size_bytes, obj_type)
        self._allocation_events.append(event)

    def record_deallocation(self, size_bytes: int, obj_type: str = "unknown"):
        """Record a memory deallocation event"""
        event = (time.time(), size_bytes, obj_type)
        self._deallocation_events.append(event)

    def get_memory_pressure(self) -> float:
        """Get current memory pressure (0.0 to 1.0)"""
        if not self._snapshots:
            return 0.0

        latest = self._snapshots[-1]
        return latest.percent / 100.0

    def get_pressure_level(self) -> MemoryPressureLevel:
        """Get current memory pressure level"""
        pressure = self.get_memory_pressure()

        if pressure >= self.pressure_thresholds["critical"]:
            return MemoryPressureLevel.CRITICAL
        if pressure >= self.pressure_thresholds["high"]:
            return MemoryPressureLevel.HIGH
        if pressure >= self.pressure_thresholds["medium"]:
            return MemoryPressureLevel.MEDIUM
        return MemoryPressureLevel.LOW

    def get_memory_trend(self, window_minutes: float = 5.0) -> tuple[float, float]:
        """Get memory usage trend over the specified window"""
        if not self._snapshots:
            return 0.0, 0.0

        cutoff_time = time.time() - (window_minutes * 60)
        recent_snapshots = [s for s in self._snapshots if s.timestamp >= cutoff_time]

        if len(recent_snapshots) < 2:
            return 0.0, 0.0

        # Calculate trend (change per minute)
        time_span = recent_snapshots[-1].timestamp - recent_snapshots[0].timestamp
        usage_change = recent_snapshots[-1].percent - recent_snapshots[0].percent

        trend_per_minute = (usage_change / time_span) * 60 if time_span > 0 else 0.0

        # Calculate growth rate
        growth_rate = (recent_snapshots[-1].percent / recent_snapshots[0].percent) - 1.0

        return trend_per_minute, growth_rate

    def get_efficiency_metrics(self) -> dict[str, float]:
        """Get memory efficiency metrics"""
        if not self._snapshots:
            return {}

        latest = self._snapshots[-1]

        # Calculate allocation/deallocation rates
        current_time = time.time()
        recent_allocations = [
            size
            for t, size, _ in self._allocation_events
            if current_time - t <= 60.0  # Last minute
        ]
        recent_deallocations = [
            size
            for t, size, _ in self._deallocation_events
            if current_time - t <= 60.0  # Last minute
        ]

        allocation_rate_mb_per_min = sum(recent_allocations) / (1024 * 1024)
        deallocation_rate_mb_per_min = sum(recent_deallocations) / (1024 * 1024)

        return {
            "arena_efficiency": latest.arena_efficiency,
            "memory_pressure": self.get_memory_pressure(),
            "gc_pressure": latest.gc_pressure,
            "allocation_rate_mb_per_min": allocation_rate_mb_per_min,
            "deallocation_rate_mb_per_min": deallocation_rate_mb_per_min,
            "net_growth_rate_mb_per_min": allocation_rate_mb_per_min - deallocation_rate_mb_per_min,
            "fragmentation_estimate": self._estimate_fragmentation(),
        }

    def _estimate_fragmentation(self) -> float:
        """Estimate memory fragmentation"""
        try:
            # Use arena allocator's fragmentation ratio
            arena_stats = self._arena.get_stats()
            return arena_stats.fragmentation_ratio
        except:
            return 0.0

    def get_potential_leaks(self) -> list[MemoryLeakInfo]:
        """Get list of potential memory leaks"""
        # Filter for high-confidence leaks
        return [leak for leak in self._potential_leaks.values() if leak.confidence > 0.5 and leak.growth_rate > 1.0]

    def get_stats(self) -> MemoryStats:
        """Get current monitoring statistics"""
        with self._stats_lock:
            # Calculate current allocation/deallocation rates
            current_time = time.time()
            recent_allocations = len([e for e in self._allocation_events if current_time - e[0] <= 60.0])
            recent_deallocations = len([e for e in self._deallocation_events if current_time - e[0] <= 60.0])

            self._stats.allocation_rate = recent_allocations / 60.0
            self._stats.deallocation_rate = recent_deallocations / 60.0

            return MemoryStats(
                snapshots_count=self._stats.snapshots_count,
                avg_usage_percent=self._stats.avg_usage_percent,
                peak_usage_mb=self._stats.peak_usage_mb,
                peak_pressure=self._stats.peak_pressure,
                leak_detections=self._stats.leak_detections,
                efficiency_score=self._stats.efficiency_score,
                allocation_rate=self._stats.allocation_rate,
                deallocation_rate=self._stats.deallocation_rate,
            )

    def get_memory_recommendations(self) -> list[str]:
        """Get memory optimization recommendations"""
        recommendations = []
        pressure_level = self.get_pressure_level()
        efficiency = self.get_efficiency_metrics()

        # Pressure-based recommendations
        if pressure_level == MemoryPressureLevel.CRITICAL:
            recommendations.append("CRITICAL: Immediate garbage collection required")
            recommendations.append("Consider increasing memory limits or reducing load")
        elif pressure_level == MemoryPressureLevel.HIGH:
            recommendations.append("HIGH: Frequent garbage collection recommended")
            recommendations.append("Monitor for memory leaks")

        # Efficiency-based recommendations
        if efficiency.get("arena_efficiency", 0) < 0.5:
            recommendations.append("Low arena efficiency - consider enabling hash-consing")

        if efficiency.get("fragmentation_estimate", 0) > 0.3:
            recommendations.append("High fragmentation detected - consider memory compaction")

        # Leak-based recommendations
        leaks = self.get_potential_leaks()
        if leaks:
            recommendations.append(f"Memory leaks detected: {len(leaks)} potential leaks")
            for leak in leaks[:3]:  # Top 3 leaks
                recommendations.append(f"- {leak.object_type}: growing at {leak.growth_rate:.1f}/min")

        # Trend-based recommendations
        trend, growth = self.get_memory_trend()
        if trend > 5.0:  # Growing fast
            recommendations.append("Rapid memory growth detected - investigate immediately")
        elif trend > 1.0:
            recommendations.append("Moderate memory growth - monitor closely")

        return recommendations

    def shutdown(self):
        """Cleanup monitoring resources"""
        self.stop_monitoring()

        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)

        self._snapshots.clear()
        self._object_counts.clear()
        self._allocation_events.clear()
        self._deallocation_events.clear()
        self._potential_leaks.clear()


# Global memory monitor instance
_global_monitor: MemoryMonitor | None = None


def get_memory_monitor(**kwargs) -> MemoryMonitor:
    """Get or create the global memory monitor"""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = MemoryMonitor(**kwargs)
        _global_monitor.start_monitoring()
    return _global_monitor


def get_memory_pressure() -> float:
    """Convenience function to get current memory pressure"""
    return get_memory_monitor().get_memory_pressure()
