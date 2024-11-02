import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models.categories import CATEGORIES
from ..core.config import get_settings
import logging
import asyncio

settings = get_settings()
logger = logging.getLogger(__name__)

def get_category_terms(category_id):
    category = next((cat for cat in CATEGORIES if cat["id"] == category_id), None)
    return category["terms"] if category else ["anime"]

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_anime_gifs(limit=20, category="all", offset=0):
    if not settings.TENOR_API_KEY:
        logger.error("TENOR_API_KEY not found")
        return []

    search_terms = get_category_terms(category) if category != "all" else ["anime"]
    
    params = {
        "key": settings.TENOR_API_KEY,
        "q": " ".join(search_terms),
        "limit": limit,
        "pos": str(offset),
        "media_filter": "gif,tinygif",
        "contentfilter": "medium",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with asyncio.timeout(5.0):
                async with session.get(
                    "https://tenor.googleapis.com/v2/search",
                    params=params
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        raise Exception(f"Tenor API error: {response.status} - {error_text}")

                    data = await response.json()
                    
                    if not data.get("results"):
                        return []

                    gifs = []
                    for result in data["results"]:
                        try:
                            gif_format = (
                                result["media_formats"].get("gif") or 
                                result["media_formats"].get("tinygif")
                            )
                            if gif_format:
                                gifs.append({
                                    "url": gif_format["url"],
                                    "preview": gif_format["url"],
                                    "size": gif_format.get("size"),
                                    "dims": gif_format.get("dims"),
                                    "source": "tenor",
                                })
                        except (KeyError, TypeError):
                            continue

                    return gifs

    except asyncio.TimeoutError:
        logger.error("Timeout while fetching from Tenor API")
        return []
    except Exception as e:
        logger.error(f"Error fetching from Tenor API: {str(e)}")
        raise
