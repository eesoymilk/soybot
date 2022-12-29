import discord

from discord import (app_commands as ac, Embed, Member, Interaction)
from discord.ext.commands import Bot
from utils import ANSI
from utils import get_lumberjack
from utils.config import Config
from extensions.autoresponse import fetch_author_responses

log = get_lumberjack(__name__, ANSI.Yellow)


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


async def avatar(interaction: Interaction, target: Member):
    if target.id == interaction.client.user.id:
        await interaction.response.send_message(f'不要ㄐ查豆漿ㄐㄐ人好ㄇ', ephemeral=True)
        return

    await interaction.response.defer()

    if isinstance(target, Member):
        avatar_url = target.display_avatar.url
    else:
        avatar_url = target.avatar.url
    description = f'**{interaction.user.display_name}**稽查了{f"{target.mention}" if interaction.user.id != target.id else "自己"}'
    embed = Embed(
        description=description,
        # description=target.nick if target.nick is not None else None,
        color=target.color,
        timestamp=target.joined_at,
    ).set_author(
        name=target,
        icon_url=target.avatar,
    ).set_footer(
        text=f'加入 {interaction.guild.name}',
        icon_url=interaction.guild.icon,
    )

    fetched_target = await interaction.client.fetch_user(target.id)
    if fetched_target.banner is not None:
        embed.set_thumbnail(
            url=avatar_url
        ).set_image(
            url=fetched_target.banner
        )
    else:
        embed.set_image(url=avatar_url)

    autoreaction = (await fetch_author_responses(interaction.client, interaction.guild)).get(target.id)

    if autoreaction is not None:
        embed.add_field(
            name=f'自動表情 (觸發機率 {autoreaction.rate})',
            value=' '.join(autoreaction.responses)
        )

    await interaction.followup.send(embed=embed)

    log_details = {
        'guild': interaction.guild.name,
        'channel': interaction.channel.name,
        'display_name': interaction.user.display_name,
        'receiver': target.display_name,
    }
    log.info(rich_logging_formatter(**log_details))


@ac.command(name="avatar", description='稽查')
@ac.rename(target='稽查對象')
async def avatar_slash(interaction: discord.Interaction, target: discord.Member) -> None:
    await avatar(interaction, target)


@ac.context_menu(name='稽查頭貼')
async def avatar_ctx_menu(interaction: discord.Interaction, target: discord.Member):
    await avatar(interaction, target=target)


async def setup(bot: Bot):
    bot.tree.add_command(avatar_slash)
    bot.tree.add_command(avatar_ctx_menu)
    log.info('extension loaded')
