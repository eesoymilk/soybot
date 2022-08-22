
import discord
from textwrap import dedent
from discord import Member
from discord.ext import commands
from discord.ext.commands import Cog, Bot
from utils import ANSI, get_lumberjack

# lanm_id = 874556062815100938  # debug
# intro_channel_id = 1011283972166266962  # debug
lanm_id = 1010521652079120384
intro_channel_id = 1010824070767583242
logger = get_lumberjack('LANM', ANSI.Yellow)


class LanmCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_join(self, mem: Member) -> None:
        await mem.guild.system_channel.send(dedent(f'''\
            歡迎{mem.mention}加入**文新社DC群**！

            請至{mem.guild.get_channel(intro_channel_id).mention}發個簡短的自我介紹，
            讓我們更加認識你/妳喔！'''))


async def setup(bot: Bot) -> None:
    await bot.add_cog(
        LanmCog(bot),
        guild=discord.Object(lanm_id)
    )
    logger.info('loaded')
