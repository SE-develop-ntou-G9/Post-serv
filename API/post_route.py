from fastapi import APIRouter, HTTPException
from fastapi.responses import PlainTextResponse
from typing import List
from API.dto.driver_post import DriverPostDTO
from repository.driverPost_repository import DriverPostRepository
import uuid

router = APIRouter()

@router.post("/", response_model=str)
async def create_driver_post(dto: DriverPostDTO):
    data = dto.model_dump()  # Pydantic v2
    data["id"] = str(uuid.uuid4())
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
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getpost/{post_id}", response_model=DriverPostDTO)
async def get_post_by_id(post_id: str):
    try:
        driver_post = await DriverPostRepository.get_post_by_id(post_id)
        return DriverPostDTO.model_validate(driver_post)  # Pydantic v2
    except HTTPException as http_exc:
        raise http_exc