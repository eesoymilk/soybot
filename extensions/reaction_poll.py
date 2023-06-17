import asyncio

from discord import (
    app_commands as ac,
    Interaction,
    Embed,
    TextStyle)
from discord.ext.commands import Bot
from discord.ui import Modal, TextInput
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)


class SimplePollModal(Modal, title='Simple Reaction Poll'):

    poll_reactions = (
        '1️⃣', '2️⃣', '3️⃣', '4️⃣', '5️⃣',
        '6️⃣', '7️⃣', '8️⃣', '9️⃣', '🔟',)

    form_title = TextInput(
        label='投票標題',
    )

    form_description = TextInput(
        label='投票說明',
        placeholder='非必填',
        required=False,)

    form_options = TextInput(
        label='投票選項 (一個選項換一行)',
        style=TextStyle.long,
        default='Yes\nNo',)

    # TODO: options validation
    async def on_submit(self, intx: Interaction):
        log.info(f'{intx.user}\'s Modal received.')

        title = self.form_title.value.strip()
        description = self.form_description.value.strip()
        options = []
        for option in self.form_options.value.split('\n'):
            if option in options:
                continue
            options.append(option)

        if (length := len(options)) < 2:
            await intx.response.send_message(
                f'**cannot make a poll with {length} option(s)**',
                ephemeral=True)
            return

        embed = Embed(
            color=intx.user.color,
            title=title,
            description=description,
        ).set_author(
            name=f'由 {intx.user.display_name} 發起的投票',
            icon_url=intx.user.display_avatar
        ).set_footer(
            text='soybot is currently at beta.\n' +
                 'Please report bugs to eeSoymilk#4231 if you encounter any.'
        )
        for rxn, option in zip(self.poll_reactions, options):
            embed.add_field(name=rxn, value=option)

        await intx.response.send_message(embed=embed)

        poll_msg = await intx.original_response()
        await asyncio.gather(*[
            poll_msg.add_reaction(rxn)
            for rxn, _ in zip(self.poll_reactions, options)])

        log.info(f'{intx.user}\'s poll started.')


@ac.command()
@ac.guild_only()
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def reaction_poll(intx: Interaction):
    await intx.response.send_modal(SimplePollModal())


async def setup(bot: Bot):
    bot.tree.add_command(reaction_poll)
