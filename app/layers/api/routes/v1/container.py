# """Container endpoints"""
# from fastapi import APIRouter, Depends, HTTPException
# from sqlalchemy.ext.asyncio import AsyncSession
#
# from app.layers.api.schemas.request import ContainerRequest
# from app.layers.api.schemas.response import ContainerResponse
# from app.layers.api.validators.container_validator import validate_container_number
# from app.layers.api.dependencies import get_db_session, verify_api_key
# from app.shared.database.repositories.repository_factory import RepositoryFactory
# from app.shared.utils.logger import get_logger
#
# router = APIRouter()
# logger = get_logger(__name__)
#
#
# @router.get("/container/{container_number}", response_model=ContainerResponse)
# async def get_container(
#         container_number: str,
#         db: AsyncSession = Depends(get_db_session),
#         api_key: str = Depends(verify_api_key)
# ):
#     """
#     Get container information by container number
#
#     Returns cached data if available
#     """
#     try:
#         # Validate container number
#         normalized_id = validate_container_number(container_number)
#
#         logger.info(f"Fetching container: {normalized_id}")
#
#         # Get from database
#         repo_factory = RepositoryFactory()
#         container_repo = repo_factory.get_container_repository(db)
#
#         container = await container_repo.get_by_container_number(normalized_id)
#
#         if not container:
#             raise HTTPException(
#                 status_code=404,
#                 detail=f"Container {normalized_id} not found in cache"
#             )
#
#         return ContainerResponse(
#             status="success",
#             data=container.data,
#             cached=True,
#             last_updated=container.last_updated.isoformat() if container.last_updated else None
#         )
#
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error fetching container: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
#
#
# @router.get("/containers/recent")
# async def get_recent_containers(
#         limit: int = 50,
#         db: AsyncSession = Depends(get_db_session),
#         api_key: str = Depends(verify_api_key)
# ):
#     """Get recently queried containers"""
#     try:
#         repo_factory = RepositoryFactory()
#         container_repo = repo_factory.get_container_repository(db)
#
#         containers = await container_repo.get_all(limit=limit)
#
#         return {
#             "status": "success",
#             "data": [c.to_dict() for c in containers],
#             "count": len(containers)
#         }
#
#     except Exception as e:
#         logger.error(f"Error fetching recent containers: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))
