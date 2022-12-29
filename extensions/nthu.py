from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import random
import discord
import asyncio

from discord import app_commands as ac, Message, Member, User, StickerItem, Embed, NotFound
from discord.ext import commands
from discord.ext.commands import Cog, Bot
from textwrap import dedent
from utils import NTHU, ANSI, Config, get_lumberjack, SoyReact


def rich_logging_formatter(guild, channel=None, display_name=None, receiver=None, emoji=None, content=None) -> str:
    log_msg = ''

    if guild is not None:
        log_msg += f'{ANSI.BackgroundWhite}{ANSI.BrightBlack}{guild}{ANSI.Reset}'
    if channel is not None:
        log_msg += f'{ANSI.BackgroundWhite}{ANSI.BrightBlack} - {channel}{ANSI.Reset}'
    if display_name is not None:
        log_msg += f' {ANSI.Blue}{display_name}{ANSI.Reset}'
    if receiver is not None:
        log_msg += f'{ANSI.Blue} -> {receiver}{ANSI.Reset}'
    if emoji is not None:
        log_msg += f' {emoji}'
    if content is not None:
        log_msg += f': {content}'

    return log_msg


logger = get_lumberjack('NTHU', ANSI.Yellow)


@ac.context_menu(name='憤怒狗狗')
@ac.guilds(NTHU.guild_id)
@ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def angry_dog_reactions(interaction: discord.Interaction, message: discord.Message):
    log_details = {
        'guild': message.channel.guild.name,
        'channel': message.channel.name,
        'display_name': interaction.user.display_name,
        'receiver': message.author.display_name,
    }
    await interaction.response.defer(ephemeral=True, thinking=True)
    logger.info(rich_logging_formatter(**log_details))
    await asyncio.gather(*(
        message.add_reaction(emoji)
        for emoji in [interaction.client.get_emoji(id)
                      for id in Config.get_emoji_ids_by_tags('dog_bundle')]
    ))
    await interaction.followup.send(content='**憤怒狗狗**已送出')


@ac.context_menu(name='阿袋狗狗')
@ac.guilds(NTHU.guild_id)
@ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def ugly_dog_reactions(interaction: discord.Interaction, message: discord.Message):
    log_details = {
        'guild': message.channel.guild.name,
        'channel': message.channel.name,
        'display_name': interaction.user.display_name,
        'receiver': message.author.display_name,
    }
    await interaction.response.defer(ephemeral=True, thinking=True)
    logger.info(rich_logging_formatter(**log_details))

    emojis = []

    for id in Config.get_emoji_ids_by_tags('ugly_dog'):
        emoji = interaction.client.get_emoji(id)
        if emoji is not None:
            emojis.append(emoji)

    await asyncio.gather(*(message.add_reaction(emoji) for emoji in emojis))

    # await asyncio.gather(*(
    #     message.add_reaction(emoji)
    #     for emoji in [interaction.client.get_emoji(id)
    #                   for id in Config.get_emoji_ids_by_tags('ugly_dog')]
    # ))
    await interaction.followup.send(content='**阿袋狗狗**已送出')


class MessageStreak:
    def __init__(self, msg: Message):
        self.channel = msg.channel
        self._new_streak(msg)

    def _new_streak(self, msg: Message):
        self.content = msg.content
        self.stickers = msg.stickers
        self.reference = msg.reference
        self.author_ids = {msg.author.id}
        self.streak_count = 1

    async def do_streak(self, msg: Message):
        if not self.validate_streak(msg):
            self._new_streak(msg)
            return

        if self.reference is not None:
            if msg.reference is None or msg.reference.message_id != self.reference.message_id:
                self.reference = None

        self.author_ids.add(msg.author.id)
        self.streak_count += 1

        if self.streak_count == 3:
            self.streak_count += 1
            await self.channel.send(
                self.content,
                stickers=self.stickers,
                reference=self.reference
            )
        elif self.streak_count > 4:
            if random.random() <= 0.3:
                await self.channel.send(random.choice([
                    '阿玉在洗版',
                    '阿雪在洗版',
                    '這裡不是洗版區喔 注意一下'
                ]))

    def validate_streak(self, msg: Message):
        if msg.author.id in self.author_ids:
            return False
        if self.content and self.content == msg.content:
            return True
        if self.stickers and self.stickers == msg.stickers:
            return True
        return False


class NthuCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._streaks: dict[int, MessageStreak] = dict()

    @Cog.listener()
    async def on_member_join(self, mem: Member) -> None:
        if mem.guild.id != NTHU.guild_id:
            return

        await mem.guild.system_channel.send(dedent(f'''\
            歡迎{mem.mention}加入**{mem.guild.name}**！

            請至{mem.guild.get_channel(NTHU.intro_channel_id).mention}留下您的系級和簡短的自我介紹，
            讓我們更加認識你/妳喔！'''))

    @Cog.listener()
    async def on_user_update(self, before: User, after: User):
        daily_chat_channel_id = 771596516443029516
        nthu_guild_id = Config.guilds['nthu']

        if (nthu_guild := self.bot.get_guild(nthu_guild_id)) is None:
            nthu_guild = await self.bot.fetch_guild(nthu_guild_id)

        try:
            if (member := nthu_guild.get_member(before.id)) is None:
                member = await nthu_guild.fetch_member(before.id)
        except NotFound:
            return

        if before.avatar == after.avatar or before.id not in Config.user_ids:
            return

        try:
            if (daily_chat_channel := nthu_guild.get_channel(daily_chat_channel_id)) is None:
                daily_chat_channel = await nthu_guild.fetch_channel(daily_chat_channel_id)
        except NotFound:
            return

        await daily_chat_channel.send(f'主要！ **{member.mention}**又換頭貼了！', embed=Embed(
            description='➡原頭貼➡\n\n⬇新頭貼⬇',
            color=member.color,
            timestamp=datetime.now(),
        ).set_thumbnail(
            url=before.avatar
        ).set_image(
            url=after.avatar
        ))

    @commands.Cog.listener(name='on_message')
    async def message_streak(self, msg: Message):
        if not (msg.guild and msg.guild.id == NTHU.guild_id) or msg.author.bot:
            return

        cid = msg.channel.id

        # init a streak for a new channel
        if cid not in self._streaks:
            self._streaks[cid] = MessageStreak(msg)
            return

        await self._streaks[cid].do_streak(msg)


async def setup(bot: Bot):
    bot.tree.add_command(angry_dog_reactions)
    bot.tree.add_command(ugly_dog_reactions)
    await bot.add_cog(
        NthuCog(bot),
        guild=discord.Object(NTHU.guild_id)
    )
    logger.info('loaded')
