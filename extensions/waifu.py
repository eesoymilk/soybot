from typing import Optional
from datetime import datetime
from urllib.parse import urljoin, urlencode

from discord import (
    app_commands as ac,
    Interaction,
    Embed,
    ButtonStyle,
    Color,
)
from discord.ui import View, Button
from discord.app_commands import locale_str as _T, Choice, Group
from discord.ext.commands import Bot
from aiohttp import ClientSession

from utils import get_lumberjack, cd_but_soymilk
from bot import Soybot

log = get_lumberjack(__name__)


class WaifuGroup(Group, name='waifu'):
    BASE_URL = 'https://api.waifu.im/'

    SFW_CHOICES = [
        Choice(name=opt, value=tag)
        for opt, tag in {
            'waifu-sfw_maid': 'maid',
            'waifu-sfw_waifu': 'waifu',
            'waifu-sfw_marin-kitagawa': 'marin-kitagawa',
            'waifu-sfw_mori-calliope': 'mori-calliope',
            'waifu-sfw_raiden-shogun': 'raiden-shogun',
            'waifu-sfw_oppai': 'oppai',
            'waifu-sfw_selfies': 'selfies',
            'waifu-sfw_uniform': 'uniform',
            'waifu-sfw_kamisato-ayaka': 'kamisato-ayaka',
        }.items()
    ]

    NSFW_CHOICES = [
        Choice(name=opt, value=tag)
        for opt, tag in {
            'waifu-nsfw_hentai': 'hentai',
            'waifu-nsfw_milf': 'milf',
            'waifu-nsfw_oral': 'oral',
            'waifu-nsfw_paizuri': 'paizuri',
            'waifu-nsfw_ecchi': 'ecchi',
            'waifu-nsfw_ass': 'ass',
            'waifu-nsfw_ero': 'ero',
        }.items()
    ]

    async def _fetch(
        self, cs: ClientSession, is_nsfw: bool = False, tag: str = None
    ) -> dict:
        params = dict()
        if is_nsfw:
            params |= {'is_nsfw': 'true'}
        if tag is not None:
            params |= {'included_tags': tag}
        url = f'{urljoin(self.BASE_URL, "/search")}?{urlencode(params)}'
        async with cs.get(url) as resp:
            data = await resp.json()

        image = data['images'][0]
        return image

    def _get_embed_view(self, title: str, image: dict) -> tuple[Embed, View]:
        tags = [t['name'] for t in image['tags']]
        embed = (
            Embed(
                title=title,
                description=''.join([f'#{t}' for t in tags]),
                color=Color.from_str(image['dominant_color']),
                timestamp=datetime.fromisoformat(image['uploaded_at']),
            )
            .set_image(
                url=image['url'],
            )
            .set_footer(text='uploaded at')
        )
        view = View().add_item(
            Button(
                style=ButtonStyle.link,
                url=image['source'],
                label='查看圖源',
            )
        )

        return embed, view

    # Run the command
    async def _run(
        self, intx: Interaction, tag: Optional[Choice[str]], is_nsfw: bool
    ):
        try:
            await intx.response.defer(thinking=True)

            if tag is not None:
                tag = tag.value
                title = await intx.translate(tag)
            else:
                title = await intx.translate(_T('random', shared=True))

            bot: Soybot = intx.client
            image = await self._fetch(bot.cs, tag=tag)
            embed, view = self._get_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except (KeyError, AttributeError) as err:
            log.exception(err)
            await intx.followup.send(await intx.translate('error'))

    @ac.command(name='waifu-sfw')
    @ac.describe(tag='tag')
    @ac.choices(tag=SFW_CHOICES)
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def sfw_coro(
        self, intx: Interaction, tag: Optional[Choice[str]] = None
    ):
        await self._run(intx, tag, False)

    @ac.command(name='waifu-nsfw')
    @ac.describe(tag='tag')
    @ac.choices(tag=NSFW_CHOICES)
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def nsfw_coro(
        self, intx: Interaction, tag: Optional[Choice[str]] = None
    ):
        # manually check if the channel is nsfw due to discord limitation
        if not intx.channel.nsfw:
            return await intx.response.send_message(
                await intx.translate('no_horny'), ephemeral=True
            )
        await self._run(intx, tag, True)


async def setup(bot: Bot):
    bot.tree.add_command(WaifuGroup())
