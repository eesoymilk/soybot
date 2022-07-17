import discord

from discord.ext import commands
from utils import Config


TEST_GUILD = discord.Object(Config.guilds['debug'].id)


class eeSoybot(commands.Bot):
    async def setup_hook(self):
        self.owner_id = Config.users['soymilk'].id
        await self.tree.sync(guild=TEST_GUILD)
        ...
