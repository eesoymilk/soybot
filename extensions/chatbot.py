import textwrap

from discord import Message
from discord.ext.commands import Cog, Bot

from utils import get_lumberjack

log = get_lumberjack(__name__)


class ChatbotCog(Cog):
    SYSYEM_MESSAGE = textwrap.dedent('''\
        This is a discord channel with potentially multiple people chatting.
        Now you are to chat with them.
        Just have fun and chat with people in discord.
        If you are to respond in Chinese, please use traditional Chinese (繁體中文).
    ''')

    def __init__(self, bot: Bot):
        self.bot = bot
        self.chat_history: dict[int, str] = dict()

    def append_chat_history(self, msg: Message):
        if msg.channel.id not in self.chat_history:
            self.chat_history[msg.channel.id] = ''

        self.chat_history[msg.channel.id] += f'{msg.author.display_name}: {msg.content}\n'

    @Cog.listener()
    async def on_message(self, msg: Message):
        self.append_chat_history(msg)

        if msg.author == self.bot.user:
            return

        is_mentioned = False
        if msg.reference is not None:
            refernced_msg = await msg.channel.fetch_message(
                msg.reference.message_id
            )
            if refernced_msg.author == self.bot.user:
                is_mentioned = True

        if not (
            is_mentioned or
            msg.content.strip().startswith(self.bot.user.mention)
        ):
            return

        # TODO Chatbot


async def setup(bot: Bot):
    await bot.add_cog(ChatbotCog(bot))
