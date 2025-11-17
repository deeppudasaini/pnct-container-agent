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
                }
            )

            self.page = await context.new_page()
            self.page.set_default_timeout(settings.BROWSER_TIMEOUT)

            logger.info("PNCT scraper initialized")

        except Exception as e:
            logger.error(f"Browser initialization failed: {str(e)}", exc_info=True)
            raise BrowserError(f"Failed to initialize browser: {str(e)}")

    def _generate_dummy_data(self, container_id: str) -> str:
        """Generate dummy HTML table data for testing"""

        html_template = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Container Availability Results</title>
</head>
<body>
    <div class="mt-4 mb-4 table-responsive scrollbar-deep-purple bordered-deep-purple thin square">
        <table class="table table-sm z-depth-1 table-hover">
            <thead class="cloudy-knoxville-gradient">
                <tr>
                    <th>Container Number</th>
                    <th>Available</th>
                    <th>Location</th>
                    <th>Trucker</th>
                    <th>Customs Status</th>
                    <th>Freight Status</th>
                    <th>Misc Holds</th>
                    <th>Terminal Demurrage Amount</th>
                    <th>Last Free Day</th>
                    <th>Last Guar. Day</th>
                    <th>Pay Through Date</th>
                    <th>Non Demurrage Amount</th>
                    <th>SSCO</th>
                    <th>Type</th>
                    <th>Length</th>
                    <th>Height</th>
                    <th>Hazardous</th>
                    <th>Genset Required</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{container_id}</td>
                    <td>YES</td>
                    <td>YARD-A-123</td>
                    <td>ABC TRUCKING</td>
                    <td>RELEASED</td>
                    <td>FULL</td>
                    <td>NONE</td>
                    <td>$250.00</td>
                    <td>11/15/2025</td>
                    <td>11/20/2025</td>
                    <td>11/17/2025</td>
                    <td>$0.00</td>
                    <td>MAEU</td>
                    <td>DRY</td>
                    <td>40</td>
                    <td>HC</td>
                    <td>NO</td>
                    <td>NO</td>
                </tr>
            </tbody>
        </table>
    </div>
</body>
</html>
"""
        return html_template

    @retry_async(max_attempts=3, delay=2.0, backoff=2.0)
    async def search_container(self, container_id: str, use_dummy: bool = True) -> str:
        """
        Search for container information

        Args:
            container_id: The container ID to search for
            use_dummy: If True, return dummy data instead of scraping (for testing)

        Returns:
            HTML content with container information
        """

        # Return dummy data if requested
        if use_dummy:
            logger.info(f"Returning dummy data for container: {container_id}")
            return self._generate_dummy_data(container_id)

        try:
            logger.info(f"Searching for container: {container_id}")

            if not self.page:
                await self.initialize()

            # Navigate to the page
            await self.page.goto(
                settings.PNCT_SEARCH_URL,
                wait_until="networkidle",
                timeout=30000
            )

            # Wait for the form to be ready
            await self.page.wait_for_selector('select#InquiryType', timeout=10000)

            # Select "Container Availability by Container" from the dropdown
            await self.page.select_option('select#InquiryType', 'ContainerAvailabilityByCntr')

            # Wait a moment for any JavaScript to process the selection
            await asyncio.sleep(0.5)

            # Fill in the container ID in the textarea
            await self.page.fill('textarea#Key', container_id)

            # Click the search button
            await self.page.click('button#btnTosInquiry')

            # Wait for results to load
            try:
                await self.page.wait_for_load_state('networkidle', timeout=15000)
                await asyncio.sleep(2)

            except Exception as e:
                logger.warning(f"Timeout waiting for results, proceeding anyway: {str(e)}")

            # Get the HTML content
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
