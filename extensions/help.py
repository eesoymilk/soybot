from discord import Embed
from discord.ext.commands import Command, Cog, MinimalHelpCommand, Bot
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)
help_attributes = {
    'aliases': ['h', 'helps'],
    'cooldown': cd_but_soymilk
}


class SoyHelp(MinimalHelpCommand):
    async def send_bot_help(self, mapping: dict[Cog, list[Command]]):
        embed = Embed(title='Help')
        for cog, commands in mapping.items():
            filtered = await self.filter_commands(commands, sort=True)
            command_signatures = [
                self.get_command_signature(c) for c in filtered
            ]
            if command_signatures:
                cog_name = getattr(cog, 'qualified_name', 'No Category')
                embed.add_field(
                    name=cog_name,
                    value='\n'.join(command_signatures),
                    inline=False
                )

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_command_help(self, command: Command):
        embed = Embed(title=self.get_command_signature(command))
        embed.add_field(name='Help', value=command.help)
        alias = command.aliases
        if alias:
            embed.add_field(
                name='Aliases',
                value=', '.join(alias),
                inline=False
            )

        channel = self.get_destination()
        await channel.send(embed=embed)

    async def send_pages(self):
        channel = self.get_destination()
        for page in self.paginator.pages:
            await channel.send(embed=Embed(description=page))


class SoyHelpCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._original_help_command = bot.help_command
        bot.help_command = SoyHelp()
        bot.help_command.command_attrs = help_attributes
        bot.help_command.cog = self

    def cog_unload(self):
        self.bot.help_command = self._original_help_command


async def setup(bot: Bot):
    await bot.add_cog(SoyHelpCog(bot))
