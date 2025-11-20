"""
Compilation Cache System

Persistent caching system for compiled optimizations
with intelligent invalidation and size management.
"""

import pickle
import sqlite3
import tempfile
import threading
import time
from dataclasses import dataclass
from dataclasses import field
from pathlib import Path

from .jit_optimizer import CompilationTier
from .jit_optimizer import OptimizationResult


@dataclass
class CacheConfig:
    """Configuration for compilation cache"""

    max_cache_size_mb: float = 100.0
    cache_ttl_hours: float = 24.0
    enable_persistence: bool = True
    cache_dir: str | None = None
    max_entries: int = 10000
    compression_enabled: bool = True


@dataclass
class CacheEntry:
    """Entry in compilation cache"""

    func_key: str
    tier: CompilationTier
    result: OptimizationResult
    cache_time: float
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    size_bytes: int = 0


class CompilationCache:
    """Persistent cache for compiled optimizations"""

    def __init__(self, config: CacheConfig | None = None):
        self.config = config or CacheConfig()

        # In-memory cache
        self._cache: dict[str, CacheEntry] = {}
        self._cache_lock = threading.Lock()

        # Persistent storage
        self._db_connection: sqlite3.Connection | None = None
        self._cache_dir: Path | None = None

        # Statistics
        self._hits = 0
        self._misses = 0
        self._evictions = 0

        # Initialize persistent storage if enabled
        if self.config.enable_persistence:
            self._init_persistent_storage()

    def _init_persistent_storage(self):
        """Initialize persistent cache storage"""
        try:
            # Create cache directory
            if self.config.cache_dir:
                self._cache_dir = Path(self.config.cache_dir)
            else:
                self._cache_dir = Path(tempfile.gettempdir()) / "jit_cache"

            self._cache_dir.mkdir(parents=True, exist_ok=True)

            # Initialize SQLite database
            db_path = self._cache_dir / "compilation_cache.db"
            self._db_connection = sqlite3.connect(str(db_path))
            self._db_connection.execute("""
                CREATE TABLE IF NOT EXISTS cache_entries (
                    key TEXT PRIMARY KEY,
                    tier INTEGER,
                    data BLOB,
                    cache_time REAL,
                    access_count INTEGER DEFAULT 0,
                    last_access REAL DEFAULT 0,
                    size_bytes INTEGER DEFAULT 0
                )
            """)
            self._db_connection.commit()

        except Exception as e:
            print(f"Failed to initialize persistent cache: {e}")
            self.config.enable_persistence = False

    def _generate_cache_key(self, func_key: str, tier: CompilationTier) -> str:
        """Generate cache key for function and tier"""
        return f"{func_key}:{tier.name}:{tier.value}"

    async def store_compilation(self, func_key: str, result: OptimizationResult) -> bool:
        """Store compilation result in cache"""
        cache_key = self._generate_cache_key(func_key, result.tier)

        try:
            # Serialize result
            data = pickle.dumps(result)
            if self.config.compression_enabled:
                import gzip

                data = gzip.compress(data)

            # Create cache entry
            entry = CacheEntry(
                func_key=func_key, tier=result.tier, result=result, cache_time=time.time(), size_bytes=len(data)
            )

            # Store in memory
            with self._cache_lock:
                # Check cache size limit
                if len(self._cache) >= self.config.max_entries:
                    await self._evict_lru()

                self._cache[cache_key] = entry

            # Store in persistent storage
            if self.config.enable_persistence and self._db_connection:
                self._db_connection.execute(
                    "INSERT OR REPLACE INTO cache_entries VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        cache_key,
                        result.tier.value,
                        data,
                        entry.cache_time,
                        entry.access_count,
                        entry.last_access,
                        entry.size_bytes,
                    ),
                )
                self._db_connection.commit()

            return True

        except Exception as e:
            print(f"Failed to store compilation result: {e}")
            return False

    async def get_compilation(self, func_key: str, tier: CompilationTier) -> OptimizationResult | None:
        """Retrieve compilation result from cache"""
        cache_key = self._generate_cache_key(func_key, tier)

        try:
            # Check memory cache first
            with self._cache_lock:
                if cache_key in self._cache:
                    entry = self._cache[cache_key]
                    entry.access_count += 1
                    entry.last_access = time.time()
                    self._hits += 1
                    return entry.result

            # Check persistent storage
            if self.config.enable_persistence and self._db_connection:
                cursor = self._db_connection.execute(
                    "SELECT data, cache_time, access_count FROM cache_entries WHERE key = ?", (cache_key,)
                )
                row = cursor.fetchone()

                if row:
                    data, cache_time, access_count = row

                    # Decompress if needed
                    if self.config.compression_enabled:
                        import gzip

                        data = gzip.decompress(data)

                    # Deserialize
                    result = pickle.loads(data)

                    # Load into memory cache
                    entry = CacheEntry(
                        func_key=func_key,
                        tier=tier,
                        result=result,
                        cache_time=cache_time,
                        access_count=access_count + 1,
                        last_access=time.time(),
                    )

                    with self._cache_lock:
                        self._cache[cache_key] = entry
                        self._hits += 1

                    return result

            self._misses += 1
            return None

        except Exception as e:
            print(f"Failed to retrieve compilation result: {e}")
            self._misses += 1
            return None

    async def _evict_lru(self):
        """Evict least recently used entries from cache"""
        with self._cache_lock:
            if not self._cache:
                return

            # Sort by last access time
            entries = sorted(self._cache.items(), key=lambda x: x[1].last_access)

            # Evict oldest 10% or enough to meet size limit
            evict_count = max(1, len(entries) // 10)

            for i in range(evict_count):
                cache_key, entry = entries[i]
                del self._cache[cache_key]

                # Remove from persistent storage
                if self.config.enable_persistence and self._db_connection:
                    self._db_connection.execute("DELETE FROM cache_entries WHERE key = ?", (cache_key,))

            if self._db_connection:
                self._db_connection.commit()

            self._evictions += evict_count

    async def cleanup_expired(self):
        """Clean up expired cache entries"""
        if not self.config.enable_persistence or not self._db_connection:
            return

        current_time = time.time()
        expiry_time = self.config.cache_ttl_hours * 3600

        with self._cache_lock:
            # Remove expired from memory
            expired_keys = [key for key, entry in self._cache.items() if current_time - entry.cache_time > expiry_time]

            for key in expired_keys:
                del self._cache[key]

            # Remove from persistent storage
            if self._db_connection:
                self._db_connection.execute(
                    "DELETE FROM cache_entries WHERE ? - cache_time > ?", (current_time, expiry_time)
                )
                self._db_connection.commit()

    def get_stats(self) -> dict:
        """Get cache statistics"""
        with self._cache_lock:
            memory_entries = len(self._cache)
            memory_size_bytes = sum(entry.size_bytes for entry in self._cache.values())

        hit_rate = self._hits / (self._hits + self._misses) if (self._hits + self._misses) > 0 else 0.0

        return {
            "memory_entries": memory_entries,
            "memory_size_mb": memory_size_bytes / (1024 * 1024),
            "cache_hits": self._hits,
            "cache_misses": self._misses,
            "hit_rate": hit_rate,
            "evictions": self._evictions,
            "persistence_enabled": self.config.enable_persistence,
        }

    def clear(self):
        """Clear all cache entries"""
        with self._cache_lock:
            self._cache.clear()

        if self.config.enable_persistence and self._db_connection:
            self._db_connection.execute("DELETE FROM cache_entries")
            self._db_connection.commit()

    def close(self):
        """Close cache and cleanup resources"""
        if self._db_connection:
            self._db_connection.close()
            self._db_connection = None


# Global compilation cache instance
_global_compilation_cache: CompilationCache | None = None


def get_compilation_cache(**kwargs) -> CompilationCache:
    """Get or create the global compilation cache"""
    global _global_compilation_cache
    if _global_compilation_cache is None:
        _global_compilation_cache = CompilationCache(**kwargs)
    return _global_compilation_cache
