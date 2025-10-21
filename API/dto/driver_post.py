from pydantic import BaseModel
from typing import Optional

class DriverPostDTO(BaseModel):
    id: int
    vehicle_info: str
    driver_id: int
    post_id: int
    timestamp: Optional[str] = None
    status: str
    starting_point:str
    destination:str