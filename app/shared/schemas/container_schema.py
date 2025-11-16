"""Container schemas"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ContainerBase(BaseModel):
    container_number: str = Field(..., min_length=11, max_length=11)


class ContainerData(BaseModel):
    container_number: str
    status: Optional[str] = None
    location: Optional[str] = None
    availability: Optional[str] = None
    holds: List[str] = Field(default_factory=list)
    last_free_day: Optional[str] = None
    size: Optional[str] = None
    type: Optional[str] = None
    weight: Optional[str] = None
    seal_number: Optional[str] = None
    booking_number: Optional[str] = None
    vessel: Optional[str] = None
    voyage: Optional[str] = None
    discharge_date: Optional[str] = None
    available_for_pickup: Optional[bool] = None
    additional_info: Dict[str, Any] = Field(default_factory=dict)


class ContainerResponse(BaseModel):
    container_number: str
    data: ContainerData
    source: str = "PNCT"
    last_updated: Optional[datetime] = None
    cached: bool = False

    class Config:
        from_attributes = True
