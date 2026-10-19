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
from typing import List
from pyrogram.types import Chat
from pyrogram.enums import ChatMembersFilter
import cache.admins


async def get_administrators(chat: Chat) -> List[int]:
    cached = cache.admins.get(chat.id)
    if cached is not False and cached is not None:
        return cached

    to_set = []
    client = getattr(chat, "_client", None)
    if client:
        try:
            async for member in client.get_chat_members(chat.id, filter=ChatMembersFilter.ADMINISTRATORS):
                if member.user:
                    to_set.append(member.user.id)
        except Exception as e:
            print(f"Error fetching administrators for chat {chat.id}: {e}")

    cache.admins.set(chat.id, to_set)
    return to_set
