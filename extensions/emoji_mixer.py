import json
import random
from typing import Optional

from discord import app_commands, Interaction
from discord.ext.commands import Bot
from discord.interactions import Interaction

from utils import get_lumberjack, EmojiKitchen

log = get_lumberjack(__name__)


def emoji_to_unicode(emoji: str, sep: str = '-'):
    """Convert a emoji in string to unicode string 
    and check if it's supported by Emoji Kitchen."""
    code = sep.join([(f'{ord(c):X}') for c in emoji]).lower()
    if code not in EmojiKitchen.SUPPORTED_EMOJIS:
        raise ValueError(f'{emoji} is not a supported emoji.')
    return code


def prefix_unicode(code: str, prefix: str = 'u', sep: str = '-'):
    """Prefix unicode parts widockth 'u'."""
    return sep.join(f'{prefix}{part}' for part in code.split(sep))


def find_output(entries: list[dict], code1: str, code2: str):
    """Find the emoji output from the provided codes in emojiOutput.json."""
    if code2 is None:
        return random.choice(entries)

    if code1 == code2:
        return next((
            entry for entry in entries
            if entry['leftEmoji'] == code1 and entry['rightEmoji'] == code1
        ))

    return next((
        entry for entry in entries
        if code2 in (entry['leftEmoji'], entry['rightEmoji'])
    ))


@app_commands.command(name='emoji_kitchen', description='Mix emojis together!')
@app_commands.describe(
    emoji1='Enter 1 unicode emoji',
    emoji2='Enter 1 unicode emoji (random if left empty)'
)
@app_commands.rename(emoji1='first_emoji', emoji2='second_emoji')
async def emoji_mixer(
    intx: Interaction,
    emoji1: str,
    emoji2: Optional[str] = None
):
    """App command that mixes the provided emojis together."""
    try:
        code1 = emoji_to_unicode(emoji1)
        code2 = emoji_to_unicode(emoji2) if emoji2 is not None else None
        output = find_output(intx.client.emoji_kitchen[code1], code1, code2)

        left_emoji, right_emoji, date = output.values()
        left_emoji = prefix_unicode(left_emoji)
        right_emoji = prefix_unicode(right_emoji)
        output_url = f'{EmojiKitchen.ROOT_URL}/{date}/{left_emoji}/{left_emoji}_{right_emoji}.png'

        await intx.response.send_message(output_url)

    except (ValueError, StopIteration) as e:
        if isinstance(e, StopIteration):
            msg = f'Failed to combine {emoji1} with {emoji2}.'
        else:
            msg = str(e)

        await intx.response.send_message(
            f'{msg}\n' +
            'Please refer to https://emojikitchen.dev/ for all combinations.',
            ephemeral=True
        )

    log.info(' | '.join([
        f'{intx.user}',
        f'{intx.guild}',
        f'{intx.channel}',
        f'{emoji1=}',
        f'{emoji2=}'
    ]))


async def setup(bot: Bot) -> None:
    with open('./assets/emojiOutput.json') as f:
        bot.emoji_kitchen = json.load(f)
        log.info(f'emojiOutput.json loaded')

    bot.tree.add_command(emoji_mixer)
    log.info(f'{__name__} loaded')
