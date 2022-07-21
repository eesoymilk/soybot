from random import choice
import discord
import asyncio

from datetime import datetime
from discord import app_commands
from discord.ext import commands
from discord.app_commands import (
    guilds, describe, rename, choices, guild_only,
    Choice, Range,
    AppCommandError, CommandOnCooldown
)
from commands import Poll
from commands import starburst_stream
from utils import ANSI
from utils import Config
from utils import get_lumberjack


class SoyCommands(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._last_member: discord.Member | discord.User | None = None

        bot.tree.on_error = self.on_app_command_error
        bot.tree.add_command(app_commands.ContextMenu(
            name='稽查頭貼',
            callback=self.avatar_ctx_menu,
        ))

        self.logger = get_lumberjack('SoyCommands', ANSI.BrightGreen)
        self.logger.info('initialized')

    # Starburst Stream slash command
    @app_commands.command(name="starburst", description='C8763')
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    @guilds(*Config.guild_ids)
    async def starburst(self, interaction: discord.Interaction) -> None:
        await interaction.response.send_message(await starburst_stream())

    # Poll slash command
    @app_commands.command(name="poll", description='發起投票吧！')
    @describe(duration='預設為20秒')
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
    # @guilds(Config.guilds['debug'].id)
    @guilds(*Config.guild_ids)
    @guild_only()
    async def poll_coro(
        self,
        interaction: discord.Interaction,
        anonymity: Choice[str],
        format: Choice[str],
        duration: Range[float, 10, 180] = 20.0
    ) -> None:
        settings = {
            'chat_interaction': interaction,
            'is_public': anonymity.value == 'public',
            'is_single': format.value == 'single',
            'duration': duration
        }
        poll = Poll(**settings)
        await poll.prompt_details()
        if await poll.modal.wait():
            return
        await poll.start()
        self.logger.info('start timer')
        await asyncio.sleep(poll.duration)
        self.logger.info('call end function')
        # await asyncio.sleep(3)
        await poll.end()

    @app_commands.command(name='soy', description='用豆漿ㄐㄐ人說話ㄅ')
    @rename(message='讓豆漿ㄐㄐ人講的話')
    @guilds(*Config.guild_ids)
    @guild_only()
    @app_commands.checks.cooldown(1, 10.0, key=lambda i: (i.channel.id, i.user.id))
    async def echo(self, interaction: discord.Interaction, message: str):
        self.logger.info(f'{interaction.user.display_name}: {message}')
        await interaction.channel.send(message)
        await interaction.response.send_message('已成功傳送', ephemeral=True)

    async def avatar_coro(self, interaction: discord.Interaction, target: discord.Member):
        if target.id == self.bot.user.id:
            await interaction.response.send_message(f'不要ㄐ查豆漿ㄐㄐ人的頭貼好ㄇ', ephemeral=True)
            return

        description = f'**{interaction.user.display_name}** 稽查了 **{target.display_name}** 的頭貼'
        if interaction.user.id == target.id:
            description = f'**{interaction.user.display_name}** 稽查了自己的頭貼'

        color = target.color

        embed = discord.Embed(
            color=color,
            description=description,
            type='image',
            # url='user.display_avatar.url',
            timestamp=datetime.now(),
        )
        embed.set_image(url=target.display_avatar.url)
        await interaction.response.send_message(
            f'{target.mention} 的頭貼是 **{choice(["伊織萌", "Saber"])}** {self.bot.get_emoji(780263339808522280)}',
            embed=embed
        )

    @app_commands.command(name="avatar", description='稽查頭貼')
    @rename(target='稽查對象')
    @guilds(*Config.guild_ids)
    @guild_only()
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def avatar_slash(self, interaction: discord.Interaction, target: discord.Member) -> None:
        await self.avatar_coro(interaction, target)

    @guilds(*Config.guild_ids)
    @app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def avatar_ctx_menu(self, interaction: discord.Interaction, user: discord.Member):
        await self.avatar_coro(interaction, target=user)

    async def on_app_command_error(self, interaction: discord.Interaction, error: AppCommandError):
        if isinstance(error, CommandOnCooldown):
            msg = f'冷卻中...\n請稍後**{str(round(error.retry_after, 2)).rstrip("0").rstrip(".")}**秒再試'
            await interaction.response.send_message(msg, ephemeral=True)
