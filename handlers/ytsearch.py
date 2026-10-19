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
import logging
from pyrogram.types import Message
from youtube_search import YoutubeSearch
from pyrogram import Client, filters

logger = logging.getLogger(__name__)


@Client.on_message(filters.command(["search"]))
async def ytsearch(_, message: Message):
    try:
        if len(message.command) < 2:
            await message.reply_text("❗ `/search` needs an argument! (e.g. `/search Believer`)")
            return

        query = message.text.split(None, 1)[1]
        m = await message.reply_text("🔍 Searching YouTube...")
        results = YoutubeSearch(query, max_results=5).to_dict()

        if not results:
            await m.edit("❌ No results found. Please try a different query.")
            return

        text = ""
        for res in results[:5]:
            title = res.get('title', 'Unknown Title')
            duration = res.get('duration', 'N/A')
            views = res.get('views', 'N/A')
            channel = res.get('channel', 'Unknown Channel')
            url_suffix = res.get('url_suffix', '')
            text += f"**Title:** {title}\n"
            text += f"**Duration:** {duration}\n"
            text += f"**Views:** {views}\n"
            text += f"**Channel:** {channel}\n"
            text += f"🔗 https://youtube.com{url_suffix}\n\n"

        await m.edit(text.strip(), disable_web_page_preview=True)
    except Exception as e:
        await message.reply_text(f"❌ Error: {e}")
