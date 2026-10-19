"""
MIT License

Copyright (c) 19-10-2026 @HuntingBots for MatrixVcBot

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""
import asyncio
import os
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from urllib.parse import quote_plus
import aiofiles
import aiohttp
from yt_dlp import YoutubeDL

try:
    import ujson as json_parser
except ImportError:
    import json as json_parser


class TrackMetadata:
    """Memory-optimized data holder using __slots__ to eliminate __dict__ memory overhead."""

    __slots__ = ("track_id", "title", "media_url")

    def __init__(self, track_id: str, title: str, media_url: Optional[str] = None):
        self.track_id: str = track_id
        self.title: str = title
        self.media_url: Optional[str] = media_url


class OptimizedWynkEngine:
    __slots__ = (
        "_processed_ids",
        "_download_dir",
        "_concurrency_limit",
        "_semaphore",
    )

    def __init__(self, download_dir: str = "./downloads", max_concurrent: int = 10):
        self._processed_ids: Set[str] = set()
        self._download_dir: str = download_dir
        self._concurrency_limit: int = max_concurrent
        self._semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrent)
        os.makedirs(self._download_dir, exist_ok=True)

    async def _fetch_search(
        self, session: aiohttp.ClientSession, query: str
    ) -> List[TrackMetadata]:
        """Fetches search query asynchronously using pre-allocated connection pool."""
        url = "https://wynk.in/api/v1/search"
        params = {"q": query}
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept": "application/json, text/plain, */*",
        }

        try:
            async with session.get(url, params=params, headers=headers, timeout=aiohttp.ClientTimeout(total=5)) as response:
                if response.status != 200:
                    return []

                raw_text = await response.text()
                data = json_parser.loads(raw_text)

                tracks: List[TrackMetadata] = []
                seen_add = self._processed_ids.add
                seen_contains = self._processed_ids.__contains__

                for item in data.get("items", []):
                    t_id = str(item.get("id", ""))
                    if not t_id:
                        continue

                    if not seen_contains(t_id):
                        seen_add(t_id)

                        title = " ".join(item.get("title", query).split())
                        media_url = item.get("media_url")

                        tracks.append(TrackMetadata(t_id, title, media_url))

                return tracks
        except Exception:
            return []

    async def _download_stream(
        self, session: aiohttp.ClientSession, track: TrackMetadata
    ) -> Optional[str]:
        """Stream chunks directly to disk with non-blocking I/O (Prevents RAM spikes)."""
        if not track.media_url:
            return None

        file_path = os.path.join(self._download_dir, f"{track.track_id}.mp3")
        if os.path.exists(file_path):
            return file_path

        async with self._semaphore:
            try:
                headers = {"User-Agent": "Mozilla/5.0"}
                async with session.get(track.media_url, headers=headers, timeout=aiohttp.ClientTimeout(total=30)) as response:
                    if response.status == 200:
                        async with aiofiles.open(file_path, "wb") as f:
                            async for chunk in response.content.iter_chunked(65536):
                                await f.write(chunk)
                        return file_path
            except Exception:
                pass
        return None

    async def get_track(self, query: str) -> Tuple[str, str]:
        """High-level method: searches Wynk engine and streams the track with instant audio fallback."""
        connector = aiohttp.TCPConnector(limit=10, ttl_dns_cache=300, enable_cleanup_closed=True)
        async with aiohttp.ClientSession(connector=connector, json_serialize=json_parser.dumps) as session:
            tracks = await self._fetch_search(session, query)
            if tracks and tracks[0].media_url:
                file_path = await self._download_stream(session, tracks[0])
                if file_path and os.path.exists(file_path):
                    return file_path, tracks[0].title

            try:
                deezer_url = f"https://api.deezer.com/search?q={quote_plus(query)}"
                async with session.get(deezer_url, timeout=aiohttp.ClientTimeout(total=5)) as d_resp:
                    if d_resp.status == 200:
                        d_data = await d_resp.json(content_type=None)
                        d_tracks = d_data.get("data", [])
                        if d_tracks and d_tracks[0].get("preview"):
                            first = d_tracks[0]
                            t_title = f"{first.get('title', query)} - {first.get('artist', {}).get('name', '')}".strip(" -")
                            track_meta = TrackMetadata(f"wynk_{first['id']}", t_title, first["preview"])
                            file_path = await self._download_stream(session, track_meta)
                            if file_path and os.path.exists(file_path):
                                return file_path, t_title
            except Exception:
                pass

        loop = asyncio.get_running_loop()

        def _fallback_dl():
            safe_name = re.sub(r'[^a-zA-Z0-9]', '_', query)[:20]
            out_file = os.path.join(self._download_dir, f"wynk_{safe_name}.mp3")
            opts = {
                "format": "bestaudio/best",
                "outtmpl": out_file,
                "quiet": True,
                "no_warnings": True,
            }
            if os.path.exists("cookies.txt"):
                opts["cookiefile"] = "cookies.txt"
            with YoutubeDL(opts) as ydl:
                info = ydl.extract_info(f"ytsearch1:{query}", download=True)
                entry = info["entries"][0]
                dl_path = ydl.prepare_filename(entry)
                return dl_path, entry.get("title", query)

        return await loop.run_in_executor(None, _fallback_dl)

    async def process_batch(
        self, queries: List[str]
    ) -> List[Dict[str, Any]]:
        """Macro-optimized pipeline running parallel search and streaming downloads."""
        connector = aiohttp.TCPConnector(
            limit=100, ttl_dns_cache=300, enable_cleanup_closed=True
        )

        async with aiohttp.ClientSession(
            connector=connector, json_serialize=json_parser.dumps
        ) as session:
            search_tasks = [
                self._fetch_search(session, query) for query in queries
            ]
            nested_results = await asyncio.gather(*search_tasks)

            all_tracks: List[TrackMetadata] = [
                track for sublist in nested_results for track in sublist
            ]

            download_tasks = [
                self._download_stream(session, track) for track in all_tracks
            ]
            await asyncio.gather(*download_tasks)

            return [
                {"id": t.track_id, "title": t.title} for t in all_tracks
            ]


wynk_engine = OptimizedWynkEngine()
