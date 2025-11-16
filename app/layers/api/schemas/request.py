from pydantic import BaseModel, Field


class QueryRequest(BaseModel):
    query: str = Field(..., min_length=1, max_length=500, description="Natural language query")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Get info for container MSDU123456"
            }
        }


class ContainerRequest(BaseModel):
    container_number: str = Field(..., min_length=11, max_length=11)

    class Config:
        json_schema_extra = {
            "example": {
                "container_number": "MSDU1234567"
            }
        }
