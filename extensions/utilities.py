import asyncio
from pathlib import Path

from discord.ext.commands import command, Context, Bot
from utils import get_lumberjack

log = get_lumberjack(__name__)


@command()
async def sync(ctx: Context, prompt: str = None):
    if ctx.author != ctx.bot.owner:
        await ctx.send('You have no permissions')
        return

    await ctx.bot.tree.sync()
    await ctx.send('commands synced to all guilds')


@command()
async def reload(ctx: Context, query: str = None):
    if ctx.author != ctx.bot.owner:
        await ctx.send('You have no permissions')
        return

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
