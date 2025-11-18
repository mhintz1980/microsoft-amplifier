"""
Quality Metrics Storage with MCP Integration

Persistent storage system for quality metrics, validation results, and
performance data using MCP storage for long-term retention and analysis.
"""

import json
import asyncio
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import gzip
import pickle

from amplifier.mcp.persistent_storage import store_result, retrieve_result


@dataclass
class QualityMetricsSnapshot:
    """Snapshot of quality metrics at a point in time."""

    skill_name: str
    timestamp: datetime
    validation_score: float
    test_coverage: float
    performance_score: float
    security_score: float
    compliance_score: float
    user_satisfaction: float
    metadata: Dict[str, Any]


@dataclass
class QualityTrendData:
    """Aggregated trend data for analysis."""

    skill_name: str
    metric_type: str
    time_period: str  # "daily", "weekly", "monthly"
    data_points: List[Dict[str, Any]]
    trend_analysis: Dict[str, Any]
    created_at: datetime


@dataclass
class QualityThresholds:
    """Configurable quality thresholds."""

    min_validation_score: float = 0.95
    min_test_coverage: float = 0.80
    min_performance_score: float = 0.75
    min_security_score: float = 0.90
    min_compliance_score: float = 0.85
    max_error_rate: float = 0.02


class QualityMetricsStorage:
    """Persistent storage system for quality metrics using MCP."""

    def __init__(self, retention_days: int = 365, compression_enabled: bool = True, cache_size: int = 1000):
        """
        Initialize quality metrics storage.

        Args:
            retention_days: Number of days to retain metrics
            compression_enabled: Enable data compression for storage
            cache_size: Size of in-memory cache
        """
        self.retention_days = retention_days
        self.compression_enabled = compression_enabled
        self.cache_size = cache_size

        # In-memory cache for frequently accessed data
        self.cache: Dict[str, Any] = {}
        self.cache_timestamps: Dict[str, datetime] = {}

        # Storage namespaces
        self.snapshots_namespace = "quality_metrics_snapshots"
        self.trends_namespace = "quality_trends"
        self.thresholds_namespace = "quality_thresholds"
        self.aggregated_namespace = "quality_aggregated"

    async def store_snapshot(self, snapshot: QualityMetricsSnapshot) -> bool:
        """
        Store a quality metrics snapshot.

        Args:
            snapshot: Quality metrics snapshot to store

        Returns:
            True if stored successfully
        """
        try:
            # Prepare data for storage
            snapshot_data = asdict(snapshot)
            snapshot_data["timestamp"] = snapshot.timestamp.isoformat()

            # Create storage key
            key = f"{snapshot.skill_name}_{snapshot.timestamp.strftime('%Y%m%d_%H%M%S')}"

            # Compress data if enabled
            if self.compression_enabled:
                serialized_data = self._compress_data(snapshot_data)
            else:
                serialized_data = snapshot_data

            # Store in MCP
            await store_result(
                namespace=self.snapshots_namespace, key=key, data=serialized_data, compressed=self.compression_enabled
            )

            # Update cache
            self._update_cache(f"snapshot_{snapshot.skill_name}", snapshot_data)

            return True

        except Exception:
            return False

    async def retrieve_snapshots(
        self,
        skill_name: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 100,
    ) -> List[QualityMetricsSnapshot]:
        """
        Retrieve quality metrics snapshots.

        Args:
            skill_name: Name of the skill
            start_date: Start date for retrieval
            end_date: End date for retrieval
            limit: Maximum number of snapshots to retrieve

        Returns:
            List of quality metrics snapshots
        """
        try:
            # Check cache first
            cache_key = f"snapshots_{skill_name}_{start_date}_{end_date}_{limit}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                return [self._deserialize_snapshot(data) for data in cached_data]

            # Build query for MCP storage
            snapshots = []

            # In a real implementation, you'd query MCP storage with filters
            # For now, return cached or simulated data
            query_key = f"{skill_name}_"

            # Simulate retrieval (actual implementation would query MCP)
            for i in range(min(limit, 10)):  # Simulate up to 10 snapshots
                snapshot_data = {
                    "skill_name": skill_name,
                    "timestamp": datetime.now() - timedelta(hours=i),
                    "validation_score": 0.9 + (i * 0.01),
                    "test_coverage": 0.8 + (i * 0.02),
                    "performance_score": 0.85 + (i * 0.01),
                    "security_score": 0.95 + (i * 0.005),
                    "compliance_score": 0.9 + (i * 0.01),
                    "user_satisfaction": 4.2 + (i * 0.1),
                    "metadata": {"simulated": True},
                }

                # Apply date filters
                snapshot_time = snapshot_data["timestamp"]
                if start_date and snapshot_time < start_date:
                    continue
                if end_date and snapshot_time > end_date:
                    continue

                snapshots.append(self._deserialize_snapshot(snapshot_data))

            # Update cache
            serialized_snapshots = [asdict(s) for s in snapshots]
            for s in serialized_snapshots:
                s["timestamp"] = s["timestamp"].isoformat()
            self._update_cache(cache_key, serialized_snapshots)

            return snapshots

        except Exception:
            return []

    async def store_trend_data(self, trend_data: QualityTrendData) -> bool:
        """
        Store aggregated trend data.

        Args:
            trend_data: Trend data to store

        Returns:
            True if stored successfully
        """
        try:
            # Prepare data for storage
            data = asdict(trend_data)
            data["created_at"] = trend_data.created_at.isoformat()

            # Create storage key
            key = f"{trend_data.skill_name}_{trend_data.metric_type}_{trend_data.time_period}_{trend_data.created_at.strftime('%Y%m%d')}"

            # Store in MCP
            await store_result(namespace=self.trends_namespace, key=key, data=data)

            # Update cache
            self._update_cache(f"trend_{trend_data.skill_name}_{trend_data.metric_type}", data)

            return True

        except Exception:
            return False

    async def retrieve_trend_data(
        self, skill_name: str, metric_type: Optional[str] = None, time_period: str = "daily", days_back: int = 30
    ) -> List[QualityTrendData]:
        """
        Retrieve trend data for analysis.

        Args:
            skill_name: Name of the skill
            metric_type: Type of metric to retrieve
            time_period: Time period for trend data
            days_back: Number of days to look back

        Returns:
            List of trend data
        """
        try:
            # Check cache first
            cache_key = f"trends_{skill_name}_{metric_type}_{time_period}_{days_back}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                return [self._deserialize_trend_data(data) for data in cached_data]

            trend_data_list = []

            # Simulate retrieval (actual implementation would query MCP)
            for i in range(days_back // 7):  # Weekly data
                data = {
                    "skill_name": skill_name,
                    "metric_type": metric_type or "validation_score",
                    "time_period": time_period,
                    "data_points": [
                        {
                            "date": (datetime.now() - timedelta(days=i * 7 + j)).isoformat(),
                            "value": 0.85 + (i * 0.01) + (j * 0.005),
                        }
                        for j in range(7)
                    ],
                    "trend_analysis": {
                        "direction": "improving" if i % 2 == 0 else "stable",
                        "slope": 0.01 * (i % 3),
                        "correlation": 0.8,
                    },
                    "created_at": (datetime.now() - timedelta(days=i * 7)).isoformat(),
                }
                trend_data_list.append(self._deserialize_trend_data(data))

            # Update cache
            serialized_data = [asdict(t) for t in trend_data_list]
            for t in serialized_data:
                t["created_at"] = t["created_at"].isoformat()
            self._update_cache(cache_key, serialized_data)

            return trend_data_list

        except Exception:
            return []

    async def store_thresholds(self, skill_name: str, thresholds: QualityThresholds) -> bool:
        """
        Store quality thresholds for a skill.

        Args:
            skill_name: Name of the skill
            thresholds: Quality thresholds

        Returns:
            True if stored successfully
        """
        try:
            # Prepare data
            data = asdict(thresholds)
            data["updated_at"] = datetime.now().isoformat()

            # Store in MCP
            await store_result(namespace=self.thresholds_namespace, key=f"{skill_name}_thresholds", data=data)

            # Update cache
            self._update_cache(f"thresholds_{skill_name}", data)

            return True

        except Exception:
            return False

    async def retrieve_thresholds(self, skill_name: str) -> Optional[QualityThresholds]:
        """
        Retrieve quality thresholds for a skill.

        Args:
            skill_name: Name of the skill

        Returns:
            Quality thresholds if found
        """
        try:
            # Check cache first
            cache_key = f"thresholds_{skill_name}"
            if cache_key in self.cache:
                cached_data = self.cache[cache_key]
                return QualityThresholds(**cached_data)

            # Retrieve from MCP
            try:
                data = await retrieve_result(namespace=self.thresholds_namespace, key=f"{skill_name}_thresholds")
                if data:
                    thresholds = QualityThresholds(**data)
                    self._update_cache(cache_key, data)
                    return thresholds
            except Exception:
                pass

            # Return default thresholds
            return QualityThresholds()

        except Exception:
            return None

    async def get_aggregated_metrics(
        self, skill_name: str, period: str = "week", metric_types: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated quality metrics for a skill.

        Args:
            skill_name: Name of the skill
            period: Aggregation period ("day", "week", "month")
            metric_types: Types of metrics to aggregate

        Returns:
            Aggregated metrics dictionary
        """
        try:
            # Check cache first
            cache_key = f"aggregated_{skill_name}_{period}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Retrieve recent snapshots
            days_back = 1 if period == "day" else 7 if period == "week" else 30
            snapshots = await self.retrieve_snapshots(skill_name=skill_name, limit=days_back)

            if not snapshots:
                return {}

            # Aggregate metrics
            aggregated = {
                "skill_name": skill_name,
                "period": period,
                "snapshot_count": len(snapshots),
                "date_range": {
                    "start": min(s.timestamp for s in snapshots).isoformat(),
                    "end": max(s.timestamp for s in snapshots).isoformat(),
                },
            }

            # Calculate aggregates for each metric type
            metric_fields = [
                "validation_score",
                "test_coverage",
                "performance_score",
                "security_score",
                "compliance_score",
                "user_satisfaction",
            ]

            if metric_types:
                metric_fields = [m for m in metric_fields if m in metric_fields]

            for field in metric_fields:
                values = [getattr(s, field) for s in snapshots if hasattr(s, field)]
                if values:
                    aggregated[field] = {
                        "average": sum(values) / len(values),
                        "min": min(values),
                        "max": max(values),
                        "latest": values[-1] if values else None,
                        "trend": self._calculate_simple_trend(values),
                    }

            # Store aggregation
            await store_result(
                namespace=self.aggregated_namespace,
                key=f"{skill_name}_{period}_{datetime.now().strftime('%Y%m%d')}",
                data=aggregated,
            )

            # Update cache
            self._update_cache(cache_key, aggregated)

            return aggregated

        except Exception:
            return {}

    async def get_quality_summary(self, skill_name: Optional[str] = None, days_back: int = 7) -> Dict[str, Any]:
        """
        Get comprehensive quality summary.

        Args:
            skill_name: Specific skill name (None for all skills)
            days_back: Number of days to include

        Returns:
            Quality summary dictionary
        """
        try:
            summary = {"generated_at": datetime.now().isoformat(), "period_days": days_back, "skills": {}}

            if skill_name:
                skills = [skill_name]
            else:
                # Get list of all skills (simplified)
                skills = ["skill_1", "skill_2", "skill_3"]  # In practice, query storage

            for skill in skills:
                # Get aggregated metrics
                aggregated = await self.get_aggregated_metrics(skill_name=skill, period="week")

                # Get thresholds
                thresholds = await self.retrieve_thresholds(skill)

                # Calculate compliance with thresholds
                compliance = {}
                if aggregated and thresholds:
                    for metric in [
                        "validation_score",
                        "test_coverage",
                        "performance_score",
                        "security_score",
                        "compliance_score",
                    ]:
                        if metric in aggregated and hasattr(thresholds, f"min_{metric}"):
                            threshold_value = getattr(thresholds, f"min_{metric}")
                            actual_value = aggregated[metric]["average"]
                            compliance[metric] = {
                                "compliant": actual_value >= threshold_value,
                                "threshold": threshold_value,
                                "actual": actual_value,
                                "gap": max(0, threshold_value - actual_value),
                            }

                summary["skills"][skill] = {
                    "aggregated_metrics": aggregated,
                    "compliance": compliance,
                    "overall_health": self._calculate_overall_health(compliance),
                }

            return summary

        except Exception:
            return {"error": "Failed to generate quality summary"}

    async def cleanup_old_data(self) -> int:
        """
        Clean up data older than retention period.

        Returns:
            Number of records cleaned up
        """
        try:
            cutoff_date = datetime.now() - timedelta(days=self.retention_days)
            cleaned_count = 0

            # In a real implementation, you'd query MCP storage for old records
            # and delete them. For now, simulate cleanup.

            # Clear old cache entries
            keys_to_remove = []
            for key, timestamp in self.cache_timestamps.items():
                if timestamp < cutoff_date:
                    keys_to_remove.append(key)

            for key in keys_to_remove:
                if key in self.cache:
                    del self.cache[key]
                if key in self.cache_timestamps:
                    del self.cache_timestamps[key]
                cleaned_count += 1

            return cleaned_count

        except Exception:
            return 0

    def _update_cache(self, key: str, data: Any):
        """Update in-memory cache."""
        # Remove oldest entries if cache is full
        if len(self.cache) >= self.cache_size:
            oldest_key = min(self.cache_timestamps.keys(), key=lambda k: self.cache_timestamps[k])
            if oldest_key in self.cache:
                del self.cache[oldest_key]
            if oldest_key in self.cache_timestamps:
                del self.cache_timestamps[oldest_key]

        # Add new entry
        self.cache[key] = data
        self.cache_timestamps[key] = datetime.now()

    def _compress_data(self, data: Dict[str, Any]) -> bytes:
        """Compress data for storage."""
        json_str = json.dumps(data, default=str)
        return gzip.compress(json_str.encode("utf-8"))

    def _decompress_data(self, compressed_data: bytes) -> Dict[str, Any]:
        """Decompress stored data."""
        json_str = gzip.decompress(compressed_data).decode("utf-8")
        return json.loads(json_str)

    def _deserialize_snapshot(self, data: Dict[str, Any]) -> QualityMetricsSnapshot:
        """Deserialize snapshot data."""
        if isinstance(data.get("timestamp"), str):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return QualityMetricsSnapshot(**data)

    def _deserialize_trend_data(self, data: Dict[str, Any]) -> QualityTrendData:
        """Deserialize trend data."""
        if isinstance(data.get("created_at"), str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return QualityTrendData(**data)

    def _calculate_simple_trend(self, values: List[float]) -> str:
        """Calculate simple trend direction."""
        if len(values) < 2:
            return "insufficient_data"

        # Simple comparison of first and last values
        if values[-1] > values[0] * 1.05:
            return "improving"
        elif values[-1] < values[0] * 0.95:
            return "degrading"
        else:
            return "stable"

    def _calculate_overall_health(self, compliance: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate overall health score."""
        if not compliance:
            return {"score": 0.0, "status": "unknown"}

        compliant_count = sum(1 for c in compliance.values() if c.get("compliant", False))
        total_count = len(compliance)

        if total_count == 0:
            score = 0.0
        else:
            score = compliant_count / total_count

        if score >= 0.9:
            status = "excellent"
        elif score >= 0.8:
            status = "good"
        elif score >= 0.6:
            status = "fair"
        else:
            status = "poor"

        return {"score": score, "status": status, "compliant_metrics": compliant_count, "total_metrics": total_count}

    async def export_data(
        self, skill_name: Optional[str] = None, format_type: str = "json", days_back: int = 30
    ) -> Optional[bytes]:
        """
        Export quality data for analysis.

        Args:
            skill_name: Specific skill name (None for all)
            format_type: Export format ("json", "csv", "parquet")
            days_back: Number of days to include

        Returns:
            Exported data as bytes
        """
        try:
            # Collect data
            if skill_name:
                snapshots = await self.retrieve_snapshots(skill_name, limit=days_back)
                trend_data = await self.retrieve_trend_data(skill_name, days_back=days_back)
            else:
                # In a real implementation, collect all skill data
                snapshots = []
                trend_data = []

            export_data = {
                "export_timestamp": datetime.now().isoformat(),
                "skill_name": skill_name,
                "period_days": days_back,
                "snapshots": [asdict(s) for s in snapshots],
                "trend_data": [asdict(t) for t in trend_data],
            }

            # Serialize in requested format
            if format_type == "json":
                json_str = json.dumps(export_data, default=str, indent=2)
                return json_str.encode("utf-8")
            elif format_type == "csv":
                # Convert to CSV format (simplified)
                import csv
                import io

                if snapshots:
                    output = io.StringIO()
                    writer = csv.writer(output)
                    writer.writerow(
                        [
                            "skill_name",
                            "timestamp",
                            "validation_score",
                            "test_coverage",
                            "performance_score",
                            "security_score",
                            "compliance_score",
                            "user_satisfaction",
                        ]
                    )

                    for snapshot in snapshots:
                        writer.writerow(
                            [
                                snapshot.skill_name,
                                snapshot.timestamp.isoformat(),
                                snapshot.validation_score,
                                snapshot.test_coverage,
                                snapshot.performance_score,
                                snapshot.security_score,
                                snapshot.compliance_score,
                                snapshot.user_satisfaction,
                            ]
                        )
                    return output.getvalue().encode("utf-8")

            return None

        except Exception:
            return None
