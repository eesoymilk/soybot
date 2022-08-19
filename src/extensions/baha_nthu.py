import discord
import asyncio

from discord import app_commands as ac
from discord.ext import commands
from utils import ANSI
from utils import Config
from utils import get_lumberjack


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
nthu_guild_id = Config.guilds['nthu'].id


@ac.context_menu(name='憤怒狗狗')
@ac.guilds(nthu_guild_id)
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


async def setup(bot: commands.Bot):
    bot.tree.add_command(angry_dog_reactions)
    logger.info('loaded')
