import os
import asyncpraw
import random
import logging
from typing import List, Dict, Optional
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential
from ..core.config import get_settings
from ..models.categories import CATEGORIES


logger = logging.getLogger(__name__)
settings = get_settings()

def get_category_subreddits(category_id: str) -> List[str]:
    """Get subreddits for a given category ID"""
    category = next((cat for cat in CATEGORIES if cat["id"] == category_id), None)
    return category.get("subreddits", ["animegifs"]) if category else ["animegifs"]

async def init_reddit() -> asyncpraw.Reddit:
    """Initialize Reddit API client"""
    try:
        if not settings.REDDIT_CLIENT_ID or not settings.REDDIT_CLIENT_SECRET:
            raise ValueError("Missing Reddit API credentials")

        return asyncpraw.Reddit(
            client_id=settings.REDDIT_CLIENT_ID,
            client_secret=settings.REDDIT_CLIENT_SECRET,
            user_agent="AnimeGifAPI/1.0",
            timeout=settings.REQUEST_TIMEOUT,
        )
    except Exception as e:
        logger.error(f"Failed to initialize Reddit client: {str(e)}")
        raise

async def fetch_subreddit_posts(
    reddit: asyncpraw.Reddit, 
    subreddit_name: str, 
    limit: int
) -> List[Dict]:
    """Fetch posts from a specific subreddit"""
    try:
        gifs = []
        subreddit = await reddit.subreddit(subreddit_name)
        
        async with asyncio.timeout(15.0):
            async for post in subreddit.hot(limit=limit):
                if not hasattr(post, "url"):
                    continue

                url = post.url.lower()
                if not (url.endswith(".gif") or url.endswith(".gifv")):
                    continue

                url = url.replace(".gifv", ".gif")
                
                gifs.append({
                    "url": url,
                    "preview": url,
                    "size": None,
                    "dims": None,
                    "source": "reddit",
                    "title": getattr(post, "title", ""),
                    "subreddit": subreddit_name,
                })

        return gifs
    except asyncio.TimeoutError:
        logger.warning(f"Timeout fetching from r/{subreddit_name}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from r/{subreddit_name}: {str(e)}")
        return []

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=4, max=10),
    retry_error_callback=lambda _: []
)
async def get_reddit_gifs(
    limit: int = 20,
    category: str = "all",
    offset: int = 0
) -> List[Dict]:
    """Fetch anime GIFs from Reddit"""
    reddit = None
    try:
        reddit = await init_reddit()
        subreddit_names = get_category_subreddits(category)
        
        tasks = [
            fetch_subreddit_posts(reddit, subreddit, min(limit * 2, 50))
            for subreddit in subreddit_names
        ]
        
        async with asyncio.timeout(settings.REQUEST_TIMEOUT):
            results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_gifs = []
        for result in results:
            if isinstance(result, list):
                all_gifs.extend(result)
        
        if all_gifs:
            random.shuffle(all_gifs)
            if offset >= len(all_gifs):
                offset = 0
            end_idx = min(offset + limit, len(all_gifs))
            return all_gifs[offset:end_idx]
            
        return []

    except asyncio.TimeoutError:
        logger.error("Timeout in get_reddit_gifs")
        return []
    except Exception as e:
        logger.error(f"Error in get_reddit_gifs: {str(e)}")
        raise
    finally:
        if reddit:
            try:
                await reddit.close()
            except Exception as e:
                logger.error(f"Error closing Reddit instance: {str(e)}")