import asyncio
from pathlib import Path
import discord
from discord.ext import commands
from discord.ext.commands import Context
from utils import Config


soyid = Config.users['soymilk'].id


# sync to all guilds in config.py
@commands.command()
async def sync(ctx: Context):
    if ctx.author.id != soyid:
        return
    await asyncio.gather(*[
        ctx.bot.tree.sync(guild=discord.Object(guild_id))
        # ctx.bot.tree.sync(guild=discord.Object(guild_id))
        for guild_id in Config.guilds.values()
    ])
    await ctx.send("commands synced to all guilds")


# sync to all
@commands.command()
async def syncall(ctx: Context):
    if ctx.author.id != soyid:
        return
    await ctx.bot.tree.sync()
    await ctx.send("commands synced to all guilds")


# reload extension
@commands.command()
async def reload(ctx: Context, query: str = None):
    if ctx.author.id != soyid:
        return

    exts = [p.stem for p in Path('./extensions').glob('*.py')]
    if query is not None:
        exts = list(filter(lambda ext: query in ext, exts))
    await asyncio.gather(*[
        ctx.bot.reload_extension(f'extensions.{ext}') for ext in exts
    ])
    await ctx.send(f'**{", ".join(exts)}** reloaded')


@commands.command()
async def test(ctx: commands.Context):
    await ctx.send(discord.Object(771595191638687784))
    await ctx.message.add_reaction(discord.Object(771595191638687784))


async def setup(bot: commands.Bot):
    bot.add_command(sync)
    bot.add_command(syncall)
    bot.add_command(reload)
    bot.add_command(test)
