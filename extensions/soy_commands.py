import discord

from discord import app_commands
from discord.ext import commands
from commands import starburst_stream
from utils import ANSI
from utils import get_lumberjack

log = get_lumberjack(__name__, ANSI.Yellow)


class SoyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    # Starburst Stream slash command
    @app_commands.command(name="starburst", description='C8763')
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def starburst(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(await starburst_stream())

    @app_commands.command(description='用豆漿ㄐㄐ人說話ㄅ')
    @app_commands.rename(message='讓豆漿ㄐㄐ人講的話')
    @app_commands.guild_only()
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.channel.id, i.user.id))
    async def soy(self, interaction: discord.Interaction, message: str):
        log.info(f'{interaction.user.display_name}: {message}')
        await interaction.channel.send(message)
        await interaction.response.send_message('已成功傳送', ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(SoyCommands(bot))
    log.info('loaded')
