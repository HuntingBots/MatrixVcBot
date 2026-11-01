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
import os
import re
import time
import urllib.parse
import requests
from config import DURATION_LIMIT
from helpers.errors import DurationLimitError

try:
    from yt_dlp import YoutubeDL
except ImportError:
    YoutubeDL = None

YTTOWAV_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    ),
    "Referer": "https://yttowav.net/",
    "Origin": "https://yttowav.net",
    "Accept": "application/json, text/plain, */*",
}


def extract_video_id(url_or_id: str) -> str:
    if not url_or_id:
        return ""
    text = str(url_or_id).strip()
    patterns = [
        r"(?:v=|\/embed\/|\/shorts\/|\/v\/|youtu\.be\/|\/watch\?v=|\/live\/)([0-9A-Za-z_-]{11})",
        r"^([0-9A-Za-z_-]{11})$",
    ]
    for pattern in patterns:
        m = re.search(pattern, text)
        if m:
            return m.group(1)
    return ""


def download_from_yttowav(url: str, output_format: str = "wav") -> str:
    os.makedirs("downloads", exist_ok=True)
    video_id = extract_video_id(url)
    clean_url = f"https://www.youtube.com/watch?v={video_id}" if video_id else url

    valid_formats = {"wav", "mp3", "flac", "m4a", "ogg"}
    fmt = output_format.lower() if output_format.lower() in valid_formats else "wav"

    filename = f"{video_id if video_id else int(time.time())}.{fmt}"
    out_file = os.path.join("downloads", filename)

    if os.path.isfile(out_file) and os.path.getsize(out_file) > 10240:
        return out_file

    encoded_url = urllib.parse.quote(clean_url, safe="")
    api_url = f"https://yttowav.net/convert.php?url={encoded_url}&format={fmt}"

    data = None
    last_err = None
    for attempt in range(4):
        try:
            resp = requests.get(api_url, headers=YTTOWAV_HEADERS, timeout=25)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("success"):
                    break
                if data.get("code") == "SERVER_BUSY" and attempt < 3:
                    time.sleep(2)
                    continue
                last_err = data.get("error") or data.get("code")
        except Exception as e:
            last_err = str(e)
            if attempt < 3:
                time.sleep(2)

    if not data or not data.get("success"):
        raise RuntimeError(f"yttowav conversion failed: {last_err or 'unknown error'}")

    download_url = data.get("download_url")

    if not download_url:
        job_id = data.get("job_id")
        if not job_id:
            raise RuntimeError("No job_id or download_url returned by yttowav")

        status_url = f"https://api.yttowav.net/api/status/{urllib.parse.quote(job_id)}"
        poll_start = time.time()
        timeout_seconds = 120

        while time.time() - poll_start < timeout_seconds:
            try:
                sresp = requests.get(status_url, headers=YTTOWAV_HEADERS, timeout=15)
                if sresp.status_code == 200:
                    sdata = sresp.json()
                    status = sdata.get("status")

                    if status == "done" or sdata.get("success"):
                        download_url = sdata.get("download_url")
                        break
                    elif status == "failed":
                        err_msg = sdata.get("error") or sdata.get("code") or "Conversion failed on server"
                        raise RuntimeError(f"yttowav failed: {err_msg}")
            except RuntimeError:
                raise
            except Exception:
                pass

            time.sleep(1.2)

    if not download_url:
        raise TimeoutError("Timed out waiting for audio conversion on yttowav")

    if not download_url.startswith("http"):
        download_url = "https://api.yttowav.net" + download_url

    part_file = f"{out_file}.part"
    try:
        with requests.get(download_url, headers=YTTOWAV_HEADERS, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(part_file, "wb") as f:
                for chunk in r.iter_content(chunk_size=65536):
                    if chunk:
                        f.write(chunk)

        if os.path.exists(out_file):
            try:
                os.remove(out_file)
            except Exception:
                pass
        os.replace(part_file, out_file)
        return out_file
    except Exception:
        if os.path.exists(part_file):
            try:
                os.remove(part_file)
            except Exception:
                pass
        raise


def download_from_ytdlp(url: str, output_format: str = "wav") -> str:
    if not YoutubeDL:
        raise RuntimeError("yt-dlp is not available")

    os.makedirs("downloads", exist_ok=True)
    ydl_opts = {
        "format": "bestaudio/best",
        "geo_bypass": True,
        "nocheckcertificate": True,
        "outtmpl": "downloads/%(id)s.%(ext)s",
        "quiet": True,
        "no_warnings": True,
    }
    if os.path.exists("cookies.txt"):
        ydl_opts["cookiefile"] = "cookies.txt"

    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        duration = round((info.get("duration") or 0) / 60)
        if duration > DURATION_LIMIT:
            raise DurationLimitError(
                f"❌ Videos longer than {DURATION_LIMIT} minute(s) aren't allowed, the provided video is {duration} minute(s)"
            )
        ydl.download([url])
        return ydl.prepare_filename(info)


def download(url: str, format: str = "wav") -> str:
    if not extract_video_id(url) and not url.startswith("http"):
        try:
            from youtube_search import YoutubeSearch
            res = YoutubeSearch(url, max_results=1).to_dict()
            if res:
                url = f"https://www.youtube.com{res[0]['url_suffix']}"
        except Exception:
            pass

    try:
        return download_from_yttowav(url, output_format=format)
    except Exception as e:
        print(f"[yttowav] Download failed: {e}. Attempting yt-dlp fallback...")
        try:
            return download_from_ytdlp(url, output_format=format)
        except Exception as yt_err:
            print(f"[yt-dlp] Fallback also failed: {yt_err}")
            raise RuntimeError(f"Download failed: {e}")
