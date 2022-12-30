from dataclasses import dataclass
from datetime import datetime
from enum import IntEnum
import random
import discord

from discord.ext import commands
from textwrap import dedent
from utils import ANSI, get_lumberjack


log = get_lumberjack(__name__, ANSI.Yellow)


class MessageStreak:
    def __init__(self, message: discord.Message):
        self.channel = message.channel
        self.init_streak(message)

    def init_streak(self, message: discord.Message):
        self.content = message.content
        self.stickers = message.stickers
        self.reference = message.reference
        self.author_ids = [message.author.id]
        self.streak_count = 1

    async def do_streak(self, message: discord.Message):
        if not self.validate_streak(message):
            self.init_streak(message)
            return

        if self.reference is not None:
            ref_id = self.reference.message_id
            if not message.reference or message.reference.message_id != ref_id:
                self.reference = None

        self.author_ids.append(message.author.id)
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
                    '度度在拉屎',
                    '這裡不是洗版區喔 注意一下'
                ]))

    def validate_streak(self, message: discord.Message):
        if message.author.id in self.author_ids:
            return False
        if self.content and self.content == message.content:
            return True
        if self.stickers and self.stickers == message.stickers:
            return True
        return False


class StreakCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self._streaks: dict[int, MessageStreak] = dict()

    @commands.Cog.listener(name='on_message')
    async def message_streak(self, message: discord.Message):
        if not (message.guild) or message.author.bot:
            return

        # init a streak for a new channel
        if message.channel.id not in self._streaks:
            self._streaks[message.channel.id] = MessageStreak(message)
            return

        await self._streaks[message.channel.id].do_streak(message)


async def setup(bot: commands.Bot):
    await bot.add_cog(StreakCog(bot))
    log.info('loaded')
