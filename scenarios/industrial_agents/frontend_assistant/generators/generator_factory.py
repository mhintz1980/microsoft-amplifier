"""
Generator Factory for Industrial Frontend Components

Creates framework-specific generators for industrial interfaces.
"""

from .base_generator import BaseGenerator
from .react_generator import ReactGenerator
from .streamlit_generator import StreamlitGenerator
from .vue_generator import VueGenerator


class GeneratorFactory:
    """Factory for creating framework-specific generators."""

    def __init__(self):
        """Initialize generator factory."""
        self._generators = {
            "react": ReactGenerator,
            "vue": VueGenerator,
            "streamlit": StreamlitGenerator,
        }

    def create_generator(self, framework: str) -> BaseGenerator | None:
        """Create a generator for the specified framework.

        Args:
            framework: Target framework (react, vue, streamlit)

        Returns:
            Generator instance or None if framework not supported
        """
        generator_class = self._generators.get(framework.lower())
        if generator_class:
            return generator_class()
        return None

    def get_supported_frameworks(self) -> list[str]:
        """Get list of supported frameworks.

        Returns:
            List of supported framework names
        """
        return list(self._generators.keys())

    def is_framework_supported(self, framework: str) -> bool:
        """Check if a framework is supported.

        Args:
            framework: Framework name to check

        Returns:
            True if supported, False otherwise
        """
        return framework.lower() in self._generators
