from sqlalchemy.sql import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, update
from fastapi import FastAPI, HTTPException
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
        
    @staticmethod
    async def get_post_by_driver_id(driver_id: str):
        query = select(DriverPost).where(DriverPost.driver_id == driver_id)
        try:
            rows = await database.fetch_all(query)
            if rows:
                return [dict(r) for r in rows]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete driver posts: {str(e)}"
            )
        
    @staticmethod
    async def search_destination(keyname: str, partial: bool = False,
                                         case_insensitive: bool = True,
                                         limit: int = 50, offset: int = 0):
        # name_expr = func.json_unquote(func.json_extract(DriverPost.destination, '$.Name'))
        des_name = func.json_unquote(func.json_extract(DriverPost.destination, '$.Name'))
        des_address = func.json_unquote(func.json_extract(DriverPost.destination, '$.Address'))

        if case_insensitive:
            # compare lower(name_expr) with lower(param)
            if partial:
                pattern = f"%{keyname.lower()}%"
                cond = or_(func.lower(des_name).like(pattern), func.lower(des_address).like(pattern))
            else:
                cond = or_(func.lower(des_name) == keyname.lower(), func.lower(des_address) == keyname.lower())
        else:
            if partial:
                pattern = f"%{keyname}%"
                cond = or_(des_name.like(pattern), des_address.like(pattern))
            else:
                cond = or_(des_name == keyname, des_address == keyname)

        query = (
            select(DriverPost)
            .where(cond)
            .order_by(DriverPost.id)
            .limit(limit)
            .offset(offset)
        )
        rows = await database.fetch_all(query)
        return [dict(r) for r in rows]
    

    @staticmethod
    async def delete_all_post():
        query = delete(DriverPost)
        try:
            await database.execute(query)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete driver posts: {str(e)}"
            )
        
    @staticmethod
    async def delete_post_by_id(post_id: str):
        query = delete(DriverPost).where(DriverPost.id == post_id)
        try:
            result = await database.execute(query)
            if result == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver post not found"
                )
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to delete driver post: {str(e)}"
            )

