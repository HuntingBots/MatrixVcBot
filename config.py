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
from os import getenv
from dotenv import load_dotenv

load_dotenv()

que = {}
admins = {}

SESSION_NAME = getenv("SESSION_NAME", "session")
BOT_TOKEN = getenv("BOT_TOKEN", "")
BOT_NAME = getenv("BOT_NAME", "Matrix VC Bot")

raw_api_id = getenv("API_ID", "")
API_ID = int(raw_api_id) if raw_api_id.strip().isdigit() else 0

API_HASH = getenv("API_HASH", "")

raw_limit = getenv("DURATION_LIMIT", "15")
DURATION_LIMIT = int(raw_limit) if raw_limit.strip().isdigit() else 15

COMMAND_PREFIXES = list(getenv("COMMAND_PREFIXES", "/ !").split())

sudo_env = getenv("SUDO_USERS", "")
SUDO_USERS = [int(x) for x in sudo_env.split() if x.strip().isdigit()]
