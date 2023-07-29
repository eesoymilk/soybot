import re
import asyncio
from typing import Optional
from datetime import datetime

from discord import (
    Message,
    Reaction,
    Member,
    Guild,
    PartialEmoji,
    Emoji,
    Sticker,
)
from discord.ext.commands import Cog, Bot

from attr import frozen
from emoji import emoji_list

from utils import get_lumberjack

log = get_lumberjack(__name__)


@frozen
class EmojiUsage:
    id: Optional[int] = None
    message_id: int

    custom_emoji_id: Optional[int] = None
    unicode_emoji: Optional[str] = None

    timestamp: datetime


class EmojiNotFoundError(Exception):
    pass


class MojitrackCog(Cog):
    custom_emoji_regex = r'<(a?):([a-zA-Z0-9_]{2,32}):([0-9]{18,22})>'

    def __init__(self, bot: Bot):
        self.bot = bot

    @staticmethod
    async def get_or_fetch_emoji(
        guild: Guild, emoji_id: int
    ) -> Emoji:
        if (e := guild.get_emoji(emoji_id)) is not None:
            return e
        return await guild.fetch_emoji(emoji_id)

    async def _fetch_emoji_usages(
        self, msg: Message, timestamp: datetime
    ) -> tuple[tuple[Emoji | str, ...], tuple[EmojiUsage, ...]]:
        # match all valid discord custom emojis, also known as a PartialEmoji
        partial_emojis = [
            PartialEmoji.from_str(
                match.group()
            ) for match in re.finditer(self.custom_emoji_regex, msg.content)
        ]

        # we only need custom emojis from this current guild
        fetched_emojis = await asyncio.gather(*[
            self.get_or_fetch_emoji(msg.guild, e.id) for e in partial_emojis
        ], return_exceptions=True)
        custom_emojis = [r for r in fetched_emojis if isinstance(r, Emoji)]

        # find all unicode emojis
        unicode_emojis = [e['emoji'] for e in emoji_list(msg.content)]
        if not (emojis := custom_emojis + unicode_emojis):
            raise EmojiNotFoundError('No emojis are usged in this message')

        # create instances of emoji_usages
        custom_emoji_usages = [
            EmojiUsage(
                message_id=msg.id,
                timestamp=timestamp,
                custom_emoji_id=e.id
            ) for e in custom_emojis
        ]
        unicode_emoji_usages = [
            EmojiUsage(
                message_id=msg.id,
                timestamp=timestamp,
                unicode_emoji=e
            ) for e in unicode_emojis
        ]
        emoji_usages = custom_emoji_usages + unicode_emoji_usages

        return tuple(emojis), tuple(emoji_usages)

    def _get_sticker_usages(
        self, msg: Message, timestamp: datetime
    ) -> tuple[tuple[Sticker, ...], tuple[EmojiUsage, ...]]:
        ...

    @Cog.listener()
    async def on_message(self, msg: Message):
        try:
            # TODO: store emoji usages and message to db
            emojis, emoji_usages = await self._fetch_emoji_usages(
                msg, datetime.utcnow()
            )
        except EmojiNotFoundError as err:
            log.debug(f'{err}')
            return

        log.info(' | '.join([
            f'{msg.guild}',
            f'{msg.channel}',
            f'{msg.author}',
            f'{emojis}'
            f'{emoji_usages}'
        ]))

    @Cog.listener()
    async def on_reaction_add(self, rxn: Reaction, user: Member):
        if isinstance(rxn.emoji, PartialEmoji):
            return

        # TODO: add reaction to db
        if isinstance(rxn.emoji, Emoji):
            ...
        else:
            ...

    @Cog.listener()
    async def on_reaction_remove(self, rxn: Reaction, user: Member):
        ...

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        ...


async def setup(bot: Bot):
    await bot.add_cog(MojitrackCog(bot))
