import discord
import asyncio

from random import choice
from datetime import datetime
from discord import app_commands
from discord.ext import commands
from discord.app_commands import (
    guilds, describe, rename, choices, guild_only,
    Choice, Range,
    AppCommandError, CommandOnCooldown
)
from commands import starburst_stream
from utils import ANSI
from utils import Config
from utils import get_lumberjack


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


class SoyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member: discord.Member | discord.User | None = None

        bot.tree.on_error = self.on_app_command_error
        bot.tree.add_command(app_commands.ContextMenu(
            name='稽查頭貼',
            callback=self.avatar_ctx_menu,
        ))
        bot.tree.add_command(app_commands.ContextMenu(
            name='憤怒狗狗反應套餐',
            callback=self.dog_reactions,
        ))

        self.logger = get_lumberjack('SoyCommands', ANSI.Yellow)
        self.logger.info('initialized')

    # Starburst Stream slash command
    @app_commands.command(name="starburst", description='C8763')
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    @guilds(*Config.guild_ids)
    async def starburst(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(await starburst_stream())

    @app_commands.command(name='soy', description='用豆漿ㄐㄐ人說話ㄅ')
    @rename(message='讓豆漿ㄐㄐ人講的話')
    @guilds(*Config.guild_ids)
    @guild_only()
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.channel.id, i.user.id))
    async def soy(self, interaction: discord.Interaction, message: str):
        self.logger.info(f'{interaction.user.display_name}: {message}')
        await interaction.channel.send(message)
        await interaction.response.send_message('已成功傳送', ephemeral=True)

    async def avatar(self, interaction: discord.Interaction, target: discord.Member):
        if target.id == self.bot.user.id:
            await interaction.response.send_message(f'不要ㄐ查豆漿ㄐㄐ人的頭貼好ㄇ', ephemeral=True)
            return

        description = f'**{interaction.user.display_name}** 稽查了 **{target.display_name}** 的頭貼'
        if interaction.user.id == target.id:
            description = f'**{interaction.user.display_name}** 稽查了自己的頭貼'

        embed = discord.Embed(
            color=target.color,
            description=description,
            type='image',
            timestamp=datetime.now(),
        )
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(
            f'{target.mention} 的頭貼是 **{choice(["伊織萌", "Saber"])}** {self.bot.get_emoji(780263339808522280)}',
            embed=embed
        )

        log_details = {
            'guild': interaction.guild.name,
            'channel': interaction.channel.name,
            'display_name': interaction.user.display_name,
            'receiver': target.display_name,
        }
        self.logger.info(rich_logging_formatter(**log_details))

    @app_commands.command(name="avatar", description='稽查頭貼')
    @rename(target='稽查對象')
    @guilds(*Config.guild_ids)
    @guild_only()
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def avatar_slash(self, interaction: discord.Interaction, target: discord.Member) -> None:
        await self.avatar(interaction, target)

    @guilds(*Config.guild_ids)
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def avatar_ctx_menu(self, interaction: discord.Interaction, user: discord.Member):
        await self.avatar(interaction, target=user)

    @guilds(*Config.guild_ids)
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def dog_reactions(self, interaction: discord.Interaction, message: discord.Message):
        log_details = {
            'guild': message.channel.guild.name,
            'channel': message.channel.name,
            'display_name': interaction.user.display_name,
            'receiver': message.author.display_name,
        }
        await interaction.response.send_message('**送出反應中...**', ephemeral=True)
        self.logger.info(rich_logging_formatter(**log_details))
        await asyncio.gather(*(
            message.add_reaction(emoji)
            for emoji in [self.bot.get_emoji(id)
                          for id in Config.get_emoji_ids_by_tags('dog_bundle')]
        ))
        await interaction.edit_original_message(content='**憤怒狗狗反應套餐**已送出')

    async def on_app_command_error(self, interaction: discord.Interaction, error: AppCommandError):
        if isinstance(error, CommandOnCooldown):
            msg = f'冷卻中...\n請稍後**{str(round(error.retry_after, 2)).rstrip("0").rstrip(".")}**秒再試'
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            self.logger.exception(error)


async def setup(bot: commands.Bot):
    await bot.add_cog(SoyCommands(bot))
