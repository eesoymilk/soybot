import json
import random
from typing import Optional
from urllib.parse import urljoin

from discord import app_commands as ac, Interaction
from discord.ext.commands import Cog, Bot
from discord.interactions import Interaction

from utils import get_lumberjack, cd_but_soymilk, EmojiKitchen

log = get_lumberjack(__name__)


def emoji_to_unicode(*emojis: str, sep: str = '-') -> tuple[Optional[str]]:
    """Convert a emoji in string to unicode string 
    and check if it's supported by Emoji Kitchen."""
    res: list[Optional[str]] = []
    for emoji in emojis:
        if emoji is None:
            res.append(None)
            continue
        code = sep.join([(f'{ord(c):X}') for c in emoji]).lower()
        if code not in EmojiKitchen.SUPPORTED_EMOJIS:
            raise ValueError(f'{emoji} is not a supported emoji.')
        res.append(code)
    return tuple(res)


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


class EmojiKitchenCog(Cog):

    def __init__(self, bot: Bot):
        self.bot = bot

        with open(EmojiKitchen.OUTPUT_PATH) as f:
            self.outputs = json.load(f)
            log.info(f'{f.name} loaded')

    def cog_unload(self):
        del self.outputs

    @ac.command()
    @ac.describe(emoji1='emoji1', emoji2='emoji2')
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def emoji_kitchen(
        self,
        intx: Interaction,
        emoji1: str,
        emoji2: Optional[str] = None
    ):
        """App command that mixes the provided emojis together."""
        await intx.response.defer(thinking=True)

        try:
            code1, code2 = emoji_to_unicode(emoji1, emoji2)
            # code2 = emoji_to_unicode(emoji2) if emoji2 is not None else None
            output = find_output(self.outputs[code1], code1, code2)

            left_emoji, right_emoji, date = output.values()
            left_emoji = prefix_unicode(left_emoji)
            right_emoji = prefix_unicode(right_emoji)
            path = f'{date}/{left_emoji}/{left_emoji}_{right_emoji}.png'
            output_url = urljoin(EmojiKitchen.ROOT_URL, path)

            await intx.followup.send(output_url)

        except (ValueError, StopIteration) as e:
            if isinstance(e, StopIteration):
                msg = f'Failed to combine {emoji1} with {emoji2}.'
            else:
                msg = str(e)

            await intx.followup.send(
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


async def setup(bot: Bot):
    await bot.add_cog(EmojiKitchenCog(bot))
