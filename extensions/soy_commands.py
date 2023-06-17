from discord import app_commands as ac, Interaction, Embed
from discord.app_commands import locale_str as _T
from discord.ext.commands import Cog, Bot
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)


class SoyCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @ac.command(name='echo')
    @ac.rename(msg='msg')
    @ac.describe(msg='msg')
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def soy(self, intx: Interaction, msg: str):
        log.info(f'user locale: {intx.locale}')
        log.info(f'guild locale: {intx.guild_locale}')

        await intx.channel.send(msg)

        await intx.response.send_message(
            embed=Embed(
                description=await intx.translate('embed_desc'),
                color=intx.user.color,
            ).add_field(
                name=await intx.translate('embed_message'),
                value=msg
            ).add_field(
                name=await intx.translate('embed_channel'),
                value=intx.channel.mention
            ).set_author(
                name=intx.user,
                icon_url=intx.user.avatar,
            ).set_footer(
                text=await intx.translate(_T('beta', shared=True))
            ),
            ephemeral=True
        )

        log.info(f'{intx.user} | {intx.guild} | {intx.channel} | {msg}')


async def setup(bot: Bot):
    await bot.add_cog(SoyCommands(bot))
    log.info(f'{__name__} loaded')
