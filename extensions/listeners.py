from discord import Message, Reaction, Member
from discord.ext.commands import Cog, Bot
from discord.abc import Messageable
from datetime import datetime
from utils import get_lumberjack

log = get_lumberjack(__name__)


class Listeners(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @Cog.listener()
    async def on_message(self, msg: Message):
        if msg.author.id == self.bot.user.id:
            return

        log.info(f'{msg.guild} | {msg.channel} | {msg.author} | {msg.content}')

    @Cog.listener()
    async def on_reaction_add(self, rxn: Reaction, user: Member):
        if user == self.bot.user:
            return

        log.info(' | '.join([
            'on_reaction_add',
            rxn.message.guild.name,
            rxn.message.channel,
            user,
            rxn.emoji,
            rxn.message.mentions
        ]))

    @Cog.listener()
    async def on_reaction_remove(self, rxn: Reaction, user: Member):
        if user == self.bot.user:
            return

        log.info(' | '.join([
            'on_reaction_remove',
            rxn.message.guild.name,
            rxn.message.channel,
            user,
            rxn.emoji,
            rxn.message.mentions
        ]))

    @Cog.listener()
    async def on_typing(
        self,
        ch: Messageable,
        user: Member,
        when: datetime
    ):
        ...

    @Cog.listener()
    async def on_message_edit(self, before: datetime, after: datetime):
        ...

    @Cog.listener()
    async def on_member_update(self, before: Member, after: Member):
        ...


async def setup(bot: Bot):
    await bot.add_cog(Listeners(bot))
