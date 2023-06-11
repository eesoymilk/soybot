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

    @ac.command(
        name='抽老婆',
        description='這我婆 那我婆 這個也我婆'
    )
    @ac.describe(tag='你今天要哪種老婆')
    @ac.rename(tag='老婆類型')
    @ac.choices(
        tag=[
            Choice(
                name=option,
                value=tag_name
            ) for option, tag_name in {
                '老婆': 'waifu',
                '制服': 'uniform',
                '女僕': 'maid',
                '森美聲': 'mori-calliope',
                '喜多川海夢': 'marin-kitagawa',
                '原神 雷電將軍': 'raiden-shogun',
                '大奶': 'oppai',
                '自拍': 'selfies',
            }.items()
        ]
    )
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def sfw_coro(self, intx: Interaction, tag: Choice[str] = None):
        await intx.response.defer(thinking=True)
        
        if tag is not None:
            title = tag.name
            url = f'{waifu_im_api}/search?included_tags={tag.value}'
        else:
            title = '隨機'
            url = f'{waifu_im_api}/search'

        bot: Soybot = intx.client
        try:
            image = await fetch_waifu(bot.cs, url)
            embed, view = build_waifu_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except KeyError:
            await intx.followup.send('醒 你沒老婆')
        

    @ac.command(
        name='可以色色',
        description='社會性死亡注意!',
        nsfw=True
    )
    @ac.describe(tag='你今天想要哪種色色')
    @ac.rename(tag='色色類型')
    @ac.choices(
        tag=[
            Choice(
                name=option,
                value=tag_name
            ) for option, tag_name in {
                'Hentai': 'hentai',
                '人妻': 'milf',
                '咬': 'oral',
                '大奶': 'paizuri',
                'H': 'ecchi',
                '尻': 'ass',
                '色色': 'ero',
            }.items()
        ]
    )
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def nsfw_coro(self, intx: Interaction, tag: Choice[str] = None):
        if not intx.channel.nsfw:
            await intx.response.send_message(
                '😡😡請勿在非限制級頻道色色 **BONK!**\n' + 
                '請至**限制級頻道**',
                ephemeral=True)
            return
        
        await intx.response.defer(thinking=True)
        
        url = f'{waifu_im_api}/search?is_nsfw=true'
        if tag is not None:
            title = tag.name
            url += f'&included_tags={tag.value}'
        else:
            title = '隨機'

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
