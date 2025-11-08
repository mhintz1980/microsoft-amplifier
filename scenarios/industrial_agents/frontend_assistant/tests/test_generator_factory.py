"""
Tests for Generator Factory
"""

from generators.generator_factory import GeneratorFactory
from generators.react_generator import ReactGenerator
from generators.streamlit_generator import StreamlitGenerator
from generators.vue_generator import VueGenerator


class TestGeneratorFactory:
    """Test cases for GeneratorFactory."""

    def setup_method(self):
        """Set up test fixtures."""
        self.factory = GeneratorFactory()

    def test_create_react_generator(self):
        """Test creating React generator."""
        generator = self.factory.create_generator("react")
        assert isinstance(generator, ReactGenerator)

    def test_create_vue_generator(self):
        """Test creating Vue generator."""
        generator = self.factory.create_generator("vue")
        assert isinstance(generator, VueGenerator)

    def test_create_streamlit_generator(self):
        """Test creating Streamlit generator."""
        generator = self.factory.create_generator("streamlit")
        assert isinstance(generator, StreamlitGenerator)

    def test_create_unsupported_generator(self):
        """Test creating unsupported generator returns None."""
        generator = self.factory.create_generator("angular")
        assert generator is None

    def test_get_supported_frameworks(self):
        """Test getting supported frameworks."""
        frameworks = self.factory.get_supported_frameworks()
        assert "react" in frameworks
        assert "vue" in frameworks
        assert "streamlit" in frameworks

    def test_is_framework_supported(self):
        """Test framework support checking."""
        assert self.factory.is_framework_supported("react")
        assert self.factory.is_framework_supported("vue")
        assert self.factory.is_framework_supported("streamlit")
        assert not self.factory.is_framework_supported("angular")
        assert not self.factory.is_framework_supported("svelte")

    def test_case_insensitive_framework_names(self):
        """Test case insensitive framework names."""
        generator_upper = self.factory.create_generator("REACT")
        generator_lower = self.factory.create_generator("react")
        generator_mixed = self.factory.create_generator("React")

        assert isinstance(generator_upper, ReactGenerator)
        assert isinstance(generator_lower, ReactGenerator)
        assert isinstance(generator_mixed, ReactGenerator)
