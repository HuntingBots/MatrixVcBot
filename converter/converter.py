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
import asyncio
from helpers.errors import FFmpegReturnCodeError


async def convert(file_path: str) -> str:
    os.makedirs("raw_files", exist_ok=True)
    base_name = os.path.basename(file_path)
    name, _ = os.path.splitext(base_name)
    out = os.path.join("raw_files", f"{name}.raw")

    if os.path.isfile(out):
        return out

    try:
        proc = await asyncio.create_subprocess_exec(
            "ffmpeg",
            "-y",
            "-i",
            file_path,
            "-f",
            "s16le",
            "-ac",
            "1",
            "-ar",
            "48000",
            "-acodec",
            "pcm_s16le",
            out,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        _, stderr = await proc.communicate()

        if proc.returncode != 0:
            err_msg = stderr.decode(errors="replace") if stderr else "Unknown error"
            print(f"FFmpeg conversion failed: {err_msg}")
            raise FFmpegReturnCodeError(f"FFmpeg did not return 0: {err_msg}")

        return out
    except Exception as e:
        if isinstance(e, FFmpegReturnCodeError):
            raise
        print(f"FFmpeg error: {e}")
        raise FFmpegReturnCodeError(str(e))
