# API/dto/driver_post.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime

class DriverPostDTO(BaseModel):
    driver_id: str
    client_id: Optional[str] = "unknown"
    vehicle_info: Optional[str] = None
    status: Literal["open", "matched", "closed"] = "open"

    time_stamp: Optional[datetime] = Field(None, alias="timestamp")
    start_point: Dict[str, Any] = Field(..., alias="starting_point")
    destination: Dict[str, Any]

    meet_point: Dict[str, Any] = Field(..., alias="meet_point")
    departure_time: datetime = Field(..., alias="departure_time")
    notes: Optional[str] = None
    description: Optional[str] = None
    helmet: bool = False
    contact: Dict[str, str] = Field(..., alias="contact_info")
    leave: bool = False
    image_url: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

class UploadImageResponse(BaseModel):
    message: str
    image_url: str | None = None
