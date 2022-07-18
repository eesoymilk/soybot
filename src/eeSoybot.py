import asyncio
import discord
from discord.ext import commands
from utils import get_lumberjack
from utils import Config


class eeSoybot(commands.Bot):
    def __init__(self, owner_id: int, test_guild: discord.Object, nthu_guild: discord.Object, **kwargs) -> None:
        self.owner_id = owner_id
        self.test_guild = test_guild
        self.nthu_guild = nthu_guild
        self.logger = get_lumberjack('eeSoybot')
        super().__init__(**kwargs)

    async def setup_hook(self):
        self.logger.info('syncing commands')
        await asyncio.gather(
            self.tree.sync(guild=self.test_guild),
            self.tree.sync(guild=self.nthu_guild)
        )
        self.logger.info('commands synced')
