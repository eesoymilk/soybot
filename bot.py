import aiohttp

from discord import (
    Message,
    Game,
    User,
    Intents,
    Interaction,
)
from discord.utils import setup_logging
from discord.app_commands import AppCommandError, CommandOnCooldown
from discord.ext.commands import Bot

from utils import get_lumberjack
from utils.i18n import SoybotTranslator

log = get_lumberjack(__name__)
initial_extensions = (
    "extensions.help",
    "extensions.inspect",
    "extensions.emoji_kitchen",
    "extensions.waifu",
    "extensions.listeners",
    "extensions.reaction_poll",
    "extensions.soy_commands",
    "extensions.chatbot",
    "extensions.admin",
)


class Soybot(Bot):
    def __init__(self, *args, **kwargs):
        activity = Game(name="🥛 Drinking Soymilk 🥛")
        intents = Intents(
            guilds=True,
            members=True,
            bans=True,
            emojis=True,
            voice_states=True,
            messages=True,
            reactions=True,
            message_content=True,
        )
        super().__init__(intents=intents, activity=activity, **kwargs)

    async def setup_hook(self):
        self.bot_app_info = await self.application_info()
        self.cs = aiohttp.ClientSession()

        setup_logging()

        for ext in initial_extensions:
            try:
                await self.load_extension(ext)
                log.info(f"{ext} loaded")
            except Exception as e:
                log.exception(f"Failed to load extension {ext}: {e}")

        self.tree.on_error = self.on_app_command_error
        await self.tree.set_translator(SoybotTranslator())

    @property
    def owner(self) -> User:
        return self.bot_app_info.owner

    async def on_app_command_error(
        self, intx: Interaction, err: AppCommandError
    ):
        if isinstance(err, CommandOnCooldown):
            await intx.response.send_message(
                f'冷卻中...\n請稍後**{str(round(err.retry_after, 1)).rstrip("0").rstrip(".")}**秒再試',
                ephemeral=True,
            )
        else:
            log.exception(err)
