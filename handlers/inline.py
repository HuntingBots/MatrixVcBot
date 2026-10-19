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
from pyrogram import Client, errors
from pyrogram.types import InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from youtubesearchpython import VideosSearch


@Client.on_inline_query()
async def inline(client: Client, query: InlineQuery):
    answers = []
    search_query = query.query.strip()

    if not search_query:
        try:
            await client.answer_inline_query(
                query.id,
                results=[],
                switch_pm_text="Type a YouTube video name...",
                switch_pm_parameter="help",
                cache_time=0
            )
        except Exception:
            pass
        return

    try:
        search = VideosSearch(search_query, limit=25)
        res_data = search.result()
        results = res_data.get("result", [])

        for result in results:
            vid_id = result.get("id")
            title = result.get("title", "Unknown Title")
            duration = result.get("duration", "N/A")
            views = result.get("viewCount", {}).get("short", "0 views")
            thumbnails = result.get("thumbnails", [])
            thumb_url = thumbnails[0].get("url") if thumbnails else None

            description = f"{duration}, {views}."
            content = f"https://www.youtube.com/watch?v={vid_id}"

            item = InlineQueryResultArticle(
                title=title,
                description=description,
                input_message_content=InputTextMessageContent(content),
                thumb_url=thumb_url
            )
            answers.append(item)

        await query.answer(
            results=answers,
            cache_time=10
        )
    except errors.QueryIdInvalid:
        pass
    except Exception as e:
        print(f"Inline search error: {e}")
        try:
            await query.answer(
                results=[],
                cache_time=0,
                switch_pm_text="Search error occurred",
                switch_pm_parameter="help"
            )
        except Exception:
            pass
