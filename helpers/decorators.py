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
from typing import Callable
from functools import wraps

from pyrogram import Client
from pyrogram.types import Message

from helpers.admins import get_administrators
from config import SUDO_USERS


def errors(func: Callable) -> Callable:
    @wraps(func)
    async def decorator(client: Client, message: Message, *args, **kwargs):
        try:
            return await func(client, message, *args, **kwargs)
        except Exception as e:
            await message.reply(f"{type(e).__name__}: {e}")

    return decorator


def authorized_users_only(func: Callable) -> Callable:
    @wraps(func)
    async def decorator(client: Client, message: Message, *args, **kwargs):
        if message.from_user:
            user_id = message.from_user.id
            if user_id in SUDO_USERS:
                return await func(client, message, *args, **kwargs)

            administrators = await get_administrators(message.chat)
            if user_id in administrators:
                return await func(client, message, *args, **kwargs)
        elif message.sender_chat and message.sender_chat.id == message.chat.id:
            return await func(client, message, *args, **kwargs)

    return decorator
