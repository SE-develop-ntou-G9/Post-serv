from fastapi import APIRouter, HTTPException, Query
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
    
@router.get("/search/by-name", response_model=List[DriverPostDTO])
async def search_by_destination_name(
    name: str = Query(..., description="目的地名稱(搜尋用)"),
    partial: bool = Query(False, description="是否模糊搜尋"),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
):
    posts = await DriverPostRepository.search_by_destination_name(name, partial=partial, limit=limit, offset=offset)
    return [DriverPostDTO.model_validate(p) for p in posts]
    
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