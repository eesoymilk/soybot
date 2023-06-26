import asyncio
from typing import NamedTuple

from discord import (
    app_commands as ac,
    Interaction,
    Embed,
    TextStyle
)
from discord.app_commands import locale_str as _T
from discord.ext.commands import Bot
from discord.ui import Modal, TextInput
from utils import get_lumberjack, cd_but_soymilk

log = get_lumberjack(__name__)


class ReactionPollModal(Modal):
    # pass this namedtuple to data parameter when translating
    # this helps resolving the correct keys in translation dict
    command = (NamedTuple('DummyCommand', name=str))('reaction_poll')
    
    default_reactions = (
        '1️⃣', 
        '2️⃣', 
        '3️⃣', 
        '4️⃣', 
        '5️⃣', 
        '6️⃣', 
        '7️⃣', 
        '8️⃣', 
        '9️⃣',
        '🇦', 
        '🇧', 
        '🇨', 
        '🇩', 
        '🇪', 
        '🇫', 
        '🇬', 
        '🇭', 
        '🇮', 
        '🇯',
        '🇰',
    )
    
    
    def __init__(
        self,
        modal_title: str,
        form_title: TextInput, 
        form_desc: TextInput, 
        form_opts: TextInput,
    ):
        self.form_title = form_title
        self.form_desc = form_desc
        self.form_opts = form_opts
        
        super().__init__(title=modal_title)
        
        self.add_item(
            form_title
        ).add_item(
            form_desc
        ).add_item(
            form_opts
        )

    async def on_submit(self, intx: Interaction):
        try:
            log.info(f'{intx.user}\'s Modal received.')
            title = self.form_title.value.strip()
            desc = self.form_desc.value.strip()
            opts = []
            for opt in self.form_opts.value.split('\n'):
                if opt not in opts:
                    opts.append(opt)

            n_opts = len(opts)
            if n_opts < 2:
                raise ValueError('err_few')
            
            if n_opts > 20:
                raise ValueError('err_many')
                
            opt_fileds = [{
                'name': reaction,
                'value': opt
            } for reaction, opt in zip(self.default_reactions, opts)]
            
            embed = Embed(
                title=title,
                description=desc,
                color=intx.user.color,
            ).set_author(
                name=(
                    await intx.translate('embed_author', data=self.command)
                ).format(intx.user.display_name),
                icon_url=intx.user.display_avatar,
            ).set_footer(
                text=await intx.translate(_T('beta', shared=True))
            )
            
            for opt_field in opt_fileds:
                embed.add_field(**opt_field)
                
            await intx.response.send_message(embed=embed)
            poll_msg = await intx.original_response()
            await asyncio.gather(*[
                poll_msg.add_reaction(opt_field['name'])
                for opt_field in opt_fileds
            ])

            log.info(f'{intx.user}\'s poll started.')

        except ValueError as err:
            sep = '、' if intx.locale.value == 'zh-TW' else ', '
            err_msg = (
                await intx.translate(f'{err}', data=self.command)
            ).format(
                n_opts, sep.join(opts)
            )
            await intx.response.send_message(err_msg, ephemeral=True)

@ac.command()
@ac.guild_only()
@ac.checks.dynamic_cooldown(cd_but_soymilk)
async def reaction_poll(intx: Interaction):
    modal_title = await intx.translate('modal_title')
    form_title = TextInput(
        label=await intx.translate('title'),
        max_length=256,
    )
    form_desc = TextInput(
        label=await intx.translate('desc'),
        placeholder=await intx.translate('desc_placeholder'),
        required=False,
        max_length=4000,
    )
    form_opts = TextInput(
        label=await intx.translate('opts'),
        style=TextStyle.long,
        default=await intx.translate('opts_default'),
        max_length=1024,
    )

    modal = ReactionPollModal(
        modal_title,
        form_title, 
        form_desc, 
        form_opts,
    )

    await intx.response.send_modal(modal)
    

async def setup(bot: Bot):
    bot.tree.add_command(reaction_poll)
