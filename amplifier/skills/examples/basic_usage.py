#!/usr/bin/env python3
"""
Basic Skills Framework Usage Examples

Demonstrates core functionality of the Skills framework.
"""

from amplifier.skills import SkillContext
from amplifier.skills import SkillLevel
from amplifier.skills import compress_conversation_context
from amplifier.skills import find_and_execute_skill
from amplifier.skills import get_skill_recommendations


def example_context_compression():
    """Example: Compress conversation context."""
    print("=== Context Compression Example ===")

    messages = [
        {"role": "user", "content": "I need help with a complex Python project"},
        {"role": "assistant", "content": "I'd be happy to help! What specific aspects are you working on?"},
        {"role": "user", "content": "I'm building a data processing pipeline with pandas and numpy"},
        {"role": "assistant", "content": "Great! For data processing, you'll want to consider..."},
        {"role": "user", "content": "The pipeline processes large CSV files and generates reports"},
    ]

    # Compress to summary level
    result = compress_conversation_context(messages=messages, max_tokens=500, level="summary")

    print(f"Original messages: {result['original_messages']}")
    print(f"Tokens used: {result['tokens_used']}")
    print(f"Compression ratio: {result['compression_ratio']:.2f}")
    print(f"Compressed content:\n{result['compressed_content']}")
    print()


def example_skill_discovery():
    """Example: Discover relevant skills."""
    print("=== Skill Discovery Example ===")

    context = SkillContext(
        query="compress this long conversation to fit in token limits",
        conversation_history=[
            {"role": "user", "content": "This is a very long conversation..."},
            {"role": "assistant", "content": "I understand you need help with compression..."},
        ],
        available_tokens=2000,
    )

    # Get skill recommendations
    recommendations = get_skill_recommendations(context, limit=3)

    print("Skill recommendations:")
    for rec in recommendations:
        print(f"  • {rec['skill']} (confidence: {rec['confidence']:.2f})")
        print(f"    Description: {rec['description']}")
        print(f"    Reason: {rec['reason']}")
        print(f"    Tags: {', '.join(rec['tags'])}")
        print()


def example_automatic_skill_execution():
    """Example: Automatically find and execute best skill."""
    print("=== Automatic Skill Execution Example ===")

    context = SkillContext(
        query="summarize this technical discussion about databases",
        conversation_history=[
            {"role": "user", "content": "I'm working with PostgreSQL and need to optimize queries"},
            {"role": "assistant", "content": "For PostgreSQL optimization, consider indexing strategies..."},
            {"role": "user", "content": "What about connection pooling?"},
        ],
        available_tokens=1000,
    )

    # Find and execute best skill automatically
    result = find_and_execute_skill(context, level=SkillLevel.SUMMARY)

    print(f"Executed skill: {result.skill_name}")
    print(f"Tokens used: {result.tokens_used}")
    print(f"Execution time: {result.execution_time:.3f}s")
    print(f"Result:\n{result.content}")
    print()


def example_progressive_loading():
    """Example: Progressive context loading."""
    print("=== Progressive Loading Example ===")

    messages = [
        {"role": "system", "content": "You are a helpful AI assistant"},
        {"role": "user", "content": "Can you explain machine learning concepts?"},
        {"role": "assistant", "content": "Machine learning involves training algorithms..."},
        {"role": "user", "content": "What about neural networks specifically?"},
        {"role": "assistant", "content": "Neural networks are inspired by biological neurons..."},
    ]

    from amplifier.skills.templates import progressive_context_loading

    # Load progressively from metadata to full
    progressive = progressive_context_loading(messages, start_level="metadata")

    for level, result in progressive.items():
        print(f"=== {level.upper()} LEVEL ===")
        print(f"Tokens: {result['tokens_used']}")
        print(f"Content:\n{result['compressed_content']}\n")


def example_auto_context_management():
    """Example: Automatic context management."""
    print("=== Auto Context Management Example ===")

    messages = [
        {"role": "user", "content": f"Message {i}: This is a long message with lots of content."}
        for i in range(50)  # 50 messages
    ]

    from amplifier.skills.templates import auto_context_management

    # Manage context automatically based on token budget
    result = auto_context_management(messages=messages, available_tokens=2000, query="summarize the key points")

    print(f"Compression applied: {result['compression_applied']}")
    print(f"Original tokens: {result.get('original_tokens', 'N/A')}")
    print(f"Final tokens: {result['tokens_used']}")
    print(f"Strategy used: {result['level']}")
    print(f"Content preview:\n{result['content'][:300]}...")
    print()


if __name__ == "__main__":
    example_context_compression()
    example_skill_discovery()
    example_automatic_skill_execution()
    example_progressive_loading()
    example_auto_context_management()
