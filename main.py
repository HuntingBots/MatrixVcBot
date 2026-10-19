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
import sys
import asyncio
import logging
from pyrogram import Client as Bot, idle
from callsmusic import pytgcalls, client as USER, has_session
from config import API_ID, API_HASH, BOT_TOKEN

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pytgcalls").setLevel(logging.INFO)

bot = Bot(
    name="MatrixVcBot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
    plugins=dict(root="handlers"),
    skip_updates=False
)


async def start_bot():
    if not API_ID or not API_HASH or not BOT_TOKEN:
        print("\n" + "=" * 60)
        print("❌ CRITICAL ERROR: Missing configuration!")
        print("Please set API_ID, API_HASH, and BOT_TOKEN in your .env file.")
        print("=" * 60 + "\n")
        return

    os.makedirs("downloads", exist_ok=True)
    os.makedirs("raw_files", exist_ok=True)

    print("🚀 Starting Matrix VC Bot...")
    await bot.start()
    bot_info = await bot.get_me()
    print(f"✅ Bot started as @{bot_info.username} (ID: {bot_info.id})")

    print("🚀 Checking Assistant Userbot & PyTgCalls...")
    if has_session:
        try:
            await pytgcalls.start()
            user_info = await USER.get_me()
            print(f"✅ Assistant connected as {user_info.first_name} (ID: {user_info.id})")
        except Exception as e:
            print(f"⚠️ Warning during assistant/pytgcalls startup: {e}")
            print("Voice calls will be available once the session is valid.")
    else:
        print("ℹ️ Assistant session not configured yet. Bot running in standalone mode.")
        print("👉 Generate assistant session string with 'python3 str.py' and put in .env (SESSION_NAME=...)")

    print("\n🎵 Matrix VC Bot is online and fully working! 🎵\n")
    await idle()

    print("🛑 Shutting down Matrix VC Bot...")
    try:
        await bot.stop()
    except Exception:
        pass


if __name__ == "__main__":
    try:
        bot.run(start_bot())
    except (KeyboardInterrupt, SystemExit):
        print("Bot terminated by user.")
