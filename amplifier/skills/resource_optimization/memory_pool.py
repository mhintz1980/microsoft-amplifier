"""
Memory Pool Management

Pre-allocated buffer management for high-frequency allocation patterns
with automatic resizing and pool tier management.
"""

import asyncio
import threading
import time
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from dataclasses import field

from .arena_allocator import get_arena_allocator


@dataclass
class PoolConfig:
    """Configuration for memory pool behavior"""

    # Pool tier sizes (bytes)
    small_size: int = 1024  # 1KB
    medium_size: int = 64 * 1024  # 64KB
    large_size: int = 1024 * 1024  # 1MB

    # Pool limits
    max_small_blocks: int = 1000
    max_medium_blocks: int = 100
    max_large_blocks: int = 10

    # Growth and shrinking
    growth_factor: float = 1.5
    shrink_threshold: float = 0.3
    max_expansions: int = 5

    # Performance tuning
    preallocate_ratio: float = 0.7
    reclaim_interval: float = 30.0  # seconds
    thread_pool_size: int = 4


@dataclass
class PoolStats:
    """Statistics for memory pool performance"""

    pool_hits: int = 0
    pool_misses: int = 0
    allocations_from_pool: int = 0
    allocations_direct: int = 0
    total_pool_size: int = 0
    utilization_ratio: float = 0.0
    expansion_count: int = 0
    shrink_count: int = 0


@dataclass
class MemoryBlock:
    """A pre-allocated memory block"""

    size: int
    tier: str
    allocated: bool = False
    last_used: float = field(default_factory=time.time)
    allocation_count: int = 0
    data: bytes | None = None
    arena_offset: int | None = None


class MemoryPool:
    """High-performance memory pool with tier-based allocation"""

    def __init__(self, config: PoolConfig | None = None):
        self.config = config or PoolConfig()
        self._arena = get_arena_allocator()

        # Memory pools by tier
        self._pools: dict[str, deque] = {
            "small": deque(maxlen=self.config.max_small_blocks),
            "medium": deque(maxlen=self.config.max_medium_blocks),
            "large": deque(maxlen=self.config.max_large_blocks),
        }

        # Free blocks by tier
        self._free_blocks: dict[str, deque] = {"small": deque(), "medium": deque(), "large": deque()}

        # Block tracking
        self._blocks: dict[str, MemoryBlock] = {}
        self._tier_size_map = {
            "small": self.config.small_size,
            "medium": self.config.medium_size,
            "large": self.config.large_size,
        }

        # Statistics
        self._stats = PoolStats()
        self._stats_lock = threading.Lock()

        # Thread pool for async operations
        self._executor = ThreadPoolExecutor(max_workers=self.config.thread_pool_size)

        # Background tasks
        self._maintenance_task: asyncio.Task | None = None
        self._running = True

        # Pre-allocate initial blocks
        self._preallocate_blocks()

        # Start maintenance task
        self._start_maintenance()

    def _preallocate_blocks(self):
        """Pre-allocate initial pool blocks"""
        preallocate_counts = {
            "small": int(self.config.max_small_blocks * self.config.preallocate_ratio),
            "medium": int(self.config.max_medium_blocks * self.config.preallocate_ratio),
            "large": int(self.config.max_large_blocks * self.config.preallocate_ratio),
        }

        for tier, count in preallocate_counts.items():
            for _ in range(count):
                self._create_block(tier)

    def _create_block(self, tier: str) -> MemoryBlock:
        """Create a new memory block for the specified tier"""
        size = self._tier_size_map[tier]
        block_id = f"{tier}_{len(self._blocks)}"

        # Allocate from arena
        data = b"\x00" * size
        arena_memory = self._arena.allocate(data)

        block = MemoryBlock(
            size=size,
            tier=tier,
            arena_offset=arena_memory.allocation_time,  # Simplified - would need proper offset tracking
            data=data,
        )

        self._blocks[block_id] = block
        self._free_blocks[tier].append(block)

        return block

    def _determine_tier(self, size: int) -> str:
        """Determine which tier can accommodate the requested size"""
        if size <= self.config.small_size:
            return "small"
        if size <= self.config.medium_size:
            return "medium"
        if size <= self.config.large_size:
            return "large"
        return "large"  # Oversized allocations go to large tier

    def allocate(self, size: int) -> tuple[MemoryBlock, bool]:
        """Allocate a memory block from the pool"""
        tier = self._determine_tier(size)

        with self._stats_lock:
            if self._free_blocks[tier]:
                # Pool hit
                block = self._free_blocks[tier].popleft()
                block.allocated = True
                block.last_used = time.time()
                block.allocation_count += 1

                self._stats.pool_hits += 1
                self._stats.allocations_from_pool += 1

                return block, True
            # Pool miss
            self._stats.pool_misses += 1
            self._stats.allocations_direct += 1

            # Try to create new block if under limit
            if len(self._pools[tier]) < self.config.max_blocks_for_tier(tier):
                block = self._create_block(tier)
                block.allocated = True
                block.last_used = time.time()
                block.allocation_count += 1

                return block, True
            # Pool exhausted, allocate directly
            return self._allocate_direct(size), False

    def _allocate_direct(self, size: int) -> MemoryBlock:
        """Allocate directly from arena when pool is exhausted"""
        data = b"\x00" * size
        arena_memory = self._arena.allocate(data)

        block = MemoryBlock(
            size=size,
            tier="direct",
            allocated=True,
            last_used=time.time(),
            allocation_count=1,
            data=data,
            arena_offset=arena_memory.allocation_time,
        )

        return block

    def deallocate(self, block: MemoryBlock):
        """Return a block to the appropriate pool"""
        if block.tier == "direct":
            # Direct allocations go back to arena
            return

        block.allocated = False
        block.last_used = time.time()

        # Return to free pool if space available
        if len(self._free_blocks[block.tier]) < len(self._pools[block.tier]):
            self._free_blocks[block.tier].append(block)

    def _start_maintenance(self):
        """Start the background maintenance task"""
        if self._maintenance_task is None:
            self._maintenance_task = asyncio.create_task(self._maintenance_loop())

    async def _maintenance_loop(self):
        """Background maintenance loop for pool management"""
        while self._running:
            try:
                await asyncio.sleep(self.config.reclaim_interval)
                await self._perform_maintenance()
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Pool maintenance error: {e}")

    async def _perform_maintenance(self):
        """Perform pool maintenance tasks"""
        await asyncio.to_thread(self._reclaim_unused_blocks)
        await asyncio.to_thread(self._resize_pools_if_needed)
        await asyncio.to_thread(self._update_statistics)

    def _reclaim_unused_blocks(self):
        """Reclaim blocks that haven't been used recently"""
        current_time = time.time()
        reclaim_age = self.config.reclaim_interval * 2  # Reclaim blocks unused for 2x interval

        for tier in ["small", "medium", "large"]:
            blocks_to_reclaim = []
            for block in self._free_blocks[tier]:
                if current_time - block.last_used > reclaim_age:
                    blocks_to_reclaim.append(block)

            # Remove old blocks (simplified - would need proper arena deallocation)
            for block in blocks_to_reclaim:
                self._free_blocks[tier].remove(block)
                # Remove from blocks dict
                block_id = f"{block.tier}_{id(block)}"
                if block_id in self._blocks:
                    del self._blocks[block_id]

            with self._stats_lock:
                self._stats.shrink_count += len(blocks_to_reclaim)

    def _resize_pools_if_needed(self):
        """Resize pools based on usage patterns"""
        for tier in ["small", "medium", "large"]:
            current_size = len(self._pools[tier])
            free_blocks = len(self._free_blocks[tier])
            utilization = (current_size - free_blocks) / current_size if current_size > 0 else 0

            max_size = self.config.max_blocks_for_tier(tier)

            # Expand if utilization is high
            if utilization > 0.8 and current_size < max_size:
                expansion_count = min(int(current_size * (self.config.growth_factor - 1)), max_size - current_size)

                for _ in range(expansion_count):
                    self._create_block(tier)

                with self._stats_lock:
                    self._stats.expansion_count += expansion_count

            # Shrink if utilization is low
            elif utilization < self.config.shrink_threshold and current_size > 1:
                shrink_count = int(current_size * (1 - self.config.shrink_threshold))
                blocks_to_remove = list(self._free_blocks[tier])[:shrink_count]

                for block in blocks_to_remove:
                    self._free_blocks[tier].remove(block)
                    # Remove from blocks dict
                    block_id = f"{block.tier}_{id(block)}"
                    if block_id in self._blocks:
                        del self._blocks[block_id]

                with self._stats_lock:
                    self._stats.shrink_count += shrink_count

    def _update_statistics(self):
        """Update pool statistics"""
        total_blocks = 0
        used_blocks = 0
        total_size = 0

        for tier in ["small", "medium", "large"]:
            total_blocks += len(self._pools[tier])
            used_blocks += len(self._pools[tier]) - len(self._free_blocks[tier])
            total_size += len(self._pools[tier]) * self._tier_size_map[tier]

        with self._stats_lock:
            self._stats.total_pool_size = total_size
            self._stats.utilization_ratio = used_blocks / total_blocks if total_blocks > 0 else 0

    def get_stats(self) -> PoolStats:
        """Get current pool statistics"""
        self._update_statistics()
        with self._stats_lock:
            return PoolStats(
                pool_hits=self._stats.pool_hits,
                pool_misses=self._stats.pool_misses,
                allocations_from_pool=self._stats.allocations_from_pool,
                allocations_direct=self._stats.allocations_direct,
                total_pool_size=self._stats.total_pool_size,
                utilization_ratio=self._stats.utilization_ratio,
                expansion_count=self._stats.expansion_count,
                shrink_count=self._stats.shrink_count,
            )

    def get_pool_efficiency(self) -> float:
        """Calculate pool hit ratio"""
        with self._stats_lock:
            total_requests = self._stats.pool_hits + self._stats.pool_misses
            return self._stats.pool_hits / total_requests if total_requests > 0 else 0

    def get_memory_efficiency(self) -> float:
        """Calculate memory utilization efficiency"""
        stats = self.get_stats()
        return stats.utilization_ratio

    def shutdown(self):
        """Cleanup pool resources"""
        self._running = False

        if self._maintenance_task and not self._maintenance_task.done():
            self._maintenance_task.cancel()
            try:
                asyncio.run(self._maintenance_task)
            except asyncio.CancelledError:
                pass

        if hasattr(self, "_executor"):
            self._executor.shutdown(wait=True)

        # Clear all pools
        self._blocks.clear()
        for tier in ["small", "medium", "large"]:
            self._pools[tier].clear()
            self._free_blocks[tier].clear()


# Extend PoolConfig to include max_blocks_for_tier method
def max_blocks_for_tier(self, tier: str) -> int:
    """Get maximum blocks for a tier"""
    return {"small": self.max_small_blocks, "medium": self.max_medium_blocks, "large": self.max_large_blocks}.get(
        tier, 0
    )


# Monkey patch the method
PoolConfig.max_blocks_for_tier = max_blocks_for_tier


# Global memory pool instance
_global_pool: MemoryPool | None = None


def get_memory_pool(**kwargs) -> MemoryPool:
    """Get or create the global memory pool"""
    global _global_pool
    if _global_pool is None:
        _global_pool = MemoryPool(**kwargs)
    return _global_pool


def allocate_from_pool(size: int) -> tuple[MemoryBlock, bool]:
    """Convenience function to allocate from global memory pool"""
    return get_memory_pool().allocate(size)
