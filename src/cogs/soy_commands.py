import discord
import asyncio

from discord import app_commands
from discord.ext import commands
from discord.app_commands import Choice, Range
from commands import Poll
from commands import starburst_stream
from utils import Config


class SoyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member: discord.Member | discord.User | None = None

    # Starburst Stream
    @app_commands.command(name="starburst", description='C8763')
    @app_commands.guilds(*Config.guild_ids)
    async def starburst(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(await starburst_stream())

    # Poll
    @app_commands.command(name="poll", description='預設設定：公開 單選 20秒')
    # @app_commands.describe(anonymity='公開 or 匿名', format='單選 or 複選', duration='投票持續秒數')
    @app_commands.rename(anonymity='計票方式', format='投票形式', duration='投票持續秒數')
    @app_commands.choices(
        anonymity=[
            Choice(name='公開', value='public'),
            Choice(name='匿名', value='anonymous'),
        ],
        format=[
            Choice(name='單選', value='single'),
            Choice(name='複選', value='multiple'),
        ]
    )
    @app_commands.guilds(*Config.guild_ids)
    @app_commands.guild_only()
    async def poll_coro(
        self,
        interaction: discord.Interaction,
        anonymity: Choice[str] = 'public',
        format: Choice[str] = 'single',
        duration: Range[float, 10, 180] = 20.0
    ) -> None:
        settings = {
            'chat_interaction': interaction,
            'is_public': anonymity == 'public',
            'is_single': format == 'single',
            'duration': duration
        }
        poll = Poll(**settings)
        await poll.prompt_details()
        if await poll.modal.wait():
            return
        await poll.start()
        await asyncio.sleep(3)
        await poll.end()

    # manually sync commands
    @commands.command(name="sync")
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.send('commands syncing...')
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send('commands synced.')
