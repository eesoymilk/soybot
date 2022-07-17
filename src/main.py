import discord
import logging
import logging.handlers
import os

from dotenv import load_dotenv
from utils.config import *
from utils.eeSoybot import eeSoybot
from utils.lumberjack import get_lumberjack


# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
logger = get_lumberjack(name='discord')
logging.getLogger('discord.http').setLevel(logging.INFO)

bot = eeSoybot(
    command_prefix='?',
    intents=discord.Intents.all(),
)

load_dotenv()
bot.run(os.environ.get('TOKEN'), log_handler=None)

# async def main():
#     async with bot:
#         await bot.start(TOKEN)

# asyncio.run(main())
