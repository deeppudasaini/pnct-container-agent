from app.layers.api.schemas.request.query_request import QueryRequest


class QueryService:
    async def execute_query(self, query:QueryRequest):
        return query