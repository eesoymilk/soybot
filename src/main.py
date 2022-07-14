import discord
import asyncio
import logging
import logging.handlers
import os

from eeSoybot import eeSoybot
from dotenv import load_dotenv
from config import *

logger = logging.getLogger('discord')
logger.setLevel(logging.DEBUG)
logging.getLogger('discord.http').setLevel(logging.INFO)

handler = logging.handlers.RotatingFileHandler(
    filename='discord.log',
    encoding='utf-8',
    maxBytes=32 * 1024 * 1024,  # 32 MiB
    backupCount=5,  # Rotate through 5 files
)
dt_fmt = '%Y/%m/%d %H:%M:%S'
formatter = logging.Formatter(
    '[{asctime}] [{levelname:<8}] {name}: {message}', dt_fmt, style='{')
handler.setFormatter(formatter)
logger.addHandler(handler)


bot = eeSoybot(
    command_prefix='?',
    intents=discord.Intents.all(),
)

load_dotenv()
bot.run(os.environ.get('TOKEN'))

# async def main():
#     async with bot:
#         await bot.start(TOKEN)

# asyncio.run(main())
