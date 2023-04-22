import os
import logging
from logging import getLogger, Logger, Formatter, StreamHandler
from logging.handlers import RotatingFileHandler


def get_lumberjack(
    name: str,
    file_level=logging.DEBUG,
    console_level=logging.INFO
) -> Logger:
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logger = getLogger(name)
    if not logger.propagate:
        return logger

    # Configure the logger
    logger.propagate = False
    logger.setLevel(file_level)

    # custom formatter
    formatter = Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # console handler
    ch = StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(formatter)

    # file handler
    fh = RotatingFileHandler(
        filename=f'logs/{name}.log',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
        encoding='utf-8',
        mode='a'
    )
    fh.setLevel(file_level)
    fh.setFormatter(formatter)

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
