from datetime import datetime

from discord import Embed, Color, ButtonStyle
from discord.ui import View, Button
from discord.app_commands import Choice
from aiohttp import ClientSession


class WaifuIm:
    BASE_URL = 'https://api.waifu.im'

    SFW_CHOICES = [Choice(name=opt, value=tag) for opt, tag in {
        'waifu-sfw_waifu': 'waifu',
        'waifu-sfw_uniform': 'uniform',
        'waifu-sfw_maid': 'maid',
        'waifu-sfw_mori-calliope': 'mori-calliope',
        'waifu-sfw_marin-kitagawa': 'marin-kitagawa',
        'waifu-sfw_raiden-shogun': 'raiden-shogun',
        'waifu-sfw_oppai': 'oppai',
        'waifu-sfw_selfies': 'selfies',
    }.items()]

    NSFW_CHOICES = [Choice(name=opt, value=tag) for opt, tag in {
        'waifu-nsfw_hentai': 'hentai',
        'waifu-nsfw_milf': 'milf',
        'waifu-nsfw_oral': 'oral',
        'waifu-nsfw_paizuri': 'paizuri',
        'waifu-nsfw_ecchi': 'ecchi',
        'waifu-nsfw_ass': 'ass',
        'waifu-nsfw_ero': 'ero',
    }.items()]

    @staticmethod
    async def fetch(cs: ClientSession, url: str) -> dict:
        async with cs.get(url) as resp:
            data = await resp.json()

        image = data['images'][0]
        return image
    
    @staticmethod
    def build_embed_view(title: str, image: dict) -> tuple[Embed, View]:
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
