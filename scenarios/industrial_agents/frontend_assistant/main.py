#!/usr/bin/env python3
"""
Industrial Frontend Assistant - Main CLI and Orchestrator

Generates industrial-grade dashboards, control panels, and engineering interfaces
optimized for factory environments.
"""

import sys
from pathlib import Path

import click

from amplifier.utils.logger import get_logger

from .generators.generator_factory import GeneratorFactory
from .utils.project_builder import ProjectBuilder
from .utils.template_manager import TemplateManager
from .validators.factory_validator import FactoryValidator

logger = get_logger(__name__)


class IndustrialFrontendAssistant:
    """Main orchestrator for industrial frontend generation."""

    def __init__(self, output_dir: Path):
        """Initialize the assistant.

        Args:
            output_dir: Directory where generated code will be placed
        """
        self.output_dir = output_dir
        self.template_manager = TemplateManager()
        self.generator_factory = GeneratorFactory()
        self.validator = FactoryValidator()
        self.project_builder = ProjectBuilder(output_dir)

    def generate(
        self,
        interface_type: str,
        framework: str,
        template: str,
        factory_options: list[str],
        theme: str,
        data_source: str,
        features: list[str],
        responsive: bool,
        offline_support: bool,
    ) -> bool:
        """Generate industrial frontend interface.

        Args:
            interface_type: Type of interface (dashboard, control-panel, calculator, documentation)
            framework: Target framework (react, vue, streamlit)
            template: Specific template to use
            factory_options: Factory environment optimizations
            theme: Color theme to apply
            data_source: Data source configuration
            features: Additional features to include
            responsive: Enable responsive design
            offline_support: Add offline capabilities

        Returns:
            True if successful, False otherwise
        """
        try:
            # Validate inputs
            logger.info(f"🏭 Generating industrial {interface_type} with {framework}")

            # Get template configuration
            template_config = self.template_manager.get_template(interface_type, framework, template)
            if not template_config:
                logger.error(f"Template not found: {interface_type}/{framework}/{template}")
                return False

            # Validate factory requirements
            if not self.validator.validate_requirements(factory_options):
                logger.error("Factory requirements validation failed")
                return False

            # Create generator
            generator = self.generator_factory.create_generator(framework)
            if not generator:
                logger.error(f"Unsupported framework: {framework}")
                return False

            # Generate project structure
            project_config = {
                "type": interface_type,
                "framework": framework,
                "template": template,
                "factory_options": factory_options,
                "theme": theme,
                "data_source": data_source,
                "features": features,
                "responsive": responsive,
                "offline_support": offline_support,
            }

            # Build the project
            success = self.project_builder.build_project(template_config, project_config, generator)

            if success:
                # Run post-generation validation
                if self.validator.validate_generated_code(self.output_dir):
                    logger.info("✅ Industrial interface generated successfully")
                    logger.info(f"📁 Output directory: {self.output_dir}")
                    return True
                logger.error("Generated code validation failed")
                return False
            logger.error("Project generation failed")
            return False

        except Exception as e:
            logger.error(f"Generation failed: {e}")
            return False


# CLI Interface
@click.command()
@click.option(
    "--type",
    "interface_type",
    type=click.Choice(["dashboard", "control-panel", "calculator", "documentation"]),
    required=True,
    help="Type of industrial interface to generate",
)
@click.option(
    "--framework",
    type=click.Choice(["react", "vue", "streamlit"]),
    required=True,
    help="Target framework for the interface",
)
@click.option(
    "--template",
    type=str,
    required=True,
    help="Specific template to use (e.g., pump-monitoring, pipe-sizing)",
)
@click.option(
    "--output",
    type=click.Path(path_type=Path),
    required=True,
    help="Output directory for generated code",
)
@click.option(
    "--factory-opts",
    "factory_options",
    multiple=True,
    default=["touch-friendly", "high-contrast"],
    help="Factory environment optimizations",
)
@click.option(
    "--theme",
    type=click.Choice(["factory-dark", "factory-light", "high-contrast"]),
    default="factory-dark",
    help="Color theme for the interface",
)
@click.option(
    "--data-source",
    type=click.Choice(["mqtt", "rest-api", "websocket", "mock"]),
    default="mock",
    help="Data source configuration",
)
@click.option(
    "--features",
    multiple=True,
    default=[],
    help="Additional features (alerts, export, authentication)",
)
@click.option(
    "--responsive/--no-responsive",
    default=True,
    help="Enable responsive design for different screen sizes",
)
@click.option(
    "--offline-support/--no-offline-support",
    default=True,
    help="Add offline capabilities",
)
@click.option(
    "--verbose",
    is_flag=True,
    help="Enable verbose logging",
)
def main(
    interface_type: str,
    framework: str,
    template: str,
    output: Path,
    factory_options: tuple[str],
    theme: str,
    data_source: str,
    features: tuple[str],
    responsive: bool,
    offline_support: bool,
    verbose: bool,
):
    """Industrial Frontend Assistant - Generate factory-optimized interfaces.

    Generate industrial-grade dashboards, control panels, and engineering tools
    optimized for factory environments with touch interfaces and real-time data.

    Example:
        python -m scenarios.industrial_agents.frontend_assistant \\
            --type dashboard \\
            --framework react \\
            --template pump-monitoring \\
            --output factory_dashboard/ \\
            --factory-opts touch-friendly high-contrast
    """
    # Setup logging
    if verbose:
        logger.logger.setLevel("DEBUG")

    # Create output directory
    output.mkdir(parents=True, exist_ok=True)

    # Initialize assistant
    assistant = IndustrialFrontendAssistant(output)

    # Convert tuples to lists
    factory_opts_list = list(factory_options)
    features_list = list(features)

    # Display configuration
    logger.info("🏭 Industrial Frontend Assistant")
    logger.info(f"  Interface Type: {interface_type}")
    logger.info(f"  Framework: {framework}")
    logger.info(f"  Template: {template}")
    logger.info(f"  Output: {output}")
    logger.info(f"  Theme: {theme}")
    logger.info(f"  Data Source: {data_source}")
    logger.info(f"  Factory Options: {', '.join(factory_opts_list)}")
    if features_list:
        logger.info(f"  Features: {', '.join(features_list)}")
    logger.info(f"  Responsive: {responsive}")
    logger.info(f"  Offline Support: {offline_support}")

    # Generate the interface
    success = assistant.generate(
        interface_type=interface_type,
        framework=framework,
        template=template,
        factory_options=factory_opts_list,
        theme=theme,
        data_source=data_source,
        features=features_list,
        responsive=responsive,
        offline_support=offline_support,
    )

    if success:
        logger.info("\n✨ Industrial interface generation complete!")
        logger.info(f"📁 Generated in: {output}")
        logger.info("\nNext steps:")
        logger.info(f"  1. cd {output}")
        logger.info("  2. Follow the README.md for setup instructions")
        logger.info("  3. Start development server and test in factory environment")
        return 0
    logger.error("\n❌ Interface generation failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
