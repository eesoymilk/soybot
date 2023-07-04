from typing import Optional

from discord import (
    app_commands as ac,
    Embed,
    Member,
    User,
    Interaction,
    ButtonStyle,
    NotFound,
)
from discord.app_commands import locale_str as _T
from discord.ui import View, Button
from discord.ext.commands import Bot, Cog
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)


class InspectCog(Cog):
    def __init__(self, bot: Bot):
        self.bot = bot
        self.ctx_menu = ac.ContextMenu(
            name='inspect_user',
            callback=self.inspect_ctx_menu
        )
        self.bot.tree.add_command(self.ctx_menu)

    async def _get_target_detail(self, target: Member | User) -> str:
        if target.global_name is None:
            name = f'{target.name}#{target.discriminator}'
        else:
            name = target.global_name
        if target.nick is not None:
            name += f' ({target.display_name})'

        color = target.color
        avatar_url = target.display_avatar.url

        fetched_target = await self.bot.fetch_user(target.id)
        banner_url = fetched_target.banner.url if fetched_target.banner else None

        return name, color, avatar_url, banner_url

    async def inspect_coro(
        self, intx: Interaction, user: Member, target: Member
    ):
        await intx.response.defer()

        target = await intx.guild.fetch_member(target.id)
        name, color, avatar_url, banner_url = await self._get_target_detail(target)

        if user == target:
            desc = (await intx.translate('self_inspection')).format(
                user.mention
            )
        else:
            desc = (await intx.translate('other_inspection')).format(
                user.mention, target.mention
            )

        view = View().add_item(Button(
            style=ButtonStyle.link,
            url=f'{target.avatar}',
            label=await intx.translate('avatar_src'),
        ))

        embed = Embed(
            description=desc,
            color=color,
        ).set_author(
            name=name,
            icon_url=target.avatar,
        ).set_footer(
            text=await intx.translate(_T('beta', shared=True))
        )

        if banner_url is not None:
            view.add_item(Button(
                style=ButtonStyle.link,
                url=banner_url,
                label=await intx.translate('banner_src'),
            ))
            embed.set_thumbnail(
                url=avatar_url
            ).set_image(
                url=banner_url
            )
        else:
            embed.set_image(url=avatar_url)

        await intx.followup.send(embed=embed, view=view)

    @ac.command(name='inspect')
    @ac.describe(target='target')
    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def inspect_slash(self, intx: Interaction, target: Member | User):
        try:
            await self.inspect_coro(intx, intx.user, target)
        except NotFound as err:
            log.exception(err)

    @ac.checks.dynamic_cooldown(cd_but_soymilk)
    async def inspect_ctx_menu(self, intx: Interaction, target: Member):
        try:
            await self.inspect_coro(intx, intx.user, target)
        except NotFound as err:
            log.exception(err)


async def setup(bot: Bot):
    await bot.add_cog(InspectCog(bot))
