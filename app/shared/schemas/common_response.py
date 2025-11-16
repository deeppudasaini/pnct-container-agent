from pydantic import BaseModel
from typing import Optional
from app.shared.schemas.response_metadata import ResponseMetadata

class CommonResponse(BaseModel):
    status: int
    message: str
    metadata: Optional[ResponseMetadata] = None

    model_config = {
        "arbitrary_types_allowed": True
    }
