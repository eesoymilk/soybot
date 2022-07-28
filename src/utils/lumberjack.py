import logging
import re

loggers_log: set[str] = set()


class ANSI:
    # text colors
    Black = '\u001b[30m'
    Red = '\u001b[31m'
    Green = '\u001b[32m'
    Yellow = '\u001b[33m'
    Blue = '\u001b[34m'
    Magenta = '\u001b[35m'
    Cyan = '\u001b[36m'
    White = '\u001b[37m'
    BrightBlack = '\u001b[30;1m'
    BrightRed = '\u001b[31;1m'
    BrightGreen = '\u001b[32;1m'
    BrightYellow = '\u001b[33;1m'
    BrightBlue = '\u001b[34;1m'
    BrightMagenta = '\u001b[35;1m'
    BrightCyan = '\u001b[36;1m'
    BrightWhite = '\u001b[37;1m'

    # background colors
    BackgroundBlack = '\u001b[40m'
    BackgroundRed = '\u001b[41m'
    BackgroundGreen = '\u001b[42m'
    BackgroundYellow = '\u001b[43m'
    BackgroundBlue = '\u001b[44m'
    BackgroundMagenta = '\u001b[45m'
    BackgroundCyan = '\u001b[46m'
    BackgroundWhite = '\u001b[47m'
    BackgroundBrightBlack = '\u001b[40;1m'
    BackgroundBrightRed = '\u001b[41;1m'
    BackgroundBrightGreen = '\u001b[42;1m'
    BackgroundBrightYellow = '\u001b[43;1m'
    BackgroundBrightBlue = '\u001b[44;1m'
    BackgroundBrightMagenta = '\u001b[45;1m'
    BackgroundBrightCyan = '\u001b[46;1m'
    BackgroundBrightWhite = '\u001b[47;1m'

    # text decorations
    Bold = '\u001b[1m'
    Underline = '\u001b[4m'
    Reversed = '\u001b[7m'

    # reset
    Reset = '\u001b[0m'


class RichLoggingFormat(logging.Formatter):

    Level_Rich_Formats = {
        logging.NOTSET: (ANSI.BackgroundBlack, ANSI.BrightBlack),
        logging.DEBUG: (ANSI.BackgroundGreen, ANSI.BrightBlack),
        logging.INFO: (ANSI.BackgroundBlue, ANSI.BrightBlack),
        logging.WARNING: (ANSI.BackgroundYellow, ANSI.BrightBlack),
        logging.ERROR: (ANSI.BackgroundRed, ANSI.BrightBlack),
        logging.CRITICAL: (ANSI.BackgroundRed, ANSI.BrightBlack),
    }

    def __init__(self, name_color=ANSI.Green, is_console=False):
        self.name_color = name_color
        self.is_console = is_console

    def format(self, record: logging.LogRecord):
        asctime_rich = '{asctime}'
        level_rich = '{levelname:<8}'
        name_rich = '{name}'
        funcName_rich = ''
        message_rich = '{message}'

        if record.name in ['Listeners', 'SoyCommands']:
            funcName_rich = ' {funcName}'
            record.funcName = record.funcName.lstrip('on_')

        if self.is_console:
            level_bg, level_color = self.Level_Rich_Formats[record.levelno]
            asctime_rich = f'{ANSI.BrightBlack}{asctime_rich}{ANSI.Reset}'
            level_rich = f'{level_bg}{level_color}{level_rich}{ANSI.Reset}'
            name_rich = f'{self.name_color}{name_rich}'
            message_rich = f'{ANSI.Reset}{message_rich}'
        else:   # get rid of ANSI charaters
            record.msg = re.sub(r'\u001b\[\d\d?(;\d)?m', '', record.msg)

        rich_format = f'{asctime_rich} {level_rich} {name_rich}{funcName_rich} | {message_rich}'
        date_format = '%Y-%m-%d %H:%M:%S'
        super().__init__(rich_format, date_format, '{')
        return super().format(record)


def get_lumberjack(
        name: str,
        name_color=ANSI.BrightBlue,
        file_level=logging.DEBUG,
        console_level=logging.INFO
) -> logging.Logger:
    logger = logging.getLogger(name)

    if name in loggers_log:
        return logger

    loggers_log.add(name)
    logger.setLevel(file_level)

    # console handler
    ch = logging.StreamHandler()
    ch.setLevel(console_level)
    ch.setFormatter(RichLoggingFormat(name_color=name_color, is_console=True))

    # file handler
    fh = logging.handlers.RotatingFileHandler(
        filename=f'logs\\{name}.log',
        maxBytes=32 * 1024 * 1024,  # 32 MiB
        backupCount=5,  # Rotate through 5 files
        encoding='utf-8',
        mode='a'
    )
    fh.setFormatter(RichLoggingFormat())

    logger.addHandler(ch)
    logger.addHandler(fh)

    return logger
