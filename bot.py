import aiohttp
import discord
from discord.ext.commands import Bot
from discord import app_commands
from utils import get_lumberjack

log = get_lumberjack(__name__)
initial_extensions = (
    # 'extensions.autoresponse',
    'extensions.avatar',
    # 'extensions.emomix',
    # 'extensions.waifu',
    'extensions.listeners',
    'extensions.simple_poll',
    # 'extensions.poll',
    'extensions.soy_commands',
    'extensions.utilities',
    # 'extensions.streak',
    # 'extensions.nthu',
)


class Soybot(Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            case_insensitive=True,
            intents=discord.Intents.all())

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.bot_app_info = await self.application_info()
        self.tree.on_error = self.on_app_command_error

        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
            except Exception as e:
                log.exception(f'Failed to load extension {ext}.')

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner

    async def on_app_command_error(
        self,
        interaction: discord.Interaction,
        error: app_commands.AppCommandError
    ):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f'冷卻中...\n請稍後**{str(round(error.retry_after, 1)).rstrip("0").rstrip(".")}**秒再試'
            await interaction.response.send_message(msg, ephemeral=True)
        else:
            log.exception(error)
