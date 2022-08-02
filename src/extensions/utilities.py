import asyncio
from pathlib import Path
import discord
from discord.ext import commands
from utils import Config

soyid = Config.users['soymilk'].id


# sync to all guilds in config.py
@commands.command()
async def sync(ctx: commands.Context):
    if ctx.author.id != soyid:
        return
    await asyncio.gather(*[
        ctx.bot.tree.sync(guild=guild_id)
        # ctx.bot.tree.sync(guild=discord.Object(guild_id))
        for guild_id in Config.guilds.values()
    ])
    await ctx.send("commands synced to all guilds")


# reload extension
@commands.command()
async def reload(ctx: commands.Context, extension: str = None):
    if ctx.author.id != soyid:
        return
    if extension is not None:
        await ctx.bot.reload_extension(f'extensions.{extension}')
    else:
        exts = [f'extensions.{p.stem}'
                for p in Path('./src/extensions').glob('*.py')]
        await asyncio.gather(*[ctx.bot.reload_extension(ext) for ext in exts])


@commands.command()
async def test(ctx: commands.Context):
    await ctx.send(discord.Object(771595191638687784))
    await ctx.message.add_reaction(discord.Object(771595191638687784))


async def setup(bot: commands.Bot):
    bot.add_command(sync)
    bot.add_command(reload)
    bot.add_command(test)
