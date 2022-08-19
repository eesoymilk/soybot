from datetime import datetime
import discord
import aiohttp
from urllib.parse import urlencode, urlparse, urlunparse
from discord import app_commands as ac, Color, Embed, Interaction
from discord.app_commands import Choice
from discord.ext import commands
from discord.ui import View, Button
from utils import Config

waifu_im_url = 'https://api.waifu.im/random/'
all_tags = {
    'sfw': {
        '老婆': 'waifu',
        '制服': 'uniform',
        '女僕': 'maid',
        '喜多川海夢': 'marin-kitagawa',
        '原神 巴爾': 'raiden-shogun',
        '大奶': 'oppai',
        '自拍': 'selfies',
    },
    'nsfw': {
        'Hentai': 'hentai',
        'MILF': 'milf',
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
        query_seq.append(('is_nsfw', True))
    if many:
        query_seq.append(('many', True))

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


@ac.command(description='你老婆真好用...')
@ac.describe(tag='你今天要哪種老婆')
@ac.rename(tag='老婆類型')
@ac.choices(tag=[Choice(name=k, value=v) for k, v in all_tags['sfw'].items()])
# @ac.guilds(Config.guilds['debug'].id)
@ac.guilds(*Config.guild_ids)
@ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def waifu(interaction: Interaction, tag: Choice[str] = None):
    await interaction.response.defer(thinking=True)
    try:
        embed, view = await fetch_waifu(tag=tag)
        await interaction.followup.send(embed=embed, view=view)
    except:
        await interaction.followup.send('醒 你沒老婆')
        raise

# @ac.command(description='可以色色...', nsfw=True)
# @ac.describe(category='你今天想要哪種色色', n='你想要幾張色圖')
# @ac.rename(category='色色類型', n='色圖數量')
# @ac.choices(category=[Choice(name=k, value=v) for k, v in categories['nsfw'].items()])
# @ac.guilds(Config.guilds['debug'].id)
# # @ac.guilds(*Config.guild_ids)
# async def horny(
#         interaction: discord.Interaction,
#         category: Choice[str] = None,
#         n: Range[int, 1, 10] = 1
# ):
#     if category is None:
#         category = Choice(name='隨機', value='waifu')
#     tag = f'**#{category.value}**'
#     async with aiohttp.ClientSession() as session:
#         if n > 1:
#             url = urljoin(waifu_im_url, f'many/nsfw/{category.value}')
#             async with session.post(url, json={'exclude': []}) as resp:
#                 try:
#                     files = (await resp.json())['files']
#                     await interaction.response.send_message('\n'.join([tag] + files[:n]))
#                 except KeyError:
#                     await interaction.response.send_message('**不可以色色**')
#         else:
#             url = urljoin(waifu_im_url, f'nsfw/{category.value}')
#             async with session.get(url) as resp:
#                 try:
#                     file = (await resp.json())['url']
#                     await interaction.response.send_message(f'{tag}\n{file}')
#                 except KeyError:
#                     await interaction.response.send_message('**不可以色色**')


async def setup(bot: commands.Bot) -> None:
    # bot.tree.add_command(waifu)
    # bot.tree.add_command(horny)
    ...
