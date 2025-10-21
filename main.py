from fastapi import FastAPI, APIRouter
from infrastructure.database import engine, database
from domain.product import Base
from fastapi.middleware.cors import CORSMiddleware
from API.post_route import router as product_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup():
    try:
        await database.connect()
        Base.metadata.create_all(bind=engine)
        print("Database connected successfully.")
    except Exception as e:
        print(f"Database connection error: {e}")

@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()
    print("Database disconnected successfully.")

router = APIRouter()
@router.get("/", response_model=str)
async def demo():
    return "hello NTOUber!"

app.include_router(router, prefix="/api")
app.include_router(product_router, prefix="/api/product", tags=["Products"])