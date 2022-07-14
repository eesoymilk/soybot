import asyncio
import discord
import copy

from discord import SelectOption
from discord.ui import InputText, Modal, View, Button, Select
from enum import Enum
from datetime import datetime, timedelta


class PollFormat(Enum):
    Single = 1
    Multiple = 2


polling_channel_ids: dict[int, datetime] = dict()
settings: dict[str, dict[str, list[SelectOption]]] = {
    'anonymity': {'placeholder': '投票模式 - Mode',
                  'options': [SelectOption(label='公開', value='public', description='public', emoji='👀'),
                              SelectOption(label='匿名', value='anonymous', description='anonymous', emoji='🤫')]},
    'format': {'placeholder': '投票方式 - Format',
               'options': [SelectOption(label='單選', value='single', description='single choice', emoji='1️⃣'),
                           SelectOption(label='複選', value='multiple', description='multiple choice', emoji='♾️')]},
    'duration': {'placeholder': '投票時間 - poll duration',
                 'options': [SelectOption(label=f'{t} seconds', value=str(t), default=t == 20) for t in range(10, 101, 10)]}
}
default_settings: dict[str, any] = {
    'anonymity': False,
    'format': PollFormat.Single,
    'duration': 20
}


def is_available(channel_id: int):
    if channel_id not in polling_channel_ids:
        return True
    if datetime.now() > polling_channel_ids[channel_id]:
        return True
    return False


def enter_polling(channel_id: int, duartion: int):
    if channel_id not in polling_channel_ids or datetime.now() + timedelta(seconds=duartion) > polling_channel_ids[channel_id]:
        polling_channel_ids[channel_id] = datetime.now() + \
            timedelta(seconds=duartion)


def validate_poll(title: str, options: list[str]) -> list[str]:
    errors = []

    if not title:
        errors.append('標題不能空白')

    if len(options) <= 1:
        errors.append('選項至少要有兩項')

    if any(len(option) > 25 for option in options):
        errors.append('各個選項不可超過25個字')

    return errors


def result_embed_gen(poll) -> discord.Embed:
    embed = discord.Embed(
        title=f'投票結果 - **{poll.title}**',
        description=f'**{poll.anonymity_cn_str}**、**{poll.format_cn_str}**',
        timestamp=datetime.now(),
        color=poll.color
    )
    embed.set_footer(text=f'由 {poll.ctx.author.display_name} 發起',
                     icon_url=poll.ctx.author.display_avatar.url)

    # compute poll result
    zero_pools: list[str] = [option for option,
                             pool in poll.pools.items() if not pool]
    sorted_pools: list[str, set[discord.Member]] = sorted(
        poll.pools.items(),
        key=lambda x: len(x[1]),
        reverse=True
    )
    if len(zero_pools) > 1:
        sorted_pools = [(option, pool)
                        for option, pool in sorted_pools if pool]
    else:
        zero_pools = []

    if poll.is_anonymous:
        for option, pool in sorted_pools:
            embed.add_field(name=f'{len(pool)} 票', value=f'**{option}**')
    else:
        for option, pool in sorted_pools:
            if pool:
                voters_str = ''
                for voter in pool:
                    voters_str += f'**{voter.display_name}**\n'
                voters_str = voters_str[:-1]
                embed.add_field(
                    name=f'**{len(pool)}** 票 - **{option}**',
                    value=voters_str, inline=False)
            else:
                embed.add_field(
                    name=f'**0** 票 - **{option}**',
                    value='**None**', inline=False)
    if zero_pools:
        title = '**沒有任何人投票，可憐！**\n以下為本次投票選項' if len(
            zero_pools) == len(poll.pools) else '以下為 ***0 票*** 選項:'
        value = ''
        for option in zero_pools:
            value += f'**{option}**\n'
        value = value[:-1]

        embed.add_field(
            name=title, value=value, inline=False)

    if poll.is_anonymous and len(zero_pools) < len(poll.pools):
        voters_str = ''
        for voter in poll.voters:
            voters_str += f'**{voter.display_name}**\n'
        voters_str = voters_str[:-1]
        embed.add_field(
            name=f'本次參與投票人數 - **{len(poll.voters)}** 人',
            value=voters_str, inline=False)

    return embed


class PollModal(Modal):
    def __init__(self, poll) -> None:
        self.poll = poll
        super().__init__(
            *[InputText(
                label='投票名稱 - Poll Name',
                placeholder='標題上限50個字 - Max title length is 50 characters long.',
                max_length=50),
              InputText(
                style=discord.InputTextStyle.long,
                label='投票選項 - Options',
                placeholder='請用**換行**隔開選項。\nSeparate different options with **newlines**.',
                value='Yes\nNo')],
            title='發起投票 - Make a Poll'
        )

    async def callback(self, interaction: discord.Interaction):
        # removing blank characters and duplicate options, then validate
        title = self.children[0].value.strip()
        options = tuple({option.strip() for option in self.children[1].value.split(
            '\n') if option.strip()})
        errors = validate_poll(title, options)
        if errors:
            error_msg = ''
            for error in errors:
                error_msg += f'**{error}**\n'
            errors_msg = error_msg[:-1]
            await interaction.response.send_message(errors_msg)
            return

        # Poll details
        self.poll.title = title
        self.poll.pools = {option: set() for option in options}
        self.poll.color = discord.Color.random()

        # Since Discord does not provide any means of knowing the on-going modal status
        # poll.start() can only be called here to avoid errors
        await self.poll.start(interaction)


class SetupSelect(Select):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction) -> None:
        await interaction.response.defer()


class SetupView(View):
    def __init__(self, poll):
        self.poll = poll
        super().__init__(*[SetupSelect(**options, row=i)
                           for i, options in enumerate(settings.values())], timeout=180)

    @discord.ui.button(label='Next', style=discord.ButtonStyle.green, emoji='➡', row=len(settings))
    async def confirm_btn_cb(self, btn: Button, interaction: discord.Interaction):
        values = [
            child.values[0] if child.values else None for child in self.children[2:]]
        if values[0] == 'anonymous':
            self.poll.settings['anonymity'] = True
        if values[1] == 'multiple':
            self.poll.settings['format'] = PollFormat.Multiple
        if values[2]:
            self.poll.settings['duration'] = int(values[2])

        self.stop()
        await asyncio.gather(
            self.poll.messages['setup'].edit(
                content=f'投票已設定完畢：**{self.poll.anonymity_cn_str}**、**{self.poll.format_cn_str}**、**{self.poll.settings["duration"]}** 秒',
                view=None),
            interaction.response.send_modal(PollModal(self.poll))
        )

    @discord.ui.button(label='Cancel', style=discord.ButtonStyle.red, emoji='✖', row=len(settings))
    async def cancel_btn_cb(self, btn: Button, interaction: discord.Interaction):
        self.stop()
        await asyncio.gather(
            self.poll.messages['setup'].edit(
                content=f'**已取消發起投票**', view=None),
            interaction.response.defer()
        )

    async def on_timeout(self) -> None:
        self.stop()
        await self.poll.messages['setup'].edit(
            content=f'**你設定太久啦 請再試一次**', view=None)


class PollSelect(Select):
    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    async def callback(self, interaction: discord.Interaction) -> None:
        print(
            f'< POLL - {self.view.poll.title} - {interaction.user.display_name} > ', end='')
        self.view.poll.voters.add(interaction.user)
        if self.view.poll.poll_format == PollFormat.Single:
            new_option = self.values[0]
            prev_option: str = ''
            for option, pool in self.view.poll.pools.items():
                if interaction.user in pool:
                    prev_option = option
                    pool.discard(interaction.user)
            self.view.poll.pools[new_option].add(interaction.user)
            if prev_option:
                await interaction.response.send_message(f'你換了投票選項：**{prev_option}** -> **{new_option}** 。', ephemeral=True)
                print(f'{prev_option} -> {new_option}')
            else:
                await interaction.response.send_message(f'你投了 **{new_option}** 。', ephemeral=True)
                print(new_option)
        else:
            msg = ''
            for option in self.values:
                msg += f'**{option}**\n'
                self.view.poll.pools[option].add(interaction.user)
            for option, pool in self.view.poll.pools.items():
                if interaction.user in pool and option not in self.values:
                    pool.remove(interaction.user)
            msg = msg[:-1]
            await interaction.response.send_message(f'你投了 {msg} 。', ephemeral=True)
            print(msg.replace('**', ''))


class PollView(View):
    def __init__(self, poll):
        self.poll = poll
        super().__init__(PollSelect(placeholder=f'開始投票 - {poll.title}',
                                    max_values=1 if poll.settings['format'] == PollFormat.Single else len(
                                        poll.pools),
                                    options=[SelectOption(label=k)
                                             for k in poll.pools.keys()]), timeout=poll.settings['duration'])


class Poll:
    def __init__(self, ctx: discord.ApplicationContext) -> None:
        self.ctx = ctx
        self.messages: dict[str, discord.InteractionResponse] = {
            'setup': None, 'poll': None, 'result': None}
        self.views: dict[str, View] = {'setup': None, 'poll': None}
        self.settings: dict[str, any] = copy.deepcopy(default_settings)
        self.poll_embed: discord.Embed = None

        # poll details
        self.title: str
        self.pools: dict[str, set[discord.Member]]
        self.voters: set[discord.Member] = set()
        self.color: discord.Color

    @property
    def is_anonymous(self) -> bool:
        return self.settings['anonymity']

    @property
    def poll_format(self) -> PollFormat:
        return self.settings['format']

    @property
    def duration(self) -> int:
        return self.settings['duration']

    @property
    def anonymity_cn_str(self) -> str:
        return '匿名' if self.is_anonymous else '公開'

    @property
    def format_cn_str(self) -> str:
        return '單選' if self.poll_format == PollFormat.Single else '複選'

    async def initiate(self) -> None:
        if is_available(self.ctx.channel.id):
            # configure settings
            self.views['setup'] = SetupView(self)
            init_interaction = await self.ctx.respond('請設定您的投票：**是否匿名?**、**單選複選?**、**投票時長**',
                                                      view=self.views['setup'],
                                                      ephemeral=True)
            self.messages['setup'] = await init_interaction.original_message()
        else:
            # respond cause this is the last message
            await self.ctx.respond('目前的投票尚未結束，請稍後~', ephemeral=True)

    async def start(self, modal_interaction: discord.Interaction) -> None:
        # process modal info into View and Embed
        self.views['poll'] = PollView(self)
        self.color = discord.Color.random()
        self.poll_embed = discord.Embed(
            title=f'投票開始 - **{self.title}**',
            description=f'**{self.anonymity_cn_str}{self.format_cn_str}**\n限時 **{self.duration}** 秒',
            timestamp=datetime.now(),
            color=self.color
        )
        self.poll_embed.set_footer(text=f'由 {self.ctx.author.display_name} 發起',
                                   icon_url=self.ctx.author.display_avatar.url)

        # start the poll at the discord channel
        self.messages['poll'] = await self.ctx.channel.send(view=self.views['poll'], embed=self.poll_embed)
        await modal_interaction.response.send_message(
            '已成功發起投票',
            view=View(Button(
                style=discord.ButtonStyle.link,
                url=self.messages['poll'].jump_url,
                label='查看投票')),
            ephemeral=True
        )

        # set on-going poll
        enter_polling(self.ctx.channel.id, self.duration)
        await asyncio.sleep(self.duration)
        await self.end()

    async def end(self):
        self.messages['result'] = await self.messages['poll'].reply(embed=result_embed_gen(self))

        # edit poll message
        self.views['poll'].stop()
        self.views['poll'].disable_all_items()
        self.views['poll'].add_item(Button(
            label='查看投票結果',
            style=discord.ButtonStyle.link,
            url=self.messages['result'].jump_url)
        )
        options_str = ''
        for option in self.pools.keys():
            options_str += f'**{option}**\n'
        options_str = options_str[:-1]
        self.poll_embed.title = f'*投票已結束 - {self.title}*'
        self.poll_embed.add_field(
            name='投票選項', value=options_str)
        await self.messages['poll'].edit(view=self.views['poll'], embed=self.poll_embed)
