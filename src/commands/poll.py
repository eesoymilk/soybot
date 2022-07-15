import discord

from datetime import datetime
from discord import ui


def list_to_str(l: list[str], sep: str = ' ', bold: bool = True, italic: bool = False) -> str:
    output = ''
    wrap = ''
    if bold:
        wrap += '**'
    if italic:
        wrap += '*'
    for s in l:
        output += wrap + s + wrap + sep
    output = output[:-1]
    return output


def poll_result_embed(poll):
    embed = discord.Embed(
        color=poll.color,
        title=f'投票結果 - **{poll.title}**',
        description=f'**{poll.description["anonymity"]}{poll.description["format"]}**',
        timestamp=datetime.now(),
    )
    embed.set_footer(
        text=f'由 {poll.chat_interaction.user.display_name} 發起',
        icon_url=poll.chat_interaction.user.display_avatar.url
    )

    # compute poll result
    zero_pools = [
        option
        for option, pool in poll.pools.items()
        if not pool
    ]
    sorted_pools = list(filter(lambda x: x[1], sorted(
        poll.pools.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )))

    fields: list[dict[str, str]]

    # vote pools
    if poll.is_public:
        fields = [{
            'name': f'**{len(pool)}**票 - **{option}**',
            'value': list_to_str([voter.display_name for voter in pool], sep='\n'),
            'inline': False
        } for option, pool in sorted_pools if pool]
    else:
        fields = [{
            'name': f'**{len(pool)}**票',
            'value': f'**{option}**'
        } for option, pool in sorted_pools if pool]

    # Zero pools
    if len(zero_pools) == 1:
        if poll.is_public:
            fields += [{'name': f'**0**票 - **{zero_pools[0]}**',
                        'value': '**None**'}]
        else:
            fields += [{'name': f'**0**票',
                        'value': f'**{zero_pools[0]}**'}]
    elif len(zero_pools) == len(poll.pools):
        fields += [{'name': '**沒有任何人投票，可憐！**\n以下為本次投票選項',
                    'value': list_to_str(zero_pools, sep='\n'),
                    'inline': False}]
    elif len(zero_pools) > 1:
        fields += [{'name': '**0**票選項',
                    'value': list_to_str(zero_pools, sep='\n'),
                    'inline': False}]

    # show anonymous voters
    if not poll.is_public and len(zero_pools) < len(poll.pools):
        fields += [{
            'name': f'本次參與投票人數 - **{len(poll.voters)}** 人',
            'value': list_to_str([voter.display_name for voter in poll.voters], sep='\n'),
            'inline': False
        }]

    for field in fields:
        embed.add_field(**field)

    return embed


class PollDetails(ui.Modal):

    form_title = ui.TextInput(
        label='投票標題',
        # placeholder='Poll Title',
        default='Test Poll',
    )

    form_options = ui.TextInput(
        label='投票選項 (一個選項換一行)',
        style=discord.TextStyle.long,
        # placeholder='Poll Options',
        default='Yes\nNo',
    )

    def __init__(self, poll) -> None:
        self.poll = poll
        modal_title = '發起【公開單選、限時20秒】的投票'
        if not self.poll.is_public:
            modal_title = modal_title.replace('公開', '匿名')
        if not self.poll.is_single:
            modal_title = modal_title.replace('單選', '多選')
        if self.poll.duration != 20.0:
            modal_title = modal_title.replace('20', str(self.poll.duration))
        super().__init__(title=modal_title)

    async def on_timeout(self):
        ...

    async def on_submit(self, interaction: discord.Interaction):
        # defer the response so that it can be called in poll.start()
        # await interaction.response.defer()

        # setup poll details
        self.poll.modal_interaction = interaction
        self.poll.color = discord.Color.random()
        self.poll.title = self.form_title.value
        self.poll.options = tuple({
            option.strip()
            for option in self.form_options.value.split('\n')
            if option.strip()
        })
        self.poll.pools = {option: set() for option in self.poll.options}
        self.poll.voters = set()

        # setup the view and embed for the poll in advanced
        self.poll.poll_view = PollView(self.poll)
        self.poll.poll_embed = discord.Embed(
            color=self.poll.color,
            title=f'投票開始 - **{self.poll.title}**',
            description=f'{self.poll.description["anonymity"]}{self.poll.description["format"]}\n限時{self.poll.duration}秒',
        )
        self.poll.poll_embed.set_footer(
            text=f'由 {interaction.user.display_name} 發起',
            icon_url=interaction.user.display_avatar.url
        )

        # stop the view so that the coro proceed
        self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        print(error)
        await interaction.response.send_message('Oops! Something went wrong.', ephemeral=True)
        # Make sure we know what the error actually is
        # traceback.print_tb(error.__traceback__)
        ...


class PollSelect(ui.Select):
    def __init__(self, poll) -> None:
        self.poll = poll
        placeholder = f'開始投票 - {poll.title}'
        max_values = 1 if poll.is_single else len(poll.options)
        options = [discord.SelectOption(label=option)
                   for option in poll.options]
        super().__init__(
            placeholder=placeholder,
            max_values=max_values,
            options=options
        )

    async def callback(self, interaction: discord.Interaction) -> None:
        self.poll.voters.add(interaction.user)

        if self.poll.is_single:
            for option, pool in self.poll.pools.items():
                if option == self.values[0]:
                    pool.add(interaction.user)
                else:
                    pool.discard(interaction.user)
        else:
            for option, pool in self.poll.pools.items():
                if option in self.values:
                    pool.add(interaction.user)
                else:
                    pool.discard(interaction.user)

        await interaction.response.send_message('Thanks for your vote!')


class PollView(ui.View):
    def __init__(self, poll):
        super().__init__()
        self.add_item(PollSelect(poll))

    async def on_timeout(self) -> None:
        ...


class Poll:
    def __init__(
        self,
        chat_interaction: discord.Interaction,
        is_public: bool,
        is_single: bool,
        duration: float
    ) -> None:
        self.chat_interaction = chat_interaction
        self.is_public = is_public
        self.is_single = is_single
        self.duration = duration
        self.modal: ui.Modal = PollDetails(self)

        self.modal_interaction: discord.Interaction
        self.color: discord.Color
        self.poll_view: ui.View
        self.poll_embed: discord.Embed
        self.poll_message: discord.Message
        self.res_message: discord.Message
        self.pools: dict[str, set[discord.Member]]
        self.voters: set[discord.Member]

    @property
    def description(self):
        return {
            'anonymity': '公開' if self.is_public else '匿名',
            'format': '單選' if self.is_single else '複選',
        }

    async def prompt_details(self) -> None:
        await self.chat_interaction.response.send_modal(self.modal)

    async def start(self) -> None:
        # start the poll
        self.poll_embed.timestamp = datetime.now()
        await self.modal_interaction.response.send_message(view=self.poll_view, embed=self.poll_embed)
        self.poll_message = await self.modal_interaction.original_message()

        # TODO queue if multiple polls
        ...

    async def end(self):
        # send poll result
        self.res_message = await self.poll_message.reply(embed=poll_result_embed(self))

        # edit poll message
        self.poll_view.clear_items().add_item(ui.Button(
            style=discord.ButtonStyle.link,
            url=self.res_message.jump_url,
            label='查看投票結果',
        ))
        self.poll_embed.title = f'***投票已結束 - {self.title}***'
        # self.poll_embed.add_field(name='投票選項', value=options_str)
        await self.poll_message.edit(view=self.poll_view, embed=self.poll_embed)
