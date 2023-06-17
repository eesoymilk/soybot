import os
import asyncio
from pathlib import Path
from typing import Optional, Literal

from discord import Object, HTTPException
from discord.ext import commands
from discord.ext.commands import (
    Cog,
    Context,
    Greedy,
    Bot
)

from utils import get_lumberjack

log = get_lumberjack(__name__)


class AdminCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot

    @commands.command(help='Sync commands', aliases=['s'])
    @commands.guild_only()
    @commands.is_owner()
    async def sync(
        self,
        ctx: Context,
        guilds: Greedy[Object],
        spec: Optional[Literal['~', '*', '^']] = None
    ):
        if not guilds:
            if spec == '~':
                log.info('Syncing to current guild...')
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == '*':
                ctx.bot.tree.copy_global_to(guild=ctx.guild)
                synced = await ctx.bot.tree.sync(guild=ctx.guild)
            elif spec == '^':
                ctx.bot.tree.clear_commands(guild=ctx.guild)
                await ctx.bot.tree.sync(guild=ctx.guild)
                synced = []
            else:
                log.info('Syncing globally...')
                synced = await ctx.bot.tree.sync()

            msg = f'Synced {len(synced)} commands {"globally" if spec is None else "to the current guild."}'
            log.info(msg)
            await ctx.send(msg)

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

    @commands.command(help='Reload extensions', aliases=['r', 're'])
    @commands.guild_only()
    @commands.is_owner()
    async def reload(
        self,
        ctx: Context,
        *exts_prompt: str
    ):
        if not exts_prompt or '*' in exts_prompt:
            exts = list(ctx.bot.extensions.keys())
        else:
            exts = []
            for ext in exts_prompt:
                path = Path('./extensions')/f'{ext}.py'
                if os.path.isfile(path):
                    exts.append(f'extensions.{ext}')

        if not exts:
            return await ctx.send(f'Unrecognized extension(s)')

        # Python 3.11+
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(ctx.bot.reload_extension(ext))
                     for ext in exts]

        await ctx.send(f'**{"**, **".join(exts)}** reloaded')


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
