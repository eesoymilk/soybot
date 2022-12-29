import aiohttp
import discord
from discord.ext.commands import Bot
from motor.motor_asyncio import AsyncIOMotorDatabase
from utils import get_lumberjack

log = get_lumberjack(__name__)
initial_extensions = (
    'extensions.autoresponse',
    'extensions.avatar',
    'extensions.emomix',
    'extensions.listeners',
    'extensions.lnmc',
    'extensions.poll',
    'extensions.soy_commands',
    'extensions.utilities',
)


class eeSoybot(Bot):
    def __init__(self):
        super().__init__(
            command_prefix='!',
            case_insensitive=True,
            intents=discord.Intents.all()
        )

    async def setup_hook(self):
        self.session = aiohttp.ClientSession()
        self.bot_app_info = await self.application_info()
        self.owner_id = self.bot_app_info.owner.id

        self.author_reactions = dict()

        for extension in initial_extensions:
            try:
                await self.load_extension(extension)
            except Exception as e:
                log.exception('Failed to load extension %s.', extension)

    @property
    def owner(self) -> discord.User:
        return self.bot_app_info.owner
