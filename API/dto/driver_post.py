from pydantic import BaseModel
from typing import Optional

class DriverPostDTO(BaseModel):
    driver_id: int
    post_id: int
    timestamp: Optional[str] = None
    status: str
    starting_point:str
    destination:str