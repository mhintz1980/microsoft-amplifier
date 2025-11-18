"""
Token utilities for documentation management.
"""

import re
import json


def estimate_tokens(text: str) -> int:
    """
    Estimate token count for text.

    This is a simplified estimation - actual token count may vary
    based on the specific tokenizer being used.

    Args:
        text: Text to estimate tokens for

    Returns:
        Estimated token count
    """
    if not text:
        return 0

    # Basic token estimation (rough approximation)
    # In practice, this would use the actual tokenizer
    # For now, we use word-based estimation

    # Count words
    words = len(text.split())

    # Count punctuation and special characters as separate tokens
    special_chars = len(re.findall(r"[^\w\s]", text))

    # Count code blocks (tend to be more token-dense)
    code_blocks = len(re.findall(r"```.*?```", text, re.DOTALL))
    code_tokens = code_blocks * 50  # Rough estimate for code blocks

    # Estimate tokens (rough approximation: 1 token ~ 4 characters or 0.75 words)
    char_based = len(text) / 4
    word_based = words * 1.3

    # Take the higher estimate and add special characters and code tokens
    estimated = max(char_based, word_based) + special_chars / 2 + code_tokens

    return int(estimated)


def estimate_documentation_tokens(documentation: dict) -> dict:
    """
    Estimate token count for documentation structure.

    Args:
        documentation: Documentation dictionary

    Returns:
        Dictionary with token counts per level and section
    """
    token_counts = {"total": 0, "metadata": 0, "summary": 0, "detailed": 0, "full": 0, "sections": {}}

    # Count tokens for each level
    for level in ["metadata", "summary", "detailed", "full"]:
        content = documentation.get(level, {})

        if isinstance(content, dict) and "sections" in content:
            # Count sections
            level_tokens = 0
            for section_name, section_content in content["sections"].items():
                section_tokens = estimate_tokens(str(section_content))
                token_counts["sections"][f"{level}_{section_name}"] = section_tokens
                level_tokens += section_tokens

            token_counts[level] = level_tokens
            token_counts["total"] += level_tokens

        elif isinstance(content, str):
            level_tokens = estimate_tokens(content)
            token_counts[level] = level_tokens
            token_counts["total"] += level_tokens

    return token_counts


def optimize_for_tokens(text: str, target_tokens: int) -> str:
    """
    Optimize text to fit within target token limit.

    Args:
        text: Text to optimize
        target_tokens: Target token count

    Returns:
        Optimized text
    """
    if not text:
        return text

    current_tokens = estimate_tokens(text)

    if current_tokens <= target_tokens:
        return text

    # Calculate compression ratio needed
    compression_ratio = target_tokens / current_tokens

    # Apply optimization strategies based on compression needed
    if compression_ratio > 0.8:
        # Light compression - remove extra whitespace
        optimized = re.sub(r"\n{3,}", "\n\n", text)
        optimized = re.sub(r" +", " ", optimized)
    elif compression_ratio > 0.6:
        # Medium compression - summarize sections
        optimized = _summarize_text(text, compression_ratio)
    else:
        # Heavy compression - extract key points only
        optimized = _extract_key_points(text, target_tokens)

    # Verify we're within target
    final_tokens = estimate_tokens(optimized)
    if final_tokens > target_tokens:
        # Trim further if needed
        optimized = _trim_to_token_limit(optimized, target_tokens)

    return optimized


def _summarize_text(text: str, compression_ratio: float) -> str:
    """Summarize text to achieve target compression ratio."""

    # Split into paragraphs
    paragraphs = text.split("\n\n")

    # Keep most important paragraphs (based on simple heuristics)
    important_paragraphs = []

    for paragraph in paragraphs:
        # Keep short paragraphs and code blocks
        if len(paragraph) < 200 or paragraph.strip().startswith("```"):
            important_paragraphs.append(paragraph)
        # Keep paragraphs with emphasis
        elif "**" in paragraph or "*" in paragraph:
            important_paragraphs.append(paragraph)
        # Keep first paragraph
        elif not important_paragraphs:
            important_paragraphs.append(paragraph)

    return "\n\n".join(important_paragraphs)


def _extract_key_points(text: str, target_tokens: int) -> str:
    """Extract key points from text to fit within token limit."""

    # Extract headings and emphasized text
    lines = text.split("\n")
    key_lines = []

    for line in lines:
        line = line.strip()

        # Keep headings
        if line.startswith("#") or line.startswith("##") or line.startswith("###"):
            key_lines.append(line)

        # Keep emphasized text
        elif line.startswith("**") or line.startswith("*"):
            key_lines.append(line)

        # Keep code blocks
        elif line.startswith("```"):
            key_lines.append(line)

    # If still too long, take first few key lines
    result = "\n".join(key_lines)

    if estimate_tokens(result) > target_tokens:
        lines = result.split("\n")
        result = "\n".join(lines[: len(lines) // 2])

    return result


def _trim_to_token_limit(text: str, target_tokens: int) -> str:
    """Trim text to fit within exact token limit."""

    # Simple approach: truncate at sentence boundaries
    sentences = re.split(r"[.!?]+", text)

    result = ""
    for sentence in sentences:
        test_result = result + sentence + "."
        if estimate_tokens(test_result) > target_tokens:
            break
        result = test_result

    return result or text[: target_tokens * 3]  # Fallback to character truncation


def analyze_token_efficiency(documentation: dict) -> dict:
    """
    Analyze token efficiency of documentation.

    Args:
        documentation: Documentation to analyze

    Returns:
        Token efficiency analysis
    """
    token_counts = estimate_documentation_tokens(documentation)

    analysis = {
        "total_tokens": token_counts["total"],
        "token_distribution": {
            level: token_counts.get(level, 0) for level in ["metadata", "summary", "detailed", "full"]
        },
        "efficiency_score": 0.0,
        "recommendations": [],
    }

    # Calculate efficiency score
    if token_counts["total"] > 0:
        # Prefer documentation under 1000 total tokens
        optimal_size = 1000
        if token_counts["total"] <= optimal_size:
            analysis["efficiency_score"] = 1.0
        else:
            analysis["efficiency_score"] = optimal_size / token_counts["total"]

    # Generate recommendations
    if token_counts["total"] > 1500:
        analysis["recommendations"].append("Documentation is quite long - consider progressive disclosure")

    if token_counts["metadata"] > 100:
        analysis["recommendations"].append("Metadata exceeds recommended 50 tokens - make more concise")

    if token_counts["summary"] > 300:
        analysis["recommendations"].append("Summary exceeds recommended 200 tokens - focus on key points")

    return analysis
