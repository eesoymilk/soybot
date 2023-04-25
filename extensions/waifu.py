import aiohttp

from datetime import datetime
from urllib.parse import urlencode, urlparse, urlunparse
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
from utils import get_lumberjack
from bot import Soybot

logger = get_lumberjack('waifu')
waifu_im_api = 'https://api.waifu.im/'


async def fetch_waifu(
    *,
    tag: Choice = None,
    is_nsfw: bool = False,
    many: bool = False
) -> tuple[Embed | list[Embed], View]:
    query_seq = []
    if tag is not None:
        query_seq.append(('included_tags', tag.value))
    if is_nsfw:
        query_seq.append(('is_nsfw', 'true'))
    if many:
        query_seq.append(('many', 'true'))

    url_parts = list(urlparse(waifu_im_api))
    url_parts[4] = urlencode(query_seq)
    url = urlunparse(url_parts)

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            data = await resp.json()
            try:
                if many:
                    ...
                else:
                    image = data['images'][0]
                    tags = [t['name'] for t in image['tags']]
                    embed = Embed(
                        title='隨機' if tag is None else tag.name,
                        description=''.join([f'#{t}' for t in tags]),
                        color=Color.from_str(image['dominant_color']),
                        timestamp=datetime.fromisoformat(image['uploaded_at']),
                    ).set_image(
                        url=image['url'],
                    ).set_footer(
                        text='uploaded at',
                    )
                    view = View().add_item(Button(
                        style=ButtonStyle.link,
                        url=image['source'],
                        label='查看圖源',
                    ))
                    return embed, view
            except KeyError:
                raise


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
    @ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def sfw_coro(self, intx: Interaction, tag: Choice[str] = None):
        await intx.response.defer(thinking=True)

        bot: Soybot = intx.client
        async with bot.session.get(waifu_im_api):
            ...
        
        try:
            embed, view = await fetch_waifu(tag=tag)
            await intx.followup.send(embed=embed, view=view)
        except:
            await intx.followup.send('醒 你沒老婆')
            raise

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
    async def nsfw_coro(self, intx: Interaction, tag: Choice[str] = None):
        if not intx.channel.nsfw:
            await intx.response.send_message(
                '😡😡請勿在非限制級頻道色色 **BONK!**\n請至**限制級頻道**',
                ephemeral=True
            )
            return

        await intx.response.defer(thinking=True)
        try:
            embed, view = await fetch_waifu(tag=tag, is_nsfw=True)
            await intx.followup.send(embed=embed, view=view)
        except:
            await intx.followup.send('不可以色色')
            raise


async def setup(bot: Bot) -> None:
    bot.tree.add_command(WaifuGroup())
    logger.info('loaded')
