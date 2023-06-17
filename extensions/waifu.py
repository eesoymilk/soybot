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
from bot import Soybot

log = get_lumberjack('waifu')
waifu_im_api = 'https://api.waifu.im'
sfw_choices = [Choice(name=opt,value=tag) for opt, tag in {
    'waifu-sfw_waifu': 'waifu',
    'waifu-sfw_uniform': 'uniform',
    'waifu-sfw_maid': 'maid',
    'waifu-sfw_mori-calliope': 'mori-calliope',
    'waifu-sfw_marin-kitagawa': 'marin-kitagawa',
    'waifu-sfw_raiden-shogun': 'raiden-shogun',
    'waifu-sfw_oppai': 'oppai',
    'waifu-sfw_selfies': 'selfies',
}.items()]
nsfw_choices = [Choice(name=opt,value=tag) for opt, tag in {
    'waifu-nsfw_hentai': 'hentai',
    'waifu-nsfw_milf': 'milf',
    'waifu-nsfw_oral': 'oral',
    'waifu-nsfw_paizuri': 'paizuri',
    'waifu-nsfw_ecchi': 'ecchi',
    'waifu-nsfw_ass': 'ass',
    'waifu-nsfw_ero': 'ero',
}.items()]

async def fetch_waifu(cs: ClientSession, url: str) -> dict:
    async with cs.get(url) as resp:
        data = await resp.json()

    image = data['images'][0]
    return image


def build_waifu_embed_view(title: str, image: dict) -> tuple[Embed, View]:
    tags = [t['name'] for t in image['tags']]
    embed = Embed(
        title=title,
        description=''.join([f'#{t}' for t in tags]),
        color=Color.from_str(image['dominant_color']),
        timestamp=datetime.fromisoformat(image['uploaded_at']),
    ).set_image(
        url=image['url'],
    ).set_footer(
        text='uploaded at'
    )
    view = View().add_item(Button(
        style=ButtonStyle.link,
        url=image['source'],
        label='查看圖源',
    ))

    return embed, view


class WaifuGroup(Group, name='waifu'):

    @ac.command(name='waifu-sfw')
    @ac.describe(tag='tag')
    @ac.choices(tag=sfw_choices)
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def sfw_coro(
        self,
        intx: Interaction,
        tag: Optional[Choice[str]] = None
    ):
        await intx.response.defer(thinking=True)

        url = f'{waifu_im_api}/search'
        if tag is not None:
            tag = tag.value
            title = tag
            url += f'?included_tags={tag}'
        else:
            title = 'Random'

        bot: Soybot = intx.client
        try:
            image = await fetch_waifu(bot.cs, url)
            embed, view = build_waifu_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except KeyError:
            await intx.followup.send('醒 你沒老婆')

    @ac.command(name='waifu-nsfw', nsfw=True)
    @ac.describe(tag='tag')
    @ac.choices(tag=nsfw_choices)
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

        url = f'{waifu_im_api}/search?is_nsfw=true'
        if tag is not None:
            title = tag.name_localizations[intx.locale.value]
            url += f'&included_tags={tag.value}'
        else:
            title = 'Random'

        bot: Soybot = intx.client
        try:
            image = await fetch_waifu(bot.cs, url)
        except KeyError:
            await intx.followup.send('不可以色色')
            return

        embed, view = build_waifu_embed_view(title, image)

        await intx.followup.send(embed=embed, view=view)


async def setup(bot: Bot):
    bot.tree.add_command(WaifuGroup())
    log.info(f'{__name__} loaded')
