from sqlalchemy.sql import insert, delete, select, update
from sqlalchemy.orm import Session
from sqlalchemy import func, or_, update
from fastapi import FastAPI, HTTPException
from infrastructure.database import database
from domain.driverPost import DriverPost

class DriverPostRepository:
    @staticmethod
    async def create_driver_post(driver_post: dict):
        query = select(DriverPost).where(DriverPost.driver_id == driver_post['driver_id'])
        post = await database.fetch_one(query)
        print(post)

        if post:
            return f'Driver post with id {driver_post["driver_id"]} already exists.'
        else:
            query = insert(DriverPost).values(**driver_post)
            await database.execute(query)
            return "successfully created driver post with id " + str(driver_post["driver_id"])