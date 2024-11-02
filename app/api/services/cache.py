import aiohttp
import json
from ..core.config import get_settings
import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)
settings = get_settings()

class UpstashRedis:
    def __init__(self, url: str, token: str):
        self.base_url = url
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

    async def _make_request(self, command: list) -> Any:
        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(
                    self.base_url,
                    headers=self.headers,
                    json=command
                ) as response:
                    if response.status != 200:
                        logger.error(f"Upstash error: {response.status}")
                        return None
                    
                    result = await response.json()
                    return result.get("result")
            except Exception as e:
                logger.error(f"Error making Upstash request: {str(e)}")
                return None

async def cache_get(key: str) -> Optional[Any]:
    """Get value from Upstash Redis"""
    redis = UpstashRedis(
        url=settings.UPSTASH_REDIS_REST_URL,
        token=settings.UPSTASH_REDIS_REST_TOKEN
    )
    
    try:
        result = await redis._make_request(["GET", key])
        return json.loads(result) if result else None
    except json.JSONDecodeError:
        return result if result else None
    except Exception as e:
        logger.error(f"Error in cache_get: {str(e)}")
        return None

async def cache_set(key: str, value: Any, ex: int = 3600) -> bool:
    """Set value in Upstash Redis with expiration"""
    redis = UpstashRedis(
        url=settings.UPSTASH_REDIS_REST_URL,
        token=settings.UPSTASH_REDIS_REST_TOKEN
    )
    
    try:
        value_str = json.dumps(value)
        # Set with expiration using SETEX command
        result = await redis._make_request(["SETEX", key, str(ex), value_str])
        return result == "OK"
    except Exception as e:
        logger.error(f"Error in cache_set: {str(e)}")
        return False

async def cache_invalidate(category: str) -> bool:
    """Invalidate cache for a category"""
    redis = UpstashRedis(
        url=settings.UPSTASH_REDIS_REST_URL,
        token=settings.UPSTASH_REDIS_REST_TOKEN
    )
    
    try:
        if category == "all":
            result = await redis._make_request(["FLUSHDB"])
            return result == "OK"
        else:
            result = await redis._make_request(["DEL", f"gifs_{category}"])
            return result >= 0
    except Exception as e:
        logger.error(f"Error in cache_invalidate: {str(e)}")
        return False