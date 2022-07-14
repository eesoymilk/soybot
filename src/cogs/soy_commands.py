import discord

from discord import app_commands
from discord.ext import commands
from commands.starburst import starburst_stream
from config import *


class SoyCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self._last_member = None

    @app_commands.command(name="starburst", description='C8763')
    @app_commands.guilds(*guild_ids)
    async def starburst(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(await starburst_stream())

    @commands.command(name="starburst")
    async def starburst(self, ctx) -> None:
        await ctx.send(await starburst_stream())
