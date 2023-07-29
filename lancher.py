import os
import argparse
import asyncio
import logging
import textwrap

from discord.utils import setup_logging
from dotenv import load_dotenv

from utils import get_lumberjack
from bot import Soybot

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
    elif env in ('prod', 'production'):
        env_file = '.env'
        command_prefix = '!'
    else:
        env_file = f'.env.{env}'
        command_prefix = '?'

    load_enviorment(env_file)

    async with Soybot(command_prefix=command_prefix) as bot:
        await bot.start(os.getenv('TOKEN'))


if __name__ == '__main__':
    asyncio.run(main())
