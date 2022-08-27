from discord.ext import commands
from utils import get_lumberjack


class eeSoybot(commands.Bot):
    def __init__(self, owner_id: int, **kwargs) -> None:
        self.owner_id = owner_id
        self.logger = get_lumberjack('eeSoybot')
        super().__init__(**kwargs)

    async def setup_hook(self):
        ...
