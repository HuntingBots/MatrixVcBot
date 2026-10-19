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
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(
    filters.command("start")
    & filters.private
)
async def start_(client: Client, message: Message):
    first_name = message.from_user.first_name if message.from_user else "there"
    await message.reply_text(
        f"""<b>Hi {first_name}!
\nHello, I'm Matrix VC Bot. I can play music in your group's voice chat. [🎵](https://telegra.ph/file/73d737b83d58322eda419.jpg) 
I'm here to entertain you.
\nTo add me in your group, please contact my master or add me directly.
\nHit /help for a list of available commands.
</b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🤴 My Master", url="https://t.me/The_Ghost_Hunter",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💬 Group", url="https://t.me/helpcenterbot1"
                    ),
                    InlineKeyboardButton(
                        "🔊 My Channel", url="https://t.me/fire_world_entertainment6"
                    ),
                    InlineKeyboardButton(
                        "📚 Logs", url="https://t.me/helpcenterbotloges"
                    ),
                ],
                [
                    InlineKeyboardButton(
                        "💾 Source code", url="https://github.com/HuntingBots/MatrixVcBot"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➕ Add To Your Group ➕", url=f"https://t.me/{(await client.get_me()).username}?startgroup=true"
                    ) 
                ]
            ]
        ),
        disable_web_page_preview=False
    )


@Client.on_message(
    filters.command("start")
    & filters.group
)
async def start(client: Client, message: Message):
    await message.reply_text(
        "🔍 Do you want to search for a YouTube video?",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Channel", url="https://t.me/fire_world_entertainment"
                    )
                ],    
                [    
                    InlineKeyboardButton(
                        "✅ Yes", switch_inline_query_current_chat=""
                    ),
                    InlineKeyboardButton(
                        "No ❌", callback_data="cls"
                    )
                ]
            ]
        )
    )


@Client.on_message(
    filters.command("help")
    & filters.private
)
async def help(client: Client, message: Message):
    first_name = message.from_user.first_name if message.from_user else "there"
    await message.reply_text(
        f"""<b>Hi {first_name}!
\n/play &lt;song name or link&gt; - play song you requested
/dplay &lt;song name&gt; - play song you requested via deezer
/wplay &lt;song name&gt; - play song you requested via Wynk Music
/playlist - Show now playing list
/current - Show now playing
/song &lt;song name&gt; - download songs you want quickly
/search &lt;query&gt; - search videos on youtube with details
/deezer &lt;song name&gt; - download songs you want quickly via deezer
/wynk &lt;song name&gt; - download songs you want quickly via Wynk Music
/video &lt;song name&gt; - download videos you want quickly
\n*Admins only*
/player - open music player settings panel
/pause - pause song play
/resume - resume song play
/skip - play next song
/end - stop music play
/userbotjoin - invite assistant to your chat
/userbotleave - remove assistant from your chat
/admincache - Refresh admin list
</b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Channel", url="https://t.me/fire_world_entertainment5"
                    )
                ]
            ]
        )
    )
