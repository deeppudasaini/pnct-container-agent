from pydantic import BaseModel
from typing import Literal

class ContainerParseSchema(BaseModel):
    container_id: str
    intent: Literal[
        "get_info",
        "check_availability",
        "get_location",
        "check_holds",
        "get_lfd"
    ]
    confidence: float
