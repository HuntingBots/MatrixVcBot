from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton



@Client.on_message(
    filters.command("start")
    & filters.private
    & ~ filters.edited
)
async def start_(client: Client, message: Message):
    await message.reply_sticker,
    await message.reply_text(
        f"""<b>Hi {message.from_user.first_name}!
\nI Hello I'm Matrix VC Bot I can play music in your group's voice chat [🎵](https://telegra.ph/file/73d737b83d58322eda419.jpg") 
I'm here for Entertain you.
\nTo add in your group please contact my master at [HELP CENTER](@helpcenterbot1).
\nHit /help list of available commands.
 </b>""",
      
       
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🤴My Master", url="https://t.me/The_Ghosht_Hunter",
                    )
                ],
                [
                    InlineKeyboardButton(
                        "💬 Group", url="https://t.me/helpcenterbot1"
                    ),
                    InlineKeyboardButton(
                        "🔊 My Channel", url="https://t.me/fire_world_entertainment"
                    ),
                    InlineKeyboardButton(
                        "📚 Loges", url="https://t.me/helpcenterbotloges"
                    )
                ],
                [
                
                    InlineKeyboardButton(
                        "💾 Source code", url="https://github.com/HuntingBots/MatrixVcBot"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "➕ Add To Your Group ➕", url="https://t.me/Matrix_Vcbot?startgroup=true"
                    ) 
                ]
            ]
        )
    )

@Client.on_message(
    filters.command("start")
    & filters.group
    & ~ filters.edited
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
                        "No ❌", callback_data="close"
                    )
                ]
            ]
        )
    )

@Client.on_message(
    filters.command("help")
    & filters.private
    & ~ filters.edited
)
async def help(client: Client, message: Message):
    await message.reply_text(
        f"""<b>Hi {message.from_user.first_name}!
\n/play <song name> - play song you requested
/dplay <song name> - play song you requested via deezer
/splay <song name> - play song you requested via jio saavn
/playlist - Show now playing list
/current - Show now playing
/song <song name> - download songs you want quickly
/search <query> - search videos on youtube with details
/deezer <song name> - download songs you want quickly via deezer
/saavn <song name> - download songs you want quickly via saavn
/video <song name> - download videos you want quickly
\n*Admins only*
/player - open music player settings panel
/pause - pause song play
/resume - resume song play
/skip - play next song
/end - stop music play
/userbotjoin - invite assistant to your chat
/admincache - Refresh admin list
 </b>""",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "🔊 Channel", url="https://t.me/fire_world_entertainment"
                    )
                ]
            ]
        )
    )    
