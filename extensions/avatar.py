from typing import Optional

from discord import (
    app_commands as ac,
    Embed,
    Client,
    Member,
    User,
    Interaction,
    ButtonStyle,
    Asset,
)
from discord.ui import View, Button
from discord.ext.commands import Bot
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)


def get_name(target: Member | User) -> str:
    if target.global_name is None:
        name = f'{target.name}#{target.discriminator}'
    else:
        name = target.global_name
    if target.nick is not None:
        name += f' ({target.display_name})'
    return name


def get_desc(user: Member | User, target: Member | User) -> str:
    desc = f'{user.mention} inspected '
    if user != target:
        desc += target.mention
    else:
        desc += 'him/her-self'
    return desc


async def fetch_banner(client: Client, target_id: int) -> Optional[Asset]:
    return (await client.fetch_user(target_id)).banner


async def avatar(intx: Interaction, target: Member | User):

    await intx.response.defer()

    name = get_name(target)

    desc = get_desc(intx.user, target)

    view = View().add_item(Button(
        style=ButtonStyle.link,
        url=f'{target.avatar}',
        label='Avatar Source',
    ))

    embed = Embed(
        description=desc,
        color=target.color,
    ).set_author(
        name=name,
        icon_url=target.avatar,
    ).set_footer(
        text='soybot is currently in beta.\nPlease report bugs to soymilk if you encounter any.'
    )

    fetched_target = await intx.client.fetch_user(target.id)
    if fetched_target.banner is not None:
        view.add_item(Button(
            style=ButtonStyle.link,
            url=f'{fetched_target.banner}',
            label='Bannar Source',
        ))

        embed.set_thumbnail(
            url=target.display_avatar
        ).set_image(
            url=fetched_target.banner
        )
    else:
        embed.set_image(url=target.display_avatar)

    await intx.followup.send(embed=embed, view=view)


@ac.command(description='avatar_desc')
@ac.rename(target='avatar_target')
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def avatar_slash(intx: Interaction, target: Member):
    await avatar(intx, target)
    log.info(
        f'{intx.user} used avatar on {target if intx.user != target else "him/her-self"}')


@ac.context_menu()
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def avatar_ctx_menu(intx: Interaction, target: Member):
    await avatar(intx, target)
    log.info(
        f'{intx.user} used avatar on {target if intx.user != target else "him/her-self"}')


async def setup(bot: Bot):
    bot.tree.add_command(avatar_slash)
    bot.tree.add_command(avatar_ctx_menu)
    log.info(f'{__name__} loaded')
