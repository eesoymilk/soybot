import json
import random
from typing import Optional
from urllib.parse import urljoin

from emoji import emoji_list
from discord import app_commands as ac, Interaction
from discord.app_commands import Transformer, Transform, Range
from discord.ext.commands import Cog, Bot

from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)


class UnicodeEmoji:
    __slots__ = ('emoji', 'unicode', 'prefixed')

    def __init__(
        self,
        emoji: str,
        unicode: Optional[str] = None,
        prefixed: Optional[str] = None
    ):
        self.emoji = emoji
        self.unicode = '-'.join(
            [f'{ord(c):X}' for c in emoji]
        ).lower() if unicode is None else unicode
        self.prefixed = '-'.join(
            f'u{part}' for part in self.unicode.split('-')
        ) if prefixed is None else prefixed

    @staticmethod
    def from_unicode(unicode: str):
        emoji = ''.join(chr(int(part, 16)) for part in unicode.split('-'))
        return UnicodeEmoji(emoji, unicode)

    def __repr__(self):
        return f'{self.__class__.__name__}({self.emoji})'


class UnicodeEmojiTransformer(Transformer):
    async def transform(
        self,
        intx: Interaction,
        value: Range[str, 1, 2]
    ) -> tuple[UnicodeEmoji]:
        return tuple([UnicodeEmoji(e['emoji']) for e in emoji_list(value)])


class EmojiKitchenError(Exception):
    def __init__(self, *emojis: UnicodeEmoji):
        self.emojis = emojis


class EmojiKitchenCog(Cog):

    OUTPUT_PATH = './assets/emojiOutput.json'

    ROOT_URL = 'https://www.gstatic.com/android/keyboard/emojikitchen'

    REF_URL = 'https://emojikitchen.dev/'

    def __init__(self, bot: Bot):
        self.bot = bot

        with open(self.OUTPUT_PATH) as f:
            self.emoji_kitchen = json.load(f)
            log.info(f'{f.name} loaded')

    def cog_unload(self):
        del self.emoji_kitchen

    def merge(
        self, emojis: tuple[UnicodeEmoji]
    ) -> tuple[UnicodeEmoji, UnicodeEmoji, str]:
        if len(emojis) < 1 or len(emojis) > 2:
            raise ValueError('too many emojis')

        if unsupported := ([
            e for e in emojis if e.unicode not in self.emoji_kitchen.keys()
        ]):
            raise EmojiKitchenError(*unsupported)

        entries = self.emoji_kitchen[emojis[0].unicode]

        if len(emojis) == 1:
            output: dict = random.choice(entries)
        elif emojis[0] == emojis[1]:
            output: dict = next((
                entry for entry in entries
                if entry['leftEmoji'] == emojis[0].unicode
                and entry['rightEmoji'] == emojis[0].unicode
            ))
        else:
            output: dict = next((
                entry for entry in entries
                if emojis[1].unicode in (
                    entry['leftEmoji'], entry['rightEmoji']
                )
            ))

        left_unicode, right_unicode, date = output.values()
        left_emoji = UnicodeEmoji.from_unicode(left_unicode)
        right_emoji = UnicodeEmoji.from_unicode(right_unicode)

        return left_emoji, right_emoji, date

    @ac.command(name='emoji_kitchen')
    @ac.describe(emojis='emojis')
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def _emoji_kitchen(
        self,
        intx: Interaction,
        emojis: Transform[tuple[UnicodeEmoji], UnicodeEmojiTransformer]
    ):
        """App command that mixes the provided emojis together."""

        try:
            if len(emojis) == 0:
                raise ValueError('err_none')
            if len(emojis) >= 3:
                raise ValueError('err_many')

            left_emoji, right_emoji, date = self.merge(emojis)

            output_url = '/'.join([
                self.ROOT_URL,
                date,
                left_emoji.prefixed,
                f'{left_emoji.prefixed}_{right_emoji.prefixed}.png'
            ])

            await intx.response.send_message(output_url)

        except (ValueError, StopIteration, EmojiKitchenError) as err:
            if isinstance(err, EmojiKitchenError):
                sep = '、' if intx.locale.value == 'zh-TW' else ', '
                err_msg = (
                    await intx.translate('err_unsupported')
                ).format(sep.join([e.emoji for e in err.emojis]))
            elif isinstance(err, StopIteration):
                err_msg = (
                    await intx.translate('err_failed')
                ).format(emojis)
            else:
                err_msg = await intx.translate(f'{err}')

            help_msg = (await intx.translate('help')).format(self.REF_URL)

            await intx.response.send_message(
                f'{err_msg}\n\n{help_msg}',
                ephemeral=True
            )

        log.info(' | '.join([
            f'{intx.user}',
            f'{intx.guild}',
            f'{intx.channel}',
            f'{emojis=}',
        ]))


async def setup(bot: Bot):
    await bot.add_cog(EmojiKitchenCog(bot))
