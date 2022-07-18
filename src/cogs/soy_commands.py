import discord
import asyncio

from discord import app_commands
from discord.ext import commands
from discord.app_commands import guilds, describe, rename, choices, guild_only, Choice, Range
from commands import Poll
from commands import starburst_stream
from utils import ANSI
from utils import Config
from utils import get_lumberjack


class SoyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member: discord.Member | discord.User | None = None

        self.bot.tree.add_command(app_commands.ContextMenu(
            name='稽查頭貼',
            callback=self.avatar,
        ))

        self.logger = get_lumberjack('SoyCommands', ANSI.BrightGreen)
        self.logger.info('initialized')

    # Starburst Stream slash command
    @app_commands.command(name="starburst", description='C8763')
    # @app_commands.checks.cooldown(rate=1, per=10)
    @guilds(*Config.guild_ids)
    async def starburst(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(await starburst_stream())

    # Poll slash command
    @app_commands.command(name="poll", description='預設設定：公開 單選 20秒')
    # @describe(anonymity='公開 or 匿名', format='單選 or 複選', duration='投票持續秒數')
    @rename(anonymity='計票方式', format='投票形式', duration='投票持續秒數')
    @choices(
        anonymity=[
            Choice(name='公開', value='public'),
            Choice(name='匿名', value='anonymous'),
        ],
        format=[
            Choice(name='單選', value='single'),
            Choice(name='複選', value='multiple'),
        ]
    )
    @guilds(*Config.guild_ids)
    @guild_only()
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

    # manually prefixed sync commands
    @commands.command(name="sync")
    async def sync(self, ctx: commands.Context) -> None:
        await ctx.send('commands syncing...')
        await self.bot.tree.sync(guild=ctx.guild)
        await ctx.send('commands synced.')

    # @app_commands.checks.cooldown(rate=1, per=10)
    @guilds(*Config.guild_ids)
    async def avatar(self, interaction: discord.Interaction, user: discord.Member):
        embed = discord.Embed(
            title=f'{user.display_name} 的頭貼是 **伊織萌**',
            color=discord.Color.random()
        )
        # embed.set_author(name=interaction.user.display_name,
        #                  icon_url=interaction.user.display_avatar.url)
        embed.set_image(url=user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

    async def cog_command_error(self, ctx: commands.Context, error: commands.CommandError) -> None:
        print('error handler fired')
        return await super().cog_command_error(ctx, error)

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        print('error handler fired')
        # if isinstance(error, app_commands.CommandOnCooldown):
        await interaction.response.send_message(str(error), ephemeral=True)
        # return await super().cog_command_error(interaction, error)
    # @app_commands.error
    # async def error_handler(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
    #     if isinstance(error, app_commands.CommandOnCooldown):
    #         await interaction.response.send_message(str(error), ephemeral=True)
