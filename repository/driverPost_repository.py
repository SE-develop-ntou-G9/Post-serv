# repository/driverPost_repository.py
from fastapi import HTTPException, status
from sqlalchemy import select, insert
from infrastructure.database import database
from domain.driverPost import DriverPost

class DriverPostRepository:
    @staticmethod
    async def create_driver_post(driver_post: dict) -> str:
        query = insert(DriverPost).values(**driver_post)
        try:
            await database.execute(query)
            return driver_post["id"]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create driver post: {str(e)}"
            )
        
    @staticmethod
    async def get_all_driver_posts():
        query = select(DriverPost)
        rows = await database.fetch_all(query)
        return [dict(r) for r in rows]  # 轉成 list[dict]
    
    @staticmethod
    async def get_post_by_id(post_id: str):
        query = select(DriverPost).where(DriverPost.id == post_id)
        row = await database.fetch_one(query)
        if row:
            return dict(row)
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver post not found"
            )

