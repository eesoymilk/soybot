import asyncio
import logging
import config

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from utils import get_lumberjack
from bot import eeSoybot

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
logger = get_lumberjack(name='discord')
logging.getLogger('discord.http').setLevel(logging.INFO)


async def main():
    motor_client = AsyncIOMotorClient(config.mongodb_connection_str)
    async with eeSoybot() as bot:
        bot.db: AsyncIOMotorDatabase = motor_client.eesoybot
        await bot.start(config.token)

if __name__ == '__main__':
    asyncio.run(main())
