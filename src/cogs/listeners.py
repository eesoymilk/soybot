import asyncio
import logging
import discord
from datetime import datetime
from discord.ext import commands

# from events.message import react_user, react_keyword
from utils.config import *
from utils.lumberjack import ANSI, get_lumberjack


def logging_formatter(guild, channel, user, ) -> str:
    ...


def rich_logging_formatter(guild, channel=None, display_name=None, receiver=None, emoji=None, content=None) -> str:
    log_msg = ''

    if guild is not None:
        log_msg += f'{ANSI.BackgroundWhite}{ANSI.BrightBlack}{guild}{ANSI.Reset}'
    if channel is not None:
        log_msg += f'{ANSI.BackgroundWhite}{ANSI.BrightBlack} - {channel}{ANSI.Reset}'
    if display_name is not None:
        log_msg += f' {ANSI.Blue}{display_name}{ANSI.Reset}'
    if receiver is not None:
        log_msg += f'{ANSI.Blue} -> {receiver}{ANSI.Reset}'
    if emoji is not None:
        log_msg += f' {emoji}'
    if content is not None:
        log_msg += f' :\n{content}'

    return log_msg


class Listeners(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None
        self.logger = get_lumberjack('Listeners', ANSI.BrightGreen)
        self.logger.info("Listeners cog initialized.")

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        if msg.author == self.bot.user:
            return

        log_details = {
            'guild': msg.guild.name,
            'channel': msg.channel.name,
            'display_name': msg.author.display_name,
            'content': msg.content,
        }

        self.logger.info(rich_logging_formatter(**log_details))

        # self.logger.info(
        #     f'{msg.channel.guild.name} {msg.channel.name} {msg.author.display_name} {msg.content}')

        # await asyncio.gather(
        #     react_user(self.bot, msg),
        #     react_keyword(self.bot, msg)
        # )

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        self.logger.info(
            f'{reaction.message.channel.guild.name} {reaction.message.channel.name} {reaction.message.author.display_name} {reaction.emoji}')

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
