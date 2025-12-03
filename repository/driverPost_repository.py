from sqlalchemy.sql import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, update, true
from datetime import datetime
from typing import Optional
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
    async def search_destination(
        start_point: Optional[str] = None,
        end_point: Optional[str] = None,
        time: Optional[datetime] = None,
        partial: bool = False,
        limit: int = 50,
        offset: int = 0,
    ):
        str_name = func.json_unquote(func.json_extract(DriverPost.start_point, '$.Name'))
        str_address = func.json_unquote(func.json_extract(DriverPost.start_point, '$.Address'))
        des_name = func.json_unquote(func.json_extract(DriverPost.destination, '$.Name'))
        des_address = func.json_unquote(func.json_extract(DriverPost.destination, '$.Address'))

        filters = []
        if start_point is None and end_point is None and time is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one search parameter (start_point, end_point, time) must be provided."
            )
        if start_point and end_point and time:
            if partial:
                filters.append(
                    and_(
                        or_(
                            func.lower(str_name).like(f"%{start_point.lower()}%"),
                            func.lower(str_address).like(f"%{start_point.lower()}%"),
                        ),
                        or_(
                            func.lower(des_name).like(f"%{end_point.lower()}%"),
                            func.lower(des_address).like(f"%{end_point.lower()}%"),
                        ),
                        DriverPost.departure_time >= time,
                        DriverPost.departure_time <= time + timedelta(hours=5)
                    )
                )
            else:
                filters.append(
                    and_(
                        or_(str_name == start_point, str_address == start_point),
                        or_(des_name == end_point, des_address == end_point),
                        DriverPost.departure_time >= time,
                        DriverPost.departure_time <= time + timedelta(hours=5)
                    )
                )

        if start_point:
            if partial:
                filters.append(
                    or_(
                        func.lower(str_name).like(f"%{start_point.lower()}%"),
                        func.lower(str_address).like(f"%{start_point.lower()}%"),
                    )
                )
            else:
                filters.append(or_(str_name == start_point, str_address == start_point))

        if end_point:
            if partial:
                filters.append(
                    or_(
                        func.lower(des_name).like(f"%{end_point.lower()}%"),
                        func.lower(des_address).like(f"%{end_point.lower()}%"),
                    )
                )
            else:
                filters.append(or_(des_name == end_point, des_address == end_point))

        if time:
            filters.append(DriverPost.departure_time >= time)
            filters.append(DriverPost.departure_time <= time + timedelta(hours=5))

        cond = and_(*filters) if filters else true()

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

