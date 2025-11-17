from datetime import timedelta
from temporalio import workflow
from temporalio.common import RetryPolicy
from typing import Dict, Any

# DO NOT IMPORT ACTIVITIES IN WORKFLOWS!
# Activities are referenced by their activity name string


@workflow.defn
class ContainerScraperWorkflow:
    """Workflow for scraping container data"""

    @workflow.run
    async def run(self, container_id: str, operation: str = "get_full_info") -> Dict[str, Any]:

        workflow.logger.info(f"Starting workflow for container: {container_id}, operation: {operation}")

        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=1),
            maximum_interval=timedelta(seconds=10),
            maximum_attempts=3,
            backoff_coefficient=2.0,
        )

        try:

            browser_session = await workflow.execute_activity(
                "init_browser",
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )
            workflow.logger.info("Browser initialized")

            search_result = await workflow.execute_activity(
                "search_container",
                args=[browser_session, container_id],
                start_to_close_timeout=timedelta(seconds=45),
                retry_policy=retry_policy,
            )
            workflow.logger.info("Container search completed")

            extracted_data = await workflow.execute_activity(
                "extract_data",  # Activity name as STRING
                args=[search_result, operation],
                start_to_close_timeout=timedelta(seconds=30),
                retry_policy=retry_policy,
            )
            workflow.logger.info("Data extracted")

            validated_data = await workflow.execute_activity(
                "validate_data",  # Activity name as STRING
                args=[extracted_data, container_id],
                start_to_close_timeout=timedelta(seconds=10),
                retry_policy=retry_policy,
            )
            workflow.logger.info("Data validated")

            await workflow.execute_activity(
                "store_data",  # Activity name as STRING
                args=[validated_data, container_id],
                start_to_close_timeout=timedelta(seconds=20),
                retry_policy=retry_policy,
            )
            workflow.logger.info(f"Workflow completed successfully for {container_id}")

            return {
                "status": "success",
                "container_id": container_id,
                "data": validated_data,
                "operation": operation
            }

        except Exception as e:
            workflow.logger.error(f"Workflow failed: {str(e)}")
            return {
                "status": "failed",
                "container_id": container_id,
                "error": str(e),
                "operation": operation
            }
