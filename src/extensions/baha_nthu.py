from dataclasses import dataclass
import discord
import asyncio

from discord import app_commands as ac, Message
from discord.ext import commands
from discord.ext.commands import Cog, Bot
from utils import NTHU, ANSI, Config, get_lumberjack


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


logger = get_lumberjack('NTHU', ANSI.Yellow)


@ac.context_menu(name='憤怒狗狗')
@ac.guilds(NTHU.guild_id)
@ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def angry_dog_reactions(interaction: discord.Interaction, message: discord.Message):
    log_details = {
        'guild': message.channel.guild.name,
        'channel': message.channel.name,
        'display_name': interaction.user.display_name,
        'receiver': message.author.display_name,
    }
    await interaction.response.defer(ephemeral=True, thinking=True)
    logger.info(rich_logging_formatter(**log_details))
    await asyncio.gather(*(
        message.add_reaction(emoji)
        for emoji in [interaction.client.get_emoji(id)
                      for id in Config.get_emoji_ids_by_tags('dog_bundle')]
    ))
    await interaction.followup.send(content='**憤怒狗狗**已送出')


def is_cohesive(a: Message, b: Message) -> bool:
    if a.author == b.author:
        return False
    if a.content and a.content == b.content:
        return True
    if a.stickers and a.stickers == b.stickers:
        return True
    return False


@dataclass()
class MessageStreak:
    last_message: Message
    count: int = 1


class NthuCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._streaks: dict[int, MessageStreak] = dict()

    @commands.Cog.listener()
    async def on_message(self, msg: Message):
        # ignore own message and bots
        if msg.author.id == self.bot.user.id or msg.author.bot:
            return

        if msg.channel.id not in self._streaks:
            self._streaks[msg.channel.id] = MessageStreak(msg)
            return

        if is_cohesive(msg, self._streaks[msg.channel.id].last_message):
            self._streaks[msg.channel.id].count += 1
        else:
            self._streaks[msg.channel.id].count = 1

        if self._streaks[msg.channel.id].count == 3:
            await msg.channel.send(msg.content, stickers=msg.stickers)

        self._streaks[msg.channel.id].last_message = msg

        # log_details = {
        #     'guild': msg.guild.name,
        #     'channel': msg.channel.name,
        #     'display_name': msg.author.display_name,
        #     'content': msg.content,
        # }
        # self.logger.info(rich_logging_formatter(**log_details))

    # @commands.Cog.listener()
    # async def on_reaction_add(self, reaction: discord.Reaction, user: discord.Member):
    #     log_details = {
    #         'guild': reaction.message.guild.name,
    #         'channel': reaction.message.channel.name,
    #         'display_name': user.display_name,
    #         'receiver': reaction.message.author.display_name
    #         if user.display_name != reaction.message.author.display_name else None,
    #         'emoji': reaction.emoji,
    #     }
    #     self.logger.info(rich_logging_formatter(**log_details))

    #     # if reaction.count > 1 and self.bot.user.id not in [user.id async for user in reaction.users()]:
    #     if reaction.count > 2:
    #         await reaction.message.add_reaction(reaction)

    # @commands.Cog.listener()
    # async def on_reaction_remove(self, reaction: discord.Reaction, user: discord.Member):
    #     log_details = {
    #         'guild': reaction.message.guild.name,
    #         'channel': reaction.message.channel.name,
    #         'display_name': user.display_name,
    #         'receiver': reaction.message.author.display_name
    #         if user.display_name != reaction.message.author.display_name else None,
    #         'emoji': reaction.emoji,
    #     }
    #     self.logger.info(rich_logging_formatter(**log_details))

    #     if user.id == self.bot.user.id and reaction.message.guild.id == Config.guilds['nthu'].id:
    #         await reaction.message.add_reaction(reaction)


async def setup(bot: Bot):
    bot.tree.add_command(angry_dog_reactions)
    await bot.add_cog(NthuCog(bot))
    logger.info('loaded')
