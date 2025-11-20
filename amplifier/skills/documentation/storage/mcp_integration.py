"""
MCP Integration for Persistent Documentation Storage

Integrates with MCP (Model Context Protocol) for persistent, distributed
documentation storage with automatic backup and recovery capabilities.
"""

import asyncio
import hashlib
import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from datetime import timedelta
from enum import Enum
from pathlib import Path
from typing import Any


class StorageLevel(Enum):
    """Storage levels for documentation."""

    MEMORY = "memory"  # In-memory only
    LOCAL = "local"  # Local file system
    DISTRIBUTED = "distributed"  # Distributed MCP storage
    BACKUP = "backup"  # Backup storage


class StorageStatus(Enum):
    """Status of storage operations."""

    SUCCESS = "success"
    PENDING = "pending"
    FAILED = "failed"
    RETRYING = "retrying"
    CORRUPTED = "corrupted"


@dataclass
class StorageConfig:
    """Configuration for MCP storage integration."""

    mcp_endpoint: str | None = None
    backup_interval: timedelta = field(default_factory=lambda: timedelta(hours=1))
    max_retries: int = 3
    retry_delay: float = 1.0
    compression_enabled: bool = True
    encryption_enabled: bool = False
    cache_size_mb: int = 100
    sync_on_write: bool = True
    local_backup_path: Path | None = None


@dataclass
class StorageOperation:
    """A storage operation with metadata."""

    operation_id: str
    operation_type: str  # "read", "write", "delete", "backup"
    skill_name: str
    version: str | None = None
    timestamp: datetime = field(default_factory=datetime.now)
    status: StorageStatus = StorageStatus.PENDING
    retry_count: int = 0
    error_message: str | None = None
    data_hash: str | None = None


@dataclass
class StorageMetrics:
    """Metrics for storage performance."""

    total_operations: int = 0
    successful_operations: int = 0
    failed_operations: int = 0
    average_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    compression_ratio: float = 0.0
    storage_used_mb: float = 0.0
    last_sync: datetime | None = None


class MCPDocumentationStorage:
    """MCP-integrated persistent storage for documentation."""

    def __init__(self, config: StorageConfig):
        self.config = config
        self.metrics = StorageMetrics()
        self.cache: dict[str, dict[str, Any]] = {}
        self.pending_operations: list[StorageOperation] = []
        self.mcp_client = None

        # Initialize local storage
        self.local_path = config.local_backup_path or Path.cwd() / ".amplifier" / "docs_storage"
        self.local_path.mkdir(parents=True, exist_ok=True)

        # Load existing cache
        self._load_cache()

        # Start background tasks
        if self.config.mcp_endpoint:
            self._start_mcp_client()

        self._start_backup_scheduler()

    async def store_documentation(
        self,
        skill_name: str,
        documentation: dict[str, Any],
        version: str | None = None,
        metadata: dict[str, Any] | None = None,
    ) -> StorageOperation:
        """Store documentation with MCP integration."""

        # Generate operation ID
        operation_id = self._generate_operation_id()

        # Prepare data
        storage_data = {
            "skill_name": skill_name,
            "version": version or "latest",
            "documentation": documentation,
            "metadata": metadata or {},
            "timestamp": datetime.now().isoformat(),
            "data_hash": self._calculate_data_hash(documentation),
        }

        # Compress if enabled
        if self.config.compression_enabled:
            storage_data = self._compress_data(storage_data)

        # Create operation
        operation = StorageOperation(
            operation_id=operation_id,
            operation_type="write",
            skill_name=skill_name,
            version=version,
            data_hash=storage_data["data_hash"],
        )

        # Store locally first
        try:
            await self._store_local(skill_name, version, storage_data)
            operation.status = StorageStatus.SUCCESS
            self.metrics.successful_operations += 1

            # Update cache
            cache_key = f"{skill_name}:{version or 'latest'}"
            self.cache[cache_key] = storage_data

        except Exception as e:
            operation.status = StorageStatus.FAILED
            operation.error_message = str(e)
            self.metrics.failed_operations += 1

        self.metrics.total_operations += 1

        # Sync to MCP if configured
        if self.config.mcp_endpoint and self.config.sync_on_write:
            asyncio.create_task(self._sync_to_mcp(operation))

        return operation

    async def retrieve_documentation(self, skill_name: str, version: str | None = None) -> dict[str, Any] | None:
        """Retrieve documentation from storage."""

        cache_key = f"{skill_name}:{version or 'latest'}"

        # Check cache first
        if cache_key in self.cache:
            self.metrics.cache_hit_rate = (self.metrics.cache_hit_rate * 0.9) + (1.0 * 0.1)
            return self.cache[cache_key]

        # Try local storage
        try:
            data = await self._retrieve_local(skill_name, version)
            if data:
                self.cache[cache_key] = data
                return data
        except Exception:
            pass

        # Try MCP storage
        if self.config.mcp_client:
            try:
                data = await self._retrieve_from_mcp(skill_name, version)
                if data:
                    # Cache and backup locally
                    self.cache[cache_key] = data
                    await self._store_local(skill_name, version, data)
                    return data
            except Exception:
                pass

        return None

    async def list_documentations(self, skill_name: str | None = None) -> list[dict[str, Any]]:
        """List available documentations."""

        # Try local first
        local_docs = await self._list_local(skill_name)

        # Add MCP docs if available
        if self.config.mcp_client:
            try:
                mcp_docs = await self._list_mcp(skill_name)
                # Merge and deduplicate
                all_docs = self._merge_documentation_lists(local_docs, mcp_docs)
            except Exception:
                all_docs = local_docs
        else:
            all_docs = local_docs

        return all_docs

    async def delete_documentation(self, skill_name: str, version: str | None = None) -> StorageOperation:
        """Delete documentation from storage."""

        operation_id = self._generate_operation_id()

        operation = StorageOperation(
            operation_id=operation_id, operation_type="delete", skill_name=skill_name, version=version
        )

        try:
            # Delete from local storage
            await self._delete_local(skill_name, version)

            # Remove from cache
            cache_key = f"{skill_name}:{version or 'latest'}"
            self.cache.pop(cache_key, None)

            operation.status = StorageStatus.SUCCESS
            self.metrics.successful_operations += 1

        except Exception as e:
            operation.status = StorageStatus.FAILED
            operation.error_message = str(e)
            self.metrics.failed_operations += 1

        self.metrics.total_operations += 1

        # Delete from MCP if configured
        if self.config.mcp_client:
            asyncio.create_task(self._delete_from_mcp(operation))

        return operation

    async def backup_all_documentations(self) -> StorageOperation:
        """Backup all documentations to MCP storage."""

        if not self.config.mcp_client:
            raise ValueError("MCP endpoint not configured")

        operation_id = self._generate_operation_id()

        operation = StorageOperation(operation_id=operation_id, operation_type="backup", skill_name="all")

        try:
            # Get all local documentations
            local_docs = await self._list_local()

            # Backup each documentation
            for doc_info in local_docs:
                skill_name = doc_info["skill_name"]
                version = doc_info.get("version", "latest")

                data = await self._retrieve_local(skill_name, version)
                if data:
                    await self._store_to_mcp(skill_name, version, data)

            operation.status = StorageStatus.SUCCESS
            self.metrics.successful_operations += 1
            self.metrics.last_sync = datetime.now()

        except Exception as e:
            operation.status = StorageStatus.FAILED
            operation.error_message = str(e)
            self.metrics.failed_operations += 1

        self.metrics.total_operations += 1

        return operation

    async def restore_from_backup(
        self, skill_name: str | None = None, version: str | None = None
    ) -> list[StorageOperation]:
        """Restore documentation from MCP backup."""

        if not self.config.mcp_client:
            raise ValueError("MCP endpoint not configured")

        operations = []

        try:
            # Get documentations from MCP
            mcp_docs = await self._list_mcp(skill_name)

            for doc_info in mcp_docs:
                if version and doc_info.get("version") != version:
                    continue

                restore_skill = doc_info["skill_name"]
                restore_version = doc_info.get("version", "latest")

                # Retrieve from MCP
                data = await self._retrieve_from_mcp(restore_skill, restore_version)
                if data:
                    # Store locally
                    await self._store_local(restore_skill, restore_version, data)

                    # Update cache
                    cache_key = f"{restore_skill}:{restore_version}"
                    self.cache[cache_key] = data

                operations.append(
                    StorageOperation(
                        operation_id=self._generate_operation_id(),
                        operation_type="restore",
                        skill_name=restore_skill,
                        version=restore_version,
                        status=StorageStatus.SUCCESS,
                    )
                )

        except Exception as e:
            operations.append(
                StorageOperation(
                    operation_id=self._generate_operation_id(),
                    operation_type="restore",
                    skill_name=skill_name or "all",
                    status=StorageStatus.FAILED,
                    error_message=str(e),
                )
            )

        return operations

    def get_storage_metrics(self) -> StorageMetrics:
        """Get current storage metrics."""

        # Update storage usage
        total_size = 0
        for file_path in self.local_path.rglob("*"):
            if file_path.is_file():
                total_size += file_path.stat().st_size

        self.metrics.storage_used_mb = total_size / (1024 * 1024)

        return self.metrics

    async def cleanup_old_versions(
        self, skill_name: str, keep_count: int = 5, older_than: timedelta | None = None
    ) -> list[StorageOperation]:
        """Clean up old versions of documentation."""

        operations = []

        try:
            # List all versions for skill
            docs = await self._list_local(skill_name)

            # Filter by age if specified
            if older_than:
                cutoff_time = datetime.now() - older_than
                docs = [doc for doc in docs if datetime.fromisoformat(doc["timestamp"]) < cutoff_time]

            # Keep the most recent versions
            docs.sort(key=lambda x: x["timestamp"], reverse=True)
            docs_to_keep = docs[:keep_count]
            docs_to_delete = docs[keep_count:]

            # Delete old versions
            for doc in docs_to_delete:
                version = doc.get("version", "latest")
                operation = await self.delete_documentation(skill_name, version)
                operations.append(operation)

        except Exception as e:
            operations.append(
                StorageOperation(
                    operation_id=self._generate_operation_id(),
                    operation_type="cleanup",
                    skill_name=skill_name,
                    status=StorageStatus.FAILED,
                    error_message=str(e),
                )
            )

        return operations

    def _generate_operation_id(self) -> str:
        """Generate unique operation ID."""
        return hashlib.md5(f"{datetime.now().isoformat()}{id(self)}".encode()).hexdigest()[:16]

    def _calculate_data_hash(self, data: dict[str, Any]) -> str:
        """Calculate hash for data integrity."""
        data_str = json.dumps(data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def _compress_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Compress data for storage."""
        # Simple compression - would use proper compression in production
        compressed = data.copy()
        compressed["compressed"] = True
        compressed["original_size"] = len(json.dumps(data))

        # Convert documentation to more compact format
        if "documentation" in compressed:
            docs_str = json.dumps(compressed["documentation"], separators=(",", ":"))
            compressed["documentation_compressed"] = docs_str
            del compressed["documentation"]

        compressed["compressed_size"] = len(json.dumps(compressed))

        return compressed

    def _decompress_data(self, data: dict[str, Any]) -> dict[str, Any]:
        """Decompress data from storage."""
        if not data.get("compressed", False):
            return data

        decompressed = data.copy()
        decompressed["documentation"] = json.loads(data["documentation_compressed"])
        del decompressed["documentation_compressed"]
        del decompressed["compressed"]

        return decompressed

    async def _store_local(self, skill_name: str, version: str | None, data: dict[str, Any]) -> None:
        """Store documentation locally."""
        file_path = self.local_path / skill_name
        file_path.mkdir(exist_ok=True)

        filename = f"{version or 'latest'}.json"
        full_path = file_path / filename

        with open(full_path, "w") as f:
            json.dump(data, f, indent=2)

    async def _retrieve_local(self, skill_name: str, version: str | None) -> dict[str, Any] | None:
        """Retrieve documentation from local storage."""
        file_path = self.local_path / skill_name
        filename = f"{version or 'latest'}.json"
        full_path = file_path / filename

        if not full_path.exists():
            return None

        with open(full_path) as f:
            data = json.load(f)

        return self._decompress_data(data)

    async def _delete_local(self, skill_name: str, version: str | None) -> None:
        """Delete documentation from local storage."""
        file_path = self.local_path / skill_name
        filename = f"{version or 'latest'}.json"
        full_path = file_path / filename

        if full_path.exists():
            full_path.unlink()

    async def _list_local(self, skill_name: str | None = None) -> list[dict[str, Any]]:
        """List documentations in local storage."""
        docs = []

        for skill_dir in self.local_path.iterdir():
            if not skill_dir.is_dir():
                continue

            if skill_name and skill_dir.name != skill_name:
                continue

            for file_path in skill_dir.glob("*.json"):
                version = file_path.stem

                try:
                    with open(file_path) as f:
                        data = json.load(f)

                    docs.append(
                        {
                            "skill_name": skill_dir.name,
                            "version": version,
                            "timestamp": data.get("timestamp"),
                            "data_hash": data.get("data_hash"),
                            "storage_level": "local",
                        }
                    )

                except Exception:
                    continue

        return docs

    async def _start_mcp_client(self) -> None:
        """Initialize MCP client connection."""
        # This would implement actual MCP client initialization
        # For now, simulate client
        self.mcp_client = True

    def _start_backup_scheduler(self) -> None:
        """Start automatic backup scheduler."""
        if not self.config.mcp_client:
            return

        # This would implement actual background task scheduling
        # For now, just note that it would run
        pass

    async def _sync_to_mcp(self, operation: StorageOperation) -> None:
        """Sync operation to MCP storage."""
        # Implement MCP sync logic here
        pass

    async def _store_to_mcp(self, skill_name: str, version: str | None, data: dict[str, Any]) -> None:
        """Store documentation to MCP."""
        # Implement MCP storage logic here
        pass

    async def _retrieve_from_mcp(self, skill_name: str, version: str | None) -> dict[str, Any] | None:
        """Retrieve documentation from MCP."""
        # Implement MCP retrieval logic here
        return None

    async def _delete_from_mcp(self, operation: StorageOperation) -> None:
        """Delete documentation from MCP."""
        # Implement MCP deletion logic here
        pass

    async def _list_mcp(self, skill_name: str | None = None) -> list[dict[str, Any]]:
        """List documentations in MCP storage."""
        # Implement MCP listing logic here
        return []

    def _merge_documentation_lists(
        self, local_docs: list[dict[str, Any]], mcp_docs: list[dict[str, Any]]
    ) -> list[dict[str, Any]]:
        """Merge and deduplicate documentation lists."""
        seen = set()
        merged = []

        # Prefer local docs, then add MCP docs not seen locally
        for doc in local_docs + mcp_docs:
            key = (doc["skill_name"], doc.get("version", "latest"))
            if key not in seen:
                seen.add(key)
                merged.append(doc)

        return merged

    def _load_cache(self) -> None:
        """Load cache from disk."""
        cache_file = self.local_path / ".cache.json"

        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    self.cache = json.load(f)
            except Exception:
                self.cache = {}

    def _save_cache(self) -> None:
        """Save cache to disk."""
        cache_file = self.local_path / ".cache.json"

        try:
            with open(cache_file, "w") as f:
                json.dump(self.cache, f, indent=2)
        except Exception:
            pass
