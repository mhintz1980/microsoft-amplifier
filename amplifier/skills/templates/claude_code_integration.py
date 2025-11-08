"""
Claude Code Integration Hooks

Integration layer for using Skills framework with Claude Code.
Provides convenient interfaces for context management and skill execution.
"""

from typing import Any

from .. import SkillContext
from .. import SkillLevel
from .. import find_and_execute_skill
from .. import get_skill_recommendations


def compress_conversation_context(
    messages: list[dict[str, Any]], max_tokens: int = 20000, level: str = "summary"
) -> dict[str, Any]:
    """
    Compress conversation context using the Skills framework.

    Args:
        messages: List of conversation messages with 'role' and 'content' keys
        max_tokens: Maximum tokens for compressed output
        level: Compression level - "metadata", "summary", or "full"

    Returns:
        Dictionary with compressed content and metadata
    """
    skill_level = (
        SkillLevel.METADATA if level == "metadata" else SkillLevel.FULL if level == "full" else SkillLevel.SUMMARY
    )

    context = SkillContext(
        query="compress conversation context", conversation_history=messages, available_tokens=max_tokens
    )

    result = find_and_execute_skill(context, level=skill_level)

    return {
        "compressed_content": result.content,
        "tokens_used": result.tokens_used,
        "compression_ratio": result.metadata.get("compression_ratio", 1.0) if result.metadata else 1.0,
        "original_messages": len(messages),
        "skill_used": result.skill_name,
        "execution_time": result.execution_time,
    }


def analyze_conversation_needs(messages: list[dict[str, Any]], query: str = "") -> list[dict[str, Any]]:
    """
    Analyze conversation and recommend relevant skills.

    Args:
        messages: List of conversation messages
        query: Current user query or task description

    Returns:
        List of skill recommendations with explanations
    """
    context = SkillContext(query=query or "analyze conversation", conversation_history=messages, available_tokens=5000)

    recommendations = get_skill_recommendations(context, limit=5)

    return [
        {
            "skill": rec["skill_name"],
            "description": rec["description"],
            "confidence": rec["confidence"],
            "reason": rec["reason"],
            "tags": rec["tags"],
        }
        for rec in recommendations
    ]


def progressive_context_loading(messages: list[dict[str, Any]], start_level: str = "metadata") -> dict[str, Any]:
    """
    Load context progressively from minimal to detailed.

    Args:
        messages: List of conversation messages
        start_level: Starting compression level

    Returns:
        Dictionary with progressive context levels
    """
    levels = ["metadata", "summary", "full"]
    start_idx = levels.index(start_level) if start_level in levels else 0

    progressive_results = {}

    for level in levels[start_idx:]:
        result = compress_conversation_context(
            messages=messages, max_tokens=20000 if level == "full" else 5000 if level == "summary" else 500, level=level
        )

        progressive_results[level] = result

        # Stop if we're using too many tokens
        if result["tokens_used"] > 15000:
            break

    return progressive_results


def auto_context_management(messages: list[dict[str, Any]], available_tokens: int, query: str = "") -> dict[str, Any]:
    """
    Automatically manage context based on available tokens.

    Args:
        messages: List of conversation messages
        available_tokens: Available token budget
        query: Current query for context relevance

    Returns:
        Optimized context within token limits
    """
    # Estimate total tokens in original messages
    total_chars = sum(len(msg.get("content", "")) for msg in messages)
    estimated_tokens = total_chars // 4  # Rough estimate

    if estimated_tokens <= available_tokens:
        # No compression needed
        return {
            "content": "\n".join(f"[{msg.get('role', 'unknown')}] {msg.get('content', '')}" for msg in messages),
            "tokens_used": estimated_tokens,
            "compression_applied": False,
            "level": "original",
        }

    # Choose appropriate compression level
    if available_tokens < 1000:
        level = "metadata"
    elif available_tokens < 5000:
        level = "summary"
    else:
        level = "full"

    result = compress_conversation_context(messages=messages, max_tokens=available_tokens, level=level)

    result["compression_applied"] = True
    result["original_tokens"] = estimated_tokens

    return result


# Claude Code specific utilities
def create_skill_context_from_claude_session(
    session_messages: list[dict[str, Any]], current_query: str, token_budget: int = 10000
) -> SkillContext:
    """
    Create SkillContext from Claude Code session data.
    """
    return SkillContext(
        query=current_query,
        conversation_history=session_messages,
        available_tokens=token_budget,
        user_preferences={
            "compression_aggressive": token_budget < 5000,
            "preserve_code_blocks": True,
            "maintain_conversation_flow": True,
        },
    )


def suggest_context_strategy(message_count: int, token_budget: int, has_code: bool = False) -> dict[str, Any]:
    """
    Suggest optimal context management strategy.
    """
    strategy = {
        "recommendation": "full_context",
        "reasoning": "Adequate token budget available",
        "compression_level": "none",
        "estimated_savings": 0,
    }

    # Estimate tokens needed
    estimated_tokens = message_count * 200  # Rough estimate per message

    if estimated_tokens > token_budget:
        if token_budget < 2000:
            strategy.update(
                {
                    "recommendation": "aggressive_compression",
                    "reasoning": "Very limited token budget",
                    "compression_level": "metadata",
                    "estimated_savings": estimated_tokens - 500,
                }
            )
        elif token_budget < 8000:
            strategy.update(
                {
                    "recommendation": "moderate_compression",
                    "reasoning": "Moderate token constraints",
                    "compression_level": "summary",
                    "estimated_savings": estimated_tokens - 3000,
                }
            )
        else:
            strategy.update(
                {
                    "recommendation": "light_compression",
                    "reasoning": "Some optimization needed",
                    "compression_level": "full",
                    "estimated_savings": estimated_tokens - token_budget * 0.8,
                }
            )

    if has_code:
        strategy["preserve_code_priority"] = True
        strategy["reasoning"] += "; Code content preservation prioritized"

    return strategy
