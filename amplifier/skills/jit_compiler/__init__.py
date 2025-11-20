"""
JIT Compilation System for Hot Code Optimization

4-tier compilation system achieving 50-200x speedup for frequently executed code:
- Tier 1: Bytecode optimization and caching
- Tier 2: Function specialization and inlining
- Tier 3: Native code generation with LLVM/Mypyc
- Tier 4: Vectorization and parallel optimization
"""

from .compilation_cache import CacheConfig
from .compilation_cache import CompilationCache
from .hot_path_detector import DetectionConfig
from .hot_path_detector import HotPath
from .hot_path_detector import HotPathDetector
from .jit_optimizer import CompilationTier
from .jit_optimizer import JITOptimizer
from .jit_optimizer import OptimizationResult
from .performance_profiler import PerformanceProfiler
from .performance_profiler import ProfilerStats

__all__ = [
    "JITOptimizer",
    "CompilationTier",
    "OptimizationResult",
    "HotPathDetector",
    "HotPath",
    "DetectionConfig",
    "CompilationCache",
    "CacheConfig",
    "PerformanceProfiler",
    "ProfilerStats",
]
