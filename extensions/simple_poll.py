import asyncio
from discord import (
    app_commands as ac, 
    Interaction,
    Embed,
    Color,
    Message,
    Member,
    TextStyle)
from discord.ext.commands import Cog, Bot
from discord.ui import Modal, TextInput
from utils import get_lumberjack

log = get_lumberjack(__name__)

class SimplePollModal(Modal, title='Simple Reaction Poll'):

    poll_reactions = {
        1: '1️⃣',
        2: '2️⃣',
        3: '3️⃣',
        4: '4️⃣',
        5: '5️⃣',
        6: '6️⃣',
        7: '7️⃣',
        8: '8️⃣',
        9: '9️⃣',
        10: '🔟'
    }

    form_title = TextInput(
        label='投票標題',
        # placeholder='Poll Title',
        # default='Test Poll',
    )

    form_description = TextInput(
        label='投票說明',
        placeholder='非必填',
        required=False,
        # default='Test Poll Description',
    )

    form_options = TextInput(
        label='投票選項 (一選項換一行、選項數量需介於2至25之間、單一選項不得超過100字元)',
        style=TextStyle.long,
        # placeholder='Poll Options',
        default='Yes\nNo',
    )

    async def on_submit(self, intx: Interaction):
        log.info(f'{intx.user}\'s Modal received.')

        title = self.form_title.value.strip()
        description = self.form_description.value.strip()
        options = []
        for option in self.form_options.value.split('\n'):
            if option not in options:
                options.append(option)

        embed = Embed(
            color=intx.user.color,
            title=title,
            description=description,
        ).set_author(
            name=f'由 {intx.user.display_name} 發起的投票',
            icon_url=intx.user.display_avatar
        ).set_footer(
            text='soybot is currently at beta.\nPlease report bugs to eeSoymilk#4231 if you encounter any.'
        )
        for rxn ,option in zip(self.poll_reactions.values(), options):
            embed.add_field(name=rxn, value=option)

        await intx.response.send_message(embed=embed)

        poll_msg = await intx.original_response()
        await asyncio.gather(*[
            poll_msg.add_reaction(rxn)
            for rxn ,_ in zip(self.poll_reactions.values(), options)
        ])
        
        log.info(f'{intx.user}\'s poll started.')


@ac.command(name='簡易投票', description='用表情符號反應來進行投票')
@ac.guild_only()
@ac.checks.cooldown(1, 60, key=lambda i: (i.channel.id, i.user.id))
async def simple_poll(intx: Interaction):
    await intx.response.send_modal(SimplePollModal())

async def setup(bot: Bot):
    bot.tree.add_command(simple_poll)
    log.info(f'{__name__} loaded')
