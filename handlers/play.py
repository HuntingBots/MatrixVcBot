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
import uuid
import aiohttp
import aiofiles
import requests
from typing import Callable
from urllib.parse import quote_plus
from PIL import Image, ImageFont, ImageDraw

from pyrogram import Client, filters
from pyrogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from pyrogram.errors import UserAlreadyParticipant
from youtube_search import YoutubeSearch
from yt_dlp import YoutubeDL

import converter
from downloaders import youtube
from callsmusic import callsmusic, queues
from callsmusic.callsmusic import client as USER
from config import BOT_NAME as bn, DURATION_LIMIT, que, SUDO_USERS
from helpers.filters import command, other_filters
from helpers.decorators import authorized_users_only
from helpers.admins import get_administrators
from cache.admins import admins as a


def cb_admin_check(func: Callable) -> Callable:
    async def decorator(client: Client, cb: CallbackQuery):
        user_id = cb.from_user.id if cb.from_user else None
        if not user_id:
            return

        if user_id in SUDO_USERS:
            return await func(client, cb)

        admemes = a.get(cb.message.chat.id)
        if admemes and user_id in admemes:
            return await func(client, cb)

        administrators = await get_administrators(cb.message.chat)
        if user_id in administrators:
            return await func(client, cb)

        await cb.answer("You are not authorized to use this button!", show_alert=True)
        return
    return decorator


def change_image_size(max_width: int, max_height: int, image: Image.Image) -> Image.Image:
    width_ratio = max_width / image.size[0]
    height_ratio = max_height / image.size[1]
    new_width = int(width_ratio * image.size[0])
    new_height = int(height_ratio * image.size[1])
    return image.resize((new_width, new_height))


async def generate_cover(requested_by: str, title: str, views: str, duration: str, thumbnail_url: str) -> str:
    uid = uuid.uuid4().hex[:8]
    bg_file = f"downloads/bg_{uid}.png"
    final_file = f"downloads/cover_{uid}.png"
    os.makedirs("downloads", exist_ok=True)

    try:
        if thumbnail_url:
            async with aiohttp.ClientSession() as session:
                async with session.get(thumbnail_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(bg_file, mode="wb") as f:
                            await f.write(await resp.read())

        if os.path.exists(bg_file) and os.path.exists("etc/foreground.png") and os.path.exists("etc/font.otf"):
            image1 = Image.open(bg_file)
            image2 = Image.open("etc/foreground.png")
            image3 = change_image_size(1280, 720, image1)
            image4 = change_image_size(1280, 720, image2)
            image5 = image3.convert("RGBA")
            image6 = image4.convert("RGBA")
            Image.alpha_composite(image5, image6).save(final_file)

            img = Image.open(final_file)
            draw = ImageDraw.Draw(img)
            font = ImageFont.truetype("etc/font.otf", 32)
            draw.text((205, 550), f"Title: {title[:35]}", (51, 215, 255), font=font)
            draw.text((205, 590), f"Duration: {duration}", (255, 255, 255), font=font)
            draw.text((205, 630), f"Views: {views}", (255, 255, 255), font=font)
            draw.text((205, 670), f"Added By: {requested_by}", (255, 255, 255), font=font)
            img.save(final_file)
            return final_file
    except Exception as e:
        print(f"Error creating cover: {e}")
    finally:
        if os.path.exists(bg_file):
            try:
                os.remove(bg_file)
            except Exception:
                pass

    if os.path.exists("etc/matrixtg_vc_bot.png"):
        return "etc/matrixtg_vc_bot.png"
    return ""


def r_ply():
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('⏹ Stop', callback_data='leave'),
                InlineKeyboardButton('⏸ Pause', callback_data='puse'),
                InlineKeyboardButton('▶️ Resume', callback_data='resume'),
                InlineKeyboardButton('⏭ Skip', callback_data='skip')
            ],
            [
                InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                InlineKeyboardButton('❌ Close', callback_data='cls')
            ]
        ]
    )


def updated_stats(chat, queue, vol=100):
    if chat.id in callsmusic.pytgcalls.active_calls:
        stats = f"🎶 **Player Status for {chat.title}**\n\n"
        stats += f"• **State:** {callsmusic.pytgcalls.active_calls[chat.id].capitalize()}\n"
        if queue and len(queue) > 0:
            stats += f"• **Songs in Queue:** `{len(queue)}`\n"
            stats += f"• **Now Playing:** `{queue[0][0]}`\n"
            req_name = getattr(queue[0][1], 'first_name', 'User')
            stats += f"• **Requested by:** {req_name}\n"
        return stats
    return None


@Client.on_message(filters.command("playlist") & filters.group)
async def playlist(_, message: Message):
    queue = que.get(message.chat.id)
    if not queue:
        await message.reply_text("ℹ️ Player is idle, no songs in playlist.")
        return

    now_playing = queue[0][0]
    by = queue[0][1].first_name if hasattr(queue[0][1], 'first_name') else "User"
    msg = f"🎶 **Now Playing** in **{message.chat.title}**:\n"
    msg += f"• `{now_playing}` | Req by: {by}\n"

    if len(queue) > 1:
        msg += "\n📜 **Upcoming Queue:**\n"
        for idx, song in enumerate(queue[1:], start=1):
            name = song[0]
            usr = song[1].first_name if hasattr(song[1], 'first_name') else "User"
            msg += f"`{idx}.` {name} | {usr}\n"

    await message.reply_text(msg)


@Client.on_message(filters.command("current") & filters.group)
async def current_playing(_, message: Message):
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply_text(stats)
    else:
        await message.reply_text("ℹ️ No active voice chat playback in this chat.")


@Client.on_message(filters.command("player") & filters.group)
@authorized_users_only
async def player_panel(_, message: Message):
    queue = que.get(message.chat.id)
    stats = updated_stats(message.chat, queue)
    if stats:
        await message.reply_text(stats, reply_markup=r_ply())
    else:
        await message.reply_text("ℹ️ No active voice chat playback in this chat.")


@Client.on_callback_query(filters.regex(pattern=r'^(playlist)$'))
async def p_cb(_, cb: CallbackQuery):
    queue = que.get(cb.message.chat.id)
    if not queue:
        await cb.message.edit("ℹ️ Player is idle, no tracks queued.")
        return

    now_playing = queue[0][0]
    by = queue[0][1].first_name if hasattr(queue[0][1], 'first_name') else "User"
    msg = f"🎶 **Now Playing** in **{cb.message.chat.title}**:\n"
    msg += f"• `{now_playing}` | Req by: {by}\n"

    if len(queue) > 1:
        msg += "\n📜 **Queue:**\n"
        for idx, song in enumerate(queue[1:], start=1):
            name = song[0]
            usr = song[1].first_name if hasattr(song[1], 'first_name') else "User"
            msg += f"`{idx}.` {name} | {usr}\n"

    await cb.message.edit(msg, reply_markup=r_ply())


@Client.on_callback_query(filters.regex(pattern=r'^(play|pause|skip|leave|puse|resume|menu|cls)$'))
@cb_admin_check
async def m_cb(_, cb: CallbackQuery):
    chat_id = cb.message.chat.id
    type_ = cb.matches[0].group(1)
    queue = que.get(chat_id)

    if type_ in ('pause', 'puse'):
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Voice chat is not active!", show_alert=True)
        elif callsmusic.pytgcalls.active_calls.get(chat_id) == 'paused':
            await cb.answer("Already paused!", show_alert=True)
        else:
            await callsmusic.pytgcalls.pause_stream(chat_id)
            await cb.answer("⏸ Paused!")
            stats = updated_stats(cb.message.chat, queue)
            if stats:
                await cb.message.edit(stats, reply_markup=r_ply())

    elif type_ in ('play', 'resume'):
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Voice chat is not active!", show_alert=True)
        elif callsmusic.pytgcalls.active_calls.get(chat_id) == 'playing':
            await cb.answer("Already playing!", show_alert=True)
        else:
            await callsmusic.pytgcalls.resume_stream(chat_id)
            await cb.answer("▶️ Resumed!")
            stats = updated_stats(cb.message.chat, queue)
            if stats:
                await cb.message.edit(stats, reply_markup=r_ply())

    elif type_ == 'cls':
        await cb.answer("Closed")
        await cb.message.delete()

    elif type_ == 'menu':
        stats = updated_stats(cb.message.chat, queue)
        if stats:
            await cb.message.edit(stats, reply_markup=r_ply())
        else:
            await cb.answer("No active playback!", show_alert=True)

    elif type_ == 'skip':
        if chat_id not in callsmusic.pytgcalls.active_calls:
            await cb.answer("Nothing is playing to skip!", show_alert=True)
            return

        callsmusic.queues.task_done(chat_id)
        skipped_name = None
        if queue:
            skipped_item = queue.pop(0)
            skipped_name = skipped_item[0]

        if callsmusic.queues.is_empty(chat_id):
            await callsmusic.pytgcalls.leave_group_call(chat_id)
            await cb.answer("Queue finished, left voice chat.")
            await cb.message.edit("⏹ No more tracks in playlist. Leaving Voice Chat!")
        else:
            next_track = callsmusic.queues.get(chat_id)
            if next_track and "file" in next_track:
                await callsmusic.pytgcalls.change_stream(chat_id, next_track["file"])
                await cb.answer("Skipped track!")
                now_name = queue[0][0] if queue else "Next song"
                await cb.message.edit(f"⏭ Skipped: **{skipped_name or 'track'}**\n▶️ Now Playing: **{now_name}**", reply_markup=r_ply())

    elif type_ == 'leave':
        if chat_id in callsmusic.pytgcalls.active_calls:
            try:
                callsmusic.queues.clear(chat_id)
            except Exception:
                pass
            if chat_id in que:
                que[chat_id] = []
            await callsmusic.pytgcalls.leave_group_call(chat_id)
            await cb.answer("Stopped playback!")
            await cb.message.edit("❌ Successfully stopped playback and left the voice chat.")
        else:
            await cb.answer("Not currently in voice chat!", show_alert=True)


async def ensure_userbot_in_chat(client: Client, message: Message, status_msg: Message) -> bool:
    chat_id = message.chat.id
    if not getattr(USER, "is_connected", False):
        await status_msg.edit(
            "❌ **Assistant account is not connected!**\n\n"
            "Voice chat playback requires an assistant user account session.\n"
            "Please generate your session string with `python3 str.py` and set `SESSION_NAME` in `.env`."
        )
        return False

    try:
        user = await USER.get_me()
        user_id = user.id
    except Exception as e:
        print(f"Assistant get_me error: {e}")
        await status_msg.edit("❌ Assistant account is not connected. Please check SESSION_NAME.")
        return False

    try:
        await client.get_chat_member(chat_id, user_id)
        return True
    except Exception:
        try:
            invite_link = await client.export_chat_invite_link(chat_id)
            await USER.join_chat(invite_link)
            return True
        except UserAlreadyParticipant:
            return True
        except Exception as e:
            print(f"Auto-join assistant error: {e}")
            await status_msg.edit(
                f"❌ Assistant `{user.first_name}` could not join this group automatically.\n\n"
                f"Please add the assistant userbot to this group manually and grant permission to join voice chats."
            )
            return False


@Client.on_message(command("play") & other_filters)
async def play(client: Client, message: Message):
    global que
    chat_id = message.chat.id
    lel = await message.reply("🔄 **Processing request...**")

    if not await ensure_userbot_in_chat(client, message, lel):
        return

    replied = message.reply_to_message
    file_path = None
    title = None
    duration = "0:0"
    views = "Telegram Audio"
    thumbnail_url = None

    if replied and (replied.audio or replied.voice):
        media = replied.audio or replied.voice
        title = getattr(media, 'title', None) or getattr(media, 'file_name', None) or "Telegram Audio"
        dur_sec = getattr(media, 'duration', 0)
        duration = f"{dur_sec // 60}:{dur_sec % 60:02d}"
        await lel.edit("⬇️ **Downloading Telegram audio...**")
        downloaded = await replied.download()
        file_path = await converter.convert(downloaded)
    else:
        if len(message.command) < 2:
            await lel.edit(
                "ℹ️ **Usage:** `/play <song name or YouTube link>`\n"
                "Or reply to an audio / voice message with `/play`."
            )
            return

        query = " ".join(message.command[1:]).strip()
        await lel.edit("🔍 **Searching on YouTube...**")

        try:
            results = YoutubeSearch(query, max_results=1).to_dict()
            if not results:
                await lel.edit("❌ Song not found. Try another search term.")
                return

            url = f"https://youtube.com{results[0]['url_suffix']}"
            title = results[0].get("title", query)[:50]
            thumbnail_url = results[0].get("thumbnails", [None])[0]
            duration = results[0].get("duration", "N/A")
            views = results[0].get("views", "N/A")

            await lel.edit("⬇️ **Downloading and converting...**")
            downloaded_raw = youtube.download(url)
            file_path = await converter.convert(downloaded_raw)
        except Exception as e:
            await lel.edit(f"❌ Failed to fetch track: {e}")
            print(f"Error in play handler: {e}")
            return

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                InlineKeyboardButton('🎛 Player', callback_data='menu')
            ],
            [
                InlineKeyboardButton('❌ Close', callback_data='cls')
            ]
        ]
    )

    requested_by = message.from_user.first_name if message.from_user else "User"
    cover_img = await generate_cover(requested_by, title, views, duration, thumbnail_url)

    if chat_id in callsmusic.pytgcalls.active_calls:
        position = await queues.put(chat_id, file=file_path)
        if chat_id not in que:
            que[chat_id] = []
        que[chat_id].append([title, message.from_user, file_path])

        caption = f"#️⃣ Queued at position **#{position}**!\n🎵 **{title}**"
        if cover_img and os.path.exists(cover_img):
            await message.reply_photo(photo=cover_img, caption=caption, reply_markup=keyboard)
        else:
            await message.reply_text(caption, reply_markup=keyboard)
        await lel.delete()
    else:
        que[chat_id] = []
        que[chat_id].append([title, message.from_user, file_path])
        await queues.put(chat_id, file=file_path)

        try:
            await callsmusic.pytgcalls.join_group_call(chat_id, file_path)
        except Exception as e:
            await lel.edit(f"❌ Could not join voice chat: {e}\nMake sure group video chat / voice chat is started!")
            que.pop(chat_id, None)
            return

        caption = f"▶️ **Now Playing:** `{title}`\nRequested by: {requested_by}"
        if cover_img and os.path.exists(cover_img):
            await message.reply_photo(photo=cover_img, caption=caption, reply_markup=keyboard)
        else:
            await message.reply_text(caption, reply_markup=keyboard)
        await lel.delete()

    if cover_img and cover_img.startswith("downloads/cover_") and os.path.exists(cover_img):
        try:
            os.remove(cover_img)
        except Exception:
            pass


@Client.on_message(filters.command("dplay") & filters.group)
async def deezer_play(client: Client, message: Message):
    global que
    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply_text("❗ Usage: `/dplay <song name>`")
        return

    lel = await message.reply("🔄 **Searching on Deezer...**")
    if not await ensure_userbot_in_chat(client, message, lel):
        return

    query = " ".join(message.command[1:]).strip()
    try:
        api_url = f"https://api.deezer.com/search?q={quote_plus(query)}"
        async with aiohttp.ClientSession() as session:
            async with session.get(api_url, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                data = await resp.json(content_type=None)

        tracks = data.get("data", [])
        if not tracks:
            await lel.edit("❌ No songs found on Deezer!")
            return

        track = tracks[0]
        title = track.get("title", query)
        artist = track.get("artist", {}).get("name", "Unknown Artist")
        preview = track.get("preview")

        await lel.edit(f"⬇️ **Downloading `{title}`...**")
        file_path = None
        if preview:
            temp_mp3 = f"downloads/deez_{uuid.uuid4().hex[:8]}.mp3"
            os.makedirs("downloads", exist_ok=True)
            async with aiohttp.ClientSession() as session:
                async with session.get(preview) as resp:
                    if resp.status == 200:
                        async with aiofiles.open(temp_mp3, mode='wb') as f:
                            await f.write(await resp.read())
            file_path = await converter.convert(temp_mp3)
        else:
            results = YoutubeSearch(f"{title} {artist}", max_results=1).to_dict()
            if results:
                url = f"https://youtube.com{results[0]['url_suffix']}"
                file_path = await converter.convert(youtube.download(url))

        if not file_path:
            await lel.edit("❌ Could not download track audio.")
            return

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                    InlineKeyboardButton('🎛 Player', callback_data='menu')
                ],
                [
                    InlineKeyboardButton('❌ Close', callback_data='cls')
                ]
            ]
        )

        requested_by = message.from_user.first_name if message.from_user else "User"
        if chat_id in callsmusic.pytgcalls.active_calls:
            position = await queues.put(chat_id, file=file_path)
            if chat_id not in que:
                que[chat_id] = []
            que[chat_id].append([title, message.from_user, file_path])
            await lel.edit(f"#️⃣ Queued at position **#{position}**!\n🎵 **{title}** by {artist}", reply_markup=keyboard)
        else:
            que[chat_id] = []
            que[chat_id].append([title, message.from_user, file_path])
            await queues.put(chat_id, file=file_path)
            await callsmusic.pytgcalls.join_group_call(chat_id, file_path)
            await lel.edit(f"▶️ **Now Playing (Deezer):** `{title}` - {artist}", reply_markup=keyboard)
    except Exception as e:
        await lel.edit(f"❌ Error: {e}")


from optimized_wynk_engine import wynk_engine


@Client.on_message(filters.command(["wplay", "wynk", "splay"]) & filters.group)
async def wynk_play(client: Client, message: Message):
    global que
    chat_id = message.chat.id
    if len(message.command) < 2:
        await message.reply_text("❗ Usage: `/wplay <song name>`")
        return

    lel = await message.reply("🔄 **Searching on Wynk Music...**")
    if not await ensure_userbot_in_chat(client, message, lel):
        return

    query = " ".join(message.command[1:]).strip()
    try:
        await lel.edit(f"⬇️ **Fetching & streaming `{query}` via Wynk Engine...**")
        raw_track_path, track_title = await wynk_engine.get_track(query)
        file_path = await converter.convert(raw_track_path)

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton('📖 Playlist', callback_data='playlist'),
                    InlineKeyboardButton('🎛 Player', callback_data='menu')
                ],
                [
                    InlineKeyboardButton('❌ Close', callback_data='cls')
                ]
            ]
        )

        requested_by = message.from_user.first_name if message.from_user else "User"
        if chat_id in callsmusic.pytgcalls.active_calls:
            position = await queues.put(chat_id, file=file_path)
            if chat_id not in que:
                que[chat_id] = []
            que[chat_id].append([track_title, message.from_user, file_path])
            await lel.edit(f"#️⃣ Queued at position **#{position}**!\n🎵 **{track_title}**", reply_markup=keyboard)
        else:
            que[chat_id] = []
            que[chat_id].append([track_title, message.from_user, file_path])
            await queues.put(chat_id, file=file_path)
            await callsmusic.pytgcalls.join_group_call(chat_id, file_path)
            await lel.edit(f"▶️ **Now Playing (Wynk):** `{track_title}`", reply_markup=keyboard)
    except Exception as e:
        await lel.edit(f"❌ Error: {e}")
