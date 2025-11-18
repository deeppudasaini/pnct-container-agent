from app.layers.scraper.scrapers.base.base_scraper import BaseScraper
from app.layers.scraper.scrapers.dymmy.dummy_data import build_dummy_html
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)
class DummyScraper(BaseScraper):
    async def initialize(self):
        logger.info(f"Initializing Dummy Scraper")
        pass

    async def search_container(self, container_id: str) -> str:
        html = build_dummy_html(container_id)
        return html

    async def close(self):
        logger.info(f"Closing Dummy Scraper")
        pass