from asyncio.log import logger
from datetime import datetime
import discord
import aiohttp
from urllib.parse import urlencode, urlparse, urlunparse
from discord import app_commands as ac, Color, Embed, Interaction
from discord.app_commands import Choice, Group
from discord.ext import commands
from discord.ui import View, Button
from utils import Config, get_lumberjack

logger = get_lumberjack('waifu')
waifu_im_url = 'https://api.waifu.im/random/'
all_tags = {
    'sfw': {
        '老婆': 'waifu',
        '制服': 'uniform',
        '女僕': 'maid',
        '森美聲': 'mori-calliope',
        '喜多川海夢': 'marin-kitagawa',
        '原神 雷電將軍': 'raiden-shogun',
        '大奶': 'oppai',
        '自拍': 'selfies',
    },
    'nsfw': {
        'Hentai': 'hentai',
        '人妻': 'milf',
        '咬': 'oral',
        '大奶': 'paizuri',
        'H': 'ecchi',
        '尻': 'ass',
        '色色': 'ero',
    },
}


async def fetch_waifu(
    *,
    tag: Choice = None,
    is_nsfw: bool = False,
    many: bool = False
) -> tuple[Embed | list[Embed], View]:
    query_seq = []
    if tag is not None:
        query_seq.append(('selected_tags', tag.value))
    if is_nsfw:
        query_seq.append(('is_nsfw', 'true'))
    if many:
        query_seq.append(('many', 'true'))

    url_parts = list(urlparse(waifu_im_url))
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
                        style=discord.ButtonStyle.link,
                        url=image['source'],
                        label='查看圖源',
                    ))
                    return embed, view
            except KeyError:
                raise


@ac.guilds(*Config.guild_ids)
class WaifuGroup(Group, name='waifu'):

    @ac.command(name='抽老婆', description='聽說紙袋又換婆了?')
    @ac.describe(tag='你今天要哪種老婆')
    @ac.rename(tag='老婆類型')
    @ac.choices(tag=[Choice(name=k, value=v) for k, v in all_tags['sfw'].items()])
    @ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
    async def sfw_coro(self, interaction: Interaction, tag: Choice[str] = None):
        await interaction.response.defer(thinking=True)
        try:
            embed, view = await fetch_waifu(tag=tag)
            await interaction.followup.send(embed=embed, view=view)
        except:
            await interaction.followup.send('醒 你沒老婆')
            raise

    @ac.command(name='可以色色', description='社會性死亡注意!!!', nsfw=True)
    @ac.describe(tag='你今天想要哪種色色')
    @ac.rename(tag='色色類型')
    @ac.choices(tag=[Choice(name=k, value=v) for k, v in all_tags['nsfw'].items()])
    async def nsfw_coro(self, interaction: Interaction, tag: Choice[str] = None):
        if not interaction.channel.nsfw:
            await interaction.response.send_message(
                '😡😡請勿在非限制級頻道色色 **BONK!**\n請至**限制級頻道**',
                ephemeral=True
            )
            return

        await interaction.response.defer(thinking=True)
        try:
            embed, view = await fetch_waifu(tag=tag, is_nsfw=True)
            await interaction.followup.send(embed=embed, view=view)
        except:
            await interaction.followup.send('不可以色色')
            raise


async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(WaifuGroup())
    logger.info('Waifu Commands Added')
