import random
import discord
import asyncio

from discord import app_commands as ac, Message, Member, User
from discord.ext import commands
from discord.ext.commands import Cog, Bot
from dataclasses import dataclass
from textwrap import dedent
from utils import NTHU, ANSI, Config, get_lumberjack, SoyReact, SoyReply


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
solitaire_seqences = {
    'starburst': ('s', 't', 'a', 'r'),
}


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


def chance(x: float = 1.0) -> bool:
    return x > random.random()


async def react_msg(soy_react: SoyReact, msg: discord.Message, bot: commands.Bot):
    if soy_react is None or not chance(soy_react.activation_probability):
        return

    matched_ids = Config.get_emoji_ids_by_tags(*soy_react.emoji_tags)
    emojis = [id if isinstance(id, str) else bot.get_emoji(id)
              for id in random.sample(matched_ids, soy_react.count)]
    await asyncio.gather(*(msg.add_reaction(emoji) for emoji in emojis))


async def reply_msg(soy_reply: SoyReply, msg: discord.Message, bot: commands.Bot):
    ...


def is_cohesive(a: Message, b: Message) -> bool:
    if a.author == b.author:
        return False
    if a.content and a.content == b.content:
        return True
    if a.stickers and a.stickers == b.stickers:
        return True
    return False


@dataclass
class MessageStreak:
    last_message: Message
    count: int = 1


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
        if not (msg.guild or msg.guild.id == NTHU.guild_id):
            return
        # process author

        # process content
        aws = []
        soy_react, soy_reply = Config.get_action_by_user_id(msg.author.id)
        aws.append(react_msg(soy_react, msg, self.bot))
        aws.append(reply_msg(soy_reply, msg, self.bot))
        await asyncio.gather(*aws)

    @commands.Cog.listener(name='on_message')
    async def message_streak(self, msg: Message):
        if not (msg.guild or msg.guild.id == NTHU.guild_id) or msg.author.bot:
            return

        # init a streak for a new channel
        if msg.channel.id not in self._streaks:
            self._streaks[msg.channel.id] = MessageStreak(msg)
            return

        # reset the streak due to a different msg
        if not is_cohesive(msg, self._streaks[msg.channel.id].last_message):
            self._streaks[msg.channel.id].count = 1
            self._streaks[msg.channel.id].last_message = msg
            return

        self._streaks[msg.channel.id].count += 1

        if msg.author.id == self.bot.user.id:
            return

        if self._streaks[msg.channel.id].count == 3:
            await msg.channel.send(msg.content, stickers=msg.stickers)


async def setup(bot: Bot):
    bot.tree.add_command(angry_dog_reactions)
    await bot.add_cog(
        NthuCog(bot),
        guild=discord.Object(NTHU.guild_id)
    )
    logger.info('loaded')
