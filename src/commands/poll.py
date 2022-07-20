import discord
from discord import ui
from utils import get_lumberjack
from datetime import datetime

logger = get_lumberjack('Poll')


def join_str(l: list[str], sep='', bold=False, italic=False) -> str:
    wrap = ''
    if bold:
        wrap += '**'
    if italic:
        wrap += '*'
    if wrap:
        l = [f'{wrap}{s}{wrap}' for s in l]
    return sep.join(l)


def poll_result_embed(poll):
    embed = discord.Embed(
        color=poll.color,
        title=f'投票結果 - **{poll.title}**',
        description=join_str(list(poll.description.values())[:-1]),
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

    if len(zero_pools) == len(poll.pools):
        embed.description = f'{embed.description}\n**沒有任何人投票**\n**可憐！**'

    fields: list[dict[str, str]]

    # vote pools
    if poll.is_public:
        fields = [{
            'name': f'**{len(pool)}**票 - **{option}**',
            'value': join_str([voter.display_name for voter in pool], sep='\n'),
            'inline': False
        } for option, pool in sorted_pools if pool]
    else:
        fields = [{
            'name': f'**{len(pool)}**票',
            'value': f'**{option}**'
        } for option, pool in sorted_pools if pool]

    # Zero pools

    zero_field = {'name': '**0**票'}
    if len(zero_pools) == 1:
        if poll.is_public:
            zero_field['name'] += f' - **{zero_pools[0]}**'
            zero_field['value'] = 'None'
        else:
            zero_field['value'] = f'**{zero_pools[0]}**'
        fields += [zero_field]
    elif len(zero_pools) > 1:
        zero_field['name'] += '選項'
        zero_field['value'] = join_str(zero_pools, sep='\n')
        zero_field['inline'] = False
        fields += [zero_field]

    # show anonymous voters
    if not poll.is_public and len(zero_pools) < len(poll.pools):
        fields += [{
            'name': f'本次共有**{len(poll.voters)}**人參與投票',
            'value': join_str([voter.display_name for voter in poll.voters], sep='\n'),
            'inline': False
        }]

    for field in fields:
        embed.add_field(**field)

    return embed


class PollDetails(ui.Modal):

    form_title = ui.TextInput(
        label='投票標題',
        # placeholder='Poll Title',
        # default='Test Poll',
    )

    form_options = ui.TextInput(
        label='投票選項 (一個選項換一行)',
        style=discord.TextStyle.long,
        # placeholder='Poll Options',
        default='Yes\nNo',
    )

    def __init__(self, poll) -> None:
        self.poll = poll
        super().__init__(title=f'【{join_str(poll.description.values())}】的投票')

    async def on_timeout(self):
        logger.warning(
            f'{self.poll.chat_interaction.user.display_name}\'s Modal timeout'
        )

    async def on_submit(self, interaction: discord.Interaction):
        # defer the response so that it can be called in poll.start()
        # await interaction.response.defer()

        logger.info(
            f'{self.poll.chat_interaction.user.display_name}\'s Modal received.'
        )

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
            # description=f'{self.poll.description["anonymity"]}{self.poll.description["format"]}\n限時{self.poll.duration}秒',
            description=join_str(
                self.poll.description.values(),
                sep=' '
            ),
        )
        self.poll.poll_embed.set_footer(
            text=f'由 {interaction.user.display_name} 發起',
            icon_url=interaction.user.display_avatar.url
        )

        logger.info(
            f'{self.poll.chat_interaction.user.display_name}\'s Poll is ready.'
        )

        # stop the view so that the coro proceed
        self.stop()

    async def on_error(self, interaction: discord.Interaction, error: Exception) -> None:
        logger.exception(error)
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
        logger.info(
            f'{self.poll.title} | {interaction.user.display_name} | {join_str(self.values, sep=", ")}'
        )

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

        await interaction.response.send_message(
            f'你投了 {join_str(self.values, sep=" ", bold=True)}',
            ephemeral=True
        )


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
        self.title: str
        self.poll_view: ui.View
        self.poll_embed: discord.Embed
        self.poll_message: discord.Message
        self.res_message: discord.Message
        self.pools: dict[str, set[discord.Member]]
        self.voters: set[discord.Member]

        logger.info(
            f'A Poll instance is created for {chat_interaction.user.display_name}'
        )

    @property
    def description(self):
        return {
            'anonymity': '公開' if self.is_public else '匿名',
            'format': '單選' if self.is_single else '複選',
            'duration': f'限時{str(self.duration).rstrip("0").rstrip(".")}秒',
        }

    async def prompt_details(self) -> None:
        await self.chat_interaction.response.send_modal(self.modal)

    async def start(self) -> None:
        logger.info(
            f'{self.title} started | {join_str(self.description.values(), sep=" ")}'
        )

        # start the poll
        self.poll_embed.timestamp = datetime.now()
        await self.modal_interaction.response.send_message(view=self.poll_view, embed=self.poll_embed)
        self.poll_message = await self.modal_interaction.original_message()

        # TODO queue if multiple polls
        ...

    async def end(self):

        # send poll result
        self.res_message = await self.poll_message.reply(embed=poll_result_embed(self))
        logger.info(f'{self.title} | result embed generated')

        # edit poll message
        self.poll_view.clear_items().add_item(ui.Button(
            style=discord.ButtonStyle.link,
            url=self.res_message.jump_url,
            label='查看投票結果',
        ))
        logger.info(f'{self.title} | original view edited')
        self.poll_embed.title = f'***投票已結束 - {self.title}***'
        self.poll_embed.add_field(
            name='投票選項',
            value=join_str(self.pools.keys(), sep='\n')
        )
        logger.info(f'{self.title} | original embed edited')
        await self.poll_message.edit(view=self.poll_view, embed=self.poll_embed)
        logger.info(f'{self.title} | ended')
