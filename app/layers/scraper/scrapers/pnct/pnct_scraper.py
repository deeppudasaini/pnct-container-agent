from playwright.async_api import async_playwright, Browser, Page
from typing import Optional
import asyncio

from app.layers.scraper.scrapers.base.base_scraper import BaseScraper
from app.shared.config.settings.base import get_settings
from app.shared.exceptions.scraper_exceptions import (
    BrowserError,
    PageLoadError,
    ContainerNotFoundError
)
from app.shared.utils.logger import get_logger
from app.shared.utils.retry import retry_async

settings = get_settings()
logger = get_logger(__name__)


class PNCTScraper(BaseScraper):

    def __init__(self):
        super().__init__()
        self.playwright = None
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None

    async def initialize(self):
        try:
            logger.info("Initializing PNCT scraper")

            self.playwright = await async_playwright().start()

            self.browser = await self.playwright.chromium.launch(
                headless=settings.BROWSER_HEADLESS,
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )

            context = await self.browser.new_context(
                viewport={
                    'width': settings.BROWSER_VIEWPORT_WIDTH,
                    'height': settings.BROWSER_VIEWPORT_HEIGHT
                },
                user_agent=settings.SCRAPER_USER_AGENT
            )

            self.page = await context.new_page()
            self.page.set_default_timeout(settings.BROWSER_TIMEOUT)

            logger.info("PNCT scraper initialized")

        except Exception as e:
            logger.error(f"Browser initialization failed: {str(e)}", exc_info=True)
            raise BrowserError(f"Failed to initialize browser: {str(e)}")

    @retry_async(max_attempts=3, delay=2.0, backoff=2.0)
    async def search_container(self, container_id: str) -> str:

        try:
            logger.info(f"Searching for container: {container_id}")

            if not self.page:
                await self.initialize()

            await self.page.goto(
                settings.PNCT_SEARCH_URL,
                wait_until="networkidle",
                timeout=30000
            )

            await self.page.wait_for_selector('input[name="container_number"]', timeout=10000)

            await self.page.fill('input[name="container_number"]', container_id)

            await self.page.click('button[type="submit"]')

            await self.page.wait_for_selector('.container-results', timeout=15000)

            html_content = await self.page.content()

            logger.info(f"Container {container_id} search completed")

            return html_content

        except Exception as e:
            logger.error(f"Container search failed: {str(e)}", exc_info=True)

            if "timeout" in str(e).lower():
                raise PageLoadError(f"Timeout searching for container: {container_id}")

            raise ContainerNotFoundError(f"Container not found: {container_id}")

    async def close(self):
        try:
            if self.page:
                await self.page.close()

            if self.browser:
                await self.browser.close()

            if self.playwright:
                await self.playwright.stop()

            logger.info("PNCT scraper closed")

        except Exception as e:
            logger.error(f"Error closing scraper: {str(e)}", exc_info=True)
