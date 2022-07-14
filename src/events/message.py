
import random
import discord
import asyncio
from typing import Union
from config import *


def rand(x=1.0) -> bool: return x > random.random()


def to_discord_emojis(bot: discord.Bot, emoji_raws: str | int) -> list[str, discord.Emoji]:
    emojis_list: list[str, discord.Emoji] = []
    for emoji_raw in emoji_raws:
        emoji: str | discord.Emoji
        if isinstance(emoji_raw, int):
            emoji = bot.get_emoji(emoji_raw)
        else:
            emoji = emoji_raw
        if emoji:
            emojis_list.append(emoji)
    return emojis_list


async def react_user(bot: discord.Bot, msg: discord.Message):
    uid = msg.author.id
    emoji_raws: list[int] | list[str] | None = None

    if uid == user_ids['soymilk'] and rand(0.1):
        emoji_raws = [emojis['wtf'][0]]
    elif uid == user_ids['howard'] and rand(0.3):
        emoji_raws = [emojis['wtf'][0]]
    elif uid == user_ids['snow_night'] and rand(0.3):
        emoji_raws = [emojis['gay'][0]]
    elif uid == user_ids['paper_bag'] and rand(0.3):
        emoji_raws = [emojis['gay'][0]]
    elif uid == user_ids['gay_dog'] and rand(0.3):
        emoji_raws = [random.choice(['🤮', '🤢'])]
    elif uid == user_ids['feilin'] and rand(0.35):
        emoji_raws = [random.choice(emojis['feilin_set'])]
    elif uid == user_ids['carl_bot'] and rand(0.8):
        emoji_raws = [emojis['gay'][0], random.choice(emojis['angry_dog'])]

    if not emoji_raws:
        return

    await asyncio.gather(*[msg.add_reaction(emoji)
                           for emoji in to_discord_emojis(bot, emoji_raws)
                           if emoji])


async def react_keyword(bot: discord.Bot, msg: discord.Message):
    aws = [msg.add_reaction(bot.get_emoji(random.choice(emojis[k])))
           for k, kws in keywords.items()
           if any(kw in msg.content for kw in kws) and rand(0.5)]

    if aws:
        await asyncio.gather(*aws)
