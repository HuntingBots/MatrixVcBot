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
from pyrogram.types import ChatMemberUpdated
from pyrogram.enums import ChatMemberStatus
from cache.admins import admins
from pyrogram import Client


@Client.on_chat_member_updated()
async def auto_admin_updater(_, chat_member_updated: ChatMemberUpdated):
    if not chat_member_updated.chat or not chat_member_updated.new_chat_member:
        return

    chat_id = chat_member_updated.chat.id
    if chat_id not in admins:
        admins[chat_id] = []

    new_member = chat_member_updated.new_chat_member
    user = new_member.user
    if not user:
        return

    user_id = user.id
    is_admin = new_member.status in (
        ChatMemberStatus.ADMINISTRATOR,
        ChatMemberStatus.OWNER,
    )

    if is_admin:
        if user_id not in admins[chat_id]:
            admins[chat_id].append(user_id)
    else:
        if user_id in admins[chat_id]:
            admins[chat_id].remove(user_id)
