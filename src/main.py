import asyncio
import os
import discord
import logging
import logging.handlers
from pathlib import Path
from dotenv import load_dotenv
from utils import Config
from utils import get_lumberjack
from eeSoybot import eeSoybot

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
logger = get_lumberjack(name='discord')
logging.getLogger('discord.http').setLevel(logging.INFO)

# bot instance
bot = eeSoybot(
    owner_id=Config.users['soymilk'].id,
    command_prefix='!',
    case_insensitive=True,
    intents=discord.Intents.all(),
)


async def main():
    exts = [f'extensions.{p.stem}'
            for p in Path('./src/extensions').glob('*.py')
            if p.stem != '__init__']
    await asyncio.gather(*[bot.load_extension(ext) for ext in exts])
    async with bot:
        load_dotenv()
        TOKEN = os.environ.get('TOKEN')
        await bot.start(TOKEN)

asyncio.run(main())
