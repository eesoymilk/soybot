from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import random
import discord
import asyncio

from discord import app_commands
from discord.ext import commands
from textwrap import dedent
from utils import ANSI, Config, get_lumberjack

nthu_guild_id = 771595191638687784


# def rich_logging_formatter(guild, channel=None, display_name=None, receiver=None, emoji=None, content=None) -> str:
#     log_msg = ''

#     if guild is not None:
#         log_msg += f'{ANSI.BackgroundWhite}{ANSI.BrightBlack}{guild}{ANSI.Reset}'
#     if channel is not None:
#         log_msg += f'{ANSI.BackgroundWhite}{ANSI.BrightBlack} - {channel}{ANSI.Reset}'
#     if display_name is not None:
#         log_msg += f' {ANSI.Blue}{display_name}{ANSI.Reset}'
#     if receiver is not None:
#         log_msg += f'{ANSI.Blue} -> {receiver}{ANSI.Reset}'
#     if emoji is not None:
#         log_msg += f' {emoji}'
#     if content is not None:
#         log_msg += f': {content}'

#     return log_msg


log = get_lumberjack('NTHU', ANSI.Yellow)


# @ac.context_menu(name='憤怒狗狗')
# @ac.guilds(nthu_guild_id)
# @ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
# async def angry_dog_reactions(interaction: discord.Interaction, message: discord.Message):
#     log_details = {
#         'guild': message.channel.guild.name,
#         'channel': message.channel.name,
#         'display_name': interaction.user.display_name,
#         'receiver': message.author.display_name,
#     }
#     await interaction.response.defer(ephemeral=True, thinking=True)
#     log.info(rich_logging_formatter(**log_details))
#     await asyncio.gather(*(
#         message.add_reaction(emoji)
#         for emoji in [interaction.client.get_emoji(id)
#                       for id in Config.get_emoji_ids_by_tags('dog_bundle')]
#     ))
#     await interaction.followup.send(content='**憤怒狗狗**已送出')


# @ac.context_menu(name='阿袋狗狗')
# @ac.guilds(nthu_guild_id)
# @ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
# async def ugly_dog_reactions(interaction: discord.Interaction, message: discord.Message):
#     log_details = {
#         'guild': message.channel.guild.name,
#         'channel': message.channel.name,
#         'display_name': interaction.user.display_name,
#         'receiver': message.author.display_name,
#     }
#     await interaction.response.defer(ephemeral=True, thinking=True)
#     log.info(rich_logging_formatter(**log_details))

#     emojis = []

#     for id in Config.get_emoji_ids_by_tags('ugly_dog'):
#         emoji = interaction.client.get_emoji(id)
#         if emoji is not None:
#             emojis.append(emoji)

#     await asyncio.gather(*(message.add_reaction(emoji) for emoji in emojis))
#     await interaction.followup.send(content='**阿袋狗狗**已送出')

class NthuCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = self.bot.get_guild(nthu_guild_id)
        if self.guild is not None:
            self.daily_bs_channel = self.guild.get_channel(
                771596516443029516)

    @commands.Cog.listener()
    async def on_member_join(self, mem: discord.Member) -> None:
        if mem.guild.id != nthu_guild_id:
            return

        await mem.guild.system_channel.send(dedent(f'''\
            歡迎{mem.mention}加入**{mem.guild.name}**！

            請至{mem.guild.get_channel(771684498986500107).mention}留下您的系級和簡短的自我介紹，
            讓我們更加認識你/妳喔！'''))

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if self.guild is None:
            self.guild = await self.bot.fetch_guild(nthu_guild_id)

        try:
            if (member := self.guild.get_member(before.id)) is None:
                member = await self.guild.fetch_member(before.id)
        except discord.NotFound:
            return

        if before.avatar == after.avatar or before.id not in Config.user_ids:
            return

        try:
            if self.daily_bs_channel is None:
                self.daily_bs_channel = await self.guild.fetch_channel(771596516443029516)
        except discord.NotFound:
            return

        await self.daily_bs_channel.send(
            f'主要！ **{member.mention}**又換頭貼了！',
            embed=discord.Embed(
                description='➡原頭貼➡\n\n⬇新頭貼⬇',
                color=member.color,
                timestamp=datetime.now(),
            ).set_thumbnail(
                url=before.avatar
            ).set_image(
                url=after.avatar
            ))


async def setup(bot: commands.Bot):
    # bot.tree.add_command(angry_dog_reactions)
    # bot.tree.add_command(ugly_dog_reactions)
    await bot.add_cog(
        NthuCog(bot),
        guild=discord.Object(nthu_guild_id)
    )
    log.info('loaded')
