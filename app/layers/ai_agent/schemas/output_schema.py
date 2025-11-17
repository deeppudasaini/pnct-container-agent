from pydantic import BaseModel, Field
from typing import Literal, Optional, Dict, Any, List
from datetime import datetime


class ContainerDetailsSchema(BaseModel):
    container_number: str = Field(description="Container number")
    available: bool = Field(description="Whether container is available")
    status: str = Field(description="Container status",default="success")
    location: Optional[str] = Field(None, description="Container location in yard")
    trucker: Optional[str] = Field(None, description="Assigned trucker")
    customs_status: Optional[str] = Field(None, description="Customs clearance status")
    customs_released: bool = Field(False, description="Whether customs is released")
    freight_status: Optional[str] = Field(None, description="Freight status")
    freight_released: bool = Field(False, description="Whether freight is released")
    holds: List[str] = Field(default_factory=list, description="List of holds on container")
    has_holds: bool = Field(False, description="Whether container has any holds")
    terminal_demurrage_amount: Optional[str] = Field(None, description="Terminal demurrage charges")
    last_free_day: Optional[str] = Field(None, description="Last free day for container")
    last_guar_day: Optional[str] = Field(None, description="Last guaranteed day")
    pay_through_date: Optional[str] = Field(None, description="Pay through date")
    non_demurrage_amount: Optional[str] = Field(None, description="Non-demurrage charges")
    ssco: Optional[str] = Field(None, description="Shipping line SCAC code")
    size: Optional[str] = Field(None, description="Container size")
    type: Optional[str] = Field(None, description="Container type")
    height: Optional[str] = Field(None, description="Container height")
    hazardous: bool = Field(False, description="Hazardous materials")
    genset_required: bool = Field(False, description="Genset required")
    days_remaining: Optional[int] = Field(None, description="Days remaining until LFD")


class ToolCallInfo(BaseModel):
    tool_name: str = Field(description="Name of the tool called")
    parameters: Dict[str, Any] = Field(description="Parameters passed to the tool")
    success: bool = Field(description="Whether the tool call was successful")


class ContainerParseSchema(BaseModel):
    # Allow null values
    container_id: Optional[str] = Field(
        None,
        description="Extracted container ID from query"
    )

    intent: Optional[
        Any
    ] = Field(
        None,
        description="User intent"
    )

    confidence: Optional[float] = Field(
        None,
        description="Confidence score for intent extraction"
    )

    message: Optional[str] = Field(
        None,
        description="Natural language response"
    )

    container_data: Optional[ContainerDetailsSchema] = Field(
        None,
        description="Structured container information"
    )

    tools_used: List[ToolCallInfo] = Field(
        default_factory=list,
        description="List of tool calls",
    )

    query_timestamp: Optional[str] = Field(
        default_factory=lambda: datetime.utcnow().isoformat(),
        description="Timestamp of processing"
    )

    data_source: Optional[str] = Field(
        "PNCT",
        description="Source of data"
    )

    has_errors: bool = Field(
        False,
        description="Whether an error occurred"
    )

    error_message: Optional[str] = Field(
        None,
        description="Error message if applicable"
    )
