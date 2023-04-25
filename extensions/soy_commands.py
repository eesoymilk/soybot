from discord import app_commands as ac, Interaction, Embed
from discord.ext.commands import Cog, Bot
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)

class SoyCommands(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @ac.command(name='匿名發言', description='匿名複讀機')
    @ac.rename(msg='複讀內容')
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def soy(self, intx: Interaction, msg: str):
        await intx.channel.send(msg)
        
        await intx.response.send_message(
            embed=Embed(
                description=f'**已成功匿名傳送**',
                color=intx.user.color,
            ).add_field(
                name='匿名訊息',
                value=msg
            ).add_field(
                name='目標頻道',
                value=intx.channel.mention
            ).set_author(
                name=intx.user,
                icon_url=intx.user.avatar,
            ).set_footer(
                text='soybot is currently at beta.\n' +
                'Please report bugs to eeSoymilk#4231 if you encounter any.'
            ),
            ephemeral=True)

        log.info(f'{intx.user} | {intx.guild} | {intx.channel} | {msg}')


async def setup(bot: Bot):
    await bot.add_cog(SoyCommands(bot))
    log.info(f'{__name__} loaded')
