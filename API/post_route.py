from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import PlainTextResponse
from typing import List
from API.dto.driver_post import DriverPostDTO
from repository.driverPost_repository import DriverPostRepository
from datetime import datetime
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
        # validate and return plain dicts to satisfy FastAPI's response validation
        return [DriverPostDTO.model_validate(p).model_dump() for p in driver_post]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getpost/{post_id}", response_model=DriverPostDTO)
async def get_post_by_id(post_id: str):
    try:
        driver_post = await DriverPostRepository.get_post_by_id(post_id)
        return DriverPostDTO.model_validate(driver_post).model_dump()
    except HTTPException as http_exc:
        raise http_exc
    
@router.get("/search/{driver_id}", response_model=List[DriverPostDTO])
async def get_post_by_id(driver_id: str):
    try:
        driver_post = await DriverPostRepository.get_post_by_driver_id(driver_id)
        return [DriverPostDTO.model_validate(p).model_dump() for p in driver_post]
    except HTTPException as http_exc:
        raise http_exc
    

@router.get("/search", response_model=List[DriverPostDTO])
async def search_destination(
    start_point: str | None = Query(None),
    end_point: str | None = Query(None),
    time: datetime | None = Query(None), 
    partial: bool = Query(False),
):
    # Normalize empty strings (e.g. ?start_point=) to None so repository treats them as omitted
    def _norm(s: str | None) -> str | None:
        if s is None:
            return None
        s2 = s.strip()
        return s2 if s2 != "" else None

    start_point = _norm(start_point)
    end_point = _norm(end_point)

    posts = await DriverPostRepository.search_destination(start_point, end_point, time, partial=partial)
    return [DriverPostDTO.model_validate(p).model_dump() for p in posts]
    
@router.delete("/deleteall", response_class=PlainTextResponse)
async def delete_all_post():
    try:
        await DriverPostRepository.delete_all_post()
        return "All driver posts deleted successfully."
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.delete("/delete/{post_id}", response_class=PlainTextResponse)
async def delete_post_by_id(post_id: str):
    try:
        await DriverPostRepository.delete_post_by_id(post_id)
        return f"Driver post with id {post_id} deleted successfully."
    except HTTPException as http_exc:
        raise http_exc