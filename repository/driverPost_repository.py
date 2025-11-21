# repository/driverPost_repository.py
from fastapi import HTTPException, status
from sqlalchemy import select, insert
from infrastructure.database import database
from domain.driverPost import DriverPost

class DriverPostRepository:
    @staticmethod
    async def create_driver_post(driver_post: dict) -> str:
        # 先查是否存在（注意：這有競態問題，見下方「更健全」作法）
        query = select(DriverPost).where(DriverPost.driver_id == driver_post["driver_id"])
        post = await database.fetch_one(query)

        if post:
            return f'Driver post with id {driver_post["driver_id"]} already exists.'
        else:
            query = insert(DriverPost).values(**driver_post)
            await database.execute(query)
            return "successfully created driver post with id " + str(driver_post["driver_id"])
        
    @staticmethod
    async def get_all_driver_posts():
        query = select(DriverPost)
        rows = await database.fetch_all(query)
        return [dict(r) for r in rows]  # 轉成 list[dict]

