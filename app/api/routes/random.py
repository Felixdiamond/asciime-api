from fastapi import APIRouter, Query, HTTPException
from ..models.schemas import RandomResponse
from ..services.gif_manager import GifManager
from ..models.categories import CATEGORIES

router = APIRouter()

@router.get("/random", response_model=RandomResponse)
async def get_random_gif(
    category: str = Query(default="all")
) -> RandomResponse:
    try:
        gif_manager = GifManager()
        categories = [cat["id"] for cat in CATEGORIES] if category == "all" else [category]
        
        gifs = await gif_manager.get_gifs(1, categories)
        if not gifs:
            raise HTTPException(status_code=404, detail="No gifs found")
        
        gif = gifs[0]
        return RandomResponse(
            success=True,
            data={
                "id": gif["id"],
                "url": gif["url"],
                "size": gif["size"],
                "dims": gif["dims"],
                "source": gif["source"],
                "category": category
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))