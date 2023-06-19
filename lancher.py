import os
import argparse
import asyncio
import logging
import textwrap

import google.cloud.logging as gc_logging
from discord.utils import setup_logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from dotenv import load_dotenv

from utils import get_lumberjack
from bot import Soybot

gc_client = gc_logging.Client()
gc_client.setup_logging()

# Multiple calls to getLogger() with the same name will return a reference to the same logger object.
# Hence, we are just calling the preset loggers in discord.py
log = get_lumberjack(__name__)
logging.getLogger('discord.http').setLevel(logging.WARNING)
setup_logging()


class EnvChoices:
    dev = ('dev', 'development')
    prod = ('prod', 'production')
    docker = ('docker',)

    @classmethod
    def all(cls):
        return cls.dev + cls.prod + cls.docker


def load_enviorment(filename: str):
    if filename is None:
        return

    load_dotenv(filename)


async def main():
    parser_description = textwrap.dedent('''\
        command line arguments for soybot
    ''')
    parser = argparse.ArgumentParser(description=parser_description)

    env_help_text = textwrap.dedent(f'''\
        This option helps load different environment variables.
        Choices are {', '.join(f'"{env}"' for env in EnvChoices.all())}
    ''')
    parser.add_argument(
        '-e', '--env',
        choices=EnvChoices.all(),
        required=True,
        help=env_help_text
    )

    env = parser.parse_args().env
    if env == 'docker':
        env_file = None
        command_prefix = '!'
    elif env == 'gcr':
        env_file = None
        command_prefix = '!'
    elif env in ('prod', 'production'):
        env_file = '.env'
        command_prefix = '!'
    else:
        env_file = f'.env.{env}'
        command_prefix = '?'

    load_enviorment(env_file)

    # motor_client = AsyncIOMotorClient(os.getenv('MONGODB_CONNECTION_STR'))
    async with Soybot(command_prefix=command_prefix) as bot:
        # bot.db: AsyncIOMotorDatabase = motor_client.eesoybot
        await bot.start(os.getenv('TOKEN'))


if __name__ == '__main__':
    asyncio.run(main())
