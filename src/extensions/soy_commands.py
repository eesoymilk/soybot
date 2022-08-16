import discord

from discord import app_commands
from discord.ext import commands
from discord.app_commands import (
    guilds, rename, guild_only,
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

    async def on_app_command_error(self, interaction: discord.Interaction, error: AppCommandError):
        if isinstance(error, CommandOnCooldown):
            msg = f'冷卻中...\n請稍後**{str(round(error.retry_after, 2)).rstrip("0").rstrip(".")}**秒再試'
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            self.logger.exception(error)


async def setup(bot: commands.Bot):
    await bot.add_cog(SoyCommands(bot))
