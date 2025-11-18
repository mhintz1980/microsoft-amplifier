#!/usr/bin/env python3
"""
Memory Checkpoint System Demo

Demonstrates the complete checkpoint system functionality including:
- Basic checkpoint creation and restoration
- Auto-triggering based on various conditions
- Semantic analysis and progressive compression
- Context integration
- Hook system integration

Usage:
    python demo_checkpoint_system.py

This demo creates sample checkpoints and shows how the system works
with different types of content and triggering conditions.
"""

import json

# Add amplifier to path
import sys
import tempfile
from pathlib import Path

amplifier_path = Path(__file__).parent / "amplifier"
sys.path.insert(0, str(amplifier_path))

try:
    from memory.checkpoint_manager import CheckpointLevel
    from memory.checkpoint_manager import CheckpointManager
    from memory.checkpoint_triggers import CheckpointTriggerSystem
    from memory.context_integration import ContextIntegration
    from memory.hook_logger import HookLogger
    from memory.semantic_checkpointing import SemanticCheckpointManager

    from utils.context_compactor import create_context_chunk
except ImportError as e:
    print(f"Failed to import checkpoint modules: {e}")
    print("Make sure you're running this from the project root")
    sys.exit(1)


def print_section(title: str):
    """Print a section header"""
    print(f"\n{'=' * 60}")
    print(f" {title}")
    print(f"{'=' * 60}")


def print_checkpoint_info(checkpoint_manager: CheckpointManager, checkpoint_id: str):
    """Print detailed information about a checkpoint"""
    checkpoint = checkpoint_manager.checkpoints[checkpoint_id]

    print(f"Checkpoint ID: {checkpoint_id}")
    print(f"Task: {checkpoint.task_name}")
    print(f"Status: {checkpoint.task_status}")
    print(f"Level: {checkpoint.level.value}")
    print(f"Trigger: {checkpoint.trigger.value}")
    print(f"Timestamp: {checkpoint.timestamp}")
    print(f"Key Findings: {len(checkpoint.key_findings)}")
    print(f"Files Modified: {len(checkpoint.files_modified)}")
    print(f"Next Steps: {len(checkpoint.next_steps)}")

    if checkpoint.metadata:
        print("Metadata:")
        for key, value in checkpoint.metadata.items():
            print(f"  {key}: {value}")


def demo_basic_checkpointing():
    """Demonstrate basic checkpoint creation and restoration"""
    print_section("Basic Checkpointing Demo")

    # Create temporary directory for demo
    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        # Initialize checkpoint manager
        checkpoint_manager = CheckpointManager(
            data_dir=temp_dir,
            max_checkpoints=5,
            checkpoint_interval_minutes=1,  # Short for demo
        )

        print("✅ Checkpoint manager initialized")

        # Create a basic checkpoint
        print("\nCreating basic checkpoint...")
        checkpoint_id1 = checkpoint_manager.create_checkpoint(
            task_name="Feature Implementation",
            task_status="in_progress",
            level=CheckpointLevel.FULL,
            key_findings=["Authentication system designed", "Database schema created", "API endpoints planned"],
            files_modified=["auth.py", "models.py", "api.py"],
            next_steps=["Implement login functionality", "Add password validation", "Create user registration flow"],
            content="# Feature Implementation\n\n## Progress\n- ✅ Authentication system designed\n- ✅ Database schema created\n- 🔄 API endpoints planned\n\n## Code Implementation\n```python\ndef authenticate_user(username, password):\n    # Implementation details\n    pass\n```",
        )

        print(f"✅ Created checkpoint: {checkpoint_id1}")
        print_checkpoint_info(checkpoint_manager, checkpoint_id1)

        # Create another checkpoint for task completion
        print("\nMarking task as completed...")
        checkpoint_id2 = checkpoint_manager.complete_task(
            task_name="Feature Implementation",
            key_findings=[
                "All authentication features implemented",
                "Unit tests passing (95% coverage)",
                "Security review completed",
            ],
            files_modified=["auth.py", "models.py", "api.py", "tests/test_auth.py"],
            next_steps=["Deploy to staging environment", "Performance testing", "Documentation update"],
        )

        print(f"✅ Created completion checkpoint: {checkpoint_id2}")

        # Demonstrate restoration
        print(f"\nRestoring checkpoint {checkpoint_id1}...")
        restored = checkpoint_manager.restore_checkpoint(checkpoint_id1)

        if restored:
            print("✅ Checkpoint restored successfully")
            print(f"Restored task: {restored['context']['task_name']}")
            print(f"Status: {restored['context']['task_status']}")
            print(f"Key findings: {restored['context']['key_findings']}")

        # Show statistics
        print("\nCheckpoint Statistics:")
        stats = checkpoint_manager.get_checkpoint_statistics()
        print(json.dumps(stats, indent=2, default=str))

    finally:
        # Clean up
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleaned up temporary directory")


def demo_trigger_system():
    """Demonstrate the trigger system"""
    print_section("Trigger System Demo")

    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        checkpoint_manager = CheckpointManager(data_dir=temp_dir)
        trigger_system = CheckpointTriggerSystem(checkpoint_manager)

        print("✅ Trigger system initialized")

        # Test task completion detection
        print("\nTesting task completion detection...")
        completion_messages = [
            "I have successfully implemented the user authentication system.",
            "The database migration is now complete and all tests are passing.",
            "Fixed the critical bug in the payment processing module.",
            "Created the responsive user interface component as requested.",
        ]

        for i, message in enumerate(completion_messages):
            checkpoint_id = trigger_system.check_task_completion(message)
            if checkpoint_id:
                print(f"✅ Detected task completion in message {i + 1}: {checkpoint_id}")
            else:
                print(f"❓ No completion detected in message {i + 1}")

        # Test context usage monitoring
        print("\nTesting context usage monitoring...")
        context_data = {
            "messages": [
                {"role": "user", "content": "User request " * 100},
                {"role": "assistant", "content": "Assistant response " * 100},
                {"role": "user", "content": "Follow-up question " * 50},
            ],
            "files": {
                "large_file.py": "def function():\n    return 'large file'\n" * 200,
                "medium_file.js": "const variable = 'value';\n" * 100,
            },
            "tools": ["tool1", "tool2", "tool3"] * 20,
        }

        usage_percent = trigger_system.context_monitor.estimate_usage(context_data)
        print(f"📊 Estimated context usage: {usage_percent}%")

        # Check if context threshold trigger should fire
        checkpoint_id = trigger_system.check_context_usage(context_data)
        if checkpoint_id:
            print(f"✅ Context threshold checkpoint created: {checkpoint_id}")
        else:
            print("ℹ️ Context usage below threshold, no checkpoint created")

        # Test work area detection
        print("\nTesting work area detection...")
        file_sets = [
            [
                "/project/frontend/components/Button.js",
                "/project/frontend/pages/Home.jsx",
                "/project/frontend/styles/main.css",
            ],
            ["/project/backend/models/User.py", "/project/backend/api/auth.py", "/project/backend/config/database.py"],
            ["/project/tests/integration/test_auth.py", "/project/tests/unit/test_models.py"],
        ]

        for i, file_paths in enumerate(file_sets):
            work_area = trigger_system.work_area_monitor.detect_work_area(file_paths)
            print(f"📁 File set {i + 1}: Detected work area '{work_area}'")

            # Check if work area switch triggers checkpoint
            checkpoint_id = trigger_system.check_work_area_switch(file_paths)
            if checkpoint_id:
                print(f"✅ Work area switch checkpoint created: {checkpoint_id}")

        # Show trigger statistics
        print("\nTrigger System Statistics:")
        stats = trigger_system.get_trigger_statistics()
        print(json.dumps(stats, indent=2, default=str))

    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleaned up temporary directory")


def demo_semantic_checkpointing():
    """Demonstrate semantic checkpointing with progressive compression"""
    print_section("Semantic Checkpointing Demo")

    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        checkpoint_manager = CheckpointManager(data_dir=temp_dir)
        semantic_manager = SemanticCheckpointManager(checkpoint_manager)

        print("✅ Semantic checkpoint manager initialized")

        # Create test context chunks with varying importance
        print("\nCreating test context chunks...")
        chunks = []

        # High importance chunks
        high_importance_content = [
            "CRITICAL: Authentication bypass vulnerability discovered in login function",
            "IMPORTANT: Database connection pool exhaustion causing service outages",
            "DECISION: We will implement OAuth 2.0 for third-party authentication",
            "SOLUTION: Implemented caching layer to improve API response times",
        ]

        for i, content in enumerate(high_importance_content):
            chunk = create_context_chunk(
                content=content,
                source=f"critical_file_{i}.py",
                chunk_type="code",
                importance_score=0.9,
                tags=["critical", "security", "decision", "solution"],
            )
            chunks.append(chunk)

        # Medium importance chunks
        medium_importance_content = [
            "Added user profile management features",
            "Updated API documentation with new endpoints",
            "Refactored authentication module for better maintainability",
            "Implemented input validation for form submissions",
        ]

        for i, content in enumerate(medium_importance_content):
            chunk = create_context_chunk(
                content=content,
                source=f"feature_file_{i}.py",
                chunk_type="code",
                importance_score=0.6,
                tags=["feature", "documentation", "refactor", "validation"],
            )
            chunks.append(chunk)

        # Low importance chunks
        low_importance_content = [
            "Minor code formatting updates",
            "Added comments to utility functions",
            "Updated README with installation instructions",
            "Fixed typos in error messages",
        ]

        for i, content in enumerate(low_importance_content):
            chunk = create_context_chunk(
                content=content,
                source=f"cleanup_file_{i}.py",
                chunk_type="code",
                importance_score=0.3,
                tags=["cleanup", "documentation", "fix"],
            )
            chunks.append(chunk)

        print(f"✅ Created {len(chunks)} context chunks")

        # Create semantic checkpoint
        print("\nCreating semantic checkpoint with progressive compression...")
        checkpoint_id = semantic_manager.create_semantic_checkpoint(
            task_name="Security & Feature Implementation",
            context_chunks=chunks,
            task_status="in_progress",
            target_tokens=300,  # Force compression
            preserve_semantics=True,
        )

        print(f"✅ Created semantic checkpoint: {checkpoint_id}")

        # Show checkpoint details
        checkpoint = checkpoint_manager.checkpoints[checkpoint_id]
        print("\nCheckpoint Details:")
        print(f"Level: {checkpoint.level.value}")
        print(f"Content length: {len(checkpoint.content)} characters")

        # Show semantic metadata
        metadata = checkpoint.metadata
        if metadata and "compression_result" in metadata:
            compression = metadata["compression_result"]
            print("\nCompression Results:")
            print(f"  Original chunks: {metadata.get('original_chunk_count', 0)}")
            print(f"  Used chunks: {metadata.get('used_chunk_count', 0)}")
            print(f"  Discarded chunks: {metadata.get('discarded_chunk_count', 0)}")
            print(f"  Compression ratio: {compression.get('compression_ratio', 0):.3f}")
            print(f"  Semantic preservation: {compression.get('semantic_preservation', 0):.3f}")
            print(f"  Original tokens: {compression.get('original_tokens', 0)}")
            print(f"  Compressed tokens: {compression.get('compressed_tokens', 0)}")

        # Show compressed content preview
        print("\nCompressed Content Preview:")
        print("-" * 40)
        content_preview = checkpoint.content[:500] + "..." if len(checkpoint.content) > 500 else checkpoint.content
        print(content_preview)
        print("-" * 40)

    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleaned up temporary directory")


def demo_context_integration():
    """Demonstrate context integration features"""
    print_section("Context Integration Demo")

    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        checkpoint_manager = CheckpointManager(data_dir=temp_dir)
        context_integration = ContextIntegration(checkpoint_manager)

        print("✅ Context integration initialized")

        # Create comprehensive context data
        print("\nCreating comprehensive context data...")
        context_data = {
            "messages": [
                {
                    "role": "user",
                    "content": "I need to implement a user authentication system with JWT tokens and password reset functionality. The system should be secure and follow OWASP guidelines.",
                },
                {
                    "role": "assistant",
                    "content": "I'll help you implement a secure authentication system. Let me start by creating the user model and authentication service. We'll use bcrypt for password hashing and JWT for session management.",
                },
                {
                    "role": "user",
                    "content": "Great! Also, make sure to include proper input validation and error handling. I want to prevent common security vulnerabilities like SQL injection and XSS.",
                },
                {
                    "role": "assistant",
                    "content": "Absolutely! I'll implement comprehensive input validation using Pydantic models, parameterized queries to prevent SQL injection, and proper output encoding to prevent XSS attacks. Let me create the implementation now.",
                },
            ],
            "files": {
                "models/user.py": """
class User(BaseModel):
    id: int
    username: str
    email: str
    password_hash: str
    created_at: datetime
    last_login: Optional[datetime]
    is_active: bool = True
""",
                "services/auth.py": """
class AuthService:
    def __init__(self, db: Database):
        self.db = db

    def register_user(self, username: str, email: str, password: str) -> User:
        # Validate input
        # Hash password with bcrypt
        # Create user in database
        pass

    def authenticate_user(self, username: str, password: str) -> Optional[User]:
        # Validate credentials
        # Check password hash
        # Return user if valid
        pass
""",
                "api/auth_routes.py": """
@router.post("/register")
async def register(user_data: UserCreate):
    # Register new user
    pass

@router.post("/login")
async def login(credentials: UserLogin):
    # Authenticate user
    # Return JWT token
    pass
""",
            },
            "tools": ["database", "bcrypt", "jwt", "pydantic", "fastapi"],
        }

        print("✅ Context data created")

        # Analyze context
        print("\nAnalyzing context and generating recommendations...")
        analysis = context_integration.analyze_and_optimize_context(context_data)

        print("📊 Context Analysis Results:")
        print(f"  Current usage: {analysis['current_usage']}%")
        print(f"  Usage trend: {analysis['usage_trend']}")
        print(f"  Recommendations: {len(analysis['recommendations'])}")

        for i, rec in enumerate(analysis["recommendations"], 1):
            print(f"    {i}. {rec}")

        # Create smart checkpoint
        print("\nCreating intelligent checkpoint...")
        checkpoint_id = context_integration.create_smart_checkpoint(
            task_name="Authentication System Implementation", context_data=context_data, importance_threshold=0.4
        )

        if checkpoint_id:
            print(f"✅ Smart checkpoint created: {checkpoint_id}")

            # Show checkpoint summary
            checkpoint = checkpoint_manager.checkpoints[checkpoint_id]
            print(f"  Level: {checkpoint.level.value}")
            print(f"  Key findings: {len(checkpoint.key_findings)}")
            print(f"  Next steps: {len(checkpoint.next_steps)}")

            if checkpoint.key_findings:
                print("  Key findings preview:")
                for finding in checkpoint.key_findings[:3]:
                    print(f"    - {finding}")
        else:
            print("ℹ️ No significant content found for checkpointing")

        # Test context restoration
        if checkpoint_id:
            print("\nRestoring context from checkpoint...")
            restored = context_integration.restore_context_from_checkpoint(checkpoint_id)

            if restored:
                print("✅ Context restored successfully")
                print(f"  Restored chunks: {len(restored['context_chunks'])}")
                print(f"  Reconstruction method: {restored['restoration_metadata']['reconstruction_method']}")
                print(f"  Checkpoint age: {restored['restoration_metadata']['checkpoint_age']}")

    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleaned up temporary directory")


def demo_complete_workflow():
    """Demonstrate a complete workflow with all features"""
    print_section("Complete Workflow Demo")

    temp_dir = Path(tempfile.mkdtemp())
    print(f"Using temporary directory: {temp_dir}")

    try:
        # Initialize all components
        checkpoint_manager = CheckpointManager(data_dir=temp_dir)
        trigger_system = CheckpointTriggerSystem(checkpoint_manager)
        context_integration = ContextIntegration(checkpoint_manager)
        semantic_manager = SemanticCheckpointManager(checkpoint_manager)

        print("✅ All components initialized")

        # Simulate a development workflow
        print("\n🚀 Starting development workflow simulation...")

        # Phase 1: Initial planning
        print("\n📋 Phase 1: Project Planning")
        checkpoint_manager.update_current_task("E-commerce Platform", "planning", "backend")

        planning_chunks = [
            create_context_chunk(
                content="Project requirements: User authentication, product catalog, shopping cart, payment processing",
                source="requirements.md",
                chunk_type="planning",
                importance_score=0.8,
                tags=["requirements", "planning"],
            ),
            create_context_chunk(
                content="Architecture decisions: Microservices with REST APIs, PostgreSQL for data, Redis for caching",
                source="architecture.md",
                chunk_type="planning",
                importance_score=0.9,
                tags=["architecture", "decisions"],
            ),
        ]

        checkpoint_id1 = context_integration.create_context_checkpoint(
            context_chunks=planning_chunks, task_name="E-commerce Platform Planning", task_status="planning_complete"
        )
        print(f"✅ Planning checkpoint created: {checkpoint_id1}")

        # Phase 2: Development
        print("\n💻 Phase 2: Development")
        checkpoint_manager.update_current_task("User Authentication", "in_progress", "backend")

        # Simulate task completion detection
        completion_message = "Successfully implemented the complete user authentication system with JWT tokens, password hashing, and secure session management. All unit tests are passing and the security review has been completed."

        checkpoint_id2 = trigger_system.check_task_completion(completion_message)
        if checkpoint_id2:
            print(f"✅ Task completion detected and checkpointed: {checkpoint_id2}")

        # Phase 3: Work area switch
        print("\n🔄 Phase 3: Work Area Switch")
        frontend_files = [
            "/project/frontend/components/Login.jsx",
            "/project/frontend/pages/Dashboard.jsx",
            "/project/frontend/styles/auth.css",
        ]

        checkpoint_id3 = trigger_system.check_work_area_switch(frontend_files)
        if checkpoint_id3:
            print(f"✅ Work area switch detected and checkpointed: {checkpoint_id3}")

        # Phase 4: Context threshold checkpointing
        print("\n📊 Phase 4: Context Management")

        # Create large context to trigger threshold
        large_chunks = []
        for i in range(15):
            chunk = create_context_chunk(
                content=f"Large code file {i}: " + "Implementation details and documentation " * 30,
                source=f"large_module_{i}.py",
                chunk_type="code",
                importance_score=0.5 + (i * 0.02),
            )
            large_chunks.append(chunk)

        # This should trigger context threshold due to large content
        checkpoint_id4 = semantic_manager.create_semantic_checkpoint(
            task_name="Large Module Implementation",
            context_chunks=large_chunks,
            target_tokens=400,
            preserve_semantics=True,
        )
        print(f"✅ Large content checkpoint created: {checkpoint_id4}")

        # Phase 5: Project completion
        print("\n🎉 Phase 5: Project Completion")

        final_checkpoint_id = checkpoint_manager.complete_task(
            task_name="E-commerce Platform",
            key_findings=[
                "Complete e-commerce platform implemented",
                "All security measures in place",
                "Performance optimization completed",
                "Documentation and testing done",
            ],
            files_modified=["auth.py", "products.py", "cart.py", "payments.py", "frontend/components/*", "tests/*"],
            next_steps=["Deploy to production", "Monitor performance metrics", "Plan phase 2 features"],
        )
        print(f"✅ Project completion checkpoint: {final_checkpoint_id}")

        # Show final statistics
        print("\n📈 Final Project Statistics:")
        stats = checkpoint_manager.get_checkpoint_statistics()

        print(f"Total checkpoints: {stats['total_checkpoints']}")
        print(f"Unique tasks: {stats['unique_tasks']}")
        print(f"Most common task: {stats.get('most_common_task', 'N/A')}")

        print("\nTrigger Statistics:")
        trigger_stats = trigger_system.get_trigger_statistics()
        print(f"Total triggers: {trigger_stats['total_triggers']}")
        print(f"Triggers per hour: {trigger_stats['triggers_per_hour']:.2f}")
        print(f"Current work area: {trigger_stats['current_work_area']}")

        print("\n✅ Complete workflow demo finished successfully!")

    finally:
        import shutil

        shutil.rmtree(temp_dir, ignore_errors=True)
        print("\n🧹 Cleaned up temporary directory")


def main():
    """Main demo function"""
    print("🚀 Memory Checkpoint System Demo")
    print("=" * 60)
    print("This demo showcases the complete checkpoint system functionality")
    print("including automatic triggering, semantic analysis, and context management.")

    try:
        # Run all demos
        demo_basic_checkpointing()
        demo_trigger_system()
        demo_semantic_checkpointing()
        demo_context_integration()
        demo_complete_workflow()

        print_section("Demo Complete")
        print("✅ All demos completed successfully!")
        print("\nKey Features Demonstrated:")
        print("• Basic checkpoint creation and restoration")
        print("• Automatic trigger detection (task completion, context usage, work area switching)")
        print("• Semantic analysis and progressive compression")
        print("• Context integration and intelligent checkpointing")
        print("• Complete development workflow simulation")
        print("• Statistics and monitoring capabilities")

        print("\nThe checkpoint system is ready for production use!")

    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
