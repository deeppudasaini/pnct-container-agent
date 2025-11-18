from temporalio import activity
from typing import Dict, Any

from app.layers.scraper.scrapers.dymmy.dummy_scraper import DummyScraper
from app.layers.scraper.scrapers.pnct.pnct_scraper import PNCTScraper
from app.layers.scraper.parsers.container_parser import ContainerParser
from app.shared.utils.logger import get_logger
from app.shared.database.session import get_db
from app.shared.database.repositories.repository_factory import RepositoryFactory

logger = get_logger(__name__)


@activity.defn(name="check_cached_html")
async def check_cached_html(container_id: str) -> Dict[str, Any]:
    activity.logger.info(f"Checking cached html for {container_id}")

    # db = None
    # try:
    #     db_gen = get_db()
    #     db = await anext(db_gen)
    #
    #     repo_factory = RepositoryFactory()
    #     container_repo = repo_factory.get_container_scraper_repository(db)
    #     cached = await container_repo.get_by_container_id(container_id)
    #
    #     if cached:
    #         return {"found": True, "html_content": cached.raw_html, "container_id": container_id}

    #
    # except Exception as e:
    #     activity.logger.error(f"Failed checking cached html: {str(e)}")
    #     raise
    # finally:
    #     if db:
    #         await db.close()

# Caching Removed for now. It can be further used for faster retreival from scraping
    return {"found": False, "container_id": container_id}


@activity.defn(name="init_browser")  # Explicitly set activity name
async def init_browser() -> Dict[str, Any]:
    activity.logger.info("Activity: Initializing browser")

    try:
        scraper = DummyScraper()
        await scraper.initialize()

        session_id = scraper.get_session_id()

        activity.logger.info(f"Browser initialized with session: {session_id}")

        return {
            "session_id": session_id,
            "status": "initialized"
        }

    except Exception as e:
        activity.logger.error(f"Browser initialization failed: {str(e)}")
        raise


@activity.defn(name="search_container")  # Explicitly set activity name
async def search_container(
        browser_session: Dict[str, Any],
        container_id: str
) -> Dict[str, Any]:
    activity.logger.info(f"Activity: Searching container {container_id}")

    scraper = None
    try:
        scraper = DummyScraper()
        await scraper.initialize()

        html_content = await scraper.search_container(container_id)

        activity.logger.info(f"Search completed for {container_id}")

        return {
            "container_id": container_id,
            "html_content": html_content,
            "status": "found"
        }

    except Exception as e:
        activity.logger.error(f"Container search failed: {str(e)}")
        raise
    finally:
        if scraper:
            await scraper.close()


@activity.defn(name="extract_data")
async def extract_data(
        search_result: Dict[str, Any],
        operation: str
) -> Dict[str, Any]:
    """Extract data from HTML content"""
    activity.logger.info(f"Activity: Extracting data for operation: {operation}")

    try:
        html_content = search_result["html_content"]
        container_id = search_result["container_id"]

        parser = ContainerParser()
        data = parser.parse(html_content, operation)

        activity.logger.info(f"Data extracted for {container_id}")

        return data

    except Exception as e:
        activity.logger.error(f"Data extraction failed: {str(e)}")
        raise


@activity.defn(name="validate_data")
async def validate_data(
        data: Dict[str, Any],
        container_id: str
) -> Dict[str, Any]:
    activity.logger.info(f"Activity: Validating data for {container_id}")

    try:
        required_fields = ["container_number", "status"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if data["container_number"] != container_id:
            raise ValueError("Container number mismatch")

        activity.logger.info(f"Data validated for {container_id}")

        return data

    except Exception as e:
        activity.logger.error(f"Data validation failed: {str(e)}")
        raise



@activity.defn(name="store_data")
async def store_data(
        data: Dict[str, Any],
        container_id: str
) -> bool:
    activity.logger.info(f"Activity: Storing data for {container_id}")

    db = None
    try:
        db_gen = get_db()
        db = await anext(db_gen)

        repo_factory = RepositoryFactory()
        container_repo = repo_factory.get_container_repository(db)

        # await container_repo.upsert(
        #     container_number=container_id,
        #     data=data,
        #     source="PNCT"
        # )

        await db.commit()

        activity.logger.info(f"Data stored for {container_id}")

        return True

    except Exception as e:
        if db:
            await db.rollback()
        activity.logger.error(f"Data storage failed: {str(e)}")
        raise
    finally:
        if db:
            await db.close()

@activity.defn(name="store_raw_html")
async def store_raw_html(container_id: str, html_content: str) -> bool:
    activity.logger.info(f"Storing raw html for {container_id}")

    db = None
    try:
        db_gen = get_db()
        db = await anext(db_gen)

        repo_factory = RepositoryFactory()
        container_scraper_repo = repo_factory.get_container_scraper_repository(db)

        await container_scraper_repo.upsert(container_id,"" ,html_content,None,"success","")
        await db.commit()

        return True

    except Exception as e:
        if db:
            await db.rollback()
        activity.logger.error(f"Raw html storage failed: {str(e)}")
        raise
    finally:
        if db:
            await db.close()
