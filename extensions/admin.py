import os
import asyncio
from pathlib import Path
from typing import Optional, Literal

from discord import Object, HTTPException, Embed
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
        *prompts: str
    ):
        try:
            exts = self.find_extensions(prompts)
        except ValueError as e:
            log.exception(e)
            return await ctx.send(
                f'Unrecognized extension(s): {e}'
            )

        # Python 3.11+
        async with asyncio.TaskGroup() as tg:
            tasks = [tg.create_task(
                ctx.bot.reload_extension(ext)
            ) for ext in exts]

        await ctx.send(f'**{"**, **".join(exts)}** reloaded')

    def find_extension(self, prompt: str):
        if os.path.isfile(Path('./extensions')/f'{prompt}.py'):
            return f'extensions.{prompt}'

        return next((
            ext
            for ext in self.bot.extensions.keys()
            if prompt in ext
        ))

    def find_extensions(self, prompts: tuple[str]):
        if not prompts:
            return self.bot.extensions.keys()

        exts = []
        failed_prompts = []
        for prompt in prompts:
            try:
                exts.append(self.find_extension(prompt))
            except StopIteration as e:
                log.exception(f'Unrecognized extension: {prompt}')
                failed_prompts.append(prompt)

        if exts:
            return exts

        raise ValueError(f'**{", ".join(failed_prompts)}**')


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
