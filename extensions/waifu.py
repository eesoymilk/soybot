from typing import Literal, Optional
from datetime import datetime
from aiohttp import ClientSession

from discord import (
    app_commands as ac,
    Interaction,
    Embed,
    Color,
    ButtonStyle
)
from discord.app_commands import Choice, Group
from discord.ext.commands import Bot
from discord.ui import View, Button

from utils import get_lumberjack, cd_but_soymilk
from utils.waifu_im import WaifuIm
from bot import Soybot

log = get_lumberjack(__name__)

class WaifuGroup(Group, name='waifu'):

    @ac.command(name='waifu-sfw')
    @ac.describe(tag='tag')
    @ac.choices(tag=WaifuIm.SFW_CHOICES)
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def sfw_coro(
        self,
        intx: Interaction,
        tag: Optional[Choice[str]] = None
    ):
        await intx.response.defer(thinking=True)

        url = f'{WaifuIm.BASE_URL}/search'
        if tag is not None:
            tag = tag.value
            title = tag
            url += f'?included_tags={tag}'
        else:
            title = 'Random'

        bot: Soybot = intx.client
        try:
            image = await WaifuIm.fetch(bot.cs, url)
            embed, view = WaifuIm.build_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except KeyError:
            await intx.followup.send('醒 你沒老婆')

    @ac.command(name='waifu-nsfw', nsfw=True)
    @ac.describe(tag='tag')
    @ac.choices(tag=WaifuIm.NSFW_CHOICES)
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def nsfw_coro(
        self,
        intx: Interaction,
        tag: Optional[Choice[str]] = None
    ):
        if not intx.channel.nsfw:
            return await intx.response.send_message(
                '😡😡請勿在非限制級頻道色色 **BONK!**\n' +
                '請至**限制級頻道**',
                ephemeral=True
            )

        await intx.response.defer(thinking=True)

        url = f'{WaifuIm.BASE_URL}/search?is_nsfw=true'
        if tag is not None:
            tag = tag.value
            title = tag
            url += f'&included_tags={tag}'
        else:
            title = 'Random'

        bot: Soybot = intx.client
        try:
            image = await WaifuIm.fetch(bot.cs, url)
        except KeyError:
            await intx.followup.send('不可以色色')
            return

        embed, view = WaifuIm.build_embed_view(title, image)

        await intx.followup.send(embed=embed, view=view)


async def setup(bot: Bot):
    bot.tree.add_command(WaifuGroup())
    log.info(f'{__name__} loaded')
