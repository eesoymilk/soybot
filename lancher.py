import os
import sys
import getopt
import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from dotenv import load_dotenv
from utils import get_lumberjack
from bot import Soybot

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
log = get_lumberjack(name='discord')
logging.getLogger('discord.http').setLevel(logging.INFO)

# TODO: Add usage


def usage():
    ...


async def main(argv: list[str]):
    try:
        opts, args = getopt.getopt(argv, 'hm:', ['--help', 'mode='])
        assert len(opts), 'No options given'
    except (AssertionError, getopt.GetoptError) as e:
        log.error(e)
        usage()

    for o, a in opts:
        if o in ('-h', '--help'):
            usage()

        if o in ('-m', '--mode'):
            if a in ('d', 'dev', 'debug'):
                log.info('Running in development mode')
                load_dotenv('.env.dev')
            elif a in ('p', 'prod'):
                log.info('Running in production mode')
                load_dotenv('.env')
            elif a in ('docker'):
                log.info('Running in a docker container')
            else:
                assert False, f'Unrecognized option: {a}'

    motor_client = AsyncIOMotorClient(os.getenv('MONGODB_CONNECTION_STR'))
    async with Soybot() as bot:
        bot.db: AsyncIOMotorDatabase = motor_client.eesoybot
        await bot.start(os.getenv('TOKEN'))

if __name__ == '__main__':
    asyncio.run(main(sys.argv[1:]))
