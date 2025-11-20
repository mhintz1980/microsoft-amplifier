"""Token counting and truncation utilities.

Fallback implementation for testing without tiktoken dependency.
"""


def estimate_tokens(text: str, model: str = "cl100k_base") -> int:
    """Estimate the number of tokens in text.

    Args:
        text: The text to count tokens for
        model: The model identifier (for compatibility)

    Returns:
        Estimated number of tokens in the text
    """
    # Simple estimation: ~4 characters per token for English text
    if not text:
        return 0

    # Word-based estimation
    words = len(text.split())

    # Character-based estimation (more conservative)
    char_estimate = len(text) // 4

    # Return the more conservative estimate
    return max(words, char_estimate)


def count_tokens(text: str, model: str = "cl100k_base") -> int:
    """Count the number of tokens in text.

    Args:
        text: The text to count tokens for
        model: The model identifier

    Returns:
        Number of tokens in the text
    """
    return estimate_tokens(text, model)


def truncate_to_tokens(text: str, max_tokens: int, model: str = "cl100k_base") -> str:
    """Truncate text to fit within token limit.

    Args:
        text: The text to truncate
        max_tokens: Maximum number of tokens allowed
        model: The model identifier

    Returns:
        Truncated text
    """
    if not text or max_tokens <= 0:
        return ""

    # Rough estimation - truncate to character limit
    # Conservative: 4 characters per token
    max_chars = max_tokens * 4

    if len(text) <= max_chars:
        return text

    # Truncate and add ellipsis
    truncated = text[: max_chars - 3] + "..."
    return truncated
