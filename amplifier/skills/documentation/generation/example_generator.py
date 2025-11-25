"""
Example generator for automatic documentation generation.

This module provides functionality to generate code examples for documentation.
"""

from typing import List, Dict, Any


class ExampleGenerator:
    """Generates code examples for documentation."""

    def __init__(self):
        """Initialize the example generator."""
        self.examples = []

    def generate_example(self, code: str, description: str, language: str = "python") -> Dict[str, Any]:
        """
        Generate a code example.

        Args:
            code: The code example
            description: Description of what the code does
            language: Programming language (default: python)

        Returns:
            Dictionary containing the example
        """
        return {
            "code": code,
            "description": description,
            "language": language
        }

    def add_example(self, example: Dict[str, Any]) -> None:
        """Add an example to the collection."""
        self.examples.append(example)

    def get_examples(self) -> List[Dict[str, Any]]:
        """Get all examples."""
        return self.examples.copy()