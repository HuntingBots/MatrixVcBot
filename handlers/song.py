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
import time
import math
import asyncio
import aiohttp
import aiofiles
import requests
from urllib.parse import quote_plus
from yt_dlp import YoutubeDL
from youtube_search import YoutubeSearch

from pyrogram import filters, Client
from pyrogram.types import Message
from pyrogram.errors import FloodWait, MessageNotModified

is_downloading = False


def humanbytes(size):
    if not size:
        return ""
    power = 2 ** 10
    raised_to_pow = 0
    dict_power_n = {0: "", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        raised_to_pow += 1
    return str(round(size, 2)) + " " + dict_power_n[raised_to_pow] + "B"


def time_formatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + " day(s), ") if days else "")
        + ((str(hours) + " hour(s), ") if hours else "")
        + ((str(minutes) + " minute(s), ") if minutes else "")
        + ((str(seconds) + " second(s), ") if seconds else "")
        + ((str(milliseconds) + " millisecond(s), ") if milliseconds else "")
    )
    return tmp[:-2] if tmp else "0s"


async def progress(current, total, message, start, type_of_ps, file_name=None):
    now = time.time()
    diff = now - start
    if round(diff % 5.0) == 0 or current == total:
        percentage = current * 100 / (total or 1)
        speed = current / (diff or 1)
        elapsed_time = round(diff) * 1000
        time_to_completion = round((total - current) / (speed or 1)) * 1000
        progress_str = "{0}{1} {2}%\n".format(
            "".join(["🔴" for _ in range(math.floor(percentage / 10))]),
            "".join(["🔘" for _ in range(10 - math.floor(percentage / 10))]),
            round(percentage, 2),
        )
        tmp = progress_str + "{0} of {1}\nETA: {2}".format(
            humanbytes(current), humanbytes(total), time_formatter(time_to_completion)
        )
        try:
            if file_name:
                await message.edit(f"{type_of_ps}\n**File:** `{file_name}`\n{tmp}")
            else:
                await message.edit(f"{type_of_ps}\n{tmp}")
        except (FloodWait, MessageNotModified):
            pass


@Client.on_message(filters.command('song') & ~filters.channel)
async def song(client: Client, message: Message):
    if len(message.command) < 2:
        await message.reply_text("❗ `/song` needs a song name! (e.g. `/song Faded`)")
        return

    query = " ".join(message.command[1:]).strip()
    m = await message.reply('🔎 Finding the song...')

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

    thumb_file = None
    audio_file = None
    try:
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await m.edit("❌ Found nothing. Try another keyword or check spelling.")
            return

        link = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0].get("title", query)[:60]
        thumbnail_url = results[0].get("thumbnails", [None])[0]
        duration_str = results[0].get("duration", "0:0")

        if thumbnail_url:
            thumb_file = f"downloads/thumb_{int(time.time())}.jpg"
            try:
                r = requests.get(thumbnail_url, timeout=10)
                if r.status_code == 200:
                    with open(thumb_file, "wb") as f:
                        f.write(r.content)
            except Exception:
                thumb_file = None

        await m.edit("⬇️ Downloading audio...")
        with YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(link, download=True)
            audio_file = ydl.prepare_filename(info)

        dur = 0
        dur_arr = duration_str.split(':')
        secmul = 1
        for i in range(len(dur_arr) - 1, -1, -1):
            if dur_arr[i].isdigit():
                dur += int(dur_arr[i]) * secmul
            secmul *= 60

        await m.edit("⬆️ Uploading to Telegram...")
        caption = f"🎵 **{title}**\nUploaded by Matrix VC Bot"
        await message.reply_audio(
            audio_file,
            caption=caption,
            thumb=thumb_file if (thumb_file and os.path.exists(thumb_file)) else None,
            title=title,
            duration=dur
        )
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Error downloading song: {e}")
        print(f"Song download error: {e}")
    finally:
        for f in (audio_file, thumb_file):
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass


from optimized_wynk_engine import wynk_engine


@Client.on_message(filters.command(["wynk", "wsong", "saavn"]))
async def wynk_song(client: Client, message: Message):
    global is_downloading
    if len(message.command) < 2:
        await message.reply_text("❗ `/wynk` requires an argument (e.g. `/wynk Kesariya`).")
        return
    if is_downloading:
        await message.reply_text("⏳ Another download is in progress, please wait a moment.")
        return

    is_downloading = True
    query = " ".join(message.command[1:]).strip()
    m = await message.reply_text("🔍 Searching on Wynk Music...")

    song_file = None
    try:
        await m.edit(f"⬇️ Streaming `{query}` via Wynk Engine...")
        song_file, track_title = await wynk_engine.get_track(query)
        await m.edit(f"⬆️ Uploading `{track_title}`...")
        await message.reply_audio(audio=song_file, title=track_title, performer="Wynk Music")
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Error: {e}")
    finally:
        is_downloading = False
        if song_file and os.path.exists(song_file):
            try:
                os.remove(song_file)
            except Exception:
                pass


@Client.on_message(filters.command("deezer"))
async def deezsong(client: Client, message: Message):
    global is_downloading
    if len(message.command) < 2:
        await message.reply_text("❗ `/deezer` requires an argument (e.g. `/deezer Faded`).")
        return
    if is_downloading:
        await message.reply_text("⏳ Another download is in progress, please wait a moment.")
        return

    is_downloading = True
    query = " ".join(message.command[1:]).strip()
    m = await message.reply_text("🔍 Searching on Deezer...")

    song_file = None
    try:
        api_url = f"https://api.deezer.com/search?q={quote_plus(query)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url) as resp:
                data = await resp.json(content_type=None)

        tracks = data.get("data", [])
        if not tracks:
            await m.edit("❌ No songs found on Deezer!")
            return

        track = tracks[0]
        title = track.get("title", query)
        artist = track.get("artist", {}).get("name", "Unknown Artist")
        preview = track.get("preview")

        if not preview:
            await m.edit("❌ Download preview not available for this track.")
            return

        await m.edit(f"⬇️ Downloading `{title}`...")
        song_file = f"downloads/deez_{int(time.time())}.mp3"
        os.makedirs("downloads", exist_ok=True)
        async with aiohttp.ClientSession() as session:
            async with session.get(preview) as resp:
                if resp.status == 200:
                    async with aiofiles.open(song_file, mode='wb') as f:
                        await f.write(await resp.read())

        await m.edit("⬆️ Uploading...")
        await message.reply_audio(audio=song_file, title=title, performer=artist)
        await m.delete()
    except Exception as e:
        await m.edit(f"❌ Error: {e}")
    finally:
        is_downloading = False
        if song_file and os.path.exists(song_file):
            try:
                os.remove(song_file)
            except Exception:
                pass


@Client.on_message(filters.command(["vsong", "video"]))
async def ytmusic(client: Client, message: Message):
    global is_downloading
    if is_downloading:
        await message.reply_text("⏳ Another download is in progress, please wait a moment.")
        return

    if len(message.command) < 2:
        await message.reply_text("❗ `/video` requires a query or YouTube link.")
        return

    query = " ".join(message.command[1:]).strip()
    pablo = await client.send_message(
        message.chat.id,
        f"🔍 `Searching for {query}...`"
    )

    vid_file = None
    thumb_path = None
    try:
        is_downloading = True
        results = YoutubeSearch(query, max_results=1).to_dict()
        if not results:
            await pablo.edit("❌ No video found.")
            return

        url = f"https://youtube.com{results[0]['url_suffix']}"
        title = results[0].get("title", query)
        vid_id = results[0].get("id", str(int(time.time())))
        thumb_url = results[0].get("thumbnails", [None])[0]

        if thumb_url:
            thumb_path = f"downloads/thumb_{vid_id}.jpg"
            try:
                r = requests.get(thumb_url, timeout=10)
                if r.status_code == 200:
                    with open(thumb_path, "wb") as f:
                        f.write(r.content)
            except Exception:
                thumb_path = None

        await pablo.edit("⬇️ Downloading video...")
        os.makedirs("downloads", exist_ok=True)
        opts = {
            "format": "best[height<=720]/best",
            "outtmpl": "downloads/%(id)s.%(ext)s",
            "geo_bypass": True,
            "nocheckcertificate": True,
            "quiet": True,
            "no_warnings": True,
        }
        if os.path.exists("cookies.txt"):
            opts["cookiefile"] = "cookies.txt"

        with YoutubeDL(opts) as ytdl:
            info = ytdl.extract_info(url, download=False)
            duration_sec = info.get("duration") or 0
            if round(duration_sec / 60) > 15:
                await pablo.edit("❌ Videos longer than 15 minutes cannot be downloaded.")
                return

            ytdl.download([url])
            vid_file = ytdl.prepare_filename(info)

        c_time = time.time()
        capy = f"🎬 **{title}**\nUploaded by Matrix VC Bot"
        await pablo.edit("⬆️ Uploading video to Telegram...")
        await client.send_video(
            message.chat.id,
            video=vid_file,
            duration=int(duration_sec),
            file_name=f"{title}.mp4",
            thumb=thumb_path if (thumb_path and os.path.exists(thumb_path)) else None,
            caption=capy,
            supports_streaming=True,
            progress=progress,
            progress_args=(pablo, c_time, "Uploading video...", os.path.basename(vid_file))
        )
        await pablo.delete()
    except Exception as e:
        await pablo.edit(f"❌ Failed to download video: {e}")
        print(f"Video download error: {e}")
    finally:
        is_downloading = False
        for f in (vid_file, thumb_path):
            if f and os.path.exists(f):
                try:
                    os.remove(f)
                except Exception:
                    pass
