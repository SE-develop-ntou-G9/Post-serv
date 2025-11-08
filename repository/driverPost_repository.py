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
            # 既然是錯誤情況，就丟例外，不要回傳字串
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f'Driver post with id {driver_post["driver_id"]} already exists.'
            )

        stmt = insert(DriverPost).values(**driver_post)
        await database.execute(stmt)
        return f'successfully created driver post with id {driver_post["driver_id"]}'
