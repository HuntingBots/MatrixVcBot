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
from typing import Union

from pyrogram.types import Message, Audio, Voice
from pyrogram.enums import MessageEntityType


def get_url(message_1: Message) -> Union[str, None]:
    messages = [message_1]

    if message_1.reply_to_message:
        messages.append(message_1.reply_to_message)

    for message in messages:
        text = message.text or message.caption or ""
        if message.entities:
            for entity in message.entities:
                if entity.type == MessageEntityType.TEXT_LINK or str(entity.type) in ("text_link", "MessageEntityType.TEXT_LINK"):
                    if entity.url:
                        return entity.url
                elif entity.type == MessageEntityType.URL or str(entity.type) in ("url", "MessageEntityType.URL"):
                    return text[entity.offset:entity.offset + entity.length]

        for word in text.split():
            if word.startswith("http://") or word.startswith("https://"):
                return word

    return None


def get_file_name(audio: Union[Audio, Voice]) -> str:
    if isinstance(audio, Voice):
        return f"{audio.file_unique_id}.ogg"
    ext = "mp3"
    if hasattr(audio, "file_name") and audio.file_name:
        parts = audio.file_name.split(".")
        if len(parts) > 1:
            ext = parts[-1]
    return f"{audio.file_unique_id}.{ext}"
