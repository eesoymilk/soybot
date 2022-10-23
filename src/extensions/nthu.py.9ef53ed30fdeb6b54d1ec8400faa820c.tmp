from dataclasses import dataclass
from enum import IntEnum
import random
import discord
import asyncio

from discord import app_commands as ac, Message, Member, User, StickerItem
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


def do_chance(x: float = 1.0) -> bool:
    return x > random.random()


async def react_msg(soy_react: SoyReact, msg: discord.Message, bot: commands.Bot):
    if soy_react is None or not do_chance(soy_react.activation_probability):
        return

    matched_ids = Config.get_emoji_ids_by_tags(*soy_react.emoji_tags)
    emojis = [id if isinstance(id, str) else bot.get_emoji(id)
              for id in random.sample(matched_ids, soy_react.count)]
    await asyncio.gather(*(msg.add_reaction(emoji) for emoji in emojis))


class ResponseType(IntEnum):
    React = 1
    Reply = 2
    Sticker = 3


nthu_users = {
    'soymilk': {
        'id': 202249480148353025,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('soymilk', 'pineapplebun'),
            'chance': 0.1
        }
    },
    'gay_dog': {
        'id': 284350778087309312,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('disgusted',),
            'chance': 0.4
        }
    },
    'howard': {
        'id': 613683023300395029,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('wtf',),
            'chance': 0.3
        }
    },
    'ayu': {
        'id': 557591275227054090,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('gay',),
            'chance': 0.4
        }
    },
    'snow': {
        'id': 565862991061581835,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('gay',),
            'chance': 0.3
        }
    },
    'paper': {
        'id': 402060040518762497,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('gay',),
            'chance': 0.3
        }
    },
    'feilin': {
        'id': 388739972343267329,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('feilin',),
            'chance': 0.3
        }
    },
    'shili': {
        'id': 777196949903376396,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('pineapplebun',),
            'chance': 0.3
        }
    },
    'dodo': {
        'id': 618679878144753664,
        'soy_response': {
            'response_type': ResponseType.React,
            'pool': ('dodo',),
            'chance': 0.1
        }
    }
}


@dataclass
class SoyResponse:
    resp_type: ResponseType
    pool: list[str | StickerItem]
    chance: float

    async def respond(self, resp_cxt):
        if self.resp_type == ResponseType.React:
            ...
        elif self.resp_type == ResponseType.Reply:
            ...
        elif self.resp_type == ResponseType.Sticker:
            ...


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
        if before.guild_avatar == after.guild_avatar:
            return

    @Cog.listener(name='on_message')
    async def auto_respond(self, msg: Message):
        if not (msg.guild and msg.guild.id == NTHU.guild_id):
            return
        # process author

        # process content
        aws = []
        soy_react, _ = Config.get_action_by_user_id(msg.author.id)
        aws.append(react_msg(soy_react, msg, self.bot))
        await asyncio.gather(*aws)

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
    await bot.add_cog(
        NthuCog(bot),
        guild=discord.Object(NTHU.guild_id)
    )
    logger.info('loaded')
