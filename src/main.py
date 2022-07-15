import discord
import os

from eeSoybot import eeSoybot
from dotenv import load_dotenv
from config import *


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
