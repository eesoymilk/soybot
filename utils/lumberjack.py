import os
import logging
from logging import Logger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

from discord.utils import _ColourFormatter


def get_lumberjack(
    name: str,
    file_level=logging.DEBUG,
    console_level=logging.INFO
) -> Logger:
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = logging.getLogger(name)
    if not logger.propagate:
        return logger

    # Configure the logger
    logger.propagate = False
    logger.setLevel(file_level)

    # console handler
    ch = StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(_ColourFormatter())

    # file handler
    fh = RotatingFileHandler(
        filename=f'logs/{name}.log',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
        encoding='utf-8',
        mode='a'
    )
    fh.setLevel(file_level)
    fh.setFormatter(Formatter(
        '[{asctime}] [{levelname:<8}] {name}: {message}',
        '%Y-%m-%d %H:%M:%S',
        style='{'
    ))

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
