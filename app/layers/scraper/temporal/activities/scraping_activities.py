from temporalio import activity
from typing import Dict, Any
import asyncio

from app.layers.scraper.scrapers.pnct.pnct_scraper import PNCTScraper
from app.layers.scraper.parsers.container_parser import ContainerParser
from app.shared.utils.logger import get_logger
from app.shared.database.session import get_db
from app.shared.database.repositories.repository_factory import RepositoryFactory

logger = get_logger(__name__)


@activity.defn
async def init_browser() -> Dict[str, Any]:
    logger.info("Activity: Initializing browser")

    try:
        scraper = PNCTScraper()
        await scraper.initialize()

        session_id = scraper.get_session_id()

        logger.info(f"Browser initialized with session: {session_id}")

        return {
            "session_id": session_id,
            "status": "initialized"
        }

    except Exception as e:
        logger.error(f"Browser initialization failed: {str(e)}", exc_info=True)
        raise


@activity.defn
async def search_container(
        browser_session: Dict[str, Any],
        container_id: str
) -> Dict[str, Any]:
    logger.info(f"Activity: Searching container {container_id}")

    try:
        scraper = PNCTScraper()
        await scraper.initialize()

        html_content = await scraper.search_container(container_id)

        logger.info(f"Search completed for {container_id}")

        return {
            "container_id": container_id,
            "html_content": html_content,
            "status": "found"
        }

    except Exception as e:
        logger.error(f"Container search failed: {str(e)}", exc_info=True)
        raise
    finally:
        await scraper.close()


@activity.defn
async def extract_data(
        search_result: Dict[str, Any],
        operation: str
) -> Dict[str, Any]:
    logger.info(f"Activity: Extracting data for operation: {operation}")

    try:
        html_content = search_result["html_content"]
        container_id = search_result["container_id"]

        parser = ContainerParser()
        data = parser.parse(html_content, operation)

        logger.info(f"Data extracted for {container_id}")

        return data

    except Exception as e:
        logger.error(f"Data extraction failed: {str(e)}", exc_info=True)
        raise


@activity.defn
async def validate_data(
        data: Dict[str, Any],
        container_id: str
) -> Dict[str, Any]:

    logger.info(f"Activity: Validating data for {container_id}")

    try:
        required_fields = ["container_number", "status"]

        for field in required_fields:
            if field not in data:
                raise ValueError(f"Missing required field: {field}")

        if data["container_number"] != container_id:
            raise ValueError("Container number mismatch")

        logger.info(f"Data validated for {container_id}")

        return data

    except Exception as e:
        logger.error(f"Data validation failed: {str(e)}", exc_info=True)
        raise


@activity.defn
async def store_data(
        data: Dict[str, Any],
        container_id: str
) -> bool:
    logger.info(f"Activity: Storing data for {container_id}")

    try:
        async for db in get_db():
            repo_factory = RepositoryFactory()
            container_repo = repo_factory.get_container_repository(db)

            # Upsert container data
            await container_repo.upsert(
                container_number=container_id,
                data=data,
                source="PNCT"
            )

            await db.commit()

            logger.info(f"Data stored for {container_id}")

            return True

    except Exception as e:
        logger.error(f"Data storage failed: {str(e)}", exc_info=True)
        raise