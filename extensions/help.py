from discord import Embed
from discord.ext.commands import Cog, MinimalHelpCommand, Bot
from utils import get_lumberjack

log = get_lumberjack(__name__)


class SoyHelp(MinimalHelpCommand):
    async def send_pages(self):
        channel = self.get_destination()
        for page in self.paginator.pages:
            await channel.send(embed=Embed(description=page))


class SoyHelpCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = SoyHelp()
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


async def setup(bot: Bot):
    await bot.add_cog(SoyHelpCog(bot))
    log.info(f'{__name__} loaded')
