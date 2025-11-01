from fastapi import FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from infrastructure.database import engine, database  # engine: SQLAlchemy Engine, database: databases.Database
from domain.driverPost import Base
from API.post_route import router as post_router

app = FastAPI()

ALLOWED_ORIGINS = [
    "http://localhost:5173/",
    "https://ntouber.zeabur.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    # 先確保 schema 存在（同步 create_all 用 sync engine 沒問題）
    Base.metadata.create_all(bind=engine)
    # 再連 databases（非同步）
    await database.connect()
    print("Database connected successfully.")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected successfully.")


app.include_router(post_router, prefix="/api/posts")

for route in app.routes:
    print(route.path)
