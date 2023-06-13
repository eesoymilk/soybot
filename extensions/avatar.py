from discord import (
    app_commands as ac, 
    Embed, 
    Member, 
    User, 
    Interaction,
    ButtonStyle,
)
from discord.ui import View, Button
from discord.ext.commands import Bot
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)

async def avatar(intx: Interaction, target: Member | User):
    # if target.id == intx.client.user.id:
    #     await intx.response.send_message(
    #         f'不要ㄐ查豆漿ㄐㄐ人好ㄇ', 
    #         ephemeral=True
    #     )
    #     return

    await intx.response.defer()

    print(f'global: {target.global_name}\nname: {target.name}')
    print(f'display: {target.display_name}')

    if target.global_name is None:
        name = f'{target.name}#{target.discriminator}'
        if target.display_name != target.name:
            name += f' ({target.display_name})'
    else:
        name = target.global_name
        if target.global_name != target.name:
            name += f' ({target.display_name})'
    
    if intx.user != target:
        description = f'{intx.user.mention} inspected {target.mention}'
    else:
        description = f'{intx.user.mention} inspected him/her-self'
    
    view = View().add_item(Button(
        style=ButtonStyle.link,
        url=f'{target.avatar}',
        label='Avatar Source',
    ))
    
    embed = Embed(
        description=description,
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


@ac.command(name="avatar", description='Avatar inspection')
# @ac.rename(target='稽查對象')
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def avatar_slash(intx: Interaction, target: Member):
    await avatar(intx, target)
    log.info(f'{intx.user} used avatar on {target if intx.user != target else "him/her-self"}')


@ac.context_menu(name='Avatar Inspection')
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def avatar_ctx_menu(intx: Interaction, target: Member):
    await avatar(intx, target)
    log.info(f'{intx.user} used avatar on {target if intx.user != target else "him/her-self"}')


async def setup(bot: Bot):
    bot.tree.add_command(avatar_slash)
    bot.tree.add_command(avatar_ctx_menu)
    log.info(f'{__name__} loaded')
