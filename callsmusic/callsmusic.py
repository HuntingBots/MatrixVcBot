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
import sqlite3
import asyncio
from pyrogram import Client
from pytgcalls import PyTgCalls, types
import config
from . import queues


def check_session_authorized(session_name: str) -> bool:
    if not session_name or session_name == "session":
        return False
    if len(session_name) > 40:
        return True
    db_file = f"{session_name}.session"
    if os.path.exists(db_file):
        try:
            con = sqlite3.connect(db_file)
            row = con.cursor().execute("SELECT user_id FROM sessions").fetchone()
            con.close()
            if row and row[0] is not None:
                return True
        except Exception:
            return False
    return False


has_session = check_session_authorized(config.SESSION_NAME)

if config.SESSION_NAME and len(config.SESSION_NAME) > 40:
    client = Client(
        name="matrix_vc_user",
        session_string=config.SESSION_NAME,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        in_memory=True
    )
else:
    client = Client(
        name=config.SESSION_NAME or "session",
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        in_memory=True
    )


class PyTgCallsWrapper:
    def __init__(self, raw_app: PyTgCalls):
        self._app = raw_app
        self.active_calls = {}

    def __getattr__(self, name):
        return getattr(self._app, name)

    async def join_group_call(self, chat_id: int, file_path: str):
        stream = types.MediaStream(file_path)
        await self._app.play(
            chat_id,
            stream,
            config=types.GroupCallConfig(auto_start=True)
        )
        self.active_calls[chat_id] = 'playing'

    async def change_stream(self, chat_id: int, file_path: str):
        stream = types.MediaStream(file_path)
        await self._app.play(chat_id, stream)
        self.active_calls[chat_id] = 'playing'

    async def pause_stream(self, chat_id: int):
        await self._app.pause(chat_id)
        self.active_calls[chat_id] = 'paused'

    async def resume_stream(self, chat_id: int):
        await self._app.resume(chat_id)
        self.active_calls[chat_id] = 'playing'

    async def leave_group_call(self, chat_id: int):
        try:
            await self._app.leave_call(chat_id)
        except Exception:
            pass
        self.active_calls.pop(chat_id, None)

    async def start(self):
        if not has_session:
            print("⚠️ No valid SESSION_NAME found. Skipping assistant startup until configured.")
            return
        await self._app.start()

    async def run(self):
        if not has_session:
            return
        await self._app.run()


_raw_pytgcalls = PyTgCalls(client)
pytgcalls = PyTgCallsWrapper(_raw_pytgcalls)


@_raw_pytgcalls.on_update()
async def _on_stream_update(_, update: types.Update):
    if isinstance(update, types.StreamEnded):
        chat_id = update.chat_id
        queues.task_done(chat_id)

        if chat_id in config.que and config.que[chat_id]:
            config.que[chat_id].pop(0)

        if queues.is_empty(chat_id):
            await pytgcalls.leave_group_call(chat_id)
        else:
            next_track = queues.get(chat_id)
            if next_track and "file" in next_track:
                await pytgcalls.change_stream(chat_id, next_track["file"])


run = pytgcalls.run
