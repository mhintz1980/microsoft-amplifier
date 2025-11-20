"""
High-Performance Garbage Collector

Efficient cleanup and recycling system with generational collection,
reference counting, and memory pressure management.
"""

import asyncio
import gc as python_gc
import os
import sys
import threading
import time
import traceback
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field
from typing import Any
from weakref import WeakRef
from weakref import WeakSet
from weakref import finalize

from .arena_allocator import get_arena_allocator
from .memory_monitor import get_memory_monitor


@dataclass
class GCConfig:
    """Configuration for garbage collector behavior"""

    # Generation thresholds
    young_gen_threshold: int = 100
    old_gen_threshold: int = 1000
    tenure_age: int = 10

    # Collection intervals
    minor_gc_interval: float = 1.0  # seconds
    major_gc_interval: float = 10.0  # seconds
    full_gc_interval: float = 60.0  # seconds

    # Memory pressure triggers
    memory_pressure_threshold: float = 0.8
    emergency_gc_threshold: float = 0.95
    gc_cpu_limit: float = 0.2  # Max 20% CPU for GC

    # Performance tuning
    parallel_workers: int = os.cpu_count() or 4
    batch_size: int = 1000
    max_collection_time: float = 5.0

    # Object lifecycle
    finalizer_timeout: float = 30.0
    weak_ref_tracking: bool = True
    object_tracking: bool = True


@dataclass
class GCStats:
    """Statistics for garbage collection performance"""

    total_collections: int = 0
    minor_collections: int = 0
    major_collections: int = 0
    full_collections: int = 0
    emergency_collections: int = 0

    objects_collected: int = 0
    bytes_collected: int = 0
    collection_time_ms: float = 0.0
    cpu_usage_ratio: float = 0.0

    generational_stats: dict[str, int] = field(default_factory=lambda: {"young_gen": 0, "old_gen": 0, "survivors": 0})


@dataclass
class TrackedObject:
    """Tracked object for GC management"""

    obj_id: int
    obj_type: type
    size_bytes: int
    creation_time: float
    last_access_time: float
    access_count: int
    generation: int = 0  # 0 = young, 1 = old
    weak_refs: set[WeakRef] = field(default_factory=set)
    finalizer: finalize | None = None
    marked: bool = False  # For mark-and-sweep


class GenerationalGC:
    """High-performance generational garbage collector"""

    def __init__(self, config: GCConfig | None = None):
        self.config = config or GCConfig()
        self._arena = get_arena_allocator()
        self._monitor = get_memory_monitor()

        # Object tracking
        self._young_generation: dict[int, TrackedObject] = {}
        self._old_generation: dict[int, TrackedObject] = {}
        self._object_registry: dict[int, TrackedObject] = {}
        self._weak_refs: dict[int, WeakSet] = defaultdict(WeakSet)

        # Collection state
        self._collecting = False
        self._collection_lock = threading.Lock()
        self._stats = GCStats()
        self._stats_lock = threading.Lock()

        # Threading
        self._executor = ThreadPoolExecutor(max_workers=self.config.parallel_workers)
        self._gc_tasks: list[asyncio.Task] = []

        # Collection scheduling
        self._last_minor_gc = 0.0
        self._last_major_gc = 0.0
        self._last_full_gc = 0.0

        # Memory pressure monitoring
        self._memory_pressure = 0.0
        self._emergency_mode = False

        # Start collection tasks
        self._start_collection_tasks()

    def track_object(self, obj: Any) -> int:
        """Start tracking an object for garbage collection"""
        if not self.config.object_tracking:
            return id(obj)

        obj_id = id(obj)
        current_time = time.time()

        # Estimate object size
        try:
            size_bytes = sys.getsizeof(obj)
        except:
            size_bytes = 64  # Default estimate

        tracked_obj = TrackedObject(
            obj_id=obj_id,
            obj_type=type(obj),
            size_bytes=size_bytes,
            creation_time=current_time,
            last_access_time=current_time,
            access_count=1,
        )

        # Add to young generation
        self._young_generation[obj_id] = tracked_obj
        self._object_registry[obj_id] = tracked_obj

        # Set up finalizer
        if self.config.weak_ref_tracking:
            try:
                tracked_obj.finalizer = finalize(obj, self._on_object_finalize, obj_id)
            except:
                pass  # Some objects can't be finalized

        return obj_id

    def access_object(self, obj_id: int):
        """Record object access for generational promotion"""
        if obj_id in self._object_registry:
            tracked_obj = self._object_registry[obj_id]
            tracked_obj.last_access_time = time.time()
            tracked_obj.access_count += 1

    def _on_object_finalize(self, obj_id: int):
        """Callback when object is finalized"""
        if obj_id in self._object_registry:
            self._remove_tracked_object(obj_id)

    def _remove_tracked_object(self, obj_id: int):
        """Remove object from all tracking structures"""
        tracked_obj = self._object_registry.get(obj_id)
        if not tracked_obj:
            return

        # Remove from appropriate generation
        if obj_id in self._young_generation:
            del self._young_generation[obj_id]
        elif obj_id in self._old_generation:
            del self._old_generation[obj_id]

        # Remove from registry and weak refs
        del self._object_registry[obj_id]
        if obj_id in self._weak_refs:
            del self._weak_refs[obj_id]

        # Update statistics
        with self._stats_lock:
            self._stats.objects_collected += 1
            self._stats.bytes_collected += tracked_obj.size_bytes

    def _start_collection_tasks(self):
        """Start background garbage collection tasks"""
        # Minor GC task
        minor_task = asyncio.create_task(self._minor_gc_loop())
        self._gc_tasks.append(minor_task)

        # Major GC task
        major_task = asyncio.create_task(self._major_gc_loop())
        self._gc_tasks.append(major_task)

        # Full GC task
        full_task = asyncio.create_task(self._full_gc_loop())
        self._gc_tasks.append(full_task)

        # Emergency GC monitoring
        emergency_task = asyncio.create_task(self._emergency_gc_loop())
        self._gc_tasks.append(emergency_task)

    async def _minor_gc_loop(self):
        """Background loop for minor garbage collection"""
        while True:
            try:
                await asyncio.sleep(self.config.minor_gc_interval)
                await self._run_minor_gc()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Minor GC error: {e}")
                traceback.print_exc()

    async def _major_gc_loop(self):
        """Background loop for major garbage collection"""
        while True:
            try:
                await asyncio.sleep(self.config.major_gc_interval)
                await self._run_major_gc()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Major GC error: {e}")
                traceback.print_exc()

    async def _full_gc_loop(self):
        """Background loop for full garbage collection"""
        while True:
            try:
                await asyncio.sleep(self.config.full_gc_interval)
                await self._run_full_gc()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Full GC error: {e}")
                traceback.print_exc()

    async def _emergency_gc_loop(self):
        """Monitor for emergency garbage collection needs"""
        while True:
            try:
                await asyncio.sleep(0.5)  # Check every 500ms
                memory_pressure = self._monitor.get_memory_pressure()

                if memory_pressure > self.config.emergency_gc_threshold:
                    await self._emergency_gc()
                elif memory_pressure > self.config.memory_pressure_threshold:
                    # Trigger more frequent collections
                    current_time = time.time()
                    if current_time - self._last_minor_gc > 0.5:
                        await self._run_minor_gc()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Emergency GC monitoring error: {e}")

    async def _run_minor_gc(self):
        """Run minor garbage collection on young generation"""
        if self._collecting:
            return

        start_time = time.time()
        current_time = start_time

        with self._collection_lock:
            self._collecting = True
            try:
                # Mark-and-sweep on young generation
                await self._mark_and_sweep_generation("young")

                # Promote survivors to old generation
                await self._promote_survivors()

                with self._stats_lock:
                    self._stats.minor_collections += 1
                    self._stats.total_collections += 1

            finally:
                self._collecting = False
                self._last_minor_gc = time.time()

        collection_time = (time.time() - start_time) * 1000
        self._update_collection_stats(collection_time)

    async def _run_major_gc(self):
        """Run major garbage collection on old generation"""
        if self._collecting:
            return

        start_time = time.time()

        with self._collection_lock:
            self._collecting = True
            try:
                # Mark-and-sweep on old generation
                await self._mark_and_sweep_generation("old")

                with self._stats_lock:
                    self._stats.major_collections += 1
                    self._stats.total_collections += 1

            finally:
                self._collecting = False
                self._last_major_gc = time.time()

        collection_time = (time.time() - start_time) * 1000
        self._update_collection_stats(collection_time)

    async def _run_full_gc(self):
        """Run full garbage collection on all generations"""
        if self._collecting:
            return

        start_time = time.time()

        with self._collection_lock:
            self._collecting = True
            try:
                # Mark-and-sweep on both generations
                await self._mark_and_sweep_generation("young")
                await self._mark_and_sweep_generation("old")

                # Run Python GC as well
                await asyncio.to_thread(python_gc.collect)

                # Clean up arena allocator
                await self._arena._run_gc_async(force=True)

                with self._stats_lock:
                    self._stats.full_collections += 1
                    self._stats.total_collections += 1

            finally:
                self._collecting = False
                self._last_full_gc = time.time()

        collection_time = (time.time() - start_time) * 1000
        self._update_collection_stats(collection_time)

    async def _emergency_gc(self):
        """Run emergency garbage collection under memory pressure"""
        if self._collecting:
            return

        start_time = time.time()

        with self._collection_lock:
            self._collecting = True
            self._emergency_mode = True
            try:
                # Aggressive collection on both generations
                await self._mark_and_sweep_generation("young", aggressive=True)
                await self._mark_and_sweep_generation("old", aggressive=True)

                # Force Python GC
                for _ in range(3):  # Run multiple times
                    await asyncio.to_thread(python_gc.collect)

                # Aggressive arena cleanup
                await self._arena._run_gc_async(force=True)

                with self._stats_lock:
                    self._stats.emergency_collections += 1
                    self._stats.total_collections += 1

            finally:
                self._collecting = False
                self._emergency_mode = False

        collection_time = (time.time() - start_time) * 1000
        self._update_collection_stats(collection_time)

    async def _mark_and_sweep_generation(self, generation: str, aggressive: bool = False):
        """Mark-and-sweep garbage collection for a specific generation"""
        if generation == "young":
            objects = self._young_generation
        elif generation == "old":
            objects = self._old_generation
        else:
            return

        # Reset marks
        for obj in objects.values():
            obj.marked = False

        # Mark phase - find reachable objects
        await self._mark_reachable_objects(objects, aggressive)

        # Sweep phase - collect unmarked objects
        to_remove = []
        for obj_id, obj in objects.items():
            if not obj.marked:
                # Check if object is actually dead (weak ref check)
                if self._is_object_dead(obj):
                    to_remove.append(obj_id)

        # Remove dead objects in parallel
        if to_remove:
            await self._remove_objects_parallel(to_remove)

    async def _mark_reachable_objects(self, objects: dict[int, TrackedObject], aggressive: bool):
        """Mark all reachable objects in the generation"""
        # Simplified reachability analysis - in practice would traverse object graphs
        current_time = time.time()
        age_threshold = 300.0 if aggressive else 3600.0  # 5 min vs 1 hour

        for obj in objects.values():
            # Mark as reachable if recently accessed or frequently accessed
            if current_time - obj.last_access_time < age_threshold or obj.access_count > 10 or aggressive:
                obj.marked = True

    def _is_object_dead(self, tracked_obj: TrackedObject) -> bool:
        """Check if a tracked object is actually dead"""
        try:
            # Check weak references
            for weak_ref in tracked_obj.weak_refs:
                if weak_ref() is not None:
                    return False
            return True
        except:
            return True  # Assume dead on error

    async def _promote_survivors(self):
        """Promote young generation objects to old generation"""
        current_time = time.time()
        age_threshold = self.config.minor_gc_interval * self.config.tenure_age

        to_promote = []
        for obj_id, obj in self._young_generation.items():
            if current_time - obj.creation_time > age_threshold or obj.access_count > 5:
                to_promote.append(obj_id)

        # Promote objects
        for obj_id in to_promote:
            if obj_id in self._young_generation:
                obj = self._young_generation[obj_id]
                obj.generation = 1  # Old generation
                self._old_generation[obj_id] = obj
                del self._young_generation[obj_id]

        with self._stats_lock:
            self._stats.generational_stats["survivors"] += len(to_promote)

    async def _remove_objects_parallel(self, obj_ids: list[int]):
        """Remove multiple objects in parallel"""
        batch_size = self.config.batch_size

        def remove_batch(batch):
            for obj_id in batch:
                self._remove_tracked_object(obj_id)

        # Process in parallel batches
        futures = []
        for i in range(0, len(obj_ids), batch_size):
            batch = obj_ids[i : i + batch_size]
            future = self._executor.submit(remove_batch, batch)
            futures.append(future)

        # Wait for all batches to complete
        for future in futures:
            future.result()

    def _update_collection_stats(self, collection_time_ms: float):
        """Update collection statistics"""
        with self._stats_lock:
            self._stats.collection_time_ms += collection_time_ms

            # Update generational stats
            self._stats.generational_stats["young_gen"] = len(self._young_generation)
            self._stats.generational_stats["old_gen"] = len(self._old_generation)

    def get_stats(self) -> GCStats:
        """Get current garbage collection statistics"""
        with self._stats_lock:
            return GCStats(
                total_collections=self._stats.total_collections,
                minor_collections=self._stats.minor_collections,
                major_collections=self._stats.major_collections,
                full_collections=self._stats.full_collections,
                emergency_collections=self._stats.emergency_collections,
                objects_collected=self._stats.objects_collected,
                bytes_collected=self._stats.bytes_collected,
                collection_time_ms=self._stats.collection_time_ms,
                cpu_usage_ratio=self._stats.cpu_usage_ratio,
                generational_stats=self._stats.generational_stats.copy(),
            )

    def get_collection_efficiency(self) -> float:
        """Calculate garbage collection efficiency"""
        stats = self.get_stats()
        if stats.total_collections == 0:
            return 0.0
        return stats.objects_collected / stats.total_collections

    def shutdown(self):
        """Cleanup garbage collector resources"""
        # Cancel all GC tasks
        for task in self._gc_tasks:
            if not task.done():
                task.cancel()

        # Wait for tasks to complete
        if self._gc_tasks:
            asyncio.run(asyncio.gather(*self._gc_tasks, return_exceptions=True))

        # Shutdown executor
        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)

        # Clear all tracked objects
        self._young_generation.clear()
        self._old_generation.clear()
        self._object_registry.clear()
        self._weak_refs.clear()


# Global GC instance
_global_gc: GenerationalGC | None = None


def get_garbage_collector(**kwargs) -> GenerationalGC:
    """Get or create the global garbage collector"""
    global _global_gc
    if _global_gc is None:
        _global_gc = GenerationalGC(**kwargs)
    return _global_gc


def track_object(obj: Any) -> int:
    """Convenience function to track an object for GC"""
    return get_garbage_collector().track_object(obj)
