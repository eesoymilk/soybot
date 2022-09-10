
from datetime import datetime, timedelta
import discord
from textwrap import dedent
from discord import Member, Embed, Color, Message, Interaction, NotFound, app_commands
from discord.ext import commands
from discord.ext.commands import Cog, Bot, Context
from utils import ANSI, get_lumberjack, Config

# lanm_id = 874556062815100938  # debug
# intro_channel_id = 1011283972166266962  # debug
lnmc_id = 1010521652079120384
intro_channel_id = 1010824070767583242
logger = get_lumberjack('LANM', ANSI.Yellow)
lnmc_events: list[dict[str, str | datetime]] = [
    {
        'name': '幹部研習會',
        'time': datetime(2022, 9, 6, 10)
    },
    {
        'name': '社團博覽會',
        'time': datetime(2022, 9, 15, 18)
    },
    {
        'name': '期初社大',
        'time': datetime(2022, 9, 19, 19)
    }
]


class LnmcCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.bulletin_msg: Message = None

    def bulletin_embed(self) -> Embed:
        embed = Embed(
            title='重要日程與公告事項',
            description='[FB](https://www.facebook.com/profile.php?id=100082972873193) | [IG](https://www.instagram.com/nthu_lnmc/)',
            timestamp=datetime.now(),
            color=Color.from_rgb(142, 167, 195),
        ).set_author(
            name='文新鯛魚燒 DC群',
            icon_url='https://cdn.discordapp.com/attachments/1010783926597455933/1011967739327422544/1658553417515.png'
        ).set_thumbnail(
            url='https://cdn.discordapp.com/attachments/1010783926597455933/1014245014903201842/1661885223317.jpg'
        ).set_image(
            url='https://cdn.discordapp.com/attachments/1010783926597455933/1014245015171645490/1661885223275.jpg'
        ).set_footer(
            text='更新於'
        )

        for e in lnmc_events:
            name, time = e.values()
            value = f'<t:{int(time.timestamp())}:F>'
            if datetime.now() + timedelta(days=7) > time:
                value = value.replace('F', 'R')
            embed.add_field(
                name=name,
                value=value,
                inline=False
            )

        return embed

    @commands.Cog.listener()
    async def on_member_join(self, mem: Member) -> None:
        if mem.guild.id != lnmc_id:
            return

        await mem.guild.system_channel.send(dedent(f'''\
            歡迎{mem.mention}加入**文新社DC群**！

            請至{mem.guild.get_channel(intro_channel_id).mention}發個簡短的自我介紹，
            讓我們更加認識你/妳喔！'''))

    @commands.command()
    async def bt(self, ctx: Context):
        if ctx.author.id != Config.users['soymilk'].id:
            return

        self.bulletin_msg = await ctx.send(embed=self.bulletin_embed())

    @app_commands.command()
    async def update_bulletin(self, interaction: Interaction):
        if interaction.user.id != Config.users['soymilk'].id:
            await interaction.response.send_message('No Permission', ephemeral=True)
            return

        if self.bulletin_msg is None:
            try:
                self.bulletin_msg = await interaction.channel.fetch_message(1018069595036332052)
            except NotFound:
                await interaction.response.send_message('找不到公告訊息', ephemeral=True)
                return

        await self.bulletin_msg.edit(embed=self.bulletin_embed())
        await interaction.response.send_message('公告已更新', ephemeral=True)


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        LnmcCog(bot),
        guild=discord.Object(lnmc_id)
    )
    logger.info('loaded')
