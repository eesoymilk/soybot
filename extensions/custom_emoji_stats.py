import re
import asyncio

from datetime import datetime
from dataclasses import dataclass

from discord import Message, Reaction, Member, PartialEmoji, Emoji
from discord.ext.commands import Cog, Bot
from discord.abc import Messageable
from utils import get_lumberjack, EmojiUsage

log = get_lumberjack(__name__)
emoji_regex = r'<(a?):([a-zA-Z0-9_]{2,32}):([0-9]{18,22})>'


class CustomEmojiStatsCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener(name='on_message')
    async def in_text_emojis(self, msg: Message):

        partial_emojis = [
            PartialEmoji.from_str(
                match.group()
            ) for match in re.finditer(emoji_regex, msg.content)]

        results = await asyncio.gather(*[
            msg.guild.fetch_emoji(e.id) for e in partial_emojis
        ], return_exceptions=True)
        emojis = [r for r in results if isinstance(r, Emoji)]

        if not emojis:
            return

        emoji_usages = [EmojiUsage.from_in_text_emoji(e, msg) for e in emojis]

        log.info(' | '.join([
            f'{msg.guild}',
            f'{msg.channel}',
            f'{msg.author}',
            f'{emojis}']))

    @Cog.listener()
    async def on_reaction_add(self, rxn: Reaction, user: Member):
        if not isinstance(rxn.emoji, Emoji):
            return

        emoji_usage = EmojiUsage.from_reaction(rxn, user)

    @Cog.listener()
    async def on_reaction_remove(self, rxn: Reaction, user: Member):
        ...

    @Cog.listener()
    async def on_message_edit(self, before: Message, after: Message):
        ...


async def setup(bot: Bot):
    await bot.add_cog(CustomEmojiStatsCog(bot))
    log.info(f'{__name__} loaded')
