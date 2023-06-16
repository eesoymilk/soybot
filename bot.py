import aiohttp
from discord import (
    Message,
    Game,
    User, 
    Intents, 
    Interaction,
)
from discord.app_commands import AppCommandError, CommandOnCooldown
from discord.ext.commands import Bot
from utils import get_lumberjack
from utils.i18n import SoybotTranslator

log = get_lumberjack(__name__)
initial_extensions = (
    'extensions.avatar',
    'extensions.emoji_mixer',
    'extensions.waifu',
    'extensions.listeners',
    'extensions.simple_poll',
    'extensions.soy_commands',
    'extensions.utilities',
)

# TODO: more flexible command prefix
def _prefix_callable(bot: Bot, msg: Message):
    user_id = bot.user.id
    base = [f'<@!{user_id}> ', f'<@{user_id}> ']
    if msg.guild is None:
        base.append('!')
        base.append('?')
    else:
        base.extend(bot.prefixes.get(msg.guild.id, ['?', '!']))
    return base

class Soybot(Bot):
    def __init__(self, *args, **kwargs):
        activity = Game(name='Your Mom')
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
        super().__init__(
            intents=intents,
            activity=activity,
            **kwargs
        )

    async def setup_hook(self):
        self.cs = aiohttp.ClientSession()
        self.bot_app_info = await self.application_info()
        self.tree.on_error = self.on_app_command_error
        await self.tree.set_translator(SoybotTranslator())

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
