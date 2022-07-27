import asyncio
import discord
from pathlib import Path
from discord.ext import commands
from utils import Config

soyid = Config.users['soymilk'].id


# sync to all guilds in config.py
@commands.command()
async def sync(ctx: commands.Context):
    if ctx.author.id != soyid:
        return
    await asyncio.gather(*[
        ctx.bot.tree.sync(guild=discord.Object(guild_id))
        for guild_id in Config.guilds.values()
    ])
    ctx.send("commands synced to all guilds")


# reload extension
@commands.command()
async def reload(ctx: commands.Context, extension: str = None):
    if ctx.author.id != soyid:
        return
    if extension is not None:
        await ctx.bot.reload_extension(f'extensions.{extension}')
    else:
        exts = [f'extensions.{p.stem}'
                for p in Path('./src/extensions').glob('*.py')
                if p.stem not in ('__init__', 'utilities')]
        await asyncio.gather(*[ctx.bot.reload_extension(ext) for ext in exts])


async def setup(bot: commands.Bot):
    bot.add_command(sync)
    bot.add_command(reload)
