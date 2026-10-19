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
from asyncio.queues import QueueEmpty
from cache.admins import set as set_cached_admins
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.enums import ChatMembersFilter
from callsmusic import callsmusic
from helpers.filters import command, other_filters
from helpers.decorators import errors, authorized_users_only
from config import que, admins as a


@Client.on_message(filters.command('adminreset') & filters.group)
@errors
@authorized_users_only
async def update_admin(client: Client, message: Message):
    global a
    new_ads = []
    async for u in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        if u.user:
            new_ads.append(u.user.id)
    a[message.chat.id] = new_ads
    set_cached_admins(message.chat.id, new_ads)
    await message.reply_text('Successfully updated admin list in **{}**'.format(message.chat.title))


@Client.on_message(command("pause") & other_filters)
@errors
@authorized_users_only
async def pause(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == 'paused'
    ):
        await message.reply_text("❗ Nothing is playing!")
    else:
        await callsmusic.pytgcalls.pause_stream(message.chat.id)
        await message.reply_text("⏸ Paused!")


@Client.on_message(command("resume") & other_filters)
@errors
@authorized_users_only
async def resume(_, message: Message):
    if (
            message.chat.id not in callsmusic.pytgcalls.active_calls
    ) or (
            callsmusic.pytgcalls.active_calls[message.chat.id] == 'playing'
    ):
        await message.reply_text("❗ Nothing is paused!")
    else:
        await callsmusic.pytgcalls.resume_stream(message.chat.id)
        await message.reply_text("▶️ Resumed!")


@Client.on_message(command("end") & other_filters)
@errors
@authorized_users_only
async def stop(_, message: Message):
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ Nothing is streaming!")
    else:
        try:
            callsmusic.queues.clear(message.chat.id)
        except QueueEmpty:
            pass

        if message.chat.id in que:
            que[message.chat.id] = []

        await callsmusic.pytgcalls.leave_group_call(message.chat.id)
        await message.reply_text("❌ Stopped streaming!")


@Client.on_message(command("skip") & other_filters)
@errors
@authorized_users_only
async def skip(_, message: Message):
    global que
    if message.chat.id not in callsmusic.pytgcalls.active_calls:
        await message.reply_text("❗ Nothing is playing to skip!")
        return

    callsmusic.queues.task_done(message.chat.id)

    qeue = que.get(message.chat.id)
    skipped_title = None
    if qeue:
        skipped_item = qeue.pop(0)
        skipped_title = skipped_item[0]

    if callsmusic.queues.is_empty(message.chat.id):
        await callsmusic.pytgcalls.leave_group_call(message.chat.id)
        msg = "- No more tracks in queue!\n- Leaving Voice Chat."
        if skipped_title:
            msg = f"- Skipped **{skipped_title}**\n" + msg
        await message.reply_text(msg)
    else:
        next_track = callsmusic.queues.get(message.chat.id)
        if next_track and "file" in next_track:
            await callsmusic.pytgcalls.change_stream(
                message.chat.id,
                next_track["file"]
            )
            now_playing = qeue[0][0] if qeue else "Next Song"
            await message.reply_text(f"- Skipped **{skipped_title or 'track'}**\n- Now Playing: **{now_playing}**")


@Client.on_message(filters.command("admincache") & filters.group)
@errors
@authorized_users_only
async def admincache(client: Client, message: Message):
    new_ads = []
    async for u in client.get_chat_members(message.chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
        if u.user:
            new_ads.append(u.user.id)
    a[message.chat.id] = new_ads
    set_cached_admins(message.chat.id, new_ads)
    await message.reply_text("❇️ Admin cache refreshed!")
