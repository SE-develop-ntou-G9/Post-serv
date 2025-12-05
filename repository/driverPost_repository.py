from sqlalchemy.sql import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, update, true
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, status
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
        # JSON extraction helpers
        str_name = func.json_unquote(func.json_extract(DriverPost.start_point, '$.Name'))
        str_address = func.json_unquote(func.json_extract(DriverPost.start_point, '$.Address'))
        des_name = func.json_unquote(func.json_extract(DriverPost.destination, '$.Name'))
        des_address = func.json_unquote(func.json_extract(DriverPost.destination, '$.Address'))

        # helper to create match expressions for name/address
        def _make_match(name_expr, address_expr, value: str):
            if value is None:
                return None
            if partial:
                lowered = value.lower()
                return or_(
                    func.lower(name_expr).like(f"%{lowered}%"),
                    func.lower(address_expr).like(f"%{lowered}%"),
                )
            else:
                return or_(name_expr == value, address_expr == value)

        if start_point is None and end_point is None and time is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one search parameter (start_point, end_point, time) must be provided."
            )

        filters = []

        # If all three params provided, combine them into a single AND filter
        if start_point and end_point and time:
            start_match = _make_match(str_name, str_address, start_point)
            end_match = _make_match(des_name, des_address, end_point)
            if start_match is not None:
                filters.append(start_match)
            if end_match is not None:
                filters.append(end_match)
            # time window: [time, time + 5 hours]
            filters.append(DriverPost.departure_time >= time)
            filters.append(DriverPost.departure_time <= time + timedelta(hours=5))
        else:
            # handle individually to avoid duplicate/overlapping filters
            if start_point:
                start_match = _make_match(str_name, str_address, start_point)
                if start_match is not None:
                    filters.append(start_match)

            if end_point:
                end_match = _make_match(des_name, des_address, end_point)
                if end_match is not None:
                    filters.append(end_match)

            if time:
                filters.append(DriverPost.departure_time >= time)
                filters.append(DriverPost.departure_time <= time + timedelta(hours=5))

        cond = and_(*filters) if filters else true()

        query = (
            select(DriverPost)
            .where(cond)
            .order_by(DriverPost.id)
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

