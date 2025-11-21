from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import List
from API.dto.driver_post import DriverPostDTO
from repository.driverPost_repository import DriverPostRepository

router = APIRouter()

@router.post("/", response_model=str)
async def create_driver_post(dto: DriverPostDTO):
    data = dto.model_dump()  # Pydantic v2
    try:
        driver_post_id = await DriverPostRepository.create_driver_post(data)
        return driver_post_id
    except Exception as e:
    # Catch actual exceptions (ValueError, DB errors, etc.)
    raise HTTPException(status_code=400, detail=str(e))
 
@router.get("/all", response_model=List[DriverPostDTO])
async def get_all_driver_post():
    try:
        driver_post = await DriverPostRepository.get_all_driver_posts()
        return [DriverPostDTO.model_validate(p) for p in driver_post]  # Pydantic v2
    except Exception as e:

