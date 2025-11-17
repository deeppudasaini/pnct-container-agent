import asyncio
from temporalio.client import Client
from temporalio.worker import Worker

from app.layers.scraper.temporal.config import (
    TEMPORAL_HOST,
    TEMPORAL_PORT,
    TEMPORAL_NAMESPACE,
    TEMPORAL_TASK_QUEUE
)
from app.layers.scraper.temporal.workflows.container_workflow import (
    ContainerScraperWorkflow
)
from app.layers.scraper.temporal.activities.scraping_activities import (
    init_browser,
    search_container,
    extract_data,
    validate_data,
    store_data,
)
from app.shared.utils.logger import get_logger

logger = get_logger(__name__)


async def main():
    logger.info("🕷️  Starting Temporal worker (Layer 5: Scraper)")
    logger.info(f"Task queue: {TEMPORAL_TASK_QUEUE}")

    # Connect to Temporal
    client = await Client.connect(
        f"{TEMPORAL_HOST}:{TEMPORAL_PORT}",
        namespace=TEMPORAL_NAMESPACE,
    )

    # Create worker
    worker = Worker(
        client,
        task_queue=TEMPORAL_TASK_QUEUE,
        workflows=[ContainerScraperWorkflow],
        activities=[
            init_browser,
            search_container,
            extract_data,
            validate_data,
            store_data,
        ],
    )

    logger.info("✅ Worker started successfully")

    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
