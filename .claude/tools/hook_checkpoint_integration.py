#!/usr/bin/env python3
"""
Checkpoint Integration Hook - Automatic Checkpointing for Claude Code

Integrates the checkpoint system with Claude Code hooks for automatic context saving.
Provides seamless checkpointing without user intervention.

Features:
- Automatic checkpoint creation on tool use
- Session start/end checkpointing
- Task completion detection
- Context usage monitoring
- Work area switching detection
"""

import json
import sys
from pathlib import Path

# Add the amplifier module to the path
amplifier_path = Path(__file__).parent.parent.parent / "amplifier"
sys.path.insert(0, str(amplifier_path))

try:
    from memory.checkpoint_manager import get_checkpoint_manager
    from memory.checkpoint_triggers import get_trigger_system
    from memory.hook_logger import HookLogger
except ImportError as e:
    print(f"Failed to import checkpoint modules: {e}", file=sys.stderr)
    sys.exit(1)


def main():
    """Main hook function"""
    # Get hook data from environment or stdin
    hook_name = sys.argv[1] if len(sys.argv) > 1 else "unknown"

    # Read hook data from stdin if available
    hook_data = {}
    try:
        if not sys.stdin.isatty():
            hook_data = json.load(sys.stdin)
    except (json.JSONDecodeError, Exception):
        pass

    # Initialize logger
    logger = HookLogger("checkpoint_integration")
    logger.info(f"Processing hook: {hook_name}")

    try:
        # Get checkpoint manager and trigger system
        checkpoint_manager = get_checkpoint_manager()
        trigger_system = get_trigger_system(checkpoint_manager)

        # Process the hook
        checkpoint_id = trigger_system.process_hook_data(hook_name, hook_data)

        if checkpoint_id:
            logger.info(f"Created checkpoint: {checkpoint_id}")
            print(f"checkpoint_created:{checkpoint_id}")
        else:
            logger.debug("No checkpoint created")

    except Exception as e:
        logger.error(f"Error processing hook: {e}")
        print(f"error:{str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
