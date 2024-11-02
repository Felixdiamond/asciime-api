from fastapi import APIRouter
from ..models.schemas import CategoriesResponse
from ..models.categories import CATEGORIES

router = APIRouter()

@router.get("/categories", response_model=CategoriesResponse)
async def get_categories() -> CategoriesResponse:
    return CategoriesResponse(success=True, data=CATEGORIES)

# app/core/config.py
from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    TENOR_API_KEY: str
    GIPHY_API_KEY: str
    REDIS_URL: str
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()