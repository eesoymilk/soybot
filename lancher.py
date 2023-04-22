import os
import asyncio
import logging

from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from utils import get_lumberjack
from bot import Soybot

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
logger = get_lumberjack(name='discord')
logging.getLogger('discord.http').setLevel(logging.INFO)


async def main():
    motor_client = AsyncIOMotorClient(os.getenv('MONGODB_CONNECTION_STR'))
    async with Soybot() as bot:
        bot.db: AsyncIOMotorDatabase = motor_client.eesoybot
        await bot.start(os.getenv('TOKEN'))

if __name__ == '__main__':
    load_dotenv()
    asyncio.run(main())
