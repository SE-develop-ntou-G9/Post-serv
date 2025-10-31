from fastapi import APIRouter, HTTPException
from API.dto.driver_post import DriverPostDTO
from repository.driverPost_repository import DriverPostRepository

router = APIRouter()

@router.post("/", response_model=str)
async def create_driver_post(dto: DriverPostDTO):
    data = dto.model_dump()  # Pydantic v2
    try:
        driver_post_id = await DriverPostRepository.create_driver_post(data)
        return driver_post_id
    except DriverPostRepository as e:
        raise HTTPException(status_code=400, detail=str(e))
