import aiohttp
from tenacity import retry, stop_after_attempt, wait_exponential
from ..models.categories import CATEGORIES
from ..core.config import get_settings
import logging

settings = get_settings()
logger = logging.getLogger(__name__)

MAX_QUERY_LENGTH = 50

def get_category_terms(category_id):
    category = next((cat for cat in CATEGORIES if cat["id"] == category_id), None)
    return category["terms"] if category else ["anime"]

def create_search_query(terms):
    query_parts = ["anime"]
    for term in terms:
        if term == "anime":
            continue
        test_query = f"{query_parts[0]} {term}"
        if len(test_query) <= MAX_QUERY_LENGTH:
            query_parts.append(term)
            break
    return " ".join(query_parts)

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
async def get_giphy_gifs(limit=20, category="all", offset=0):
    if not settings.GIPHY_API_KEY:
        logger.error("GIPHY_API_KEY not found")
        return []

    try:
        search_terms = get_category_terms(category) if category != "all" else ["anime"]
        search_query = create_search_query(search_terms)

        params = {
            "api_key": settings.GIPHY_API_KEY,
            "q": search_query,
            "limit": limit,
            "offset": offset,
            "bundle": "messaging_non_clips",
        }

        async with aiohttp.ClientSession() as session:
            async with session.get(
                "https://api.giphy.com/v1/gifs/search",
                params=params
            ) as response:
                if response.status != 200:
                    error_text = await response.text()
                    if response.status == 414:
                        logger.info("Falling back to basic 'anime' search")
                        params["q"] = "anime"
                        async with session.get(
                            "https://api.giphy.com/v1/gifs/search",
                            params=params
                        ) as retry_response:
                            if retry_response.status == 200:
                                data = await retry_response.json()
                            else:
                                raise Exception(f"Giphy API error: {retry_response.status}")
                    elif response.status == 429:
                        return []
                    else:
                        raise Exception(f"Giphy API error: {response.status}")
                else:
                    data = await response.json()

                if not data.get("data"):
                    return []

                gifs = []
                for gif in data["data"]:
                    try:
                        gif_data = (
                            gif["images"].get("original") or
                            gif["images"].get("downsized") or
                            gif["images"].get("fixed_height")
                        )
                        if gif_data:
                            gifs.append({
                                "url": gif_data["url"],
                                "size": int(gif_data.get("size", 0)) or None,
                                "dims": [
                                    int(gif_data.get("width", 0)) or None,
                                    int(gif_data.get("height", 0)) or None,
                                ],
                                "source": "giphy",
                            })
                    except (KeyError, ValueError, TypeError) as e:
                        logger.warning(f"Error processing gif data: {str(e)}")
                        continue

                return gifs

    except Exception as e:
        logger.error(f"Error fetching Giphy GIFs: {str(e)}")
        raise