# API/dto/driver_post.py
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, Literal
from datetime import datetime

class DriverPostDTO(BaseModel):
    driver_id: str
    client_id: Optional[str] = "unknown"
    vehicle_info: Optional[str] = None
    status: Literal["open", "matched", "closed"] = "open"

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

class DriverPostUpdateDTO(BaseModel):
    # 要不要讓 client_id 可改，看你業務需求：
    client_id: Optional[str] = None

    vehicle_info: Optional[str] = None
    status: Optional[Literal["open", "matched", "closed"]] = None

    time_stamp: Optional[datetime] = Field(None, alias="timestamp")  # 一般我會直接拿掉，不讓改

    start_point: Optional[Dict[str, Any]] = Field(None, alias="starting_point")
    destination: Optional[Dict[str, Any]] = None

    meet_point: Optional[Dict[str, Any]] = Field(None, alias="meet_point")
    departure_time: Optional[datetime] = Field(None, alias="departure_time")

    notes: Optional[str] = None
    description: Optional[str] = None
    helmet: Optional[bool] = None
    contact: Optional[Dict[str, str]] = Field(None, alias="contact_info")
    leave: Optional[bool] = None
    image_url: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

class DriverPostReturnDTO(DriverPostDTO):
    id: str
    time_stamp: Optional[datetime] = Field(None, alias="timestamp")

    model_config = {
        "populate_by_name": True,
        "from_attributes": True,
    }

