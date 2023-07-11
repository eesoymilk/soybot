import os
import asyncio
from pathlib import Path
from typing import Optional, Literal

from discord import Object, Guild, HTTPException
from discord.ext import commands
from discord.ext.commands import (
    Cog,
    Context,
    Greedy,
    Bot
)

from utils import get_lumberjack
from bot import Soybot

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
        bot: Soybot = ctx.bot

        if guilds:
            ret = 0
            for guild in guilds:
                try:
                    await bot.tree.sync(guild=guild)
                except HTTPException:
                    pass
                else:
                    ret += 1

            return await ctx.send(f'Synced the tree to {ret}/{len(guilds)}.')

        if spec == '~':
            log.info('Syncing to current guild...')
            synced = await bot.tree.sync(guild=ctx.guild)
        elif spec == '*':
            bot.tree.copy_global_to(guild=ctx.guild)
            synced = await bot.tree.sync(guild=ctx.guild)
        elif spec == '^':
            bot.tree.clear_commands(guild=ctx.guild)
            await bot.tree.sync(guild=ctx.guild)
            synced = []
        else:
            log.info('Syncing globally...')
            synced = await bot.tree.sync()

        msg = f'Synced {len(synced)} commands {"globally" if spec is None else "to the current guild."}'
        log.info(msg)
        await ctx.send(msg)

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

    # This command update all custom emojis, stickers and users
    # in the guilds specified
    @commands.command(
        help='Database Management Command',
        aliases=['db', 'sql']
    )
    @commands.is_owner()
    async def db_coro(
        self,
        ctx: Context,
        guilds: Greedy[Object],
        spec: Optional[str] = None
    ):
        await ctx.channel.send('Updating db...')

        bot: Soybot = ctx.bot

        if guilds:
            guilds = [await bot.fetch_guild(g.id) for g in guilds]
        elif spec == '*':
            guilds = [g async for g in bot.fetch_guilds()]
        else:
            guilds = [ctx.guild]

        await self.update_guilds(guilds)

    def find_extension(self, prompt: str):
        if os.path.isfile(Path('./extensions')/f'{prompt}.py'):
            return f'extensions.{prompt}'

        return next((
            ext
            for ext in self.bot.extensions.keys()
            if prompt in ext.split('.')[1]
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

    async def update_stickers(self, guild: Guild) -> int:
        ...

    async def update_custom_emojis(self, guild: Guild) -> int:
        ...

    async def update_guild(self, guild: Guild) -> tuple[int, int]:
        ...

    async def update_guilds(self, *guilds: Guild) -> int:
        for g in guilds:
            self.update_guild(g)


async def setup(bot: Bot):
    await bot.add_cog(AdminCog(bot))
