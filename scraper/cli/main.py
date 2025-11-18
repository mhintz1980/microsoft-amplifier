#!/usr/bin/env python3
"""
Modular Scraper CLI

Command-line interface for the modular documentation scraper.
Replaces the original monolithic CLI with enhanced functionality
and better user experience.

Features:
- Interactive configuration wizard
- Multiple operation modes (scrape, build, estimate)
- Checkpoint management and resumption
- Progress monitoring and statistics
- Error handling and recovery
- Extensible plugin architecture
"""

import argparse
import asyncio
import json
import logging
import sys
from pathlib import Path

import pydantic
from pydantic import BaseModel
from pydantic import Field

from scraper.core.categorizer import CategorizerConfig
from scraper.core.content_extractor import ExtractorConfig

# Import modular components
from scraper.core.scraper import CoreScraper
from scraper.core.scraper import ScrapingConfig
from scraper.core.scraper import estimate_page_count
from scraper.core.url_manager import URLManagerConfig
from scraper.generators.skill import SkillConfig
from scraper.generators.skill import SkillGenerator
from scraper.generators.skill import load_pages_from_data

# Configure logging for CLI
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class CLIConfig(BaseModel):
    """Configuration loaded from JSON file."""

    name: str = Field(..., description="Skill name")
    description: str = Field("", description="Skill description")
    base_url: str = Field(..., description="Base documentation URL")
    start_urls: list[str] = Field(default_factory=list, description="Additional starting URLs")
    max_pages: int = Field(500, description="Maximum pages to scrape")
    rate_limit: float = Field(0.5, description="Delay between requests")
    timeout: int = Field(30, description="Request timeout")
    max_retries: int = Field(3, description="Maximum retry attempts")
    concurrent_requests: int = Field(5, description="Concurrent requests")

    # Selectors
    selectors: dict[str, str] = Field(
        default_factory=lambda: {"main_content": "div[role='main']", "title": "title", "code_blocks": "pre code"}
    )

    # URL patterns
    url_patterns: dict[str, list[str]] = Field(default_factory=lambda: {"include": [], "exclude": []})

    # Categories
    categories: dict[str, list[str]] = Field(default_factory=dict)

    # Checkpoint settings
    checkpoint: dict[str, any] = Field(default_factory=lambda: {"enabled": True, "interval": 100})


class InteractiveConfigurator:
    """Interactive configuration wizard for new users."""

    def __init__(self):
        self.config = {}

    def run(self) -> CLIConfig:
        """Run the interactive configuration wizard."""
        print("\n" + "=" * 60)
        print("🚀 Modular Documentation Scraper - Configuration Wizard")
        print("=" * 60 + "\n")

        # Basic information
        print("📋 Basic Information")
        print("-" * 20)
        self.config["name"] = self._get_input("Skill name (e.g., 'react', 'godot')", required=True)
        self.config["description"] = self._get_input(
            "Skill description (e.g., 'React framework for building user interfaces')", required=True
        )
        self.config["base_url"] = self._get_input(
            "Base documentation URL (e.g., https://docs.example.com/)", required=True, validator=self._validate_url
        )

        # Ensure base_url ends with /
        if not self.config["base_url"].endswith("/"):
            self.config["base_url"] += "/"

        # Additional start URLs
        print("\n🔗 Additional URLs (optional)")
        print("-" * 30)
        start_urls_input = self._get_input("Additional starting URLs (comma-separated, optional)", required=False)
        if start_urls_input:
            self.config["start_urls"] = [url.strip() for url in start_urls_input.split(",")]
        else:
            self.config["start_urls"] = []

        # CSS Selectors
        print("\n🎯 CSS Selectors")
        print("-" * 15)
        print("Press Enter to use defaults for most documentation sites")

        selectors = {}
        selectors["main_content"] = self._get_input(
            "Main content selector [div[role='main']]", default="div[role='main']"
        )
        selectors["title"] = self._get_input("Title selector [title]", default="title")
        selectors["code_blocks"] = self._get_input("Code blocks selector [pre code]", default="pre code")
        self.config["selectors"] = selectors

        # URL Patterns
        print("\n🔍 URL Patterns (optional)")
        print("-" * 25)
        include_input = self._get_input("Include patterns (comma-separated, e.g., /docs/, /api/)", required=False)
        exclude_input = self._get_input("Exclude patterns (comma-separated, e.g., /search, /static/)", required=False)

        self.config["url_patterns"] = {
            "include": [p.strip() for p in include_input.split(",") if p.strip()] if include_input else [],
            "exclude": [p.strip() for p in exclude_input.split(",") if p.strip()] if exclude_input else [],
        }

        # Categories
        print("\n📂 Categories (optional)")
        print("-" * 20)
        print("Define how pages should be categorized. Press Enter to skip for auto-detection.")

        categories = {}
        while True:
            category_name = self._get_input("Category name (or press Enter to finish)", required=False)
            if not category_name:
                break

            keywords = self._get_input(f"Keywords for '{category_name}' (comma-separated)", required=True)
            categories[category_name] = [k.strip() for k in keywords.split(",")]

        self.config["categories"] = categories

        # Performance settings
        print("\n⚙️  Performance Settings")
        print("-" * 25)
        self.config["rate_limit"] = float(
            self._get_input("Rate limit in seconds [0.5]", default="0.5", validator=self._validate_float)
        )
        self.config["max_pages"] = int(
            self._get_input("Maximum pages to scrape [500]", default="500", validator=self._validate_int)
        )
        self.config["concurrent_requests"] = int(
            self._get_input("Concurrent requests [5]", default="5", validator=self._validate_int)
        )

        # Checkpoint settings
        print("\n💾 Checkpoint Settings")
        print("-" * 22)
        checkpoint_enabled = self._get_input(
            "Enable checkpoints for resumable scraping? [Y/n]", default="y"
        ).lower() in ["y", "yes", ""]

        self.config["checkpoint"] = {
            "enabled": checkpoint_enabled,
            "interval": int(
                self._get_input("Checkpoint interval (pages) [100]", default="100", validator=self._validate_int)
            ),
        }

        return CLIConfig(**self.config)

    def _get_input(self, prompt: str, required: bool = False, default: str = None, validator=None) -> str:
        """Get user input with validation."""
        while True:
            if default:
                full_prompt = f"{prompt} [{default}]: "
            else:
                full_prompt = f"{prompt}: "

            user_input = input(full_prompt).strip()

            if not user_input and default:
                return default

            if not user_input and required:
                print("❌ This field is required. Please provide a value.")
                continue

            if validator and user_input:
                try:
                    validator(user_input)
                except ValueError as e:
                    print(f"❌ Invalid input: {e}")
                    continue

            return user_input

    @staticmethod
    def _validate_url(url: str) -> None:
        """Validate URL format."""
        if not url.startswith(("http://", "https://")):
            raise ValueError("URL must start with http:// or https://")

    @staticmethod
    def _validate_float(value: str) -> None:
        """Validate float value."""
        try:
            float(value)
        except ValueError:
            raise ValueError("Must be a valid number")

    @staticmethod
    def _validate_int(value: str) -> None:
        """Validate integer value."""
        try:
            int(value)
        except ValueError:
            raise ValueError("Must be a valid integer")


class ConfigManager:
    """Manages configuration loading and validation."""

    @staticmethod
    def load_config(config_path: str) -> CLIConfig:
        """Load and validate configuration from file."""
        try:
            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in configuration file: {e}")

        try:
            return CLIConfig(**config_data)
        except pydantic.ValidationError as e:
            raise ValueError(f"Configuration validation failed: {e}")

    @staticmethod
    def save_config(config: CLIConfig, config_path: str) -> None:
        """Save configuration to file."""
        config_dir = Path(config_path).parent
        config_dir.mkdir(parents=True, exist_ok=True)

        with open(config_path, "w", encoding="utf-8") as f:
            json.dump(config.dict(), f, indent=2, ensure_ascii=False)

    @staticmethod
    def validate_config(config: CLIConfig) -> list[str]:
        """Validate configuration and return list of warnings."""
        warnings = []

        # Check for common issues
        if config.max_pages > 10000:
            warnings.append(f"Very high max_pages ({config.max_pages}) - scraping may take a very long time")

        if config.rate_limit < 0.1:
            warnings.append(f"Very low rate_limit ({config.rate_limit}s) - may get rate limited")

        if config.concurrent_requests > 20:
            warnings.append(f"High concurrent_requests ({config.concurrent_requests}) - may overload server")

        if not config.description:
            warnings.append("No description provided - consider adding one for better skill quality")

        return warnings


class ProgressDisplay:
    """Enhanced progress display for long-running operations."""

    def __init__(self):
        self.last_update = 0
        self.start_time = 0

    def start_operation(self, operation: str) -> None:
        """Start tracking an operation."""
        self.start_time = asyncio.get_event_loop().time()
        print(f"\n{'=' * 60}")
        print(f"🚀 {operation}")
        print(f"{'=' * 60}\n")

    def show_progress(self, current: int, total: int, message: str = "") -> None:
        """Show progress bar and statistics."""
        elapsed = asyncio.get_event_loop().time() - self.start_time

        if total > 0:
            percentage = (current / total) * 100
            bar_length = 40
            filled_length = int(bar_length * current // total)
            bar = "█" * filled_length + "░" * (bar_length - filled_length)

            print(f"\r[{bar}] {percentage:.1f}% ({current}/{total}) {message}", end="", flush=True)
        else:
            rate = current / elapsed if elapsed > 0 else 0
            print(f"\r⚡ {current} completed | {rate:.1f}/sec | {message}", end="", flush=True)

    def finish_operation(self, message: str) -> None:
        """Finish tracking an operation."""
        elapsed = asyncio.get_event_loop().time() - self.start_time
        print(f"\n✅ {message} (completed in {elapsed:.1f}s)\n")


class ModularCLI:
    """Main CLI application."""

    def __init__(self):
        self.progress = ProgressDisplay()

    def create_parser(self) -> argparse.ArgumentParser:
        """Create the command-line argument parser."""
        parser = argparse.ArgumentParser(
            description="Modular Documentation Scraper - Convert docs to Claude skills",
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Interactive configuration
  python -m scraper.cli.main --interactive

  # Use configuration file
  python -m scraper.cli.main --config configs/react.json

  # Quick mode
  python -m scraper.cli.main --name react --url https://react.dev/

  # Estimate page count
  python -m scraper.cli.main --estimate --config configs/react.json

  # Build from existing data
  python -m scraper.cli.main --build --data-dir output/react_data
            """,
        )

        # Operation modes
        mode_group = parser.add_mutually_exclusive_group(required=True)
        mode_group.add_argument("--interactive", "-i", action="store_true", help="Interactive configuration wizard")
        mode_group.add_argument("--config", "-c", type=str, help="Configuration file path")
        mode_group.add_argument("--quick", action="store_true", help="Quick configuration mode")
        mode_group.add_argument("--estimate", "-e", action="store_true", help="Estimate page count without scraping")
        mode_group.add_argument("--build", "-b", action="store_true", help="Build skill from existing scraped data")

        # Quick mode options
        parser.add_argument("--name", type=str, help="Skill name (for quick mode)")
        parser.add_argument("--url", type=str, help="Base URL (for quick mode)")
        parser.add_argument("--description", "-d", type=str, help="Skill description (for quick mode)")

        # Operation options
        parser.add_argument("--output-dir", "-o", type=str, default="output", help="Output directory (default: output)")
        parser.add_argument("--data-dir", type=str, help="Data directory for build mode")
        parser.add_argument(
            "--max-discovery", type=int, default=100, help="Maximum URLs to discover for estimation (default: 100)"
        )

        # Scraping options
        parser.add_argument("--resume", action="store_true", help="Resume from checkpoint")
        parser.add_argument("--fresh", action="store_true", help="Start fresh (clear checkpoint)")
        parser.add_argument("--no-checkpoint", action="store_true", help="Disable checkpointing")
        parser.add_argument("--max-pages", type=int, help="Override maximum pages to scrape")
        parser.add_argument("--dry-run", action="store_true", help="Preview what would be scraped (no actual scraping)")

        # Build options
        parser.add_argument("--skip-scrape", action="store_true", help="Skip scraping, use existing data")
        parser.add_argument(
            "--create-readme", action="store_true", default=True, help="Create README file in skill directory"
        )

        # Output options
        parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
        parser.add_argument("--quiet", "-q", action="store_true", help="Quiet output (errors only)")

        return parser

    def setup_logging(self, verbose: bool = False, quiet: bool = False) -> None:
        """Setup logging configuration."""
        if quiet:
            level = logging.ERROR
        elif verbose:
            level = logging.DEBUG
        else:
            level = logging.INFO

        logging.getLogger().setLevel(level)

    async def run_estimate(self, config: CLIConfig, max_discovery: int) -> None:
        """Run page count estimation."""
        self.progress.start_operation(f"Estimating pages for {config.name}")

        try:
            estimated_pages = await estimate_page_count(
                base_url=config.base_url,
                max_discovery=max_discovery,
                rate_limit=config.rate_limit,
                url_manager=URLManagerConfig(
                    base_url=config.base_url,
                    include_patterns=config.url_patterns["include"],
                    exclude_patterns=config.url_patterns["exclude"],
                ),
            )

            print("\n📊 Estimation Results:")
            print(f"   Base URL: {config.base_url}")
            print(f"   URLs discovered: {max_discovery}")
            print(f"   Valid URLs: ~{estimated_pages}")
            print(f"   Recommended max_pages: {min(estimated_pages, config.max_pages)}")

            # Estimate time
            estimated_time = estimated_pages * config.rate_limit / 60  # minutes
            print(f"   Estimated scraping time: {estimated_time:.1f} minutes")

            print("\n💡 To scrape with these settings:")
            print("   python -m scraper.cli.main --config config_file.json")

        except Exception as e:
            print(f"\n❌ Estimation failed: {e}")
            sys.exit(1)

    async def run_scrape(self, config: CLIConfig, output_dir: str, resume: bool = False, fresh: bool = False) -> bool:
        """Run the scraping process."""
        self.progress.start_operation(f"Scraping {config.name}")

        # Create scraping configuration
        scraping_config = ScrapingConfig(
            name=config.name,
            base_url=config.base_url,
            start_urls=config.start_urls,
            max_pages=config.max_pages,
            rate_limit=config.rate_limit,
            timeout=config.timeout,
            max_retries=config.max_retries,
            concurrent_requests=config.concurrent_requests,
            url_manager=URLManagerConfig(
                base_url=config.base_url,
                include_patterns=config.url_patterns["include"],
                exclude_patterns=config.url_patterns["exclude"],
            ),
            content_extractor=ExtractorConfig(
                title_selector=config.selectors.get("title", "title"),
                main_content_selector=config.selectors.get("main_content", "div[role='main']"),
                code_blocks_selector=config.selectors.get("code_blocks", "pre code"),
            ),
            categorizer=CategorizerConfig(categories=config.categories or {}),
        )

        try:
            async with CoreScraper(scraping_config, output_dir) as scraper:
                if fresh:
                    scraper.checkpoint_manager.clear_checkpoint()
                    print("🗑️  Cleared checkpoint - starting fresh")

                success = await scraper.scrape_all(resume=resume)

                if success:
                    stats = scraper.get_stats()
                    print("\n📊 Scraping Statistics:")
                    print(f"   Pages scraped: {stats.pages_scraped}")
                    print(f"   Pages failed: {stats.pages_failed}")
                    print(f"   URLs discovered: {stats.urls_discovered}")
                    print(f"   Content size: {stats.total_content_size:,} characters")
                    print(f"   Code samples: {stats.code_samples_found}")
                    print(f"   Patterns: {stats.patterns_extracted}")
                    print(f"   Duration: {stats.scraping_duration:.1f} seconds")

                    # Generate skill
                    self.progress.start_operation(f"Generating skill for {config.name}")
                    skill_success = await scraper.generate_skill()

                    if skill_success:
                        print(f"\n🎉 Success! Skill created at: {output_dir}/{config.name}/")
                        print(
                            f"📦 To package: python -m scraper.cli.main --build --data-dir {output_dir}/{config.name}_data"
                        )
                        return True
                    print("\n❌ Skill generation failed")
                    return False
                print("\n❌ Scraping failed")
                return False

        except KeyboardInterrupt:
            print("\n⏸️  Scraping interrupted by user")
            print("💾 Progress was saved - resume with --resume")
            return False
        except Exception as e:
            print(f"\n❌ Scraping failed: {e}")
            return False

    async def run_build(self, data_dir: str, output_dir: str, create_readme: bool = True) -> bool:
        """Build skill from existing data."""
        self.progress.start_operation("Building skill from existing data")

        try:
            # Load pages from data directory
            pages = load_pages_from_data(data_dir)
            if not pages:
                print(f"❌ No pages found in {data_dir}")
                return False

            print(f"📄 Loaded {len(pages)} pages")

            # Extract project name from data directory
            project_name = Path(data_dir).stem.replace("_data", "")

            # Create skill configuration
            skill_config = SkillConfig(
                name=project_name,
                description=f"Comprehensive assistance with {project_name}",
                base_url="https://example.com/",  # Will be updated if available
            )

            # Load summary to get base URL if available
            summary_file = Path(data_dir) / "summary.json"
            if summary_file.exists():
                with open(summary_file) as f:
                    summary = json.load(f)
                    skill_config.base_url = summary.get("base_url", skill_config.base_url)

            # Generate skill
            skill_generator = SkillGenerator(skill_config, output_dir)

            # Simple categorization if no specific categorizer
            from scraper.core.categorizer import CategorizerConfig
            from scraper.core.categorizer import SmartCategorizer

            categorizer = SmartCategorizer(CategorizerConfig())
            categories = categorizer.categorize_pages(pages)

            success = skill_generator.generate_skill(categories, create_readme=create_readme)

            if success:
                print("\n🎉 Skill built successfully!")
                print(f"📁 Output: {skill_generator.skill_dir}")
                return True
            print("\n❌ Skill building failed")
            return False

        except Exception as e:
            print(f"\n❌ Build failed: {e}")
            return False

    async def run(self, args: argparse.Namespace) -> None:
        """Run the CLI application."""
        self.setup_logging(args.verbose, args.quiet)

        try:
            if args.interactive:
                # Interactive configuration
                configurator = InteractiveConfigurator()
                config = configurator.run()

                # Save configuration
                config_path = f"configs/{config.name}.json"
                ConfigManager.save_config(config, config_path)
                print(f"💾 Configuration saved to {config_path}")

            elif args.config:
                # Load configuration from file
                config = ConfigManager.load_config(args.config)

            elif args.quick:
                # Quick mode
                if not args.name or not args.url:
                    print("❌ Quick mode requires --name and --url")
                    sys.exit(1)

                config = CLIConfig(
                    name=args.name,
                    description=args.description or f"Comprehensive assistance with {args.name}",
                    base_url=args.url,
                )

            elif args.build:
                # Build mode - no config needed
                success = await self.run_build(args.data_dir, args.output_dir, args.create_readme)
                sys.exit(0 if success else 1)

            else:
                print("❌ No operation mode specified")
                sys.exit(1)

            # Validate configuration
            warnings = ConfigManager.validate_config(config)
            if warnings and not args.quiet:
                print("⚠️  Configuration warnings:")
                for warning in warnings:
                    print(f"   - {warning}")
                print()

            # Override settings from command line
            if args.max_pages:
                config.max_pages = args.max_pages
            if args.no_checkpoint:
                config.checkpoint["enabled"] = False

            # Run the requested operation
            if args.estimate:
                await self.run_estimate(config, args.max_discovery)
            else:
                success = await self.run_scrape(config, args.output_dir, args.resume, args.fresh)
                sys.exit(0 if success else 1)

        except Exception as e:
            if args.verbose:
                import traceback

                traceback.print_exc()
            else:
                print(f"❌ Error: {e}")
            sys.exit(1)


async def main() -> None:
    """Main entry point."""
    cli = ModularCLI()
    parser = cli.create_parser()
    args = parser.parse_args()
    await cli.run(args)


if __name__ == "__main__":
    asyncio.run(main())  # type: ignore
