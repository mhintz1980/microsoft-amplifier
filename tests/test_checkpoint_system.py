"""
Tests for the Memory Checkpoint System

Comprehensive tests for checkpoint creation, restoration, triggers, and semantic analysis.
Validates that the checkpoint system works correctly and integrates properly with
other components.

Test Coverage:
- Basic checkpoint creation and restoration
- Auto-trigger functionality
- Context integration
- Semantic analysis and compression
- Hook system integration
- Edge cases and error handling
"""

import tempfile
import unittest
from pathlib import Path

from amplifier.memory.checkpoint_manager import CheckpointLevel
from amplifier.memory.checkpoint_manager import CheckpointManager
from amplifier.memory.checkpoint_manager import CheckpointTrigger
from amplifier.memory.checkpoint_triggers import CheckpointTriggerSystem
from amplifier.memory.context_integration import ContextIntegration
from amplifier.memory.semantic_checkpointing import SemanticCheckpointManager
from amplifier.utils.context_compactor import create_context_chunk


class TestCheckpointManager(unittest.TestCase):
    """Test basic checkpoint manager functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checkpoint_manager = CheckpointManager(
            data_dir=self.temp_dir,
            max_checkpoints=10,
            checkpoint_interval_minutes=1,  # Short for testing
        )

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_checkpoint_creation(self):
        """Test basic checkpoint creation"""
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name="Test Task",
            task_status="in_progress",
            level=CheckpointLevel.FULL,
            key_findings=["Test finding"],
            files_modified=["test.py"],
            next_steps=["Complete implementation"],
        )

        self.assertIsNotNone(checkpoint_id)
        self.assertIn(checkpoint_id, self.checkpoint_manager.checkpoints)

        checkpoint = self.checkpoint_manager.checkpoints[checkpoint_id]
        self.assertEqual(checkpoint.task_name, "Test Task")
        self.assertEqual(checkpoint.task_status, "in_progress")
        self.assertEqual(checkpoint.level, CheckpointLevel.FULL)
        self.assertEqual(checkpoint.key_findings, ["Test finding"])
        self.assertEqual(checkpoint.files_modified, ["test.py"])
        self.assertEqual(checkpoint.next_steps, ["Complete implementation"])

    def test_checkpoint_restoration(self):
        """Test checkpoint restoration"""
        # Create a checkpoint
        checkpoint_id = self.checkpoint_manager.create_checkpoint(
            task_name="Test Task",
            task_status="in_progress",
            content="Test content for restoration",
        )

        # Restore the checkpoint
        restored = self.checkpoint_manager.restore_checkpoint(checkpoint_id)

        self.assertIsNotNone(restored)
        self.assertEqual(restored["checkpoint"]["task_name"], "Test Task")
        self.assertEqual(restored["context"]["task_name"], "Test Task")
        self.assertEqual(restored["context"]["content"], "Test content for restoration")
        self.assertIn("restoration_metadata", restored)

    def test_task_completion(self):
        """Test task completion checkpointing"""
        checkpoint_id = self.checkpoint_manager.complete_task(
            task_name="Completed Task",
            key_findings=["Task completed successfully"],
            files_modified=["completed.py"],
            next_steps=["Start next task"],
        )

        checkpoint = self.checkpoint_manager.checkpoints[checkpoint_id]
        self.assertEqual(checkpoint.task_status, "completed")
        self.assertEqual(checkpoint.trigger, CheckpointTrigger.TASK_COMPLETION)
        self.assertIsNone(self.checkpoint_manager.current_task)

    def test_work_area_switching(self):
        """Test work area switching detection"""
        # Set initial work area
        self.checkpoint_manager.update_current_task("Test Task", work_area="frontend")

        # Switch work area
        self.checkpoint_manager.update_current_task("Test Task", work_area="backend")

        # Should have created a checkpoint for the switch
        recent_checkpoints = self.checkpoint_manager.get_recent_checkpoints(limit=5)
        switch_checkpoints = [c for c in recent_checkpoints if c.trigger == CheckpointTrigger.WORK_AREA_SWITCH]

        self.assertTrue(len(switch_checkpoints) > 0)
        switch_checkpoint = switch_checkpoints[0]
        self.assertEqual(switch_checkpoint.work_area, "backend")

    def test_checkpoint_statistics(self):
        """Test checkpoint statistics"""
        # Create multiple checkpoints
        for i in range(3):
            self.checkpoint_manager.create_checkpoint(
                task_name=f"Task {i}",
                task_status="in_progress",
                trigger=CheckpointTrigger.MANUAL,
            )

        stats = self.checkpoint_manager.get_checkpoint_statistics()

        self.assertEqual(stats["total_checkpoints"], 3)
        self.assertIn("triggers", stats)
        self.assertIn("levels", stats)
        self.assertEqual(stats["triggers"]["manual"], 3)

    def test_checkpoint_cleanup(self):
        """Test automatic cleanup of old checkpoints"""
        # Set low limit for testing
        self.checkpoint_manager.max_checkpoints = 3

        # Create more checkpoints than the limit
        for i in range(5):
            self.checkpoint_manager.create_checkpoint(
                task_name=f"Task {i}",
                task_status="in_progress",
            )

        # Should only have 3 checkpoints (the most recent ones)
        self.assertEqual(len(self.checkpoint_manager.checkpoints), 3)

        # Check that we have the most recent ones
        recent_checkpoints = self.checkpoint_manager.get_recent_checkpoints(limit=10)
        task_names = [c.task_name for c in recent_checkpoints]
        self.assertIn("Task 4", task_names)
        self.assertIn("Task 3", task_names)
        self.assertIn("Task 2", task_names)


class TestCheckpointTriggers(unittest.TestCase):
    """Test checkpoint trigger system"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checkpoint_manager = CheckpointManager(data_dir=self.temp_dir)
        self.trigger_system = CheckpointTriggerSystem(self.checkpoint_manager)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_task_completion_detection(self):
        """Test task completion detection"""
        completion_messages = [
            "I have successfully implemented the new feature.",
            "The task is now complete and all tests are passing.",
            "Fixed the bug in the authentication system.",
            "Created the user interface component as requested.",
        ]

        completion_count = 0
        for message in completion_messages:
            checkpoint_id = self.trigger_system.check_task_completion(message)
            if checkpoint_id:
                completion_count += 1

        self.assertGreater(completion_count, 0)

    def test_context_usage_monitoring(self):
        """Test context usage monitoring"""
        # Create mock context data
        context_data = {
            "messages": [
                {"role": "user", "content": "User message " * 100},
                {"role": "assistant", "content": "Assistant response " * 100},
            ],
            "files": {
                "test.py": "def test_function():\n    return 'test'\n" * 100,
            },
            "tools": ["tool1", "tool2", "tool3"] * 10,
        }

        # Check if usage monitoring works
        usage_percent = self.trigger_system.context_monitor.estimate_usage(context_data)
        self.assertIsInstance(usage_percent, int)
        self.assertGreaterEqual(usage_percent, 0)
        self.assertLessEqual(usage_percent, 100)

    def test_work_area_detection(self):
        """Test work area detection"""
        file_paths = [
            "/project/frontend/components/Button.js",
            "/project/frontend/pages/Home.jsx",
            "/project/frontend/utils/helpers.js",
        ]

        work_area = self.trigger_system.work_area_monitor.detect_work_area(file_paths)
        self.assertEqual(work_area, "frontend")

    def test_hook_data_processing(self):
        """Test hook data processing"""
        # Test session start hook
        checkpoint_id = self.trigger_system.process_hook_data("session_start", {})
        self.assertIsNotNone(checkpoint_id)

        # Test tool use hook
        tool_data = {
            "input": "Implement the user authentication system",
            "output": {"files_created": ["auth.py", "user.py"]},
        }
        checkpoint_id = self.trigger_system.process_hook_data("post_tool_use", tool_data)
        # May or may not create checkpoint depending on conditions

    def test_trigger_statistics(self):
        """Test trigger statistics"""
        stats = self.trigger_system.get_trigger_statistics()

        self.assertIn("total_triggers", stats)
        self.assertIn("trigger_types", stats)
        self.assertIn("context_usage", stats)
        self.assertIn("current_work_area", stats)


class TestContextIntegration(unittest.TestCase):
    """Test context integration functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checkpoint_manager = CheckpointManager(data_dir=self.temp_dir)
        self.context_integration = ContextIntegration(self.checkpoint_manager)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_context_checkpoint_creation(self):
        """Test creating checkpoint from context chunks"""
        # Create test context chunks
        chunks = [
            create_context_chunk(
                content="This is important code that implements a key feature",
                source="main.py",
                chunk_type="code",
                importance_score=0.8,
                tags=["important", "feature"],
            ),
            create_context_chunk(
                content="User feedback about the new interface design",
                source="feedback.txt",
                chunk_type="feedback",
                importance_score=0.6,
                tags=["user", "feedback"],
            ),
        ]

        checkpoint_id = self.context_integration.create_context_checkpoint(
            context_chunks=chunks,
            task_name="Integration Test",
            task_status="in_progress",
        )

        self.assertIsNotNone(checkpoint_id)
        checkpoint = self.checkpoint_manager.checkpoints[checkpoint_id]
        self.assertEqual(checkpoint.task_name, "Integration Test")

    def test_context_restoration(self):
        """Test context restoration from checkpoint"""
        # Create a checkpoint first
        chunks = [
            create_context_chunk(
                content="Original context content",
                source="test.txt",
                chunk_type="content",
                importance_score=0.7,
            ),
        ]

        checkpoint_id = self.context_integration.create_context_checkpoint(
            context_chunks=chunks,
            task_name="Restoration Test",
        )

        # Restore context
        restored = self.context_integration.restore_context_from_checkpoint(checkpoint_id)

        self.assertIsNotNone(restored)
        self.assertIn("checkpoint", restored)
        self.assertIn("context_chunks", restored)
        self.assertIn("reconstructed_context", restored)
        self.assertIn("restoration_metadata", restored)

    def test_context_analysis(self):
        """Test context analysis and optimization"""
        context_data = {
            "messages": [
                {"role": "user", "content": "User message content"},
                {"role": "assistant", "content": "Assistant response content"},
            ],
            "files": {
                "test.py": "def function(): pass",
            },
        }

        analysis = self.context_integration.analyze_and_optimize_context(context_data)

        self.assertIn("current_usage", analysis)
        self.assertIn("usage_trend", analysis)
        self.assertIn("recommendations", analysis)
        self.assertIn("checkpoint_suggestion", analysis)

    def test_smart_checkpoint_creation(self):
        """Test intelligent checkpoint creation"""
        context_data = {
            "messages": [
                {"role": "user", "content": "Important user request with detailed requirements"},
                {"role": "assistant", "content": "Detailed response with implementation details"},
            ],
            "files": {
                "important.py": "class ImportantClass:\n    def important_method(self):\n        pass",
            },
        }

        checkpoint_id = self.context_integration.create_smart_checkpoint(
            task_name="Smart Test",
            context_data=context_data,
            importance_threshold=0.5,
        )

        # Should create checkpoint if content meets threshold
        if checkpoint_id:
            checkpoint = self.checkpoint_manager.checkpoints[checkpoint_id]
            self.assertEqual(checkpoint.task_name, "Smart Test")
            self.assertTrue(checkpoint.metadata.get("smart_checkpoint", False))


class TestSemanticCheckpointing(unittest.TestCase):
    """Test semantic checkpointing functionality"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checkpoint_manager = CheckpointManager(data_dir=self.temp_dir)
        self.semantic_manager = SemanticCheckpointManager(self.checkpoint_manager)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_semantic_importance_scoring(self):
        """Test semantic importance scoring"""
        from amplifier.memory.semantic_checkpointing import SemanticImportanceScorer

        scorer = SemanticImportanceScorer()

        # Create test chunks with different importance levels
        high_importance_chunk = create_context_chunk(
            content="Critical error in authentication system that needs immediate fixing",
            source="auth.py",
            chunk_type="code",
            importance_score=0.7,
            tags=["error", "critical", "auth"],
        )

        low_importance_chunk = create_context_chunk(
            content="Simple comment with minor information",
            source="comment.py",
            chunk_type="comment",
            importance_score=0.3,
            tags=["comment", "minor"],
        )

        scored_chunks = scorer.score_chunks([high_importance_chunk, low_importance_chunk])

        # High importance chunk should come first
        self.assertEqual(scored_chunks[0].source, "auth.py")
        self.assertGreater(scored_chunks[0].importance_score, scored_chunks[1].importance_score)

    def test_progressive_compression(self):
        """Test progressive compression"""
        from amplifier.memory.semantic_checkpointing import ProgressiveCompressor

        compressor = ProgressiveCompressor()

        # Create test chunks
        chunks = []
        for i in range(10):
            chunk = create_context_chunk(
                content=f"This is chunk {i} with some content " * 20,
                source=f"file_{i}.py",
                chunk_type="code",
                importance_score=0.5 + (i * 0.05),  # Varying importance
            )
            chunks.append(chunk)

        # Compress with semantic preservation
        result = compressor.compress_progressively(chunks, target_tokens=100, preserve_semantics=True)

        self.assertIn("compressed_content", result)
        self.assertIn("chunks_used", result)
        self.assertIn("compression_ratio", result)
        self.assertIn("semantic_preservation", result)

        # Should use some chunks but not all (due to target token limit)
        self.assertGreater(len(result["chunks_used"]), 0)
        self.assertLess(len(result["chunks_used"]), len(chunks))

    def test_semantic_checkpoint_creation(self):
        """Test semantic checkpoint creation"""
        # Create test context chunks
        chunks = []
        for i in range(5):
            chunk = create_context_chunk(
                content=f"Important content {i}: " + "This is a detailed explanation " * 10,
                source=f"module_{i}.py",
                chunk_type="code",
                importance_score=0.6 + (i * 0.08),
                tags=[f"topic_{i}", "important"],
            )
            chunks.append(chunk)

        checkpoint_id = self.semantic_manager.create_semantic_checkpoint(
            task_name="Semantic Test",
            context_chunks=chunks,
            task_status="in_progress",
            target_tokens=200,
            preserve_semantics=True,
        )

        self.assertIsNotNone(checkpoint_id)
        checkpoint = self.checkpoint_manager.checkpoints[checkpoint_id]

        # Verify semantic checkpoint metadata
        self.assertTrue(checkpoint.metadata.get("semantic_checkpoint", False))
        self.assertIn("compression_result", checkpoint.metadata)
        self.assertIn("semantic_preservation", checkpoint.metadata)


class TestCheckpointSystemIntegration(unittest.TestCase):
    """Test integration between different checkpoint system components"""

    def setUp(self):
        """Set up test environment"""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.checkpoint_manager = CheckpointManager(data_dir=self.temp_dir)
        self.trigger_system = CheckpointTriggerSystem(self.checkpoint_manager)
        self.context_integration = ContextIntegration(self.checkpoint_manager)
        self.semantic_manager = SemanticCheckpointManager(self.checkpoint_manager)

    def tearDown(self):
        """Clean up test environment"""
        import shutil

        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_end_to_end_workflow(self):
        """Test complete workflow from creation to restoration"""
        # 1. Create context chunks
        chunks = [
            create_context_chunk(
                content="Implementation of user authentication system",
                source="auth.py",
                chunk_type="code",
                importance_score=0.8,
                tags=["auth", "security", "implementation"],
            ),
            create_context_chunk(
                content="User feedback: The login page needs improvement",
                source="feedback.txt",
                chunk_type="feedback",
                importance_score=0.6,
                tags=["user", "feedback", "ui"],
            ),
        ]

        # 2. Create semantic checkpoint
        checkpoint_id = self.semantic_manager.create_semantic_checkpoint(
            task_name="Authentication Implementation",
            context_chunks=chunks,
            task_status="in_progress",
        )

        # 3. Update current task in checkpoint manager
        self.checkpoint_manager.update_current_task("Authentication Implementation", "in_progress", work_area="backend")

        # 4. Simulate task completion
        completion_id = self.checkpoint_manager.complete_task(
            task_name="Authentication Implementation",
            key_findings=["Implemented secure login system"],
            files_modified=["auth.py", "login.html"],
            next_steps=["Add password reset functionality"],
        )

        # 5. Verify both checkpoints exist
        self.assertIn(checkpoint_id, self.checkpoint_manager.checkpoints)
        self.assertIn(completion_id, self.checkpoint_manager.checkpoints)

        # 6. Test restoration
        restored = self.context_integration.restore_context_from_checkpoint(checkpoint_id)
        self.assertIsNotNone(restored)

        # 7. Test statistics
        stats = self.checkpoint_manager.get_checkpoint_statistics()
        self.assertEqual(stats["total_checkpoints"], 2)
        self.assertIn("Authentication Implementation", stats.get("most_common_task", ""))

    def test_auto_trigger_integration(self):
        """Test integration of auto-triggers with semantic analysis"""
        # Set up current task
        self.checkpoint_manager.update_current_task("Auto Trigger Test", "in_progress")

        # Create context chunks that would trigger various conditions
        chunks = []
        for i in range(20):  # Create enough content to potentially trigger threshold
            chunk = create_context_chunk(
                content=f"Large content block {i}: " + "Detailed implementation " * 50,
                source=f"large_file_{i}.py",
                chunk_type="code",
                importance_score=0.5,
            )
            chunks.append(chunk)

        # Create semantic checkpoint (this might trigger context threshold)
        checkpoint_id = self.semantic_manager.create_semantic_checkpoint(
            task_name="Auto Trigger Test",
            context_chunks=chunks,
        )

        # Check auto-triggers
        auto_checkpoints = self.checkpoint_manager.check_auto_triggers()

        # Should have at least the semantic checkpoint
        self.assertIsNotNone(checkpoint_id)

        # May have additional auto-triggered checkpoints
        if auto_checkpoints:
            self.assertIsInstance(auto_checkpoints, list)

    def test_error_handling(self):
        """Test error handling in various scenarios"""
        # Test restoration of non-existent checkpoint
        restored = self.checkpoint_manager.restore_checkpoint("non_existent_id")
        self.assertIsNone(restored)

        # Test empty context chunks
        checkpoint_id = self.context_integration.create_context_checkpoint(
            context_chunks=[],
            task_name="Empty Test",
        )
        self.assertIsNotNone(checkpoint_id)  # Should still create checkpoint

        # Test invalid context data
        analysis = self.context_integration.analyze_and_optimize_context({})
        self.assertIn("current_usage", analysis)  # Should handle empty data gracefully


if __name__ == "__main__":
    # Run all tests
    unittest.main(verbosity=2)
