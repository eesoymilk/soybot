from dataclasses import dataclass, field
import random
from textwrap import dedent
import discord
import asyncio

from discord import app_commands as ac, Message, Member
from discord.ext import commands
from discord.ext.commands import Cog, Bot
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


@dataclass(order=True, unsafe_hash=True)
class SolitaireTracker:
    sequence: list[str] = field(hash=False, compare=False)
    index: int = field(hash=True)
    state: int = field(default=1, hash=False, compare=False)


class NthuCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self._streaks: dict[int, MessageStreak] = dict()
        self._solitaires: dict[int, set[SolitaireTracker]] = dict()

    @commands.Cog.listener()
    async def on_member_join(self, mem: Member) -> None:
        if mem.guild.id != NTHU.guild_id:
            return

        await mem.guild.system_channel.send(dedent(f'''\
            歡迎{mem.mention}加入**{mem.guild.name}**！

            請至{mem.guild.get_channel(NTHU.intro_channel_id).mention}留下您的系級和簡短的自我介紹，
            讓我們更加認識你/妳喔！'''))

    @commands.Cog.listener(name='on_message')
    async def auto_respond(self, msg: Message):
        if msg.guild.id != NTHU.guild_id:
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
        # ignore own message and bots
        if msg.author.id == self.bot.user.id or msg.author.bot:
            return

        if msg.channel.id not in self._streaks:
            self._streaks[msg.channel.id] = MessageStreak(msg)
            return

        if is_cohesive(msg, self._streaks[msg.channel.id].last_message):
            self._streaks[msg.channel.id].count += 1
        else:
            self._streaks[msg.channel.id].count = 1

        if self._streaks[msg.channel.id].count == 3:
            await msg.channel.send(msg.content, stickers=msg.stickers)

        self._streaks[msg.channel.id].last_message = msg

    @Cog.listener(name='on_message')
    async def message_solitaire(self, msg: Message):
        if msg.guild.id != Config.guilds['debug']:
            return

        content, cid = msg.content, msg.channel.id

        if cid not in self._solitaires:
            self._solitaires[cid] = set()
        if not content:
            self._solitaires[cid].clear()

        # process ongoing solitaires
        for soli in self._solitaires[cid].copy():
            next_kw = soli.sequence[soli.state + 1]
            if next_kw in content and content.index(next_kw) == soli.index:
                soli.state += 1
                if soli.state == len(soli.sequence):
                    print(f'Solitaire {"".join(soli.sequence)} Completed!')
                else:
                    print(
                        f'Solitaire {"".join(soli.sequence)} State: {soli.state}')
                    continue
            self._solitaires[cid].remove(soli)

        # detect new solitarires
        for seq in solitaire_seqences:
            if seq[0] in content:
                new_index = content.index(seq[0])
                # prevent multiple solitaires on the same index
                if all(new_index != soli.index for soli in self._solitaires[cid]):
                    print('soli added')
                    self._solitaires[cid].add(SolitaireTracker(seq, new_index))


async def setup(bot: Bot):
    bot.tree.add_command(angry_dog_reactions)
    await bot.add_cog(
        NthuCog(bot),
        guild=discord.Object(NTHU.guild_id)
    )
    logger.info('loaded')
