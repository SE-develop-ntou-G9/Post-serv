from fastapi import APIRouter, HTTPException, Query, UploadFile
from fastapi.responses import PlainTextResponse
from typing import List
from API.dto.driver_post import DriverPostDTO, DriverPostUpdateDTO, UploadImageResponse, DriverPostReturnDTO
from repository.driverPost_repository import DriverPostRepository
from datetime import datetime
import uuid
import filetype

SUPPORTED_FILE_TYPES = {
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'jpg': 'image/jpg'
}

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
 
@router.get("/all", response_model=List[DriverPostReturnDTO])
async def get_all_driver_post():
    try:
        driver_post = await DriverPostRepository.get_all_driver_posts()
        # validate and return plain dicts to satisfy FastAPI's response validation
        return [DriverPostReturnDTO.model_validate(p).model_dump() for p in driver_post]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/allpost", response_model=List[DriverPostReturnDTO])
async def get_admin_driver_posts():
    try:
        driver_post = await DriverPostRepository.get_admin_driver_posts()
        # validate and return plain dicts to satisfy FastAPI's response validation
        return [DriverPostReturnDTO.model_validate(p).model_dump() for p in driver_post]
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/getpost/{post_id}", response_model=DriverPostReturnDTO)
async def get_post_by_id(post_id: str):
    try:
        driver_post = await DriverPostRepository.get_post_by_id(post_id)
        return DriverPostReturnDTO.model_validate(driver_post).model_dump()
    except HTTPException as http_exc:
        raise http_exc
    
@router.get("/search/{user_id}", response_model=List[DriverPostReturnDTO])
async def get_post_by_id(user_id: str):
    try:
        driver_post = await DriverPostRepository.get_post_by_user_id(user_id)
        return [DriverPostReturnDTO.model_validate(p).model_dump() for p in driver_post]
    except HTTPException as http_exc:
        raise http_exc
    

@router.get("/search", response_model=List[DriverPostReturnDTO])
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
    
@router.patch("/request", response_model=DriverPostReturnDTO)
async def request_driver_post(
    post_id: str = Query(None),
    client_id: str = Query(None)
):
    try:
        updated_post = await DriverPostRepository.request_driver_post(post_id, client_id)
        return DriverPostReturnDTO.model_validate(updated_post).model_dump()
    except HTTPException as http_exc:
        raise http_exc

@router.patch("/upload_image", response_model=UploadImageResponse)
async def upload_image(post_id: str, file: UploadFile | None = None):
    if not file:
        return {"message": "No file uploaded."}
    contents = await file.read()
    size = len(contents)

    if not 0 < size <= 5 * 1024 * 1024:
        return {"message": "File size must be between 0 and 5MB."}
    
    kind = filetype.guess(contents)
    if kind is None or kind.extension not in SUPPORTED_FILE_TYPES:
        return {"message": "Unsupported file type."}
    
    folder = "driver_posts"

    file_name = f'{folder}/{post_id}_{uuid.uuid4()}.{kind.extension}'
    image_url = await DriverPostRepository.s3_upload(
        contents=contents, 
        key=file_name, 
        content_type=file.content_type, 
        acl='public-read'
    )

    await DriverPostRepository.upload_image(post_id, image_url)

    return UploadImageResponse(message="Image uploaded successfully.", image_url=image_url)

@router.patch("/driver_posts/{post_id}")
async def modify_driver_post(post_id: str, body: DriverPostUpdateDTO):
    # 只取有傳的欄位
    try:
        update_data = body.model_dump(exclude_unset=True)
        return await DriverPostRepository.modify_driver_post(post_id, update_data)
    except HTTPException as http_exc:
        raise http_exc