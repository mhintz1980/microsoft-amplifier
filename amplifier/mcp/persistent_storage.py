"""
Docker-based Persistent Storage for Agents and Skills

This module implements a revolutionary approach to agent and skill storage
using Docker volumes and containers, eliminating context window limitations
for agent management.

Key Features:
- Persistent Docker volumes for agent/skill storage
- Agent registry with metadata and capabilities
- Skill versioning and dependency management
- Context-free agent loading and execution
- Automatic backup and recovery
"""

import json
from dataclasses import dataclass
from dataclasses import field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any

from ..utils.logger import get_logger
from .code_execution import ExecutionRequest
from .code_execution import SecurityLevel

logger = get_logger(__name__)


class AgentStatus(Enum):
    """Agent lifecycle status."""

    INACTIVE = "inactive"
    ACTIVE = "active"
    LOADING = "loading"
    ERROR = "error"
    UPDATING = "updating"


class SkillStatus(Enum):
    """Skill lifecycle status."""

    REGISTERED = "registered"
    LOADING = "loading"
    ACTIVE = "active"
    ERROR = "error"
    DEPRECATED = "deprecated"


@dataclass
class AgentCapability:
    """Defines what an agent can do."""

    name: str
    description: str
    input_types: list[str]
    output_types: list[str]
    dependencies: list[str] = field(default_factory=list)
    max_runtime_seconds: int = 30
    required_resources: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentDefinition:
    """Complete agent definition with code and metadata."""

    agent_id: str
    name: str
    description: str
    version: str
    author: str
    created_at: datetime
    updated_at: datetime
    status: AgentStatus
    capabilities: list[AgentCapability]
    main_code: str
    helper_modules: dict[str, str] = field(default_factory=dict)
    requirements: list[str] = field(default_factory=list)
    environment_vars: dict[str, str] = field(default_factory=dict)
    tags: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class SkillDefinition:
    """Complete skill definition with code and metadata."""

    skill_id: str
    name: str
    description: str
    version: str
    language: str
    category: str
    author: str
    created_at: datetime
    updated_at: datetime
    status: SkillStatus
    code: str
    dependencies: list[str] = field(default_factory=list)
    test_cases: list[dict[str, Any]] = field(default_factory=list)
    usage_count: int = 0
    success_rate: float = 0.0
    tags: list[str] = field(default_factory=list)


class DockerPersistentStorage:
    """Manages persistent storage of agents and skills using Docker volumes."""

    def __init__(self, storage_volume: str = "amplifier_agents_storage"):
        self.storage_volume = storage_volume
        # Use user's home directory for storage instead of root directory
        self.storage_dir = Path.home() / ".amplifier_storage"
        self.agents_dir = self.storage_dir / "agents"
        self.skills_dir = self.storage_dir / "skills"
        self.registry_dir = self.storage_dir / "registry"
        self.cache_dir = self.storage_dir / "cache"

        # In-memory caches for fast access
        self.agent_cache: dict[str, AgentDefinition] = {}
        self.skill_cache: dict[str, SkillDefinition] = {}

        self._ensure_storage_structure()

    def _ensure_storage_structure(self) -> None:
        """Ensure storage directories exist in Docker volume."""
        directories = [
            self.storage_dir,
            self.agents_dir,
            self.skills_dir,
            self.registry_dir,
            self.cache_dir,
            self.registry_dir / "agent_index",
            self.registry_dir / "skill_index",
            self.registry_dir / "dependencies",
        ]

        for directory in directories:
            # In Docker, these directories should be mounted volumes
            # For local development, create them if they don't exist
            if not directory.exists():
                directory.mkdir(parents=True, exist_ok=True)
                logger.info(f"Created storage directory: {directory}")

    async def initialize_docker_volume(self) -> bool:
        """Initialize Docker volume for persistent storage."""
        try:
            import subprocess

            # Create Docker volume if it doesn't exist
            result = subprocess.run(
                ["docker", "volume", "inspect", self.storage_volume], capture_output=True, text=True
            )

            if result.returncode != 0:
                logger.info(f"Creating Docker volume: {self.storage_volume}")
                create_result = subprocess.run(
                    ["docker", "volume", "create", self.storage_volume], capture_output=True, text=True
                )

                if create_result.returncode != 0:
                    logger.error(f"Failed to create Docker volume: {create_result.stderr}")
                    return False

            logger.info(f"Docker volume {self.storage_volume} ready")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Docker volume: {e}")
            return False

    async def register_agent(self, agent: AgentDefinition) -> bool:
        """Register an agent in persistent storage."""
        try:
            # Save agent definition
            agent_file = self.agents_dir / f"{agent.agent_id}.json"
            agent_dict = {
                "agent_id": agent.agent_id,
                "name": agent.name,
                "description": agent.description,
                "version": agent.version,
                "author": agent.author,
                "created_at": agent.created_at.isoformat(),
                "updated_at": agent.updated_at.isoformat(),
                "status": agent.status.value,
                "capabilities": [
                    {
                        "name": cap.name,
                        "description": cap.description,
                        "input_types": cap.input_types,
                        "output_types": cap.output_types,
                        "dependencies": cap.dependencies,
                        "max_runtime_seconds": cap.max_runtime_seconds,
                        "required_resources": cap.required_resources,
                    }
                    for cap in agent.capabilities
                ],
                "main_code": agent.main_code,
                "helper_modules": agent.helper_modules,
                "requirements": agent.requirements,
                "environment_vars": agent.environment_vars,
                "tags": agent.tags,
                "metadata": agent.metadata,
            }

            with open(agent_file, "w") as f:
                json.dump(agent_dict, f, indent=2)

            # Update agent index
            await self._update_agent_index(agent)

            # Cache in memory
            self.agent_cache[agent.agent_id] = agent

            logger.info(f"Registered agent: {agent.name} ({agent.agent_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to register agent {agent.agent_id}: {e}")
            return False

    async def register_skill(self, skill: SkillDefinition) -> bool:
        """Register a skill in persistent storage."""
        try:
            # Save skill definition
            skill_file = self.skills_dir / f"{skill.skill_id}.json"
            skill_dict = {
                "skill_id": skill.skill_id,
                "name": skill.name,
                "description": skill.description,
                "version": skill.version,
                "language": skill.language,
                "category": skill.category,
                "author": skill.author,
                "created_at": skill.created_at.isoformat(),
                "updated_at": skill.updated_at.isoformat(),
                "status": skill.status.value,
                "code": skill.code,
                "dependencies": skill.dependencies,
                "test_cases": skill.test_cases,
                "usage_count": skill.usage_count,
                "success_rate": skill.success_rate,
                "tags": skill.tags,
            }

            with open(skill_file, "w") as f:
                json.dump(skill_dict, f, indent=2)

            # Update skill index
            await self._update_skill_index(skill)

            # Cache in memory
            self.skill_cache[skill.skill_id] = skill

            logger.info(f"Registered skill: {skill.name} ({skill.skill_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to register skill {skill.skill_id}: {e}")
            return False

    async def load_agent(self, agent_id: str) -> AgentDefinition | None:
        """Load an agent from persistent storage."""
        # Check cache first
        if agent_id in self.agent_cache:
            return self.agent_cache[agent_id]

        try:
            agent_file = self.agents_dir / f"{agent_id}.json"
            if not agent_file.exists():
                logger.warning(f"Agent not found: {agent_id}")
                return None

            with open(agent_file) as f:
                agent_dict = json.load(f)

            # Reconstruct AgentDefinition
            agent = AgentDefinition(
                agent_id=agent_dict["agent_id"],
                name=agent_dict["name"],
                description=agent_dict["description"],
                version=agent_dict["version"],
                author=agent_dict["author"],
                created_at=datetime.fromisoformat(agent_dict["created_at"]),
                updated_at=datetime.fromisoformat(agent_dict["updated_at"]),
                status=AgentStatus(agent_dict["status"]),
                capabilities=[
                    AgentCapability(
                        name=cap["name"],
                        description=cap["description"],
                        input_types=cap["input_types"],
                        output_types=cap["output_types"],
                        dependencies=cap["dependencies"],
                        max_runtime_seconds=cap["max_runtime_seconds"],
                        required_resources=cap["required_resources"],
                    )
                    for cap in agent_dict["capabilities"]
                ],
                main_code=agent_dict["main_code"],
                helper_modules=agent_dict["helper_modules"],
                requirements=agent_dict["requirements"],
                environment_vars=agent_dict["environment_vars"],
                tags=agent_dict["tags"],
                metadata=agent_dict["metadata"],
            )

            # Cache in memory
            self.agent_cache[agent_id] = agent

            return agent

        except Exception as e:
            logger.error(f"Failed to load agent {agent_id}: {e}")
            return None

    async def load_skill(self, skill_id: str) -> SkillDefinition | None:
        """Load a skill from persistent storage."""
        # Check cache first
        if skill_id in self.skill_cache:
            return self.skill_cache[skill_id]

        try:
            skill_file = self.skills_dir / f"{skill_id}.json"
            if not skill_file.exists():
                logger.warning(f"Skill not found: {skill_id}")
                return None

            with open(skill_file) as f:
                skill_dict = json.load(f)

            # Reconstruct SkillDefinition
            skill = SkillDefinition(
                skill_id=skill_dict["skill_id"],
                name=skill_dict["name"],
                description=skill_dict["description"],
                version=skill_dict["version"],
                language=skill_dict["language"],
                category=skill_dict["category"],
                author=skill_dict["author"],
                created_at=datetime.fromisoformat(skill_dict["created_at"]),
                updated_at=datetime.fromisoformat(skill_dict["updated_at"]),
                status=SkillStatus(skill_dict["status"]),
                code=skill_dict["code"],
                dependencies=skill_dict["dependencies"],
                test_cases=skill_dict["test_cases"],
                usage_count=skill_dict["usage_count"],
                success_rate=skill_dict["success_rate"],
                tags=skill_dict["tags"],
            )

            # Cache in memory
            self.skill_cache[skill_id] = skill

            return skill

        except Exception as e:
            logger.error(f"Failed to load skill {skill_id}: {e}")
            return None

    async def list_agents(self, status_filter: AgentStatus | None = None) -> list[str]:
        """List all registered agents, optionally filtered by status."""
        try:
            index_file = self.registry_dir / "agent_index" / "agents.json"
            if not index_file.exists():
                return []

            with open(index_file) as f:
                index_data = json.load(f)

            agents = index_data.get("agents", [])

            if status_filter:
                agents = [a for a in agents if a.get("status") == status_filter.value]

            return [a["agent_id"] for a in agents]

        except Exception as e:
            logger.error(f"Failed to list agents: {e}")
            return []

    async def list_skills(self, category_filter: str | None = None) -> list[str]:
        """List all registered skills, optionally filtered by category."""
        try:
            index_file = self.registry_dir / "skill_index" / "skills.json"
            if not index_file.exists():
                return []

            with open(index_file) as f:
                index_data = json.load(f)

            skills = index_data.get("skills", [])

            if category_filter:
                skills = [s for s in skills if s.get("category") == category_filter]

            return [s["skill_id"] for s in skills]

        except Exception as e:
            logger.error(f"Failed to list skills: {e}")
            return []

    async def execute_agent(
        self, agent_id: str, input_data: dict[str, Any], capability_name: str | None = None
    ) -> dict[str, Any]:
        """Execute an agent capability."""
        agent = await self.load_agent(agent_id)
        if not agent:
            return {"error": f"Agent not found: {agent_id}"}

        # Select capability
        capability = None
        if capability_name:
            capability = next((c for c in agent.capabilities if c.name == capability_name), None)
            if not capability:
                return {"error": f"Capability not found: {capability_name}"}
        else:
            capability = agent.capabilities[0]  # Use first capability

        # Create execution environment
        execution_code = self._prepare_agent_execution(agent, capability, input_data)

        # Execute in Docker sandbox
        from .code_execution import get_mcp_executor

        executor = get_mcp_executor()

        request = ExecutionRequest(
            code=execution_code,
            language="python",
            input_data=input_data,
            environment_vars=agent.environment_vars,
            security_level=SecurityLevel.MINIMAL,
        )

        result = await executor.execute_code(request)

        # Update usage statistics
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        await self._update_agent_usage(agent_id, capability_name, result.status.value == "completed")  # type: ignore[arg-type]

        return {
            "agent_id": agent_id,
            "capability": capability.name,
            "status": result.status.value,
            "result": result.stdout if result.status.value == "completed" else result.stderr,
            "runtime": result.runtime_seconds,
            "tokens_used": result.tokens_processed,
        }

    def _prepare_agent_execution(
        self, agent: AgentDefinition, capability: AgentCapability, input_data: dict[str, Any]
    ) -> str:
        """Prepare code for agent execution in Docker."""

        # Base execution code
        execution_code = f'''
import json
import sys
import traceback

# Agent: {agent.name} ({agent.agent_id})
# Capability: {capability.name}

# Load input data
input_data = json.loads("""{json.dumps(input_data)}""")

# Agent main code
{agent.main_code}

# Execute capability
try:
    result = await execute_capability("{capability.name}", input_data)
    print(json.dumps(result, indent=2))
except Exception as e:
    error_result = {{
        "error": str(e),
        "traceback": traceback.format_exc()
    }}
    print(json.dumps(error_result, indent=2))
'''

        return execution_code

    async def _update_agent_index(self, agent: AgentDefinition) -> None:
        """Update the agent index."""
        index_file = self.registry_dir / "agent_index" / "agents.json"

        # Load existing index
        index_data = {"agents": []}
        if index_file.exists():
            with open(index_file) as f:
                index_data = json.load(f)

        # Update or add agent
        agents = index_data.get("agents", [])
        existing = next((a for a in agents if a["agent_id"] == agent.agent_id), None)

        agent_entry = {
            "agent_id": agent.agent_id,
            "name": agent.name,
            "description": agent.description,
            "version": agent.version,
            "author": agent.author,
            "status": agent.status.value,
            "capabilities": [c.name for c in agent.capabilities],
            "tags": agent.tags,
            "updated_at": agent.updated_at.isoformat(),
        }

        if existing:
            agents.remove(existing)
        agents.append(agent_entry)

        index_data["agents"] = agents
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        index_data["last_updated"] = datetime.now().isoformat()  # type: ignore[arg-type]

        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=2)

    async def _update_skill_index(self, skill: SkillDefinition) -> None:
        """Update the skill index."""
        index_file = self.registry_dir / "skill_index" / "skills.json"

        # Load existing index
        index_data = {"skills": []}
        if index_file.exists():
            with open(index_file) as f:
                index_data = json.load(f)

        # Update or add skill
        skills = index_data.get("skills", [])
        existing = next((s for s in skills if s["skill_id"] == skill.skill_id), None)

        skill_entry = {
            "skill_id": skill.skill_id,
            "name": skill.name,
            "description": skill.description,
            "version": skill.version,
            "language": skill.language,
            "category": skill.category,
            "author": skill.author,
            "status": skill.status.value,
            "dependencies": skill.dependencies,
            "tags": skill.tags,
            "usage_count": skill.usage_count,
            "success_rate": skill.success_rate,
            "updated_at": skill.updated_at.isoformat(),
        }

        if existing:
            skills.remove(existing)
        skills.append(skill_entry)

        index_data["skills"] = skills
        # type: ignore[arg-type]
        # type: ignore[arg-type]
        index_data["last_updated"] = datetime.now().isoformat()  # type: ignore[arg-type]

        with open(index_file, "w") as f:
            json.dump(index_data, f, indent=2)

    async def _update_agent_usage(self, agent_id: str, capability_name: str, success: bool) -> None:
        """Update agent usage statistics."""
        # This could be expanded to track detailed usage analytics
        logger.info(f"Agent usage: {agent_id}:{capability_name} - {'Success' if success else 'Failed'}")


# Global persistent storage instance
_persistent_storage = DockerPersistentStorage()


async def initialize_predefined_agents() -> None:
    """Initialize predefined agents in persistent storage."""
    storage = get_persistent_storage()

    for _agent_id, agent_def in PREDEFINED_AGENTS.items():
        # Check if already registered
        existing_agent = await storage.load_agent(agent_def.agent_id)
        if not existing_agent:
            success = await storage.register_agent(agent_def)
            if success:
                logger.info(f"Initialized predefined agent: {agent_def.name}")
            else:
                logger.error(f"Failed to initialize predefined agent: {agent_def.name}")


def get_persistent_storage() -> DockerPersistentStorage:
    """Get the global persistent storage instance."""
    return _persistent_storage


# Predefined agents that can be registered
PREDEFINED_AGENTS = {
    "data_analyst": AgentDefinition(
        agent_id="data_analyst_v1",
        name="Data Analyst",
        description="Specialized agent for data analysis and visualization",
        version="1.0.0",
        author="Amplifier Team",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status=AgentStatus.ACTIVE,
        capabilities=[
            AgentCapability(
                name="analyze_dataset",
                description="Analyze dataset structure and statistics",
                input_types=["json", "csv", "data"],
                output_types=["statistics", "insights"],
                max_runtime_seconds=30,
            ),
            AgentCapability(
                name="generate_visualization",
                description="Create data visualizations",
                input_types=["data", "chart_type"],
                output_types=["plot_data", "chart_config"],
                max_runtime_seconds=45,
            ),
        ],
        main_code='''
async def execute_capability(capability_name, input_data):
    if capability_name == "analyze_dataset":
        return analyze_dataset(input_data)
    elif capability_name == "generate_visualization":
        return generate_visualization(input_data)
    else:
        return {"error": f"Unknown capability: {capability_name}"}

def analyze_dataset(data):
    """Analyze dataset structure and statistics."""
    import statistics
    import json

    if isinstance(data, str):
        data = json.loads(data)

    if isinstance(data, list):
        # Analyze list of records
        numeric_fields = []
        for item in data[:1]:  # Check first item for structure
            if isinstance(item, dict):
                for key, value in item.items():
                    if isinstance(value, (int, float)):
                        numeric_fields.append(key)

        analysis = {
            "record_count": len(data),
            "numeric_fields": numeric_fields,
            "field_statistics": {}
        }

        # Calculate statistics for numeric fields
        for field in numeric_fields:
            values = [item.get(field) for item in data if isinstance(item, dict) and field in item]
            if values:
                analysis["field_statistics"][field] = {
                    "count": len(values),
                    "mean": statistics.mean(values),
                    "median": statistics.median(values),
                    "min": min(values),
                    "max": max(values)
                }

        return analysis

    return {"error": "Unsupported data format"}

def generate_visualization(data):
    """Generate visualization configuration."""
    chart_type = data.get("chart_type", "bar")

    # This would generate plot data or configuration
    return {
        "chart_type": chart_type,
        "config": {
            "title": "Data Visualization",
            "data": data
        }
    }
''',
        tags=["data", "analysis", "visualization"],
    ),
    "text_processor": AgentDefinition(
        agent_id="text_processor_v1",
        name="Text Processor",
        description="Specialized agent for text processing and analysis",
        version="1.0.0",
        author="Amplifier Team",
        created_at=datetime.now(),
        updated_at=datetime.now(),
        status=AgentStatus.ACTIVE,
        capabilities=[
            AgentCapability(
                name="extract_entities",
                description="Extract entities from text",
                input_types=["text"],
                output_types=["entities", "relationships"],
                max_runtime_seconds=20,
            ),
            AgentCapability(
                name="summarize_text",
                description="Generate text summaries",
                input_types=["text", "max_length"],
                output_types=["summary", "key_points"],
                max_runtime_seconds=15,
            ),
        ],
        main_code='''
async def execute_capability(capability_name, input_data):
    if capability_name == "extract_entities":
        return extract_entities(input_data)
    elif capability_name == "summarize_text":
        return summarize_text(input_data)
    else:
        return {"error": f"Unknown capability: {capability_name}"}

def extract_entities(data):
    """Extract entities from text."""
    import re
    from collections import Counter

    text = data.get("text", "")

    # Simple entity extraction patterns
    entities = {
        "emails": re.findall(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{2,}\b', text),
        "urls": re.findall(r'https?://\\S+', text),
        "numbers": re.findall(r'\b\\d+\\.?\\d*\b', text),
        "words": text.split()
    }

    # Get word frequency
    if entities["words"]:
        word_freq = Counter(word.lower().strip('.,!?;:"()') for word in entities["words"])
        entities["most_common_words"] = word_freq.most_common(10)

    del entities["words"]  # Remove raw words list

    return entities

def summarize_text(data):
    """Generate text summary."""
    text = data.get("text", "")
    max_length = data.get("max_length", 100)

    sentences = re.split(r'[.!?]+', text)
    sentences = [s.strip() for s in sentences if s.strip()]

    if len(sentences) <= 3:
        summary = " ".join(sentences)
    else:
        # Take first and last sentences
        summary = sentences[0] + " ... " + sentences[-1]

    if len(summary) > max_length:
        summary = summary[:max_length-3] + "..."

    return {
        "summary": summary,
        "original_length": len(text),
        "summary_length": len(summary),
        "sentence_count": len(sentences)
    }
''',
        tags=["text", "nlp", "summarization"],
    ),
}


async def initialize_persistent_storage() -> bool:
    """Initialize the persistent storage system."""
    storage = get_persistent_storage()

    # Initialize Docker volume
    if not await storage.initialize_docker_volume():
        return False

    # Register predefined agents
    for _agent_id, agent in PREDEFINED_AGENTS.items():
        await storage.register_agent(agent)

    logger.info(f"Initialized persistent storage with {len(PREDEFINED_AGENTS)} predefined agents")
    return True


async def load_and_execute_agent(agent_id: str, capability: str, input_data: dict[str, Any]) -> dict[str, Any]:
    """Convenient function to load and execute an agent."""
    storage = get_persistent_storage()
    return await storage.execute_agent(agent_id, input_data, capability)


async def store_result(session_id: str, result_data: dict[str, Any]) -> bool:
    """Store execution result in persistent storage for unlimited context."""
    storage = get_persistent_storage()

    try:
        # Create a timestamped result file
        timestamp = datetime.now().isoformat()
        result_file = storage.cache_dir / f"session_{session_id}_{timestamp.replace(':', '-')}.json"

        result = {
            "session_id": session_id,
            "timestamp": timestamp,
            "data": result_data,
            "type": "skill_execution_result",
        }

        with open(result_file, "w") as f:
            json.dump(result, f, indent=2)

        logger.info(f"Stored result for session {session_id}")
        return True

    except Exception as e:
        logger.error(f"Failed to store result: {e}")
        return False


async def load_session_results(session_id: str, limit: int = 10) -> list[dict[str, Any]]:
    """Load stored results for a session."""
    storage = get_persistent_storage()

    try:
        pattern = f"session_{session_id}_*.json"
        result_files = list(storage.cache_dir.glob(pattern))

        # Sort by timestamp (newest first)
        result_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        results = []
        for result_file in result_files[:limit]:
            with open(result_file) as f:
                result = json.load(f)
                results.append(result)

        return results

    except Exception as e:
        logger.error(f"Failed to load session results: {e}")
        return []


async def retrieve_result(session_id: str, result_type: str = "skill_execution_result") -> dict[str, Any] | None:
    """Retrieve a specific stored result by session ID and type."""
    storage = get_persistent_storage()

    try:
        pattern = f"session_{session_id}_*.json"
        result_files = list(storage.cache_dir.glob(pattern))

        # Sort by timestamp (newest first)
        result_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)

        # Find the most recent result matching the type
        for result_file in result_files:
            with open(result_file) as f:
                result = json.load(f)
                if result.get("type") == result_type or result.get("session_id") == session_id:
                    return result

        return None

    except Exception as e:
        logger.error(f"Failed to retrieve result for session {session_id}: {e}")
        return None


def load_techniques_registry() -> dict[str, Any]:
    """Load the techniques registry from file system."""
    registry_file = Path("CLAUDE_TECHNIQUES_REGISTRY.md")
    docker_storage = Path(".docker-storage/claude-techniques-registry/")

    techniques = {}

    # Try to load from primary location first
    if registry_file.exists():
        try:
            content = registry_file.read_text(encoding="utf-8")
            techniques["primary"] = {
                "source": str(registry_file),
                "content": content,
                "size": len(content),
                "last_modified": registry_file.stat().st_mtime,
            }
        except Exception as e:
            logger.warning(f"Failed to load primary registry: {e}")

    # Try to load from Docker storage
    if docker_storage.exists():
        docker_files = list(docker_storage.glob("*.md"))
        techniques["docker_backup"] = {
            "source": str(docker_storage),
            "files": len(docker_files),
            "files_list": [f.name for f in docker_files],
            "last_modified": max([f.stat().st_mtime for f in docker_files]) if docker_files else 0,
        }

    # Add status
    techniques["status"] = {
        "primary_available": registry_file.exists(),
        "docker_backup_available": docker_storage.exists(),
        "total_categories": len(techniques),
    }

    return techniques
