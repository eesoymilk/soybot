import os
import argparse
import asyncio
import logging

from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

from dotenv import load_dotenv
from utils import get_lumberjack
from bot import Soybot

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
log = get_lumberjack(__name__)
logging.getLogger('discord.http').setLevel(logging.INFO)


class EnvironmentChoices:
    dev = ('dev', 'development')
    prod = ('prod', 'production')
    docker = ('docker',)

    @classmethod
    def all(cls):
        return cls.dev + cls.prod + cls.docker


def load_enviorment(e: str):
    if e in EnvironmentChoices.dev:
        log.info('Running in development mode')
        load_dotenv('.env.dev')
    elif e in EnvironmentChoices.prod:
        log.info('Running in production mode')
        load_dotenv('.env')
    elif e in EnvironmentChoices.docker:
        log.info('Running in a docker container')


async def main():
    parser = argparse.ArgumentParser(
        description="Your program's description here"
    )
    parser.add_argument(
        '-e', '--env',
        choices=EnvironmentChoices.all(),
        default='dev',
        required=True,
        help='This option helps load different environment variables.'
             f'Choices are {", ".join(EnvironmentChoices.all())}'
    )
    load_enviorment(parser.parse_args().env)

    motor_client = AsyncIOMotorClient(os.getenv('MONGODB_CONNECTION_STR'))
    async with Soybot() as bot:
        bot.db: AsyncIOMotorDatabase = motor_client.eesoybot
        await bot.start(os.getenv('TOKEN'))


if __name__ == '__main__':
    asyncio.run(main())
