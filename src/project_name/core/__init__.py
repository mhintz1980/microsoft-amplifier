"""
Core FastAPI application initialization
"""

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import logging
from typing import Optional, Dict, Any
from datetime import datetime
import asyncio
import uuid

logger = logging.getLogger(__name__)


# Core database models
class UserBase(BaseModel):
    id: str
    email: str
    username: str
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None


class UserProfile(UserBase):
    user_id: str
    full_name: str
    bio: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: Dict[str, Any] = {}
    statistics: Dict[str, Any] = {}
    created_at: datetime
    updated_at: Optional[datetime] = None


class FileMetadata(BaseModel):
    id: str
    filename: str
    file_type: str  # 'image', 'document', 'video'
    file_size: int
    mime_type: Optional[str] = None
    uploaded_at: datetime
    user_id: str


class Skill(BaseModel):
    id: str
    name: str
    description: str
    category: str
    input_schema: Dict[str, Any] = {}
    output_schema: Dict[str, Any] = {}
    version: str = "1.0.0"
    is_active: bool = True
    created_at: datetime
    updated_at: Optional[datetime] = None
    parameters: Dict[str, Any] = {}
    success_rate: float = 0.0
    error_rate: float = 0.0
    average_response_time: float = 0.0
    tokens_used: int = 0
    total_executions: int = 0


class SkillExecution(BaseModel):
    id: str
    skill_id: str
    user_id: str
    input_data: Dict[str, Any] = {}
    status: str  # 'pending', 'running', 'completed', 'failed'
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    execution_time: float = 0.0
    tokens_used: int = 0
    started_at: datetime
    completed_at: Optional[datetime] = None
    metrics: Dict[str, Any] = {}


class LearningInsight(BaseModel):
    id: str
    skill_id: str
    insight_type: str
    description: str
    confidence: float = 0.0
    data: Dict[str, Any] = {}
    created_at: datetime


class PerformanceMetrics(BaseModel):
    timestamp: datetime
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    active_requests: int = 0
    throughput: float = 0.0
    error_rate: float = 0.0
    latency_p95: float = 0.0
    optimization_rate: float = 0.0


# Database connection and session management
class DatabaseManager:
    def __init__(self):
        self.connection_pool = {}
        self.active_connections: Dict[str, Dict[str, Any]] = {}

    async def get_connection(self, user_id: str):
        """Get database connection for user"""
        if user_id in self.active_connections:
            return self.active_connections[user_id]

        # Create new connection
        connection_id = str(uuid.uuid4())
        self.active_connections[user_id] = {
            "connection_id": connection_id,
            "user_id": user_id,
            "created_at": datetime.now(),
            "status": "active",
            "last_activity": datetime.now(),
        }

        return self.active_connections[user_id]

    async def execute_query(self, user_id: str, query: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute database query"""
        connection = await self.get_connection(user_id)

        try:
            # Mock query execution
            if "user" in query.lower():
                result = {"users": [f"User {i}" for i in range(1, 10)]}
                execution_time = 0.1
            else:
                result = {"error": "Query not supported"}
                execution_time = 0.05
        except Exception as e:
            result = {"error": str(e)}
            execution_time = 0.05

        # Update connection activity
        if user_id in self.active_connections:
            self.active_connections[user_id]["last_activity"] = datetime.now()

        return {
            "connection_id": connection_id,
            "user_id": user_id,
            "result": result,
            "execution_time": execution_time,
            "timestamp": datetime.now(),
        }


# In-memory storage for development (replace with persistent storage in production)
class MemoryStorage:
    def __init__(self):
        self.users: Dict[str, UserBase] = {}
        self.profiles: Dict[str, UserProfile] = {}
        self.files: Dict[str, FileMetadata] = {}
        self.skill_executions: Dict[str, List[SkillExecution]] = {}
        self.performance_metrics: Dict[str, PerformanceMetrics] = {}

        # Initialize with demo data
        self._initialize_demo_data()

    def _initialize_demo_data(self):
        """Initialize with demo data"""
        # Create demo users
        self.users["user1"] = UserBase(
            id="user1", email="user1@example.com", username="user1", is_active=True, created_at=datetime.now()
        )

        self.users["user2"] = UserBase(
            id="user2", email="user2@example.com", username="user2", is_active=True, created_at=datetime.now()
        )

        # Create demo skills
        demo_skill_id = "demo_analytics"
        self.profiles["user1"].statistics = {"total_queries": 150, "avg_response_time": 0.05, "success_rate": 0.95}

        self.skills[demo_skill_id] = Skill(
            id=demo_skill_id,
            name="Demo Analytics",
            description="Demonstrates analytics capabilities",
            category="analytics",
            version="1.0.0",
            is_active=True,
            created_at=datetime.now(),
            parameters={},
            success_rate=1.0,
            error_rate=0.0,
            tokens_used=5000,
            total_executions=150,
            average_response_time=0.05,
        )

    async def get_user(self, user_id: str) -> Optional[UserBase]:
        """Get user by ID"""
        return self.users.get(user_id)

    async def get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile by user ID"""
        user = await self.get_user(user_id)
        if user:
            # Check if user has a profile
            profile_id = f"profile_{user_id}"
            if profile_id in self.profiles:
                return self.profiles[profile_id]
            else:
                # Create default profile
                new_profile = UserProfile(
                    user_id=user_id, full_name=f"User {user_id}", bio=None, created_at=datetime.now()
                )
                self.profiles[profile_id] = new_profile
                self.users[user_id].preferences = {}
        return None

    async def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile"""
        profile_id = f"profile_{user_id}"
        if profile_id not in self.profiles:
            return False

        profile = self.profiles[profile_id]
        for key, value in profile_data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        profile.updated_at = datetime.now()
        return True

    async def execute_skill(self, user_id: str, skill_id: str, input_data: Dict[str, Any] = None) -> Dict[str, Any]:
        """Execute a skill and return results"""
        skill = self.skills.get(skill_id)
        if not skill:
            return {"error": "Skill not found"}

        execution_id = str(uuid.uuid4())

        # Start execution
        started_at = datetime.now()

        try:
            # Mock skill execution based on skill type
            if skill.category == "analytics":
                result_data = {"query_results": [{"metric": "total_users", "value": 2}]}
                execution_time = 0.1
            elif skill.category == "data_processing":
                result_data = {"processed_records": 100}
                execution_time = 0.05
            else:
                result_data = {"message": f"Executed {skill.name}"}
                execution_time = 0.05
        except Exception as e:
            error_message = str(e)
            return {
                "execution_id": execution_id,
                "user_id": user_id,
                "skill_id": skill_id,
                "status": "failed",
                "result_data": None,
                "error_message": error_message,
                "execution_time": 0.05,
                "started_at": started_at,
                "completed_at": None,
            }
        finally:
            # Record execution
            execution_record = SkillExecution(
                id=execution_id,
                skill_id=skill_id,
                user_id=user_id,
                input_data=input_data,
                status="completed",
                result_data=result_data,
                execution_time=execution_time,
                started_at=started_at,
                completed_at=datetime.now(),
            )

            # Update user statistics
            if user_id in self.profiles:
                self.profiles[user_id].statistics["total_executions"] = (
                    self.profiles[user_id].statistics.get("total_executions", 0) + 1
                )
                self.profiles[user_id].statistics["average_response_time"] = (
                    self.profiles[user_id].statistics.get("average_response_time", 0) * 0.95 + execution_time * 0.05
                ) / 1.005

        return {"execution_id": execution_id, "result": execution_record, "timestamp": datetime.now()}


# Request context management
class RequestContext:
    def __init__(self, user_id: str, skill_id: Optional[str] = None):
        self.user_id = user_id
        self.skill_id = skill_id
        self.request_data: Optional[Dict[str, Any]] = None
        self.metadata: Dict[str, Any] = {}
        self.start_time = datetime.now()

    def add_metadata(self, key: str, value: Any) -> None:
        """Add metadata to request context"""
        self.metadata[key] = value

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for logging"""
        return {
            "user_id": self.user_id,
            "skill_id": self.skill_id,
            "request_data": self.request_data,
            "metadata": self.metadata,
            "start_time": self.start_time.isoformat(),
        }


# Authentication service
class AuthService:
    def __init__(self):
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.api_keys: Dict[str, str] = {"demo_key": "demo_api_key_12345"}

    def authenticate_user(self, email: str, password: str) -> Optional[str]:
        """Mock authentication"""
        # In production, use proper password hashing
        if email in self.api_keys and password == "demo_password":
            session_id = str(uuid.uuid4())
            self.active_sessions[session_id] = {
                "session_id": session_id,
                "user_id": email,
                "created_at": datetime.now(),
                "expires_at": datetime.now() + timedelta(hours=1),
            }
            return session_id
        return None

    def validate_session(self, session_id: str) -> bool:
        """Validate session"""
        if session_id not in self.active_sessions:
            return False

        session = self.active_sessions[session_id]
        return datetime.now() < session["expires_at"]

    def get_user_from_session(self, session_id: str) -> Optional[str]:
        """Get user ID from session"""
        session = self.active_sessions.get(session_id)
        return session.get("user_id") if session else None

    def revoke_session(self, session_id: str) -> bool:
        """Revoke session"""
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            return True
        return False


# Performance monitoring service
class PerformanceMonitor:
    def __init__(self):
        self.metrics_history: Dict[str, List[PerformanceMetrics]] = {}
        self.alert_rules: Dict[str, Dict[str, Any]] = {}
        self.performance_thresholds = {
            "high_cpu": 80.0,
            "high_memory": 85.0,
            "high_latency": 500.0,
            "low_throughput": 1.0,
        }

        def _initialize_alert_rules(self):
            """Initialize default alert rules"""
            self.alert_rules["high_cpu"] = {
                "name": "High CPU Usage",
                "metric": "cpu_usage",
                "threshold": self.performance_thresholds["high_cpu"],
                "operator": ">",
                "severity": "high",
                "enabled": True,
            }
            # Add more alert rules as needed

    def record_metrics(self, user_id: str, metrics: PerformanceMetrics) -> None:
        """Record performance metrics"""
        timestamp = datetime.now()
        self.metrics_history[user_id] = self.metrics_history.get(user_id, [])

        # Add new metrics to history
        self.metrics_history[user_id].append(metrics)

        # Keep only last 1000 metrics per user
        if len(self.metrics_history[user_id]) > 1000:
            self.metrics_history[user_id] = self.metrics_history[user_id][-1000:]

        # Check alert conditions
        alerts = []
        for rule_id, rule in self.alert_rules.items():
            if rule["enabled"]:
                metric_value = getattr(metrics, rule["metric"], None)
                if metric_value is not None and self._check_alert_condition(rule, metric_value):
                    alert = {
                        "rule_id": rule_id,
                        "name": rule["name"],
                        "message": f"{rule['name']}: {metric_value:.2f} (threshold: {rule['threshold']})",
                        "timestamp": timestamp,
                        "metric_value": metric_value,
                        "threshold": rule["threshold"],
                        "severity": rule["severity"],
                    }
                    alerts.append(alert)

        return {"timestamp": timestamp, "alerts": alerts, "metrics": metrics.dict()}
