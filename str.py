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
import asyncio
from pyrogram import Client

print("\n--- Matrix VC Bot Session String Generator ---")
print("Enter your app credentials from https://my.telegram.org/apps below:\n")


async def main():
    api_id_input = input("Enter API_ID: ").strip()
    api_hash_input = input("Enter API_HASH: ").strip()

    if not api_id_input.isdigit() or not api_hash_input:
        print("❌ Invalid API ID or API HASH.")
        return

    async with Client(
        name="session_generator",
        api_id=int(api_id_input),
        api_hash=api_hash_input,
        in_memory=True
    ) as app:
        session_str = await app.export_session_string()
        print("\n" + "=" * 60)
        print("✅ YOUR PYROGRAM SESSION STRING:")
        print(session_str)
        print("=" * 60)
        print("Copy the string above and paste it into your .env file as:")
        print("SESSION_NAME=" + session_str + "\n")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("\nOperation cancelled.")
