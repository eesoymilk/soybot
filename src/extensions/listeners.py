import asyncio
import random
import discord
from datetime import datetime
from discord.ext import commands
from utils import Config, SoyReact, SoyReply, ANSI, get_lumberjack


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
        log_msg += f': {content}'

    return log_msg


def chance(x: float = 1.0) -> bool:
    return x > random.random()


async def react_msg(soy_react: SoyReact, msg: discord.Message, bot: commands.Bot):
    if soy_react is None or not chance(soy_react.activation_probability):
        return

    matched_ids = Config.get_emoji_ids_by_tags(*soy_react.emoji_tags)
    emojis = [id if isinstance(id, str) else bot.get_emoji(id)
              for id in random.sample(matched_ids, soy_react.count)]
    await asyncio.gather(*(msg.add_reaction(emoji) for emoji in emojis))


async def reply_msg(soy_reply: SoyReply, msg: discord.Message, bot: commands.Bot):
    ...


class Listeners(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member = None
        self.logger = get_lumberjack('Listeners', ANSI.BrightGreen)
        self.logger.info('initialized')

    @commands.Cog.listener()
    async def on_message(self, msg: discord.Message):
        # ignore own message
        if msg.author.id == self.bot.user.id:
            return

        log_details = {
            'guild': msg.guild.name,
            'channel': msg.channel.name,
            'display_name': msg.author.display_name,
            'content': msg.content,
        }
        self.logger.info(rich_logging_formatter(**log_details))

        aws = []
        soy_react, soy_reply = Config.get_action_by_user_id(msg.author.id)
        aws.append(react_msg(soy_react, msg, self.bot))
        aws.append(reply_msg(soy_reply, msg, self.bot))
        await asyncio.gather(*aws)

    @commands.Cog.listener()
    async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
        log_details = {
            'guild': reaction.message.guild.name,
            'channel': reaction.message.channel.name,
            'display_name': user.display_name,
            'receiver': reaction.message.author.display_name
            if user.display_name != reaction.message.author.display_name else None,
            'emoji': reaction.emoji,
        }
        self.logger.info(rich_logging_formatter(**log_details))

        # if reaction.count > 1 and self.bot.user.id not in [user.id async for user in reaction.users()]:
        if reaction.count > 1:
            await reaction.message.add_reaction(reaction)

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
        if after.id == self.bot.user.id:
            await after.edit(nick=None)


async def setup(bot: commands.Bot):
    await bot.add_cog(Listeners(bot))
