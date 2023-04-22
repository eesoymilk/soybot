from discord import (app_commands as ac, Embed, Member, User, Interaction)
from discord.ext.commands import Bot
from utils import get_lumberjack

log = get_lumberjack(__name__)

async def avatar(interaction: Interaction, target: Member | User):
    if target.id == interaction.client.user.id:
        await interaction.response.send_message(f'不要ㄐ查豆漿ㄐㄐ人好ㄇ', ephemeral=True)
        return

    await interaction.response.defer()

    description = f'{interaction.user.mention}稽查了{target.mention if interaction.user != target else "自己"}'
        
    embed = Embed(
        description=description,
        color=target.color,
    ).set_author(
        name=target,
        icon_url=target.avatar,
    ).set_footer(
        text='soybot is currently at beta.\nPlease report bugs to eeSoymilk#4231 if you encounter any.'
    )

    fetched_target = await interaction.client.fetch_user(target.id)
    if fetched_target.banner is not None:
        embed.set_thumbnail(
            url=target.display_avatar
        ).set_image(
            url=fetched_target.banner
        )
    else:
        embed.set_image(url=target.display_avatar)

    await interaction.followup.send(embed=embed)


@ac.command(name="avatar", description='稽查')
@ac.rename(target='稽查對象')
async def avatar_slash(interaction: Interaction, target: Member):
    await avatar(interaction, target)
    log.info(f'{interaction.user} used avatar on {target if interaction.user != target else "him/her-self"}')


@ac.context_menu(name='稽查頭貼')
async def avatar_ctx_menu(interaction: Interaction, target: Member):
    await avatar(interaction, target)
    log.info(f'{interaction.user} used avatar on {target if interaction.user != target else "him/her-self"}')


async def setup(bot: Bot):
    bot.tree.add_command(avatar_slash)
    bot.tree.add_command(avatar_ctx_menu)
    log.info('extension loaded')
