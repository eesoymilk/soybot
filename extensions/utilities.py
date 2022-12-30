import asyncio
from pathlib import Path
from discord.ext import commands

soyid = 202249480148353025


# sync commands
@commands.command()
async def sync(ctx: commands.Context, prompt: str = None):
    if ctx.author.id != soyid:
        return

    if prompt is None:
        await ctx.bot.tree.sync()
        await ctx.send("commands synced to all guilds")
        return

    if prompt == 'nthu':
        await ctx.bot.tree.sync(771595191638687784)
        await ctx.send("commands synced to nthu guild")

    elif prompt == 'debug':
        await ctx.bot.tree.sync(874556062815100938)
        await ctx.send("commands synced to eeSoycord guild")

    elif prompt == 'test':
        await asyncio.gather(
            ctx.bot.tree.sync(771595191638687784),
            ctx.bot.tree.sync(874556062815100938)
        )
        await ctx.send("commands synced to both nthu and eeSoycord guilds")
    else:
        await ctx.send("invalid prompt")


# reload extension
@commands.command()
async def reload(ctx: commands.Context, query: str = None):
    if ctx.author.id != soyid:
        return

    exts = [p.stem for p in Path('./extensions').glob('*.py')]
    if query is not None:
        exts = list(filter(lambda ext: query in ext, exts))
    await asyncio.gather(*[
        ctx.bot.reload_extension(f'extensions.{ext}') for ext in exts
    ])
    await ctx.send(f'**{", ".join(exts)}** reloaded')


async def setup(bot: commands.Bot):
    bot.add_command(sync)
    bot.add_command(reload)
