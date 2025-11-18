"""
Modular Documentation Scraper

A comprehensive, modular system for converting documentation websites
into Claude AI skills with advanced performance optimization.

This package provides:
- Async/await scraping with concurrent processing
- Advanced content extraction and categorization
- Checkpoint management for resumable operations
- Comprehensive skill generation with examples
- Modern CLI with interactive configuration
"""

__version__ = "2.0.0"
__author__ = "Skill Seeker Team"

# Public API
from scraper.cli.main import ModularCLI
from scraper.core.scraper import CoreScraper
from scraper.core.scraper import ScrapingConfig
from scraper.core.scraper import estimate_page_count
from scraper.core.scraper import scrape_documentation
from scraper.generators.skill import SkillConfig
from scraper.generators.skill import SkillGenerator

__all__ = [
    "CoreScraper",
    "ScrapingConfig",
    "scrape_documentation",
    "estimate_page_count",
    "SkillGenerator",
    "SkillConfig",
    "ModularCLI",
]
