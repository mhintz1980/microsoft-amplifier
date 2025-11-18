"""
Dynamic Agent Loading Framework

Provides progressive agent discovery and on-demand loading to minimize
context usage while maintaining fast access to specialized agents.

Based on the progressive agent discovery pattern from the techniques registry:
- Load only metadata initially (800 tokens vs 9,900)
- On-demand loading of full agent definitions
- Tag-based discovery for efficient agent matching
- Context-aware unloading to save memory
"""

import json
import logging
import time
from dataclasses import asdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


@dataclass
class AgentMetadata:
    """Lightweight agent metadata for fast discovery"""

    identifier: str
    name: str
    description: str
    tags: list[str]
    when_to_use: str
    file_path: str
    file_type: str  # 'md' or 'json'
    size_tokens: int
    last_loaded: float | None = None
    load_count: int = 0


@dataclass
class AgentLoadResult:
    """Result of loading an agent"""

    success: bool
    agent_id: str
    content: str | None = None
    error: str | None = None
    load_time: float = 0.0


class DynamicAgentLoader:
    """
    Dynamic agent loader that implements progressive discovery pattern.

    Keeps only metadata in memory for fast searching, loads full agent
    definitions on-demand, and manages context efficiently.
    """

    def __init__(self, agents_dir: str = ".claude/agents", registry_file: str = "amplifier/agents/agent_registry.json"):
        self.agents_dir = Path(agents_dir)
        self.registry_file = Path(registry_file)
        self.metadata_cache: dict[str, AgentMetadata] = {}
        self.loaded_agents: dict[str, str] = {}
        self.max_loaded_agents = 10  # Context management
        self._ensure_directories()

    def _ensure_directories(self):
        """Ensure required directories exist"""
        self.registry_file.parent.mkdir(parents=True, exist_ok=True)

    def build_registry(self, force_rebuild: bool = False) -> int:
        """
        Build lightweight registry from agent files.

        Args:
            force_rebuild: Force rebuilding even if registry exists

        Returns:
            Number of agents processed
        """
        if not force_rebuild and self.registry_file.exists():
            logger.info(f"Loading existing registry from {self.registry_file}")
            return self._load_registry()

        logger.info(f"Building agent registry from {self.agents_dir}")
        agent_count = 0

        # Process both .md and .json agent files
        for agent_file in self.agents_dir.glob("**/*"):
            if agent_file.is_file() and agent_file.suffix in {".md", ".json"}:
                if self._should_ignore_file(agent_file):
                    continue

                metadata = self._extract_metadata(agent_file)
                if metadata:
                    self.metadata_cache[metadata.identifier] = metadata
                    agent_count += 1

        # Save registry
        self._save_registry()
        logger.info(f"Built registry with {agent_count} agents")
        return agent_count

    def _should_ignore_file(self, file_path: Path) -> bool:
        """Check if file should be ignored"""
        ignore_patterns = {".git", "node_modules", "__pycache__", ".DS_Store"}
        return any(pattern in str(file_path) for pattern in ignore_patterns)

    def _extract_metadata(self, file_path: Path) -> AgentMetadata | None:
        """Extract metadata from agent file"""
        try:
            if file_path.suffix == ".json":
                return self._extract_json_metadata(file_path)
            if file_path.suffix == ".md":
                return self._extract_md_metadata(file_path)
        except Exception as e:
            logger.warning(f"Failed to extract metadata from {file_path}: {e}")
        return None

    def _extract_json_metadata(self, file_path: Path) -> AgentMetadata | None:
        """Extract metadata from JSON agent file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)

            # Estimate token usage (rough approximation)
            content_length = len(str(data))
            estimated_tokens = content_length // 4  # ~4 chars per token

            # Handle path safely - try relative, fallback to absolute
            try:
                file_path_str = str(file_path.relative_to(Path.cwd()))
            except ValueError:
                file_path_str = str(file_path.absolute())

            return AgentMetadata(
                identifier=data.get("identifier", file_path.stem),
                name=data.get("identifier", file_path.stem).replace("-", " ").title(),
                description=data.get("whenToUse", "")[:200],  # Truncate for metadata
                tags=self._extract_tags_from_content(str(data)),
                when_to_use=data.get("whenToUse", ""),
                file_path=file_path_str,
                file_type="json",
                size_tokens=estimated_tokens,
            )
        except Exception as e:
            logger.warning(f"Failed to parse JSON agent {file_path}: {e}")
            return None

    def _extract_md_metadata(self, file_path: Path) -> AgentMetadata | None:
        """Extract metadata from markdown agent file"""
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            # Extract YAML frontmatter
            if content.startswith("---"):
                try:
                    frontmatter_end = content.find("---", 3)
                    frontmatter = content[3:frontmatter_end]
                    import yaml  # Import here to avoid dependency if not needed

                    data = yaml.safe_load(frontmatter)
                except:
                    data = {}
            else:
                data = {}

            # Estimate token usage
            estimated_tokens = len(content) // 4

            # Handle path safely - try relative, fallback to absolute
            try:
                file_path_str = str(file_path.relative_to(Path.cwd()))
            except ValueError:
                file_path_str = str(file_path.absolute())

            return AgentMetadata(
                identifier=data.get("name", file_path.stem),
                name=data.get("name", file_path.stem).replace("-", " ").title(),
                description=data.get("description", content[:200].replace("\n", " ")),
                tags=self._extract_tags_from_content(content),
                when_to_use=data.get("description", ""),
                file_path=file_path_str,
                file_type="md",
                size_tokens=estimated_tokens,
            )
        except Exception as e:
            logger.warning(f"Failed to parse MD agent {file_path}: {e}")
            return None

    def _extract_tags_from_content(self, content: str) -> list[str]:
        """Extract tags from content using simple heuristics"""
        tags = set()

        # Common agent categories
        tag_patterns = {
            "architecture": ["architecture", "design", "system", "module"],
            "development": ["code", "development", "implementation", "programming"],
            "testing": ["test", "testing", "quality", "validation"],
            "optimization": ["optimization", "performance", "efficiency", "improve"],
            "security": ["security", "defense", "protect", "analysis"],
            "analysis": ["analysis", "analyze", "examine", "review"],
            "integration": ["integration", "connect", "bridge", "mcp"],
            "cleanup": ["cleanup", "organize", "maintain", "hygiene"],
            "specialist": ["specialist", "expert", "focused", "dedicated"],
        }

        content_lower = content.lower()
        for tag, patterns in tag_patterns.items():
            if any(pattern in content_lower for pattern in patterns):
                tags.add(tag)

        return sorted(list(tags))

    def _load_registry(self) -> int:
        """Load existing registry from file"""
        try:
            with open(self.registry_file, encoding="utf-8") as f:
                data = json.load(f)

            for agent_data in data.get("agents", []):
                metadata = AgentMetadata(**agent_data)
                self.metadata_cache[metadata.identifier] = metadata

            return len(self.metadata_cache)
        except Exception as e:
            logger.warning(f"Failed to load registry: {e}")
            return 0

    def _save_registry(self):
        """Save registry to file"""
        try:
            registry_data = {
                "version": "1.0.0",
                "built_at": time.time(),
                "total_agents": len(self.metadata_cache),
                "agents": [asdict(meta) for meta in self.metadata_cache.values()],
            }

            with open(self.registry_file, "w", encoding="utf-8") as f:
                json.dump(registry_data, f, indent=2, ensure_ascii=False)

        except Exception as e:
            logger.error(f"Failed to save registry: {e}")

    def find_agent_by_tags(self, tags: list[str], require_all: bool = False) -> list[AgentMetadata]:
        """
        Find agents by tags using lightweight metadata.

        Args:
            tags: Tags to search for
            require_all: If True, agent must have ALL tags; if False, ANY tag matches

        Returns:
            List of matching agent metadata
        """
        if not self.metadata_cache:
            self.build_registry()

        matching_agents = []

        for metadata in self.metadata_cache.values():
            if require_all:
                if all(tag in metadata.tags for tag in tags):
                    matching_agents.append(metadata)
            else:
                if any(tag in metadata.tags for tag in tags):
                    matching_agents.append(metadata)

        # Sort by relevance (more tags matched = higher relevance)
        matching_agents.sort(key=lambda m: sum(tag in m.tags for tag in tags), reverse=True)

        return matching_agents

    def find_agent_by_description(self, query: str) -> list[AgentMetadata]:
        """
        Find agents by searching descriptions.

        Args:
            query: Search query

        Returns:
            List of matching agent metadata
        """
        if not self.metadata_cache:
            self.build_registry()

        query_lower = query.lower()
        matching_agents = []

        for metadata in self.metadata_cache.values():
            # Simple keyword matching in description and when_to_use
            searchable_text = f"{metadata.description} {metadata.when_to_use}".lower()
            if any(word in searchable_text for word in query_lower.split()):
                matching_agents.append(metadata)

        return matching_agents

    def load_agent_on_demand(self, agent_id: str) -> AgentLoadResult:
        """
        Load full agent definition on demand.

        Args:
            agent_id: Agent identifier

        Returns:
            AgentLoadResult with content or error
        """
        start_time = time.time()

        if agent_id not in self.metadata_cache:
            return AgentLoadResult(success=False, agent_id=agent_id, error=f"Agent '{agent_id}' not found in registry")

        # Check if already loaded
        if agent_id in self.loaded_agents:
            metadata = self.metadata_cache[agent_id]
            metadata.load_count += 1
            metadata.last_loaded = time.time()

            return AgentLoadResult(
                success=True,
                agent_id=agent_id,
                content=self.loaded_agents[agent_id],
                load_time=time.time() - start_time,
            )

        # Load from disk
        metadata = self.metadata_cache[agent_id]
        try:
            with open(metadata.file_path, encoding="utf-8") as f:
                content = f.read()

            # Manage context - unload old agents if needed
            self._manage_context()

            # Store loaded agent
            self.loaded_agents[agent_id] = content
            metadata.load_count += 1
            metadata.last_loaded = time.time()

            load_time = time.time() - start_time
            logger.info(f"Loaded agent '{agent_id}' in {load_time:.3f}s ({metadata.size_tokens} tokens)")

            return AgentLoadResult(success=True, agent_id=agent_id, content=content, load_time=load_time)

        except Exception as e:
            return AgentLoadResult(
                success=False,
                agent_id=agent_id,
                error=f"Failed to load agent: {str(e)}",
                load_time=time.time() - start_time,
            )

    def _manage_context(self):
        """Manage context by unloading least recently used agents"""
        if len(self.loaded_agents) >= self.max_loaded_agents:
            # Find least recently used agent
            lru_agent = min(self.loaded_agents.keys(), key=lambda aid: self.metadata_cache[aid].last_loaded or 0)

            del self.loaded_agents[lru_agent]
            logger.debug(f"Unloaded agent '{lru_agent}' to manage context")

    def unload_agent(self, agent_id: str) -> bool:
        """
        Manually unload an agent to free context.

        Args:
            agent_id: Agent identifier

        Returns:
            True if agent was unloaded, False if not found
        """
        if agent_id in self.loaded_agents:
            del self.loaded_agents[agent_id]
            logger.info(f"Manually unloaded agent '{agent_id}'")
            return True
        return False

    def get_registry_stats(self) -> dict[str, Any]:
        """Get registry statistics"""
        if not self.metadata_cache:
            self.build_registry()

        total_tokens = sum(meta.size_tokens for meta in self.metadata_cache.values())
        loaded_tokens = sum(self.metadata_cache[aid].size_tokens for aid in self.loaded_agents.keys())

        return {
            "total_agents": len(self.metadata_cache),
            "loaded_agents": len(self.loaded_agents),
            "total_tokens_metadata": sum(len(str(meta)) // 4 for meta in self.metadata_cache.values()),
            "total_tokens_full": total_tokens,
            "loaded_tokens": loaded_tokens,
            "memory_efficiency": (total_tokens - loaded_tokens) / total_tokens * 100 if total_tokens > 0 else 0,
            "tag_distribution": self._get_tag_distribution(),
        }

    def _get_tag_distribution(self) -> dict[str, int]:
        """Get distribution of tags across agents"""
        tag_count = {}
        for metadata in self.metadata_cache.values():
            for tag in metadata.tags:
                tag_count[tag] = tag_count.get(tag, 0) + 1
        return dict(sorted(tag_count.items(), key=lambda x: x[1], reverse=True))

    def list_all_agents(self) -> list[AgentMetadata]:
        """List all agents in registry"""
        if not self.metadata_cache:
            self.build_registry()
        return list(self.metadata_cache.values())


# Global instance for easy access
_global_loader: DynamicAgentLoader | None = None


def get_agent_loader() -> DynamicAgentLoader:
    """Get global agent loader instance"""
    global _global_loader
    if _global_loader is None:
        _global_loader = DynamicAgentLoader()
    return _global_loader


def find_agents_by_tags(tags: list[str], require_all: bool = False) -> list[AgentMetadata]:
    """Convenience function to find agents by tags"""
    return get_agent_loader().find_agent_by_tags(tags, require_all)


def find_agents_by_description(query: str) -> list[AgentMetadata]:
    """Convenience function to find agents by description"""
    return get_agent_loader().find_agent_by_description(query)


def load_agent(agent_id: str) -> AgentLoadResult:
    """Convenience function to load an agent"""
    return get_agent_loader().load_agent_on_demand(agent_id)
