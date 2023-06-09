from discord import (app_commands as ac, Embed, Member, User, Interaction)
from discord.ext.commands import Bot
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)

async def avatar(intx: Interaction, target: Member | User):
    if target.id == intx.client.user.id:
        await intx.response.send_message(f'不要ㄐ查豆漿ㄐㄐ人好ㄇ', ephemeral=True)
        return

    await intx.response.defer()

    description = f'{intx.user.mention}稽查了{target.mention if intx.user != target else "自己"}'
        
    embed = Embed(
        description=description,
        color=target.color,
    ).set_author(
        name=target,
        icon_url=target.avatar,
    ).set_footer(
        text='soybot is currently in beta.\nPlease report bugs to eesoymilk if you encounter any.'
    )

    fetched_target = await intx.client.fetch_user(target.id)
    if fetched_target.banner is not None:
        embed.set_thumbnail(
            url=target.display_avatar
        ).set_image(
            url=fetched_target.banner
        )
    else:
        embed.set_image(url=target.display_avatar)

    await intx.followup.send(embed=embed)


@ac.command(name="avatar", description='稽查')
@ac.rename(target='稽查對象')
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def avatar_slash(intx: Interaction, target: Member):
    await avatar(intx, target)
    log.info(f'{intx.user} used avatar on {target if intx.user != target else "him/her-self"}')


@ac.context_menu(name='稽查頭貼')
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def avatar_ctx_menu(intx: Interaction, target: Member):
    await avatar(intx, target)
    log.info(f'{intx.user} used avatar on {target if intx.user != target else "him/her-self"}')


async def setup(bot: Bot):
    bot.tree.add_command(avatar_slash)
    bot.tree.add_command(avatar_ctx_menu)
    log.info(f'{__name__} loaded')
