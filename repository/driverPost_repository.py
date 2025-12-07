from sqlalchemy.sql import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, and_, update, true
from datetime import datetime, timedelta
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from infrastructure.database import database
from domain.driverPost import DriverPost
import boto3
from loguru import logger
import filetype
from uuid import uuid4
import os

s3 = boto3.client(
    's3',
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
    region_name=os.getenv("aws_region")
)

import logging

logger = logging.getLogger(__name__)

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
        query = select(DriverPost).where(DriverPost.status == "open")
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
    async def get_post_by_user_id(user_id: str):
        cond = or_(DriverPost.driver_id == user_id, DriverPost.client_id == user_id)
        query = select(DriverPost).where(cond)
        try:
            rows = await database.fetch_all(query)
            if rows:
                return [dict(r) for r in rows]
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get driver posts by user id: {str(e)}"
            )
        
    @staticmethod
    async def search_destination(
        start_point: Optional[str] = None,
        end_point: Optional[str] = None,
        time: Optional[datetime] = None,
        partial: bool = False,
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

        filters.append(DriverPost.status == "open")
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
        
    @staticmethod
    async def s3_upload(contents: bytes, key: str, content_type: str, acl: str = "private", server_side_encryption: str = "AES256",) -> str:
        logger.info(f"Uploading file to S3 with key: {key} and ACL: {acl}")
        try:
            s3.put_object(
                Bucket=os.getenv("s3_bucket_name"),
                Key=key,
                Body=contents,
                ContentType=content_type,
                ACL=acl,
                ServerSideEncryption=server_side_encryption,
            )
            logger.info(f"File successfully uploaded to S3 with key: {key}")

            bucket_name = os.getenv("s3_bucket_name")
            region = os.getenv("aws_region")
            image_url = f"https://{bucket_name}.s3.{region}.amazonaws.com/{key}"

            return image_url

        except Exception as e:
            logger.error(f"Failed to upload file to S3: {e}")
            raise HTTPException(
                status_code=500,
                detail="Failed to upload file to S3",
            )

    @staticmethod
    async def request_driver_post(driver_id: str, client_id: str, time: datetime):
        cond = and_(DriverPost.driver_id == driver_id, DriverPost.time_stamp == time)
        prequery = (
            select(DriverPost).where(cond)
        )
        result = await database.fetch_one(prequery)

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Driver post not found"
            )
        if result['status'] != 'open':
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Driver post is not available for request"
            )
        
        query = (
            update(DriverPost)
            .where(cond)
            .values(status="matched", client_id=client_id)
        )
        try:
            result = await database.execute(query) # Execute the update
            if result == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver post not found"
                )
            # Fetch the updated post
            select_query = select(DriverPost).where(cond) # Fetch the updated post
            result = await database.fetch_one(select_query) 
            return dict(result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to request driver post: {str(e)}"
            ) 
    
    @staticmethod
    async def upload_image(post_id: str, image_url: str):

        query = (
            update(DriverPost)
            .where(DriverPost.id == post_id)
            .values(image_url=image_url)
        )
        try:
            result = await database.execute(query)
            if result == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver post not found"
                )
            return image_url
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to upload image: {str(e)}"
            )
        
    @staticmethod
    async def modify_driver_post(post_id: str, updated_fields: dict):
        query = (
            update(DriverPost)
            .where(DriverPost.id == post_id)
            .values(**updated_fields)
        )

        try:
            result = await database.execute(query)
            if result == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Driver post not found"
                )
            # Fetch the updated post
            select_query = select(DriverPost).where(DriverPost.id == post_id)
            result = await database.fetch_one(select_query)
            return dict(result)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to modify driver post: {str(e)}"
            )