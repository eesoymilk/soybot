import asyncio
import discord
import logging
import logging.handlers
from cogs import Listeners
from cogs import SoyCommands
from utils import Config
from utils import eeSoybot
from utils import get_lumberjack

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
logger = get_lumberjack(name='discord')
logging.getLogger('discord.http').setLevel(logging.INFO)

# bot instance
bot = eeSoybot(
    command_prefix='?',
    intents=discord.Intents.all(),
)


async def main():
    async with bot:
        await asyncio.gather(
            bot.add_cog(Listeners(bot)),
            bot.add_cog(SoyCommands(bot))
        )
        await bot.start(Config.TOKEN)

asyncio.run(main())
