import aiohttp
from discord import User, Intents, Interaction
from discord.app_commands import AppCommandError, CommandOnCooldown
from discord.ext.commands import Bot
from utils import get_lumberjack

log = get_lumberjack(__name__)
initial_extensions = (
    # 'extensions.autoresponse',
    'extensions.avatar',
    # 'extensions.emomix',
    'extensions.waifu',
    'extensions.listeners',
    'extensions.simple_poll',
    # 'extensions.poll',
    'extensions.soy_commands',
    'extensions.utilities',
    'extensions.custom_emoji_stats',
    # 'extensions.streak',
    # 'extensions.nthu',
)


class Soybot(Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

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
    def owner(self) -> User:
        return self.bot_app_info.owner

    async def on_app_command_error(
        self,
        intx: Interaction,
        e: AppCommandError
    ):
        if isinstance(e, CommandOnCooldown):
            await intx.response.send_message(
                f'冷卻中...\n請稍後**{str(round(e.retry_after, 1)).rstrip("0").rstrip(".")}**秒再試', 
                ephemeral=True)
        else:
            log.exception(e)
