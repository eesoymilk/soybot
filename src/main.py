import asyncio
from pathlib import Path
import discord
import logging
import logging.handlers
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
    # test_guild=discord.Object(Config.guilds['debug'].id),
    # nthu_guild=discord.Object(Config.guilds['nthu'].id),
    # my_guild=discord.Object(Config.guilds['trap_lovers'].id),
    command_prefix='!',
    intents=discord.Intents.all(),
)


async def main():
    exts = [f'extensions.{p.stem}'
            for p in Path('./src/extensions').glob('*.py')
            if p.stem != '__init__']
    await asyncio.gather(*[bot.load_extension(ext) for ext in exts])
    async with bot:
        await bot.start(Config.TOKEN)

asyncio.run(main())
