from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import random
import discord
import asyncio

from discord import app_commands
from discord.ext import commands
from textwrap import dedent
from utils import ANSI, Config, get_lumberjack

nthu_guild_id = 771595191638687784
log = get_lumberjack('NTHU', ANSI.Yellow)
angry_dogs_emojis = (
    '<:D11angrydog:946700998024515635>',
    '<:D121notangrydog:976082704275763210>',
    '<:D12angrydog_hat:991677468794703914>',
    '<:D12angrydog_mag:953983783995068436>',
    '<a:D12angrydog_rainbow:991676465764638810>',
    '<a:D12angrydog_shake:991676443174129764>',
    '<:D12angrydog_sleep:991677470216552620>',
    '<:D12angrydog_starburst:991676592533295164>',
    '<:D6AwkChiwawa:791134264842387496>',
    '<:D87dog:980870480804339712>',
)
ugly_dogs_emojis = (
    '<:D5NonChiwawa:791134356563034122>',
    '<:D7Chiwawa:958419880997171290>',
    '<:D7MuchUglierChiwawa:1052637556388397167>',
    '<:D7UglierChiwawa:1052638311539277844>',
    '<:D86gaydog:982197038382985246>',
    '<:Dg8dog:1052636415260897360>',
)


@app_commands.context_menu(name='憤怒狗狗')
@app_commands.guilds(nthu_guild_id)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def angry_dog_react(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True, thinking=True)
    await asyncio.gather(*(
        message.add_reaction(emoji)
        for emoji in angry_dogs_emojis
    ))
    await interaction.followup.send(content='**憤怒狗狗**已送出')


@app_commands.context_menu(name='醜狗醜醜')
@app_commands.guilds(nthu_guild_id)
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def ugly_dog_react(interaction: discord.Interaction, message: discord.Message):
    await interaction.response.defer(ephemeral=True, thinking=True)
    await asyncio.gather(*(
        message.add_reaction(emoji)
        for emoji in ugly_dogs_emojis
    ))
    await interaction.followup.send(content='**醜狗醜醜**已送出')


class NthuCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.guild = self.bot.get_guild(nthu_guild_id)
        if self.guild is not None:
            self.daily_bs_channel = self.guild.get_channel(
                771596516443029516)

    @commands.Cog.listener()
    async def on_member_join(self, mem: discord.Member) -> None:
        if mem.guild.id != nthu_guild_id:
            return

        await mem.guild.system_channel.send(dedent(f'''\
            歡迎{mem.mention}加入**{mem.guild.name}**！

            請至{mem.guild.get_channel(771684498986500107).mention}留下您的系級和簡短的自我介紹，
            讓我們更加認識你/妳喔！'''))

    @commands.Cog.listener()
    async def on_user_update(self, before: discord.User, after: discord.User):
        if self.guild is None:
            self.guild = await self.bot.fetch_guild(nthu_guild_id)

        try:
            if (member := self.guild.get_member(before.id)) is None:
                member = await self.guild.fetch_member(before.id)
        except discord.NotFound:
            return

        if before.avatar == after.avatar or before.id not in Config.user_ids:
            return

        try:
            if self.daily_bs_channel is None:
                self.daily_bs_channel = await self.guild.fetch_channel(771596516443029516)
        except discord.NotFound:
            return

        await self.daily_bs_channel.send(
            f'主要！ **{member.mention}**又換頭貼了！',
            embed=discord.Embed(
                description='➡原頭貼➡\n\n⬇新頭貼⬇',
                color=member.color,
                timestamp=datetime.now(),
            ).set_thumbnail(
                url=before.avatar
            ).set_image(
                url=after.avatar
            ))


async def setup(bot: commands.Bot):
    bot.tree.add_command(angry_dog_react)
    bot.tree.add_command(ugly_dog_react)
    await bot.add_cog(
        NthuCog(bot),
        guild=discord.Object(nthu_guild_id)
    )
    log.info('loaded')
