from fastapi import APIRouter
from ..models.schemas import CategoriesResponse
from ..models.categories import CATEGORIES

router = APIRouter()

@router.get("/categories", response_model=CategoriesResponse)
async def get_categories() -> CategoriesResponse:
    return CategoriesResponse(success=True, data=CATEGORIES)