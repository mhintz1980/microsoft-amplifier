#!/usr/bin/env python3
"""
Core Scraper Module

Main orchestration that coordinates all scraping modules.
This is the central coordinator that manages the complete workflow
from URL discovery to skill generation.

Features:
- Async/await patterns for maximum performance
- Advanced error handling and logging
- Checkpoint management for resumable scraping
- Integration with all modular components
- Performance monitoring and optimization
"""

import asyncio
import hashlib
import json
import logging
import time
from collections import deque
from pathlib import Path
from urllib.parse import urljoin

import aiohttp
from bs4 import BeautifulSoup
from pydantic import BaseModel
from pydantic import Field

from scraper.core.categorizer import CategorizerConfig
from scraper.core.categorizer import SmartCategorizer
from scraper.core.checkpoint_manager import CheckpointData
from scraper.core.checkpoint_manager import CheckpointManager
from scraper.core.content_extractor import ContentExtractor
from scraper.core.content_extractor import ExtractorConfig

# Import modular components
from scraper.core.url_manager import URLManager
from scraper.core.url_manager import URLManagerConfig
from scraper.generators.skill import Page
from scraper.generators.skill import SkillConfig
from scraper.generators.skill import SkillGenerator

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)


class ScrapingConfig(BaseModel):
    """Configuration for the scraping process."""

    name: str = Field(..., description="Project name")
    base_url: str = Field(..., description="Base URL to start scraping")
    start_urls: list[str] = Field(default_factory=list, description="Additional starting URLs")
    max_pages: int = Field(default=500, description="Maximum pages to scrape")
    rate_limit: float = Field(default=0.5, description="Delay between requests in seconds")
    timeout: int = Field(default=30, description="Request timeout in seconds")
    max_retries: int = Field(default=3, description="Maximum retry attempts")
    concurrent_requests: int = Field(default=5, description="Concurrent requests limit")
    user_agent: str = Field(default="Mozilla/5.0 (Documentation Scraper 2.0)", description="User agent string")

    # Module configurations
    url_manager: URLManagerConfig = Field(default_factory=URLManagerConfig)
    content_extractor: ExtractorConfig = Field(default_factory=ExtractorConfig)
    categorizer: CategorizerConfig = Field(default_factory=CategorizerConfig)


class ScrapingStats(BaseModel):
    """Statistics for the scraping process."""

    start_time: float = Field(default_factory=time.time)
    pages_scraped: int = Field(default=0)
    pages_failed: int = Field(default=0)
    urls_discovered: int = Field(default=0)
    total_content_size: int = Field(default=0)
    patterns_extracted: int = Field(default=0)
    code_samples_found: int = Field(default=0)
    scraping_duration: float = Field(default=0.0)
    avg_page_time: float = Field(default=0.0)
    discovery_rate: float = Field(default=0.0)


class ProgressTracker:
    """Tracks scraping progress and provides periodic updates."""

    def __init__(self, update_interval: int = 10):
        self.update_interval = update_interval
        self.last_update = 0
        self.start_time = time.time()

    def should_update(self, pages_scraped: int) -> bool:
        """Check if it's time for a progress update."""
        return pages_scraped - self.last_update >= self.update_interval

    def update(self, stats: ScrapingStats, pending_urls: int) -> None:
        """Update and display progress."""
        self.last_update = stats.pages_scraped
        elapsed = time.time() - self.start_time

        stats.scraping_duration = elapsed
        stats.avg_page_time = elapsed / max(1, stats.pages_scraped)
        stats.discovery_rate = stats.urls_discovered / max(1, elapsed)

        logger.info(
            f"Progress: {stats.pages_scraped} pages | "
            f"{pending_urls} pending | "
            f"{stats.pages_failed} failed | "
            f"{stats.avg_page_time:.2f}s/page | "
            f"{stats.discovery_rate:.1f} URLs/sec"
        )


class CoreScraper:
    """
    Main scraper that orchestrates all modular components.

    This class coordinates URL management, content extraction, categorization,
    and skill generation to provide a complete documentation scraping solution.
    """

    def __init__(self, config: ScrapingConfig, output_dir: str = "output"):
        """
        Initialize the core scraper.

        Args:
            config: Scraping configuration
            output_dir: Base output directory
        """
        self.config = config
        self.output_dir = Path(output_dir)
        self.project_dir = self.output_dir / f"{config.name}_data"
        self.skill_dir = self.output_dir / config.name

        # Initialize components
        self.url_manager = URLManager(config.url_manager)
        self.content_extractor = ContentExtractor(config.content_extractor)
        self.categorizer = SmartCategorizer(config.categorizer)
        self.checkpoint_manager = CheckpointManager(self.project_dir)

        # Initialize state
        self.session: aiohttp.ClientSession | None = None
        self.stats = ScrapingStats()
        self.progress_tracker = ProgressTracker()
        self.pages: list[Page] = []

        # Ensure directories exist
        self._ensure_directories()

        logger.info(f"CoreScraper initialized for {config.name}")
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Base URL: {config.base_url}")

    def _ensure_directories(self) -> None:
        """Create necessary directories."""
        for directory in [self.project_dir, self.skill_dir]:
            directory.mkdir(parents=True, exist_ok=True)

        pages_dir = self.project_dir / "pages"
        pages_dir.mkdir(exist_ok=True)

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop()

    async def start(self) -> None:
        """Start the scraper and initialize resources."""
        if self.session is None:
            timeout = aiohttp.ClientTimeout(total=self.config.timeout)
            connector = aiohttp.TCPConnector(limit=self.config.concurrent_requests)

            self.session = aiohttp.ClientSession(
                timeout=timeout, connector=connector, headers={"User-Agent": self.config.user_agent}
            )

            logger.info("HTTP session started")

    async def stop(self) -> None:
        """Stop the scraper and cleanup resources."""
        if self.session:
            await self.session.close()
            self.session = None
            logger.info("HTTP session closed")

    async def scrape_page(self, url: str) -> Page | None:
        """
        Scrape a single page with retry logic.

        Args:
            url: URL to scrape

        Returns:
            Page object if successful, None otherwise
        """
        for attempt in range(self.config.max_retries):
            try:
                logger.debug(f"Scraping: {url} (attempt {attempt + 1})")

                async with self.session.get(url) as response:
                    response.raise_for_status()
                    content = await response.text()

                # Parse HTML
                soup = BeautifulSoup(content, "html.parser")

                # Extract content
                page = self.content_extractor.extract_content(soup, url)

                if page.content or page.code_samples or page.patterns:
                    self.stats.pages_scraped += 1
                    self.stats.total_content_size += len(page.content)
                    self.stats.code_samples_found += len(page.code_samples)
                    self.stats.patterns_extracted += len(page.patterns)

                    # Discover new URLs
                    new_urls = self.url_manager.extract_urls(page)
                    self.stats.urls_discovered += len(new_urls)

                    return page
                logger.warning(f"No content extracted from: {url}")
                return None

            except TimeoutError:
                logger.warning(f"Timeout scraping {url} (attempt {attempt + 1})")
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(2**attempt)  # Exponential backoff

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")
                self.stats.pages_failed += 1

                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(1)

        return None

    async def scrape_batch(self, urls: list[str]) -> list[Page]:
        """
        Scrape a batch of URLs concurrently.

        Args:
            urls: List of URLs to scrape

        Returns:
            List of successfully scraped pages
        """
        semaphore = asyncio.Semaphore(self.config.concurrent_requests)

        async def scrape_with_semaphore(url: str) -> Page | None:
            async with semaphore:
                page = await self.scrape_page(url)
                if page:
                    # Rate limiting
                    await asyncio.sleep(self.config.rate_limit)
                return page

        # Execute concurrent scraping
        tasks = [scrape_with_semaphore(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Filter successful results
        pages = []
        for result in results:
            if isinstance(result, Page):
                pages.append(result)
            elif isinstance(result, Exception):
                logger.error(f"Batch scraping error: {result}")

        return pages

    async def scrape_all(self, resume: bool = False, save_checkpoint: bool = True) -> bool:
        """
        Main scraping method that orchestrates the entire process.

        Args:
            resume: Whether to resume from checkpoint
            save_checkpoint: Whether to save checkpoints

        Returns:
            True if successful, False otherwise
        """
        logger.info(f"Starting scraping for {self.config.name}")
        logger.info(f"Base URL: {self.config.base_url}")
        logger.info(f"Max pages: {self.config.max_pages}")

        # Load checkpoint if resuming
        if resume:
            checkpoint_data = self.checkpoint_manager.load_checkpoint()
            if checkpoint_data:
                logger.info(f"Resumed from checkpoint: {len(checkpoint_data.visited_urls)} URLs visited")
                self.url_manager.restore_state(checkpoint_data.visited_urls, checkpoint_data.pending_urls)
                self.stats.pages_scraped = checkpoint_data.pages_scraped
            else:
                logger.info("No checkpoint found, starting fresh")

        # Add start URLs
        start_urls = [self.config.base_url] + self.config.start_urls
        for url in start_urls:
            self.url_manager.add_url(url)

        # Main scraping loop
        try:
            while len(self.url_manager.visited_urls) < self.config.max_pages and self.url_manager.has_pending_urls():
                # Get next batch of URLs
                batch_size = min(
                    self.config.concurrent_requests, self.config.max_pages - len(self.url_manager.visited_urls)
                )
                url_batch = self.url_manager.get_next_urls(batch_size)

                if not url_batch:
                    break

                # Scrape batch
                batch_pages = await self.scrape_batch(url_batch)
                self.pages.extend(batch_pages)

                # Save individual pages
                for page in batch_pages:
                    await self.save_page(page)

                # Update progress
                if self.progress_tracker.should_update(self.stats.pages_scraped):
                    self.progress_tracker.update(self.stats, len(self.url_manager.pending_urls))

                # Save checkpoint
                if save_checkpoint and self.stats.pages_scraped > 0 and self.stats.pages_scraped % 100 == 0:
                    await self.save_checkpoint()

        except KeyboardInterrupt:
            logger.info("Scraping interrupted by user")
            if save_checkpoint:
                await self.save_checkpoint()
                logger.info("Checkpoint saved")
            return False

        except Exception as e:
            logger.error(f"Scraping failed: {e}")
            return False

        # Save final checkpoint
        if save_checkpoint:
            await self.save_checkpoint()

        # Save summary
        await self.save_summary()

        logger.info(f"Scraping completed: {self.stats.pages_scraped} pages")
        return True

    async def save_page(self, page: Page) -> None:
        """
        Save a page to the project directory.

        Args:
            page: Page to save
        """
        url_hash = hashlib.md5(page.url.encode()).hexdigest()[:10]
        safe_title = "".join(c for c in page.title if c.isalnum() or c in (" ", "-", "_"))[:50]
        safe_title = safe_title.replace(" ", "_").replace("-", "_")

        filename = f"{safe_title}_{url_hash}.json"
        filepath = self.project_dir / "pages" / filename

        # Convert to dict for JSON serialization
        page_data = {
            "url": page.url,
            "title": page.title,
            "content": page.content,
            "headings": page.headings,
            "code_samples": [
                {"code": cs.code, "language": cs.language, "description": cs.description} for cs in page.code_samples
            ],
            "patterns": [{"description": p.description, "code": p.code, "context": p.context} for p in page.patterns],
            "links": page.links,
        }

        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(page_data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save page {filepath}: {e}")

    async def save_checkpoint(self) -> None:
        """Save current progress to checkpoint."""
        checkpoint_data = CheckpointData(
            visited_urls=list(self.url_manager.visited_urls),
            pending_urls=list(self.url_manager.pending_urls),
            pages_scraped=self.stats.pages_scraped,
            timestamp=time.time(),
        )

        self.checkpoint_manager.save_checkpoint(checkpoint_data)
        logger.debug(f"Checkpoint saved: {self.stats.pages_scraped} pages")

    async def save_summary(self) -> None:
        """Save scraping summary."""
        summary = {
            "name": self.config.name,
            "base_url": self.config.base_url,
            "stats": self.stats.dict(),
            "pages": [{"title": page.title, "url": page.url} for page in self.pages],
        }

        summary_file = self.project_dir / "summary.json"
        try:
            with open(summary_file, "w", encoding="utf-8") as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            logger.info(f"Summary saved to {summary_file}")
        except Exception as e:
            logger.error(f"Failed to save summary: {e}")

    async def generate_skill(self) -> bool:
        """
        Generate the skill from scraped data.

        Returns:
            True if successful, False otherwise
        """
        if not self.pages:
            logger.error("No pages to generate skill from")
            return False

        logger.info("Generating skill from scraped data")

        # Categorize pages
        logger.info("Categorizing pages...")
        categories = self.categorizer.categorize_pages(self.pages)
        logger.info(f"Created {len(categories)} categories")

        # Generate skill
        skill_config = SkillConfig(
            name=self.config.name,
            description=f"Comprehensive assistance with {self.config.name}",
            base_url=self.config.base_url,
        )

        skill_generator = SkillGenerator(skill_config, str(self.output_dir))
        success = skill_generator.generate_skill(categories)

        if success:
            logger.info(f"Skill generated: {skill_generator.skill_dir}")

        return success

    def get_stats(self) -> ScrapingStats:
        """Get current scraping statistics."""
        return self.stats

    async def estimate_pages(self, max_discovery: int = 100) -> int:
        """
        Estimate the total number of pages that would be scraped.

        Args:
            max_discovery: Maximum URLs to discover for estimation

        Returns:
            Estimated total pages
        """
        logger.info(f"Estimating pages (max discovery: {max_discovery})")

        # Use only HEAD requests for faster estimation
        async with aiohttp.ClientSession(headers={"User-Agent": self.config.user_agent}) as session:
            discovered_urls = {self.config.base_url}
            checked_urls = set()
            urls_to_check = deque([self.config.base_url])

            while urls_to_check and len(discovered_urls) < max_discovery:
                url = urls_to_check.popleft()

                if url in checked_urls:
                    continue

                checked_urls.add(url)

                try:
                    async with session.head(url, timeout=10) as response:
                        if response.status == 200:
                            # Quick content check
                            async with session.get(url, timeout=5) as get_response:
                                content = await get_response.text()
                                if len(content) > 1000:  # Minimum content threshold
                                    # Extract links (simplified)
                                    soup = BeautifulSoup(content, "html.parser")
                                    for link in soup.find_all("a", href=True):
                                        href = urljoin(url, str(link["href"]))
                                        href = href.split("#")[0]  # Remove anchors

                                        if href not in discovered_urls and self.url_manager.is_valid_url(href):
                                            discovered_urls.add(href)
                                            if len(discovered_urls) < max_discovery:
                                                urls_to_check.append(href)

                except Exception:
                    continue  # Skip errors in estimation

        # Apply filters and estimate
        valid_urls = [url for url in discovered_urls if self.url_manager.is_valid_url(url)]
        estimated_pages = min(len(valid_urls), self.config.max_pages)

        logger.info(f"Estimated {estimated_pages} pages from {len(valid_urls)} valid URLs")
        return estimated_pages


# Convenience functions for common usage patterns
async def scrape_documentation(
    name: str, base_url: str, output_dir: str = "output", max_pages: int = 500, **kwargs
) -> bool:
    """
    Convenience function to scrape documentation with default settings.

    Args:
        name: Project name
        base_url: Base URL to scrape
        output_dir: Output directory
        max_pages: Maximum pages to scrape
        **kwargs: Additional configuration options

    Returns:
        True if successful, False otherwise
    """
    config = ScrapingConfig(name=name, base_url=base_url, max_pages=max_pages, **kwargs)

    async with CoreScraper(config, output_dir) as scraper:
        # Scrape
        success = await scraper.scrape_all()
        if not success:
            return False

        # Generate skill
        return await scraper.generate_skill()


async def estimate_page_count(base_url: str, max_discovery: int = 100, **kwargs) -> int:
    """
    Convenience function to estimate page count.

    Args:
        base_url: Base URL to estimate
        max_discovery: Maximum URLs to discover
        **kwargs: Additional configuration options

    Returns:
        Estimated page count
    """
    config = ScrapingConfig(name="estimate", base_url=base_url, **kwargs)

    async with CoreScraper(config) as scraper:
        return cast(dict[str, Any], await scraper.estimate_pages(max_discovery))
