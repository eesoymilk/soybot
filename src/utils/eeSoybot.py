import asyncio
import discord

from discord.ext import commands
from utils import Config
from cogs.listeners import Listeners
from cogs.soy_commands import SoyCommands


TEST_GUILD = discord.Object(Config.guilds['debug'].id)


class eeSoybot(commands.Bot):
    async def setup_hook(self):
        self.owner_id = Config.user_ids['soymilk']
        await asyncio.gather(
            self.add_cog(Listeners(self)),
            self.add_cog(SoyCommands(self))
        )
        await self.tree.sync(guild=TEST_GUILD)
