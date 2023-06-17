from typing import Optional

from discord import app_commands as ac, Interaction
from discord.app_commands import locale_str as _T, Choice, Group
from discord.ext.commands import Bot

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

        if tag is not None:
            tag = tag.value
            title = tag
        else:
            title = await intx.translate(_T('random', shared=True))

        try:
            bot: Soybot = intx.client
            image = await WaifuIm.fetch(bot.cs, tag=tag)
            embed, view = WaifuIm.build_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except KeyError:
            await intx.followup.send(await intx.translate('error'))

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
                await intx.translate('no_horny'),
                ephemeral=True
            )

        await intx.response.defer(thinking=True)

        if tag is not None:
            tag = tag.value
            title = tag
        else:
            title = 'Random'

        bot: Soybot = intx.client
        try:
            bot: Soybot = intx.client
            image = await WaifuIm.fetch(bot.cs, tag=tag)
            embed, view = WaifuIm.build_embed_view(title, image)
            await intx.followup.send(embed=embed, view=view)
        except KeyError as e:
            log.exception(e)
            await intx.followup.send(await intx.translate('error'))


async def setup(bot: Bot):
    bot.tree.add_command(WaifuGroup())
    log.info(f'{__name__} loaded')
