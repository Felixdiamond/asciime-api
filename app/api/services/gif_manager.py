import secrets
import asyncio
import logging
from typing import List, Dict, Set
from .tenor import get_anime_gifs
from .reddit import get_reddit_gifs
from .giphy import get_giphy_gifs
from .cache import cache_get, cache_set
import hashlib
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GifManager:
    def __init__(self):
        self.sources = ["tenor", "reddit", "giphy"]
        self.source_functions = {
            "tenor": get_anime_gifs,
            "reddit": get_reddit_gifs,
            "giphy": get_giphy_gifs,
        }
        self.max_offsets = {"reddit": 50, "tenor": 1000, "giphy": 1000}

    def _get_session_key(self, source: str) -> str:
        """Generate a session key based on source and date"""
        date = datetime.now().strftime("%Y-%m-%d")
        return f"session_{source}_{date}"

    async def get_seen_gifs(self, source: str) -> Set[str]:
        """Get previously seen GIFs for this session"""
        session_key = self._get_session_key(source)
        seen_gifs = await cache_get(session_key)
        return set(seen_gifs) if seen_gifs else set()

    async def update_seen_gifs(self, source: str, gif_urls: List[str]) -> None:
        """Update seen GIFs for this session"""
        session_key = self._get_session_key(source)
        seen_gifs = await self.get_seen_gifs(source)
        seen_gifs.update(gif_urls)
        await cache_set(session_key, list(seen_gifs), 86400)

    def _secure_shuffle(self, items: List) -> List:
        """Perform a cryptographically secure shuffle of items"""
        items = items.copy()
        for i in range(len(items) - 1, 0, -1):
            j = secrets.randbelow(i + 1)
            items[i], items[j] = items[j], items[i]
        return items

    def _get_source_offset(self, source: str) -> int:
        """Get appropriate offset for each source"""
        max_offset = self.max_offsets.get(source, 1000)
        return secrets.randbelow(max_offset)

    async def get_gifs_from_source(self, source: str, category: str) -> List[Dict]:
        """Get GIFs from a specific source with source-appropriate offset"""
        if source not in self.source_functions:
            logger.warning(f"Source {source} not configured")
            return []

        try:
            seen_gifs = await self.get_seen_gifs(source)
            offset = self._get_source_offset(source)
            
            fetch_count = 20 if source == "reddit" else 5
            gifs = await self.source_functions[source](fetch_count, category, offset)
            
            if not gifs:
                return []

            new_gifs = [gif for gif in gifs if gif["url"] not in seen_gifs]
            
            if new_gifs:
                await self.update_seen_gifs(source, [gif["url"] for gif in new_gifs])
                return new_gifs[:fetch_count]
            else:
                if len(seen_gifs) > 1000:
                    await cache_set(self._get_session_key(source), [], 86400)
                return gifs[:fetch_count]

        except Exception as e:
            logger.error(f"Error fetching from {source}: {str(e)}")
            return []

    async def get_gifs(self, count: int, categories: List[str] = None) -> List[Dict]:
        """Get random GIFs from all sources and categories"""
        if not categories:
            categories = ["all"]

        shuffled_sources = self._secure_shuffle(self.sources.copy())
        
        tasks = []
        for source in shuffled_sources:
            for category in categories:
                tasks.append(self.get_gifs_from_source(source, category))

        try:
            results = await asyncio.gather(*tasks)
            
            all_gifs = []
            for result in results:
                if isinstance(result, list) and result:
                    all_gifs.extend(result)

            if not all_gifs:
                return []

            shuffled_gifs = self._secure_shuffle(all_gifs)
            return [{
                "id": hashlib.md5(gif["url"].encode()).hexdigest(),
                **gif
            } for gif in shuffled_gifs[:count]]

        except Exception as e:
            logger.error(f"Error gathering GIFs: {str(e)}")
            return []