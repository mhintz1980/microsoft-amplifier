"""Distributed Storage Coordinator.

Manages distributed storage strategies for the skill repository system,
providing redundancy, load balancing, and geographic distribution.
"""

import asyncio
import hashlib
import json
import uuid
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger

logger = get_logger(__name__)


class StorageTier(Enum):
    """Storage tiers for different performance requirements."""

    HOT = "hot"  # Immediate access, high performance
    WARM = "warm"  # Fast access, moderate performance
    COLD = "cold"  # Slow access, archival storage
    ARCHIVAL = "archival"  # Very slow access, long-term storage


class ReplicationStrategy(Enum):
    """Replication strategies for data redundancy."""

    NONE = "none"  # No replication
    LOCAL_ONLY = "local_only"  # Local replication only
    GEO_DISTRIBUTED = "geo_distributed"  # Geographic distribution
    HYBRID = "hybrid"  # Mix of strategies


class ConsistencyLevel(Enum):
    """Consistency levels for distributed operations."""

    EVENTUAL = "eventual"  # Eventually consistent
    STRONG = "strong"  # Strong consistency
    SESSION = "session"  # Session consistency
    MONOTONIC = "monotonic"  # Monotonic consistency


@dataclass
class StorageNode:
    """Represents a storage node in the distributed system."""

    node_id: str
    name: str
    location: str
    storage_type: str
    capacity_gb: int
    available_gb: int
    latency_ms: float
    reliability_score: float
    is_active: bool = True
    last_health_check: datetime = field(default_factory=datetime.now)


@dataclass
class StorageReplica:
    """Represents a replica of data across storage nodes."""

    replica_id: str
    skill_id: str
    node_id: str
    storage_tier: StorageTier
    created_at: datetime
    last_updated: datetime
    size_bytes: int
    checksum: str
    is_primary: bool = False


@dataclass
class DistributionPolicy:
    """Policy for distributing storage across nodes."""

    replication_factor: int = 3
    storage_tiers: dict[StorageTier, float] = field(
        default_factory=lambda: {
            StorageTier.HOT: 0.1,
            StorageTier.WARM: 0.3,
            StorageTier.COLD: 0.4,
            StorageTier.ARCHIVAL: 0.2,
        }
    )
    geographic_spread: bool = True
    load_balancing: bool = True
    consistency_level: ConsistencyLevel = ConsistencyLevel.EVENTUAL


class DistributedStorageCoordinator:
    """Coordinates distributed storage for skill repository."""

    def __init__(self):
        self.storage_nodes = {}  # node_id -> StorageNode
        self.replicas = {}  # skill_id -> list[StorageReplica]
        self.distribution_policies = {}  # policy_name -> DistributionPolicy
        self.active_replications = set()  # Set of ongoing replications
        self.health_monitoring_interval = 60  # seconds

        # Performance metrics
        self.replication_stats = {
            "total_replications": 0,
            "failed_replications": 0,
            "average_replication_time_ms": 0.0,
            "data_distributed_gb": 0.0,
            "replication_efficiency": 0.0,
        }

        # Local storage configuration
        self.local_storage = Path.home() / ".amplifier_storage" / "distributed"
        self.metadata_store = self.local_storage / "metadata"
        self.replica_store = self.local_storage / "replicas"

    async def initialize(self) -> None:
        """Initialize the distributed storage coordinator."""
        await self._ensure_storage_structure()
        await self._discover_storage_nodes()
        await self._load_policies()
        await self._start_health_monitoring()
        logger.info("Distributed Storage Coordinator initialized")

    async def store_skill(self, skill_data: dict[str, Any], policy_name: str = "default") -> list[StorageReplica]:
        """Store skill data across distributed storage nodes."""
        try:
            skill_id = skill_data.get("skill_id") or str(uuid.uuid4())
            policy = self.distribution_policies.get(policy_name, self._get_default_policy())

            # Create replicas based on policy
            replicas = await self._create_replicas(skill_id, skill_data, policy)

            # Store replicas on nodes
            successful_replicas = []
            for replica in replicas:
                success = await self._store_replica(replica, skill_data)
                if success:
                    successful_replicas.append(replica)

            # Update tracking
            self.replicas[skill_id] = successful_replicas
            await self._save_replica_metadata(skill_id, successful_replicas)

            # Update stats
            self.replication_stats["total_replications"] += len(successful_replicas)
            total_size = len(json.dumps(skill_data).encode()) * len(successful_replicas)
            self.replication_stats["data_distributed_gb"] += total_size / (1024**3)

            logger.info(f"Stored skill {skill_id} across {len(successful_replicas)} nodes")
            return successful_replicas

        except Exception as e:
            logger.error(f"Failed to store skill: {e}")
            self.replication_stats["failed_replications"] += 1
            return []

    async def load_skill(
        self, skill_id: str, preferred_tier: StorageTier = StorageTier.HOT, max_attempts: int = 3
    ) -> dict[str, Any] | None:
        """Load skill data from distributed storage."""
        try:
            # Get replicas for this skill
            skill_replicas = self.replicas.get(skill_id, [])
            if not skill_replicas:
                # Try to load from metadata store
                skill_replicas = await self._load_replica_metadata(skill_id)
                if not skill_replicas:
                    logger.warning(f"No replicas found for skill {skill_id}")
                    return None

            # Sort replicas by preference (tier, latency, reliability)
            sorted_replicas = self._sort_replicas_by_preference(skill_replicas, preferred_tier)

            # Try to load from replicas in order of preference
            for attempt, replica in enumerate(sorted_replicas[:max_attempts]):
                try:
                    # Check if node is active
                    node = self.storage_nodes.get(replica.node_id)
                    if not node or not node.is_active:
                        logger.warning(f"Node {replica.node_id} is inactive, trying next replica")
                        continue

                    # Load data from replica
                    skill_data = await self._load_from_replica(replica)
                    if skill_data:
                        # Verify checksum if available
                        if replica.checksum and self._verify_checksum(skill_data, replica.checksum):
                            logger.info(f"Loaded skill {skill_id} from replica {replica.replica_id}")
                            return skill_data
                        logger.warning(f"Checksum verification failed for replica {replica.replica_id}")

                except Exception as e:
                    logger.warning(f"Failed to load from replica {replica.replica_id}: {e}")
                    continue

            logger.error(f"Failed to load skill {skill_id} from all replicas")
            return None

        except Exception as e:
            logger.error(f"Failed to load skill {skill_id}: {e}")
            return None

    async def replicate_skill(
        self, skill_id: str, target_tiers: list[StorageTier] | None = None, replication_factor: int | None = None
    ) -> bool:
        """Create additional replicas for an existing skill."""
        try:
            if skill_id not in self.replicas:
                logger.warning(f"Skill {skill_id} not found in distributed storage")
                return False

            # Load existing skill data
            skill_data = await self.load_skill(skill_id)
            if not skill_data:
                return False

            # Get current replicas
            current_replicas = self.replicas[skill_id]

            # Determine target configuration
            policy = self._get_default_policy()
            if replication_factor:
                policy.replication_factor = replication_factor
            if target_tiers:
                # Adjust storage tiers distribution
                current_tiers = set(r.storage_tier for r in current_replicas)
                needed_tiers = set(target_tiers) - current_tiers
                if needed_tiers:
                    # Need to create replicas for missing tiers
                    pass

            # Create additional replicas
            additional_replicas = await self._create_additional_replicas(skill_id, skill_data, current_replicas, policy)

            # Store additional replicas
            for replica in additional_replicas:
                try:
                    success = await self._store_replica(replica, skill_data)
                    if success:
                        current_replicas.append(replica)
                except Exception as e:
                    logger.error(f"Failed to create additional replica: {e}")

            # Update tracking
            self.replicas[skill_id] = current_replicas
            await self._save_replica_metadata(skill_id, current_replicas)

            logger.info(f"Replicated skill {skill_id} to {len(additional_replicas)} additional nodes")
            return True

        except Exception as e:
            logger.error(f"Failed to replicate skill {skill_id}: {e}")
            return False

    async def delete_skill(self, skill_id: str) -> bool:
        """Delete skill from all storage nodes."""
        try:
            if skill_id not in self.replicas:
                logger.warning(f"Skill {skill_id} not found in distributed storage")
                return False

            replicas = self.replicas[skill_id]
            deletion_successes = 0

            # Delete from all replicas
            for replica in replicas:
                try:
                    success = await self._delete_from_replica(replica)
                    if success:
                        deletion_successes += 1
                except Exception as e:
                    logger.error(f"Failed to delete from replica {replica.replica_id}: {e}")

            # Remove from tracking
            del self.replicas[skill_id]
            await self._delete_replica_metadata(skill_id)

            success = deletion_successes == len(replicas)
            logger.info(f"Deleted skill {skill_id} from {deletion_successes}/{len(replicas)} nodes")
            return success

        except Exception as e:
            logger.error(f"Failed to delete skill {skill_id}: {e}")
            return False

    async def get_storage_analytics(self) -> dict[str, Any]:
        """Get comprehensive storage analytics."""
        try:
            total_replicas = sum(len(replicas) for replicas in self.replicas.values())
            active_nodes = sum(1 for node in self.storage_nodes.values() if node.is_active)

            # Calculate storage distribution
            tier_distribution = {}
            for replicas in self.replicas.values():
                for replica in replicas:
                    tier_name = replica.storage_tier.value
                    tier_distribution[tier_name] = tier_distribution.get(tier_name, 0) + 1

            # Calculate node utilization
            node_utilization = {}
            for node_id, node in self.storage_nodes.items():
                used_gb = node.capacity_gb - node.available_gb
                utilization = (used_gb / node.capacity_gb) * 100 if node.capacity_gb > 0 else 0
                node_utilization[node_id] = {
                    "name": node.name,
                    "location": node.location,
                    "utilization_percent": utilization,
                    "used_gb": used_gb,
                    "available_gb": node.available_gb,
                    "latency_ms": node.latency_ms,
                    "reliability_score": node.reliability_score,
                }

            return {
                "total_skills_stored": len(self.replicas),
                "total_replicas": total_replicas,
                "average_replicas_per_skill": total_replicas / len(self.replicas) if self.replicas else 0,
                "active_storage_nodes": active_nodes,
                "total_storage_nodes": len(self.storage_nodes),
                "tier_distribution": tier_distribution,
                "node_utilization": node_utilization,
                "replication_stats": self.replication_stats,
                "health_status": await self._get_cluster_health(),
            }

        except Exception as e:
            logger.error(f"Failed to get storage analytics: {e}")
            return {"error": str(e)}

    async def _ensure_storage_structure(self) -> None:
        """Ensure storage directories exist."""
        directories = [
            self.local_storage,
            self.metadata_store,
            self.replica_store,
            self.metadata_store / "replicas",
            self.metadata_store / "nodes",
            self.metadata_store / "policies",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    async def _discover_storage_nodes(self) -> None:
        """Discover and initialize storage nodes."""
        try:
            # Initialize local storage node
            local_node = StorageNode(
                node_id="local_primary",
                name="Local Primary Storage",
                location="local",
                storage_type="filesystem",
                capacity_gb=100,  # 100GB local storage
                available_gb=100,
                latency_ms=1.0,
                reliability_score=0.99,
                is_active=True,
            )
            self.storage_nodes["local_primary"] = local_node

            # In a full implementation, this would discover remote storage nodes
            # For now, we'll create a few mock distributed nodes
            distributed_nodes = [
                StorageNode(
                    node_id="cloud_backup_1",
                    name="Cloud Backup Node 1",
                    location="us-west-1",
                    storage_type="cloud_s3",
                    capacity_gb=1000,
                    available_gb=950,
                    latency_ms=50.0,
                    reliability_score=0.999,
                    is_active=True,
                ),
                StorageNode(
                    node_id="cloud_backup_2",
                    name="Cloud Backup Node 2",
                    location="us-east-1",
                    storage_type="cloud_s3",
                    capacity_gb=1000,
                    available_gb=975,
                    latency_ms=45.0,
                    reliability_score=0.999,
                    is_active=True,
                ),
            ]

            for node in distributed_nodes:
                self.storage_nodes[node.node_id] = node

            # Save node metadata
            await self._save_node_metadata()

            logger.info(f"Discovered {len(self.storage_nodes)} storage nodes")

        except Exception as e:
            logger.error(f"Failed to discover storage nodes: {e}")

    async def _load_policies(self) -> None:
        """Load distribution policies."""
        try:
            # Default policy
            self.distribution_policies["default"] = DistributionPolicy()

            # High availability policy
            self.distribution_policies["high_availability"] = DistributionPolicy(
                replication_factor=5,
                geographic_spread=True,
                consistency_level=ConsistencyLevel.STRONG,
            )

            # Cost-optimized policy
            self.distribution_policies["cost_optimized"] = DistributionPolicy(
                replication_factor=2,
                storage_tiers={
                    StorageTier.HOT: 0.05,
                    StorageTier.WARM: 0.15,
                    StorageTier.COLD: 0.50,
                    StorageTier.ARCHIVAL: 0.30,
                },
                consistency_level=ConsistencyLevel.EVENTUAL,
            )

            logger.info(f"Loaded {len(self.distribution_policies)} distribution policies")

        except Exception as e:
            logger.error(f"Failed to load policies: {e}")

    async def _start_health_monitoring(self) -> None:
        """Start health monitoring of storage nodes."""
        try:
            asyncio.create_task(self._health_monitoring_loop())
            logger.info("Started health monitoring for storage nodes")

        except Exception as e:
            logger.error(f"Failed to start health monitoring: {e}")

    async def _health_monitoring_loop(self) -> None:
        """Periodic health monitoring loop."""
        while True:
            try:
                await self._check_node_health()
                await asyncio.sleep(self.health_monitoring_interval)

            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(10)  # Short retry interval

    async def _check_node_health(self) -> None:
        """Check health of all storage nodes."""
        try:
            for node_id, node in self.storage_nodes.items():
                try:
                    # Perform health check
                    is_healthy = await self._perform_health_check(node)

                    if is_healthy != node.is_active:
                        node.is_active = is_healthy
                        node.last_health_check = datetime.now()
                        logger.info(f"Node {node_id} health changed to: {is_healthy}")

                except Exception as e:
                    logger.error(f"Health check failed for node {node_id}: {e}")
                    node.is_active = False
                    node.last_health_check = datetime.now()

        except Exception as e:
            logger.error(f"Failed to check node health: {e}")

    async def _perform_health_check(self, node: StorageNode) -> bool:
        """Perform health check on a specific node."""
        try:
            if node.node_id == "local_primary":
                # Local file system check
                return self.local_storage.exists()

            # Remote node health check (mock implementation)
            # In a full implementation, this would ping the actual remote storage
            return node.reliability_score > 0.95

        except Exception as e:
            logger.warning(f"Health check failed for node {node.node_id}: {e}")
            return False

    async def _create_replicas(
        self, skill_id: str, skill_data: dict[str, Any], policy: DistributionPolicy
    ) -> list[StorageReplica]:
        """Create replicas based on distribution policy."""
        try:
            replicas = []
            skill_size_bytes = len(json.dumps(skill_data).encode())

            # Get active nodes sorted by reliability and latency
            active_nodes = [node for node in self.storage_nodes.values() if node.is_active]
            active_nodes.sort(key=lambda n: (n.reliability_score, -n.latency_ms), reverse=True)

            # Distribute replicas across tiers
            for tier, percentage in policy.storage_tiers.items():
                tier_replica_count = max(1, int(policy.replication_factor * percentage))

                for i in range(min(tier_replica_count, len(active_nodes))):
                    if i >= len(active_nodes):
                        break

                    node = active_nodes[i % len(active_nodes)]

                    replica = StorageReplica(
                        replica_id=str(uuid.uuid4()),
                        skill_id=skill_id,
                        node_id=node.node_id,
                        storage_tier=tier,
                        created_at=datetime.now(),
                        last_updated=datetime.now(),
                        size_bytes=skill_size_bytes,
                        checksum=self._calculate_checksum(skill_data),
                        is_primary=(len(replicas) == 0),  # First replica is primary
                    )

                    replicas.append(replica)

            return replicas

        except Exception as e:
            logger.error(f"Failed to create replicas: {e}")
            return []

    async def _store_replica(self, replica: StorageReplica, skill_data: dict[str, Any]) -> bool:
        """Store data on a specific replica node."""
        try:
            start_time = asyncio.get_event_loop().time()

            if replica.node_id == "local_primary":
                # Store in local filesystem
                return await self._store_locally(replica, skill_data)

            # Store in remote storage (mock implementation)
            await asyncio.sleep(0.1)  # Simulate network latency
            return True

        except Exception as e:
            logger.error(f"Failed to store replica {replica.replica_id}: {e}")
            return False

    async def _store_locally(self, replica: StorageReplica, skill_data: dict[str, Any]) -> bool:
        """Store data in local filesystem."""
        try:
            # Create directory structure based on tier
            tier_dir = self.replica_store / replica.storage_tier.value
            tier_dir.mkdir(exist_ok=True)

            # Store skill data
            skill_file = tier_dir / f"{replica.skill_id}.json"
            with open(skill_file, "w") as f:
                json.dump(skill_data, f, indent=2)

            # Store replica metadata
            metadata_file = tier_dir / f"{replica.skill_id}_metadata.json"
            with open(metadata_file, "w") as f:
                json.dump(
                    {
                        "replica_id": replica.replica_id,
                        "skill_id": replica.skill_id,
                        "node_id": replica.node_id,
                        "storage_tier": replica.storage_tier.value,
                        "created_at": replica.created_at.isoformat(),
                        "last_updated": replica.last_updated.isoformat(),
                        "size_bytes": replica.size_bytes,
                        "checksum": replica.checksum,
                        "is_primary": replica.is_primary,
                    },
                    f,
                    indent=2,
                )

            return True

        except Exception as e:
            logger.error(f"Failed to store locally: {e}")
            return False

    async def _load_from_replica(self, replica: StorageReplica) -> dict[str, Any] | None:
        """Load data from a specific replica."""
        try:
            if replica.node_id == "local_primary":
                return await self._load_locally(replica)

            # Load from remote storage (mock implementation)
            await asyncio.sleep(0.05)  # Simulate network latency
            return {}  # Mock data

        except Exception as e:
            logger.error(f"Failed to load from replica {replica.replica_id}: {e}")
            return None

    async def _load_locally(self, replica: StorageReplica) -> dict[str, Any] | None:
        """Load data from local filesystem."""
        try:
            tier_dir = self.replica_store / replica.storage_tier.value
            skill_file = tier_dir / f"{replica.skill_id}.json"

            if skill_file.exists():
                with open(skill_file) as f:
                    return json.load(f)

            return None

        except Exception as e:
            logger.error(f"Failed to load locally: {e}")
            return None

    async def _delete_from_replica(self, replica: StorageReplica) -> bool:
        """Delete data from a specific replica."""
        try:
            if replica.node_id == "local_primary":
                return await self._delete_locally(replica)

            # Delete from remote storage (mock implementation)
            await asyncio.sleep(0.05)
            return True

        except Exception as e:
            logger.error(f"Failed to delete from replica {replica.replica_id}: {e}")
            return False

    async def _delete_locally(self, replica: StorageReplica) -> bool:
        """Delete data from local filesystem."""
        try:
            tier_dir = self.replica_store / replica.storage_tier.value

            # Delete skill file
            skill_file = tier_dir / f"{replica.skill_id}.json"
            if skill_file.exists():
                skill_file.unlink()

            # Delete metadata file
            metadata_file = tier_dir / f"{replica.skill_id}_metadata.json"
            if metadata_file.exists():
                metadata_file.unlink()

            return True

        except Exception as e:
            logger.error(f"Failed to delete locally: {e}")
            return False

    def _calculate_checksum(self, data: dict[str, Any]) -> str:
        """Calculate checksum for data."""
        data_str = json.dumps(data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()

    def _verify_checksum(self, data: dict[str, Any], expected_checksum: str) -> bool:
        """Verify data checksum."""
        actual_checksum = self._calculate_checksum(data)
        return actual_checksum == expected_checksum

    def _sort_replicas_by_preference(
        self, replicas: list[StorageReplica], preferred_tier: StorageTier
    ) -> list[StorageReplica]:
        """Sort replicas by preference (tier, latency, reliability)."""

        def preference_key(replica):
            # Primary replicas come first
            primary_bonus = 100 if replica.is_primary else 0

            # Preferred tier gets bonus
            tier_bonus = 50 if replica.storage_tier == preferred_tier else 0

            # Node latency and reliability
            node = self.storage_nodes.get(replica.node_id)
            latency_penalty = node.latency_ms if node else 100
            reliability_bonus = (node.reliability_score * 10) if node else 0

            return (
                -primary_bonus,  # Negative so higher values come first
                -tier_bonus,
                latency_penalty,
                -reliability_bonus,
            )

        return sorted(replicas, key=preference_key)

    def _get_default_policy(self) -> DistributionPolicy:
        """Get default distribution policy."""
        return self.distribution_policies.get("default", DistributionPolicy())

    async def _save_replica_metadata(self, skill_id: str, replicas: list[StorageReplica]) -> None:
        """Save replica metadata to disk."""
        try:
            metadata_file = self.metadata_store / "replicas" / f"{skill_id}.json"
            with open(metadata_file, "w") as f:
                json.dump(
                    [
                        {
                            "replica_id": r.replica_id,
                            "skill_id": r.skill_id,
                            "node_id": r.node_id,
                            "storage_tier": r.storage_tier.value,
                            "created_at": r.created_at.isoformat(),
                            "last_updated": r.last_updated.isoformat(),
                            "size_bytes": r.size_bytes,
                            "checksum": r.checksum,
                            "is_primary": r.is_primary,
                        }
                        for r in replicas
                    ],
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save replica metadata for {skill_id}: {e}")

    async def _load_replica_metadata(self, skill_id: str) -> list[StorageReplica]:
        """Load replica metadata from disk."""
        try:
            metadata_file = self.metadata_store / "replicas" / f"{skill_id}.json"
            if not metadata_file.exists():
                return []

            with open(metadata_file) as f:
                data = json.load(f)

            return [
                StorageReplica(
                    replica_id=r["replica_id"],
                    skill_id=r["skill_id"],
                    node_id=r["node_id"],
                    storage_tier=StorageTier(r["storage_tier"]),
                    created_at=datetime.fromisoformat(r["created_at"]),
                    last_updated=datetime.fromisoformat(r["last_updated"]),
                    size_bytes=r["size_bytes"],
                    checksum=r["checksum"],
                    is_primary=r["is_primary"],
                )
                for r in data
            ]

        except Exception as e:
            logger.error(f"Failed to load replica metadata for {skill_id}: {e}")
            return []

    async def _delete_replica_metadata(self, skill_id: str) -> None:
        """Delete replica metadata from disk."""
        try:
            metadata_file = self.metadata_store / "replicas" / f"{skill_id}.json"
            if metadata_file.exists():
                metadata_file.unlink()

        except Exception as e:
            logger.error(f"Failed to delete replica metadata for {skill_id}: {e}")

    async def _save_node_metadata(self) -> None:
        """Save node metadata to disk."""
        try:
            metadata_file = self.metadata_store / "nodes" / "nodes.json"
            with open(metadata_file, "w") as f:
                json.dump(
                    {
                        node_id: {
                            "node_id": node.node_id,
                            "name": node.name,
                            "location": node.location,
                            "storage_type": node.storage_type,
                            "capacity_gb": node.capacity_gb,
                            "available_gb": node.available_gb,
                            "latency_ms": node.latency_ms,
                            "reliability_score": node.reliability_score,
                            "is_active": node.is_active,
                            "last_health_check": node.last_health_check.isoformat(),
                        }
                        for node_id, node in self.storage_nodes.items()
                    },
                    f,
                    indent=2,
                )

        except Exception as e:
            logger.error(f"Failed to save node metadata: {e}")

    async def _create_additional_replicas(
        self,
        skill_id: str,
        skill_data: dict[str, Any],
        current_replicas: list[StorageReplica],
        policy: DistributionPolicy,
    ) -> list[StorageReplica]:
        """Create additional replicas for existing skill."""
        try:
            # Determine what additional replicas are needed
            current_nodes = {r.node_id for r in current_replicas}
            available_nodes = [
                node for node_id, node in self.storage_nodes.items() if node.is_active and node_id not in current_nodes
            ]

            additional_replicas = []
            target_total = policy.replication_factor
            needed_count = max(0, target_total - len(current_replicas))

            for i in range(min(needed_count, len(available_nodes))):
                node = available_nodes[i % len(available_nodes)]

                # Determine tier for additional replica
                tier_distribution = list(policy.storage_tiers.items())
                tier = tier_distribution[i % len(tier_distribution)][0]

                replica = StorageReplica(
                    replica_id=str(uuid.uuid4()),
                    skill_id=skill_id,
                    node_id=node.node_id,
                    storage_tier=tier,
                    created_at=datetime.now(),
                    last_updated=datetime.now(),
                    size_bytes=len(json.dumps(skill_data).encode()),
                    checksum=self._calculate_checksum(skill_data),
                    is_primary=False,  # Additional replicas are not primary
                )

                additional_replicas.append(replica)

            return additional_replicas

        except Exception as e:
            logger.error(f"Failed to create additional replicas: {e}")
            return []

    async def _get_cluster_health(self) -> dict[str, Any]:
        """Get overall cluster health status."""
        try:
            total_nodes = len(self.storage_nodes)
            active_nodes = sum(1 for node in self.storage_nodes.values() if node.is_active)
            health_score = active_nodes / total_nodes if total_nodes > 0 else 0

            # Calculate storage health
            total_capacity = sum(node.capacity_gb for node in self.storage_nodes.values())
            total_available = sum(node.available_gb for node in self.storage_nodes.values())
            storage_health = total_available / total_capacity if total_capacity > 0 else 0

            # Calculate replica health
            total_replicas = sum(len(replicas) for replicas in self.replicas.values())
            healthy_replicas = 0  # Would need to check each replica

            return {
                "overall_health_score": (health_score + storage_health) / 2,
                "node_health": {
                    "total_nodes": total_nodes,
                    "active_nodes": active_nodes,
                    "health_score": health_score,
                },
                "storage_health": {
                    "total_capacity_gb": total_capacity,
                    "available_gb": total_available,
                    "utilization_percent": (1 - storage_health) * 100,
                    "health_score": storage_health,
                },
                "replica_health": {
                    "total_replicas": total_replicas,
                    "healthy_replicas": healthy_replicas,
                    "health_score": 1.0,  # Assume all replicas are healthy for now
                },
            }

        except Exception as e:
            logger.error(f"Failed to get cluster health: {e}")
            return {"error": str(e)}
