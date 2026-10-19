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
from callsmusic.callsmusic import client as USER
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import UserAlreadyParticipant
from helpers.decorators import errors, authorized_users_only


@Client.on_message(filters.group & filters.command(["userbotjoin"]))
@authorized_users_only
@errors
async def addchannel(client: Client, message: Message):
    chid = message.chat.id
    try:
        invitelink = await client.export_chat_invite_link(chid)
    except Exception:
        await message.reply_text(
            "<b>❌ Please promote me as an administrator of this group with 'Invite Users via Link' permission first!</b>",
        )
        return

    first_name = "Assistant"
    try:
        user = await USER.get_me()
        first_name = user.first_name or "Assistant"
    except Exception:
        pass

    try:
        await USER.join_chat(invitelink)
        await USER.send_message(message.chat.id, "I joined here as you requested! Ready to play music.")
        await message.reply_text(f"<b>✅ {first_name} joined your chat successfully!</b>")
    except UserAlreadyParticipant:
        await message.reply_text(f"<b>ℹ️ {first_name} is already in your chat!</b>")
    except Exception as e:
        print(f"Error userbot joining: {e}")
        await message.reply_text(
            f"<b>🛑 Could not join automatically:</b> `{e}`\n\n"
            f"Please add the assistant account manually to this group and try again."
        )


@Client.on_message(filters.group & filters.command(["userbotleave"]))
@authorized_users_only
@errors
async def bot_rem(client: Client, message: Message):
    try:
        await USER.leave_chat(message.chat.id)
        await message.reply_text("<b>👋 Assistant userbot has left the chat!</b>")
    except Exception as e:
        await message.reply_text(f"<b>❌ Could not leave:</b> `{e}`\nPlease remove the assistant manually.")


@USER.on_message(filters.group & filters.command(["userbotleave"]))
async def rem(client: Client, message: Message):
    try:
        await client.leave_chat(message.chat.id)
    except Exception:
        pass
