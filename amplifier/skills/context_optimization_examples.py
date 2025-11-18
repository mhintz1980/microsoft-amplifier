"""
Context Optimization Examples

Practical examples demonstrating how to use the Context Optimization Specialist
skill for various scenarios and use cases.

These examples follow ruthless simplicity while showing the full capabilities
of progressive context loading and semantic optimization.
"""

from datetime import datetime
from datetime import timedelta

from ..memory.core import MemoryStore
from ..skills_framework.skill_template import SkillContext
from ..skills_framework.skill_template import SkillLevel
from .context_memory_integration import ContextMemoryIntegration
from .context_optimization import ContextOptimizationSkill
from .context_optimization import ConversationType


def example_basic_optimization():
    """Example: Basic context optimization for a long conversation."""
    print("=== Basic Context Optimization ===")

    # Create sample conversation history
    conversation_history = [
        {
            "role": "user",
            "content": "I need to implement a user authentication system for my web application. Can you help me design it?",
            "timestamp": (datetime.now() - timedelta(hours=2)).isoformat(),
        },
        {
            "role": "assistant",
            "content": "I'll help you design a secure authentication system. Let me create a comprehensive implementation with JWT tokens, password hashing, and session management.\n\n```python\nimport bcrypt\nimport jwt\nfrom datetime import datetime, timedelta\n\nclass AuthService:\n    def __init__(self, secret_key: str):\n        self.secret_key = secret_key\n    \n    def hash_password(self, password: str) -> str:\n        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()\n    \n    def verify_password(self, password: str, hashed: str) -> bool:\n        return bcrypt.checkpw(password.encode(), hashed.encode())\n    \n    def generate_token(self, user_id: int) -> str:\n        payload = {\n            'user_id': user_id,\n            'exp': datetime.utcnow() + timedelta(hours=24)\n        }\n        return jwt.encode(payload, self.secret_key, algorithm='HS256')\n```\n\nThis implementation provides secure password handling and JWT-based authentication.",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=50)).isoformat(),
        },
        {
            "role": "user",
            "content": "This looks great! But I'm getting an error when I try to install bcrypt. It says 'Microsoft Visual C++ 14.0 is required'. What should I do?",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=45)).isoformat(),
        },
        {
            "role": "assistant",
            "content": "This is a common issue on Windows. Here are the solutions:\n\n1. **Install Microsoft C++ Build Tools**: Download from Microsoft's website\n2. **Use alternative library**: Replace bcrypt with passlib which is easier to install\n3. **Use Docker**: Containerize your application\n\nFor a Windows-friendly version, use passlib:\n\n```python\nfrom passlib.context import CryptContext\npwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')\n\nclass AuthService:\n    def hash_password(self, password: str) -> str:\n        return pwd_context.hash(password)\n    \n    def verify_password(self, password: str, hashed: str) -> bool:\n        return pwd_context.verify(password, hashed)\n```\n\nThis should resolve your installation issues.",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=40)).isoformat(),
        },
        {
            "role": "user",
            "content": "Perfect! Now how do I integrate this with my FastAPI application? I need to protect endpoints and handle user sessions.",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=35)).isoformat(),
        },
        {
            "role": "assistant",
            "content": "Here's how to integrate with FastAPI:\n\n```python\nfrom fastapi import FastAPI, Depends, HTTPException, status\nfrom fastapi.security import HTTPBearer, HTTPAuthorizationCredentials\n\napp = FastAPI()\nsecurity = HTTPBearer()\nauth_service = AuthService('your-secret-key')\n\nasync def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):\n    try:\n        payload = jwt.decode(credentials.credentials, auth_service.secret_key, algorithms=['HS256'])\n        user_id = payload.get('user_id')\n        if user_id is None:\n            raise HTTPException(status_code=401, detail='Invalid token')\n        return {'user_id': user_id}\n    except jwt.PyJWTError:\n        raise HTTPException(status_code=401, detail='Invalid token')\n\n@app.post('/login')\nasync def login(username: str, password: str):\n    # Validate user credentials\n    user = authenticate_user(username, password)\n    if not user:\n        raise HTTPException(status_code=401, detail='Invalid credentials')\n    \n    token = auth_service.generate_token(user['id'])\n    return {'access_token': token, 'token_type': 'bearer'}\n\n@app.get('/protected')\nasync def protected_route(current_user: dict = Depends(get_current_user)):\n    return {'message': f'Hello user {current_user[\"user_id\"]}'}\n```\n\nThis provides complete API integration with JWT protection.",
            "timestamp": (datetime.now() - timedelta(hours=1, minutes=30)).isoformat(),
        },
    ]

    # Create context for skill
    skill_context = SkillContext(
        query="optimize this conversation about authentication system implementation",
        conversation_history=conversation_history,
        available_tokens=1000,  # Limited tokens to trigger optimization
    )

    # Initialize skill and execute
    skill = ContextOptimizationSkill()

    print(f"Original conversation: {len(conversation_history)} messages")
    print(f"Available tokens: {skill_context.available_tokens}")
    print()

    # Try different compression levels
    for level in [SkillLevel.METADATA, SkillLevel.SUMMARY, SkillLevel.FULL]:
        result = skill.execute(skill_context, level)
        print(f"=== {level.value.upper()} LEVEL ===")
        print(f"Tokens used: {result.tokens_used}")
        print(f"Execution time: {result.execution_time:.3f}s")
        print(f"Compression ratio: {result.metadata.get('compression_ratio', 0):.1%}")
        print(f"Content preview: {result.content[:200]}...")
        print()


def example_conversation_type_detection():
    """Example: Detecting different conversation types and optimizing accordingly."""
    print("=== Conversation Type Detection ===")

    # Code development conversation
    code_conversation = [
        {"role": "user", "content": "How do I implement a binary search tree in Python?"},
        {
            "role": "assistant",
            "content": "```python\nclass TreeNode:\n    def __init__(self, val=0, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right\n\nclass BST:\n    def __init__(self):\n        self.root = None\n    \n    def insert(self, val):\n        if not self.root:\n            self.root = TreeNode(val)\n        else:\n            self._insert_recursive(self.root, val)\n```",
        },
        {"role": "user", "content": "Can you add a delete method?"},
    ]

    # Problem solving conversation
    problem_conversation = [
        {"role": "user", "content": "I'm getting a segmentation fault when I run my program"},
        {
            "role": "assistant",
            "content": "This usually happens when accessing invalid memory. Use a debugger to find the exact line",
        },
        {"role": "user", "content": "The error occurs in the free() call. What does that mean?"},
    ]

    # Planning conversation
    planning_conversation = [
        {"role": "user", "content": "I need to plan the architecture for a microservices application"},
        {"role": "assistant", "content": "Start with API Gateway, then design service boundaries"},
        {"role": "user", "content": "Should I use Docker or Kubernetes for deployment?"},
    ]

    conversations = [
        ("Code Development", code_conversation),
        ("Problem Solving", problem_conversation),
        ("Planning", planning_conversation),
    ]

    skill = ContextOptimizationSkill()

    for name, messages in conversations:
        print(f"\n--- {name} Conversation ---")

        context = SkillContext(query="analyze this conversation", conversation_history=messages, available_tokens=500)

        result = skill.execute(context, SkillLevel.SUMMARY)

        detected_type = result.metadata.get("conversation_type", "unknown")
        print(f"Detected type: {detected_type}")
        print(f"Optimized content: {result.content[:150]}...")
        print(f"Key semantic tags: {result.metadata.get('semantic_tags', [])}")


def example_memory_integration():
    """Example: Integrating with memory system for persistent context."""
    print("=== Memory Integration Example ===")

    # Initialize memory integration
    memory_store = MemoryStore()
    context_memory = ContextMemoryIntegration(memory_store)

    # Sample conversation chunks
    from .context_optimization import ContextChunk

    chunks = [
        ContextChunk(
            content="We need to implement user authentication with JWT tokens",
            importance_score=0.9,
            source="user",
            chunk_type="message",
            semantic_tags=["implementation", "decision"],
        ),
        ContextChunk(
            content="```python\nimport jwt\ndef generate_token(user_id):\n    return jwt.encode({'user_id': user_id}, 'secret')\n```",
            importance_score=0.8,
            source="assistant",
            chunk_type="message",
            semantic_tags=["code", "implementation"],
        ),
        ContextChunk(
            content="The implementation failed with a secret key error. Need to fix configuration.",
            importance_score=0.7,
            source="user",
            chunk_type="message",
            semantic_tags=["error_resolution", "question"],
        ),
    ]

    # Simulate optimization metrics
    from .context_optimization import ContextMetrics

    metrics = ContextMetrics(
        original_tokens=500,
        compressed_tokens=150,
        compression_ratio=0.7,
        processing_time=0.5,
        information_retention_score=0.85,
        semantic_coherence_score=0.9,
    )

    # Save optimized context
    memory_id = context_memory.save_optimized_context(
        chunks=chunks,
        optimized_content="User requested JWT authentication implementation. Assistant provided Python code with jwt library. User encountered secret key configuration error that needs resolution.",
        metrics=metrics,
        conversation_type=ConversationType.CODE_DEVELOPMENT,
        session_id="auth_session_001",
    )

    print(f"Saved context optimization with ID: {memory_id}")

    # Retrieve relevant contexts
    relevant_contexts = context_memory.retrieve_relevant_context(
        query="JWT authentication implementation", max_contexts=3
    )

    print(f"\nFound {len(relevant_contexts)} relevant contexts:")
    for ctx in relevant_contexts:
        print(f"- Relevance: {ctx['relevance_score']:.2f}")
        print(f"- Type: {ctx['metadata'].get('conversation_type', 'unknown')}")
        print(f"- Content: {ctx['content'][:100]}...")
        print()

    # Generate insights
    insights = context_memory.generate_context_insights(days_back=7)
    print("Context Optimization Insights:")
    for insight in insights["insights"]:
        print(f"• {insight}")
    print()
    print("Recommendations:")
    for rec in insights["recommendations"]:
        print(f"• {rec}")


def example_context_checkpoints():
    """Example: Creating and restoring context checkpoints."""
    print("=== Context Checkpoints Example ===")

    memory_store = MemoryStore()
    context_memory = ContextMemoryIntegration(memory_store)

    # Create sample chunks
    from .context_optimization import ContextChunk

    chunks = [
        ContextChunk(
            content="Initial user request for authentication system",
            importance_score=0.8,
            source="user",
            chunk_type="message",
        ),
        ContextChunk(
            content="Implemented JWT authentication with secure password hashing",
            importance_score=0.9,
            source="assistant",
            chunk_type="message",
            semantic_tags=["implementation", "code"],
        ),
        ContextChunk(
            content="User reported installation issues with bcrypt library",
            importance_score=0.7,
            source="user",
            chunk_type="message",
            semantic_tags=["error_resolution"],
        ),
    ]

    # Create checkpoint
    checkpoint_id = context_memory.create_context_checkpoint(
        session_id="session_001", chunks=chunks, checkpoint_name="initial_auth_implementation"
    )

    print(f"Created checkpoint: {checkpoint_id}")

    # Simulate some time passing and changes made
    # ... (in real scenario, conversation would continue)

    # Restore from checkpoint
    restored_chunks = context_memory.restore_context_checkpoint(checkpoint_id)

    if restored_chunks:
        print(f"Restored {len(restored_chunks)} chunks from checkpoint")
        for i, chunk in enumerate(restored_chunks):
            print(f"{i + 1}. [{chunk.source}] {chunk.content[:50]}...")
    else:
        print("Failed to restore checkpoint")


def example_performance_analysis():
    """Example: Analyzing context optimization performance over time."""
    print("=== Performance Analysis Example ===")

    # Simulate multiple optimization sessions
    memory_store = MemoryStore()
    context_memory = ContextMemoryIntegration(memory_store)

    # Simulate historical data
    from .context_optimization import ContextChunk
    from .context_optimization import ContextMetrics
    from .context_optimization import ConversationType

    sample_metrics = [
        ContextMetrics(1000, 300, 0.7, 0.5, 0.85, 0.9),  # Good performance
        ContextMetrics(800, 200, 0.75, 0.4, 0.8, 0.85),  # Better performance
        ContextMetrics(1200, 250, 0.79, 0.6, 0.88, 0.92),  # Excellent performance
        ContextMetrics(900, 400, 0.56, 0.3, 0.75, 0.8),  # Lower performance
        ContextMetrics(1500, 350, 0.77, 0.7, 0.87, 0.91),  # Good performance
    ]

    # Create some sample optimized contexts
    chunks = [ContextChunk("Sample content", 0.8, "user", "message")]

    for i, metrics in enumerate(sample_metrics):
        context_memory.save_optimized_context(
            chunks=chunks,
            optimized_content=f"Optimized content {i + 1}",
            metrics=metrics,
            conversation_type=ConversationType.CODE_DEVELOPMENT,
            session_id=f"session_{i + 1:03d}",
        )

    # Generate insights
    insights = context_memory.generate_context_insights(days_back=7)

    print("Performance Analysis Results:")
    print(f"Total optimizations: {insights['statistics']['total_optimizations']}")
    print(f"Average compression: {insights['statistics']['average_compression']:.1%}")
    print(f"Average processing time: {insights['statistics']['average_processing_time']:.2f}s")
    print(f"Average information retention: {insights['statistics']['average_information_retention']:.1%}")
    print(f"Total tokens saved: {insights['statistics']['total_tokens_saved']:,}")

    print("\nKey Insights:")
    for insight in insights["insights"]:
        print(f"• {insight}")

    print("\nRecommendations:")
    for rec in insights["recommendations"]:
        print(f"• {rec}")


def run_all_examples():
    """Run all context optimization examples."""
    print("Context Optimization Specialist - Examples")
    print("=" * 50)

    try:
        example_basic_optimization()
        print("\n" + "=" * 50)

        example_conversation_type_detection()
        print("\n" + "=" * 50)

        example_memory_integration()
        print("\n" + "=" * 50)

        example_context_checkpoints()
        print("\n" + "=" * 50)

        example_performance_analysis()

    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
