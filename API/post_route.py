from fastapi import APIRouter, HTTPException, Depends, Body, Response
from typing import List, Optional, Annotated
from fastapi.responses import JSONResponse
from API.dto.driver_post import DriverPostDTO
from domain.product import DriverPost
from infrastructure.database import database, SessionLocal
from sqlalchemy.orm import Session

router = APIRouter()

