import asyncio
from pathlib import Path
from typing import Optional, Literal

from discord import Object, HTTPException
from discord.ext.commands import (
    command,
    guild_only,
    is_owner,
    Context,
    Greedy,
    Bot
)
from utils import get_lumberjack

log = get_lumberjack(__name__)


@command()
@guild_only()
@is_owner()
async def sync(
    ctx: Context,
    guilds: Greedy[Object],
    spec: Optional[Literal['~', '*', '^']] = None
):
    if not guilds:
        if spec == '~':
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == '*':
            ctx.bot.tree.copy_global_to(guild=ctx.guild)
            synced = await ctx.bot.tree.sync(guild=ctx.guild)
        elif spec == '^':
            ctx.bot.tree.clear_commands(guild=ctx.guild)
            await ctx.bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            synced = await ctx.bot.tree.sync()

        await ctx.send(
            f'Synced {len(synced)} commands {"globally" if spec is None else "to the current guild."}'
        )
        return

    ret = 0
    for guild in guilds:
        try:
            await ctx.bot.tree.sync(guild=guild)
        except HTTPException:
            pass
        else:
            ret += 1

    await ctx.send(f'Synced the tree to {ret}/{len(guilds)}.')


@command()
@guild_only()
@is_owner()
async def reload(ctx: Context, query: str = None):
    exts = [p.stem for p in Path('./extensions').glob('*.py')]
    if query is not None:
        exts = list(filter(lambda ext: query in ext, exts))

    await asyncio.gather(*[
        ctx.bot.reload_extension(f'extensions.{ext}') for ext in exts
    ])
    await ctx.send(f'**{", ".join(exts)}** reloaded')


async def setup(bot: Bot):
    bot.add_command(sync)
    bot.add_command(reload)
    log.info(f'{__name__} loaded')
