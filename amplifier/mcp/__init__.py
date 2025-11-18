"""
MCP Infrastructure for Amplifier

Provides Model Context Protocol integration including:
- Docker-based code execution
- Persistent agent and skill storage
- Local LLM model serving
- Enhanced client reliability
"""

from .code_execution import ExecutionRequest
from .code_execution import ExecutionResult
from .code_execution import MCPCodeExecutor
from .code_execution import SecurityLevel
from .code_execution import execute_code_safely
from .code_execution import execute_skill_by_name
from .code_execution import get_mcp_executor
from .docker_model_runner import DockerModelManager
from .docker_model_runner import DockerModelRunner
from .docker_model_runner import ModelInfo
from .docker_model_runner import ModelStatus
from .docker_model_runner import chat_with_local_llm
from .docker_model_runner import get_model_runner
from .docker_model_runner import start_local_llm

# enhanced_mcp_client imports commented out - file does not exist yet
# from .enhanced_mcp_client import ConnectionMetrics
# from .enhanced_mcp_client import EnhancedMCPClient
# from .enhanced_mcp_client import EnhancedMCPManager
# from .enhanced_mcp_client import MCPConnectionConfig
# from .enhanced_mcp_client import create_reliable_mcp_client
# from .enhanced_mcp_client import get_mcp_manager
from .persistent_storage import AgentDefinition
from .persistent_storage import AgentStatus
from .persistent_storage import DockerPersistentStorage
from .persistent_storage import SkillDefinition
from .persistent_storage import SkillStatus
from .persistent_storage import get_persistent_storage
from .persistent_storage import load_and_execute_agent

__all__ = [
    # Code execution
    "get_mcp_executor",
    "execute_code_safely",
    "execute_skill_by_name",
    "MCPCodeExecutor",
    "ExecutionRequest",
    "ExecutionResult",
    "SecurityLevel",
    # Persistent storage
    "get_persistent_storage",
    "load_and_execute_agent",
    "DockerPersistentStorage",
    "AgentDefinition",
    "SkillDefinition",
    "AgentStatus",
    "SkillStatus",
    # Model runner
    "get_model_runner",
    "start_local_llm",
    "chat_with_local_llm",
    "DockerModelRunner",
    "DockerModelManager",
    "ModelInfo",
    "ModelStatus",
    # Enhanced client - commented out until file exists
    # "get_mcp_manager",
    # "create_reliable_mcp_client",
    # "EnhancedMCPClient",
    # "EnhancedMCPManager",
    # "MCPConnectionConfig",
    # "ConnectionMetrics",
]
