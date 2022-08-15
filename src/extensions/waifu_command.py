import json
from unicodedata import category
import discord
import aiohttp
import json
from urllib.parse import urljoin
from discord import app_commands
from discord.app_commands import (guilds, guild_only, choices, Choice, describe, rename)
from discord.ext import commands
from utils import Config

waifu_pics_url = 'https://api.waifu.pics'

categories = {
    'sfw': {
        'neko': '貓娘',
        'shinobu': '',
    }
}

async def fetch_waifu() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(urljoin(waifu_pics_url, 'sfw/waifu')) as response:
            img_url = (await response.json())['url']
            return img_url
            ...
    
    return ...

@app_commands.command(name='test_waifu', description='你老婆真好用...')
@describe(category='老婆類型')
@rename(category='老婆類型')
@choices(
    anonymity=[
        Choice(name='公開', value='public'),
        Choice(name='匿名', value='anonymous'),
    ],
)
@guilds(Config.guilds['debug'].id)
@guild_only()
async def test_waifu(interaction: discord.Interaction, category):
    img_url = await fetch_waifu()
    await interaction.response.send_message(img_url)

@app_commands.command(name='waifu', description='你老婆真好用...')
@guilds(*Config.guild_ids)
@guild_only()
@app_commands.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def waifu(interaction: discord.Interaction):
    img_url = await fetch_waifu()
    await interaction.response.send_message(img_url)
    
async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(waifu)
    # bot.tree.add_command(test_waifu)