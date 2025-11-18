"""Repository Factory Pattern"""
from sqlalchemy.ext.asyncio import AsyncSession
from app.shared.database.repositories.container_repository import ContainerRepository
from app.shared.database.repositories.container_scraper_result_repository import ContainerScrapeResultRepository
from app.shared.database.repositories.quer_log_repository import QueryLogRepository
from app.shared.database.repositories.workflow_repository import WorkflowRepository


class RepositoryFactory:

    @staticmethod
    def get_container_repository(session: AsyncSession) -> ContainerRepository:
        return ContainerRepository(session)
    @staticmethod
    def get_container_scraper_repository(session: AsyncSession) -> ContainerScrapeResultRepository:
        return ContainerScrapeResultRepository(session)

    @staticmethod
    def get_query_log_repository(session: AsyncSession) -> QueryLogRepository:
        return QueryLogRepository(session)

    @staticmethod
    def get_workflow_repository(session: AsyncSession) -> WorkflowRepository:
        return WorkflowRepository(session)
