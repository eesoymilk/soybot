from typing import Optional
from discord import Interaction
from discord.app_commands import Cooldown


def cd_but_soymilk(intx: Interaction) -> Optional[Cooldown]:
    return Cooldown(1, 30.0) if intx.user.id != 202249480148353025 else None
