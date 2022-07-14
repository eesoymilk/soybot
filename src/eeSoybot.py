import asyncio

from discord.ext import commands
from config import *
from cogs.listeners import Listeners
from cogs.soy_commands import SoyCommands


class eeSoybot(commands.Bot):
    async def setup_hook(self):
        self.owner_id = user_ids['soymilk']
        await asyncio.gather(
            self.add_cog(Listeners(self)),
            self.add_cog(SoyCommands(self))
        )
        await self.tree.sync()
