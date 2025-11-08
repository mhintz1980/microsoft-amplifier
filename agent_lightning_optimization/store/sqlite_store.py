"""
SQLite Lightning Store for Persistent Storage of Agent Lightning Training Data.

This module provides a robust, persistent storage solution for Agent Lightning training
sessions, model checkpoints, and optimization history. It replaces the in-memory
storage with a scalable SQLite-based solution.
"""

import json
import threading
from contextlib import asynccontextmanager
from dataclasses import asdict
from datetime import datetime
from pathlib import Path
from typing import Any
from typing import Union

import aiosqlite
from pydantic import BaseModel

from ..utils.logger import get_logger

logger = get_logger(__name__)


class TrainingSession(BaseModel):
    """Model for training session metadata."""

    session_id: str
    agent_name: str
    algorithm: str
    start_time: datetime
    end_time: datetime | None = None
    status: str = "running"  # running, completed, failed, paused
    config: dict[str, Any]
    final_metrics: dict[str, Any] | None = None
    best_model_path: str | None = None


class ModelCheckpoint(BaseModel):
    """Model for model checkpoint information."""

    checkpoint_id: str
    session_id: str
    epoch: int
    step: int
    loss: float
    metrics: dict[str, float]
    model_path: str
    created_at: datetime
    is_best: bool = False


class PromptOptimizationRecord(BaseModel):
    """Model for prompt optimization records."""

    optimization_id: str
    session_id: str
    template_name: str
    iteration: int
    reward: float
    prompt_content: str
    metrics: dict[str, float]
    created_at: datetime


class TrainingMetrics(BaseModel):
    """Model for training metrics."""

    metrics_id: str
    session_id: str
    epoch: int
    step: int
    timestamp: datetime
    metrics: dict[str, float]


class SQLiteLightningStore:
    """Persistent SQLite-based storage for Agent Lightning."""

    def __init__(self, db_path: Union[str, Path]):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._lock = threading.Lock()
        self._connection_pool = []

    async def initialize(self):
        """Initialize the database and create tables."""
        logger.info(f"Initializing SQLite store at {self.db_path}")

        async with aiosqlite.connect(self.db_path) as db:
            await db.executescript("""
                CREATE TABLE IF NOT EXISTS training_sessions (
                    session_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    algorithm TEXT NOT NULL,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    status TEXT NOT NULL DEFAULT 'running',
                    config TEXT NOT NULL,
                    final_metrics TEXT,
                    best_model_path TEXT
                );

                CREATE TABLE IF NOT EXISTS model_checkpoints (
                    checkpoint_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    epoch INTEGER NOT NULL,
                    step INTEGER NOT NULL,
                    loss REAL NOT NULL,
                    metrics TEXT NOT NULL,
                    model_path TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    is_best BOOLEAN NOT NULL DEFAULT FALSE,
                    FOREIGN KEY (session_id) REFERENCES training_sessions (session_id)
                );

                CREATE TABLE IF NOT EXISTS prompt_optimizations (
                    optimization_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    template_name TEXT NOT NULL,
                    iteration INTEGER NOT NULL,
                    reward REAL NOT NULL,
                    prompt_content TEXT NOT NULL,
                    metrics TEXT NOT NULL,
                    created_at TIMESTAMP NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES training_sessions (session_id)
                );

                CREATE TABLE IF NOT EXISTS training_metrics (
                    metrics_id TEXT PRIMARY KEY,
                    session_id TEXT NOT NULL,
                    epoch INTEGER NOT NULL,
                    step INTEGER NOT NULL,
                    timestamp TIMESTAMP NOT NULL,
                    metrics TEXT NOT NULL,
                    FOREIGN KEY (session_id) REFERENCES training_sessions (session_id)
                );

                CREATE INDEX IF NOT EXISTS idx_sessions_agent ON training_sessions (agent_name);
                CREATE INDEX IF NOT EXISTS idx_sessions_status ON training_sessions (status);
                CREATE INDEX IF NOT EXISTS idx_checkpoints_session ON model_checkpoints (session_id);
                CREATE INDEX IF NOT EXISTS idx_checkpoints_epoch ON model_checkpoints (session_id, epoch);
                CREATE INDEX IF NOT EXISTS idx_optimizations_session ON prompt_optimizations (session_id);
                CREATE INDEX IF NOT EXISTS idx_optimizations_iteration ON prompt_optimizations (session_id, iteration);
                CREATE INDEX IF NOT EXISTS idx_metrics_session ON training_metrics (session_id);
                CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON training_metrics (timestamp);
            """)

            await db.commit()

        logger.info("SQLite store initialized successfully")

    @asynccontextmanager
    async def get_connection(self):
        """Get a database connection from the pool."""
        async with aiosqlite.connect(self.db_path) as db:
            # Enable WAL mode for better concurrency
            await db.execute("PRAGMA journal_mode = WAL")
            yield db

    async def create_training_session(
        self, session_id: str, agent_name: str, algorithm: str, config: dict[str, Any]
    ) -> TrainingSession:
        """Create a new training session."""
        session = TrainingSession(
            session_id=session_id, agent_name=agent_name, algorithm=algorithm, start_time=datetime.now(), config=config
        )

        async with self.get_connection() as db:
            await db.execute(
                """
                INSERT INTO training_sessions
                (session_id, agent_name, algorithm, start_time, status, config)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    session.session_id,
                    session.agent_name,
                    session.algorithm,
                    session.start_time.isoformat(),
                    session.status,
                    json.dumps(session.config),
                ),
            )
            await db.commit()

        logger.info(f"Created training session {session_id}")
        return session

    async def get_training_session(self, session_id: str) -> TrainingSession | None:
        """Get a training session by ID."""
        async with self.get_connection() as db:
            cursor = await db.execute("SELECT * FROM training_sessions WHERE session_id = ?", (session_id,))
            row = await cursor.fetchone()

            if row:
                return self._row_to_training_session(row)
            return None

    async def update_training_session(self, session_id: str, **kwargs) -> bool:
        """Update a training session."""
        if not kwargs:
            return False

        # Build dynamic update query
        set_clauses = []
        values = []

        for key, value in kwargs.items():
            if key in ["status", "end_time", "final_metrics", "best_model_path"]:
                set_clauses.append(f"{key} = ?")
                if isinstance(value, dict | list):
                    values.append(json.dumps(value))
                elif isinstance(value, datetime):
                    values.append(value.isoformat())
                else:
                    values.append(value)

        if not set_clauses:
            return False

        set_clauses.append("updated_at = ?")
        values.append(datetime.now().isoformat())
        values.append(session_id)

        query = f"UPDATE training_sessions SET {', '.join(set_clauses)} WHERE session_id = ?"

        async with self.get_connection() as db:
            cursor = await db.execute(query, values)
            await db.commit()
            return cursor.rowcount > 0

    async def list_training_sessions(
        self, agent_name: str | None = None, status: str | None = None, limit: int = 100
    ) -> list[TrainingSession]:
        """List training sessions with optional filtering."""
        query = "SELECT * FROM training_sessions"
        params = []
        conditions = []

        if agent_name:
            conditions.append("agent_name = ?")
            params.append(agent_name)

        if status:
            conditions.append("status = ?")
            params.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY start_time DESC LIMIT ?"
        params.append(limit)

        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_training_session(row) for row in rows]

    async def save_model_checkpoint(self, checkpoint: ModelCheckpoint) -> bool:
        """Save a model checkpoint."""
        async with self.get_connection() as db:
            await db.execute(
                """
                INSERT OR REPLACE INTO model_checkpoints
                (checkpoint_id, session_id, epoch, step, loss, metrics, model_path, created_at, is_best)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    checkpoint.checkpoint_id,
                    checkpoint.session_id,
                    checkpoint.epoch,
                    checkpoint.step,
                    checkpoint.loss,
                    json.dumps(checkpoint.metrics),
                    checkpoint.model_path,
                    checkpoint.created_at.isoformat(),
                    checkpoint.is_best,
                ),
            )
            await db.commit()

        logger.debug(f"Saved checkpoint {checkpoint.checkpoint_id}")
        return True

    async def get_model_checkpoints(self, session_id: str, best_only: bool = False) -> list[ModelCheckpoint]:
        """Get model checkpoints for a session."""
        query = "SELECT * FROM model_checkpoints WHERE session_id = ?"
        params = [session_id]

        if best_only:
            query += " AND is_best = TRUE"

        query += " ORDER BY epoch DESC, step DESC"

        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_model_checkpoint(row) for row in rows]

    async def get_best_checkpoint(self, session_id: str) -> ModelCheckpoint | None:
        """Get the best checkpoint for a session."""
        async with self.get_connection() as db:
            cursor = await db.execute(
                """
                SELECT * FROM model_checkpoints
                WHERE session_id = ? AND is_best = TRUE
                ORDER BY epoch DESC, step DESC
                LIMIT 1
                """,
                (session_id,),
            )
            row = await cursor.fetchone()
            return self._row_to_model_checkpoint(row) if row else None

    async def save_prompt_optimization(self, optimization: PromptOptimizationRecord) -> bool:
        """Save a prompt optimization record."""
        async with self.get_connection() as db:
            await db.execute(
                """
                INSERT INTO prompt_optimizations
                (optimization_id, session_id, template_name, iteration, reward, prompt_content, metrics, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    optimization.optimization_id,
                    optimization.session_id,
                    optimization.template_name,
                    optimization.iteration,
                    optimization.reward,
                    optimization.prompt_content,
                    json.dumps(optimization.metrics),
                    optimization.created_at.isoformat(),
                ),
            )
            await db.commit()

        logger.debug(f"Saved prompt optimization {optimization.optimization_id}")
        return True

    async def get_prompt_optimizations(
        self, session_id: str, template_name: str | None = None
    ) -> list[PromptOptimizationRecord]:
        """Get prompt optimization records."""
        query = "SELECT * FROM prompt_optimizations WHERE session_id = ?"
        params = [session_id]

        if template_name:
            query += " AND template_name = ?"
            params.append(template_name)

        query += " ORDER BY iteration ASC"

        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_prompt_optimization(row) for row in rows]

    async def get_optimization_progress(self, session_id: str) -> dict[str, Any]:
        """Get optimization progress for a session."""
        async with self.get_connection() as db:
            # Get best reward
            cursor = await db.execute(
                "SELECT MAX(reward) as best_reward, COUNT(*) as total_iterations "
                "FROM prompt_optimizations WHERE session_id = ?",
                (session_id,),
            )
            reward_row = await cursor.fetchone()

            # Get recent iterations
            cursor = await db.execute(
                """
                SELECT iteration, reward
                FROM prompt_optimizations
                WHERE session_id = ?
                ORDER BY iteration DESC
                LIMIT 10
                """,
                (session_id,),
            )
            recent_rows = await cursor.fetchall()

            # Get checkpoints
            cursor = await db.execute(
                "SELECT COUNT(*) as checkpoint_count FROM model_checkpoints WHERE session_id = ?", (session_id,)
            )
            checkpoint_row = await cursor.fetchone()

            return {
                "best_reward": reward_row[0] if reward_row[0] else 0.0,
                "total_iterations": reward_row[1] or 0,
                "recent_rewards": [(row[0], row[1]) for row in recent_rows][::-1],  # Reverse for chronological order
                "checkpoint_count": checkpoint_row[0] or 0,
            }

    async def save_training_metrics(self, metrics: TrainingMetrics) -> bool:
        """Save training metrics."""
        async with self.get_connection() as db:
            await db.execute(
                """
                INSERT INTO training_metrics
                (metrics_id, session_id, epoch, step, timestamp, metrics)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    metrics.metrics_id,
                    metrics.session_id,
                    metrics.epoch,
                    metrics.step,
                    metrics.timestamp.isoformat(),
                    json.dumps(metrics.metrics),
                ),
            )
            await db.commit()

        return True

    async def get_training_metrics(self, session_id: str, last_n: int | None = None) -> list[TrainingMetrics]:
        """Get training metrics for a session."""
        query = "SELECT * FROM training_metrics WHERE session_id = ? ORDER BY timestamp ASC"
        params = [session_id]

        if last_n:
            query = "SELECT * FROM (SELECT * FROM training_metrics WHERE session_id = ? ORDER BY timestamp DESC LIMIT ?) ORDER BY timestamp ASC"
            params.append(last_n)

        async with self.get_connection() as db:
            cursor = await db.execute(query, params)
            rows = await cursor.fetchall()
            return [self._row_to_training_metrics(row) for row in rows]

    async def cleanup_old_sessions(self, days_old: int = 30) -> int:
        """Clean up old training sessions."""
        cutoff_date = datetime.now().timestamp() - (days_old * 24 * 3600)

        async with self.get_connection() as db:
            # Delete old sessions and related data
            await db.execute("DELETE FROM training_sessions WHERE start_time < ?", (cutoff_date,))

            # Get count of deleted rows (approximate)
            cursor = await db.execute("SELECT changes()")
            deleted_count = (await cursor.fetchone())[0]

            await db.commit()

        logger.info(f"Cleaned up {deleted_count} old training sessions")
        return deleted_count

    async def get_storage_stats(self) -> dict[str, Any]:
        """Get storage statistics."""
        async with self.get_connection() as db:
            stats = {}

            # Session counts
            cursor = await db.execute("SELECT COUNT(*) FROM training_sessions")
            stats["total_sessions"] = (await cursor.fetchone())[0]

            cursor = await db.execute("SELECT COUNT(*) FROM training_sessions WHERE status = 'completed'")
            stats["completed_sessions"] = (await cursor.fetchone())[0]

            # Checkpoint counts
            cursor = await db.execute("SELECT COUNT(*) FROM model_checkpoints")
            stats["total_checkpoints"] = (await cursor.fetchone())[0]

            # Optimization counts
            cursor = await db.execute("SELECT COUNT(*) FROM prompt_optimizations")
            stats["total_optimizations"] = (await cursor.fetchone())[0]

            # Database size
            db_size = self.db_path.stat().st_size if self.db_path.exists() else 0
            stats["database_size_bytes"] = db_size
            stats["database_size_mb"] = round(db_size / (1024 * 1024), 2)

            return stats

    async def export_session_data(self, session_id: str, export_path: Path) -> bool:
        """Export all data for a training session."""
        try:
            session = await self.get_training_session(session_id)
            if not session:
                logger.error(f"Session {session_id} not found")
                return False

            export_data = {
                "session": asdict(session),
                "checkpoints": [asdict(cp) for cp in await self.get_model_checkpoints(session_id)],
                "optimizations": [asdict(opt) for opt in await self.get_prompt_optimizations(session_id)],
                "metrics": [asdict(m) for m in await self.get_training_metrics(session_id)],
            }

            export_path.parent.mkdir(parents=True, exist_ok=True)
            with open(export_path, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            logger.info(f"Exported session {session_id} to {export_path}")
            return True

        except Exception as e:
            logger.error(f"Failed to export session {session_id}: {e}")
            return False

    async def import_session_data(self, import_path: Path, new_session_id: str | None = None) -> str | None:
        """Import session data from a JSON file."""
        try:
            with open(import_path) as f:
                import_data = json.load(f)

            # Generate new session ID if not provided
            if new_session_id:
                import_data["session"]["session_id"] = new_session_id

            session_id = import_data["session"]["session_id"]

            # Import session
            session_data = import_data["session"]
            await self.create_training_session(
                session_id=session_data["session_id"],
                agent_name=session_data["agent_name"],
                algorithm=session_data["algorithm"],
                config=session_data["config"],
            )

            # Import checkpoints
            for cp_data in import_data.get("checkpoints", []):
                checkpoint = ModelCheckpoint(**cp_data)
                await self.save_model_checkpoint(checkpoint)

            # Import optimizations
            for opt_data in import_data.get("optimizations", []):
                optimization = PromptOptimizationRecord(**opt_data)
                await self.save_prompt_optimization(optimization)

            # Import metrics
            for metrics_data in import_data.get("metrics", []):
                metrics = TrainingMetrics(**metrics_data)
                await self.save_training_metrics(metrics)

            logger.info(f"Imported session {session_id} from {import_path}")
            return session_id

        except Exception as e:
            logger.error(f"Failed to import session from {import_path}: {e}")
            return None

    def _row_to_training_session(self, row) -> TrainingSession:
        """Convert database row to TrainingSession."""
        return TrainingSession(
            session_id=row[0],
            agent_name=row[1],
            algorithm=row[2],
            start_time=datetime.fromisoformat(row[3]),
            end_time=datetime.fromisoformat(row[4]) if row[4] else None,
            status=row[5],
            config=json.loads(row[6]),
            final_metrics=json.loads(row[7]) if row[7] else None,
            best_model_path=row[8],
        )

    def _row_to_model_checkpoint(self, row) -> ModelCheckpoint:
        """Convert database row to ModelCheckpoint."""
        return ModelCheckpoint(
            checkpoint_id=row[0],
            session_id=row[1],
            epoch=row[2],
            step=row[3],
            loss=row[4],
            metrics=json.loads(row[5]),
            model_path=row[6],
            created_at=datetime.fromisoformat(row[7]),
            is_best=bool(row[8]),
        )

    def _row_to_prompt_optimization(self, row) -> PromptOptimizationRecord:
        """Convert database row to PromptOptimizationRecord."""
        return PromptOptimizationRecord(
            optimization_id=row[0],
            session_id=row[1],
            template_name=row[2],
            iteration=row[3],
            reward=row[4],
            prompt_content=row[5],
            metrics=json.loads(row[6]),
            created_at=datetime.fromisoformat(row[7]),
        )

    def _row_to_training_metrics(self, row) -> TrainingMetrics:
        """Convert database row to TrainingMetrics."""
        return TrainingMetrics(
            metrics_id=row[0],
            session_id=row[1],
            epoch=row[2],
            step=row[3],
            timestamp=datetime.fromisoformat(row[4]),
            metrics=json.loads(row[5]),
        )


class LightningStoreManager:
    """Manager for SQLite Lightning Store with backup and recovery."""

    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.base_path.mkdir(parents=True, exist_ok=True)
        self.stores: dict[str, SQLiteLightningStore] = {}

    def get_store(self, store_name: str = "default") -> SQLiteLightningStore:
        """Get or create a store instance."""
        if store_name not in self.stores:
            db_path = self.base_path / f"{store_name}.db"
            self.stores[store_name] = SQLiteLightningStore(db_path)
        return self.stores[store_name]

    async def initialize_all_stores(self):
        """Initialize all stores."""
        for store in self.stores.values():
            await store.initialize()

    async def backup_all_stores(self, backup_dir: Path):
        """Backup all stores to specified directory."""
        backup_dir.mkdir(parents=True, exist_ok=True)

        for store_name, store in self.stores.items():
            backup_path = backup_dir / f"{store_name}.db"
            if store.db_path.exists():
                import shutil

                shutil.copy2(store.db_path, backup_path)
                logger.info(f"Backed up store {store_name} to {backup_path}")

    async def cleanup_stores(self, days_old: int = 30):
        """Cleanup old data in all stores."""
        total_deleted = 0
        for store in self.stores.values():
            deleted = await store.cleanup_old_sessions(days_old)
            total_deleted += deleted
        return total_deleted
