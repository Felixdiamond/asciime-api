from fastapi import APIRouter, Query, HTTPException
from ..models.schemas import BatchResponse
from ..services.gif_manager import GifManager
from ..models.categories import CATEGORIES

router = APIRouter()

@router.get("/batch", response_model=BatchResponse)
async def get_batch_gifs(
    count: int = Query(default=5, le=50),
    category: str = Query(default="all")
) -> BatchResponse:
    try:
        gif_manager = GifManager()
        categories = [cat["id"] for cat in CATEGORIES] if category == "all" else [category]
        
        gifs = await gif_manager.get_gifs(count, categories)
        if not gifs:
            raise HTTPException(status_code=404, detail="No gifs found")
        
        return BatchResponse(
            success=True,
            data=[{
                "id": gif["id"],
                "url": gif["url"],
                "size": gif["size"],
                "dims": gif["dims"],
                "source": gif["source"],
                "category": category
            } for gif in gifs]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))