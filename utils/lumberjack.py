import os
import logging
from logging import Logger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler


class ColorFormatter(Formatter):

    # ANSI codes are a bit weird to decipher if you're unfamiliar with them, so here's a refresher
    # It starts off with a format like \x1b[XXXm where XXX is a semicolon separated list of commands
    # The important ones here relate to colour.
    # 30-37 are black, red, green, yellow, blue, magenta, cyan and white in that order
    # 40-47 are the same except for the background
    # 90-97 are the same but "bright" foreground
    # 100-107 are the same as the bright ones but for the background.
    # 1 means bold, 2 means dim, 0 means reset, and 4 means underline.

    LEVEL_COLOURS = [
        (logging.DEBUG, '\x1b[40;1m'),
        (logging.INFO, '\x1b[34;1m'),
        (logging.WARNING, '\x1b[33;1m'),
        (logging.ERROR, '\x1b[31m'),
        (logging.CRITICAL, '\x1b[41m'),
    ]

    FORMATS = {
        level: logging.Formatter(
            f'\x1b[30;1m%(asctime)s\x1b[0m {colour}%(levelname)-8s\x1b[0m \x1b[35m%(name)s\x1b[0m \x1b[36m%(funcName)s\x1b[0m %(message)s',
            '%Y-%m-%d %H:%M:%S',
        )
        for level, colour in LEVEL_COLOURS
    }

    def format(self, record):
        formatter = self.FORMATS.get(record.levelno)
        if formatter is None:
            formatter = self.FORMATS[logging.DEBUG]

        # Override the traceback to always print in red
        if record.exc_info:
            text = formatter.formatException(record.exc_info)
            record.exc_text = f'\x1b[31m{text}\x1b[0m'

        output = formatter.format(record)

        # Remove the cache layer
        record.exc_text = None
        return output


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
    ch.setFormatter(ColorFormatter())

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
        '[{asctime}] [{levelname:<8}] {name} {funcName}: {message}',
        '%Y-%m-%d %H:%M:%S',
        style='{'
    ))

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
