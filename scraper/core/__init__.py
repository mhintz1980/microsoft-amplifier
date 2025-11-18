"""
Core scraper modules.

This package contains the core functionality for the modular scraper:
- URL management and validation
- Content extraction from HTML
- Smart categorization of pages
- Checkpoint management for resumable operations
- Main orchestration logic
"""

from scraper.core.scraper import CoreScraper
from scraper.core.scraper import ScrapingConfig
from scraper.core.scraper import estimate_page_count
from scraper.core.scraper import scrape_documentation

__all__ = ["CoreScraper", "ScrapingConfig", "scrape_documentation", "estimate_page_count"]
