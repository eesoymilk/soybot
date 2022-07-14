import asyncio
import discord
from datetime import datetime
from discord.ext import commands

# custom modules
# from events.message import react_user, react_keyword
from config import *


debug_guild_id = 874556062815100938
debug_role_ids = [874556062815100938, 993084722081181789,
                  993067016376295486, 993067123066818640]


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author == self.bot.user:
            return

        print(f'[{msg.channel.name} - {msg.author.display_name}] {msg.content}')

        # await asyncio.gather(
        #     react_user(self.bot, msg),
        #     react_keyword(self.bot, msg)
        # )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        ...

    @commands.Cog.listener()
    async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
        ...

    @commands.Cog.listener()
    async def on_typing(self, channel: discord.abc.Messageable, user: discord.Member, when: datetime):
        ...

    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        ...

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member):
        ...
