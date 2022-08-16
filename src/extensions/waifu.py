import discord
import aiohttp
from urllib.parse import urljoin
from discord import app_commands as ac
from discord.app_commands import Choice
from discord.ext import commands
from datetime import datetime
from utils import Config

waifu_pics_url = 'https://api.waifu.pics'
categories = {
    'sfw': {
        '貓娘': 'neko',
        '忍野忍': 'shinobu',
        '惠惠': 'megumin',
        '抱抱': 'cuddle',
        '哭哭': 'cry',
        '抱抱': 'hug',
        '親親': 'kiss',
        '舔舔': 'lick',
        '摸摸': 'pat',
        '傲嬌': 'smug',
        'YEET': 'yeet',
        '臉紅': 'blush',
        '好ㄘ': 'nom',
        '咬': 'bite',
        '踢人': 'kick',
        '開心': 'happy',
        '眨眼': 'wink',
        '跳舞': 'dance',
    },
    'nsfw': {
        '貓娘': 'neko',
        '偽娘': 'trap',
        '咬': 'blowjob',
    },
}


@ac.command(description='你老婆真好用...')
@ac.describe(category='你今天要哪種老婆')
@ac.rename(category='老婆類型')
@ac.choices(category=[Choice(name=k, value=v) for k, v in categories['sfw'].items()],)
# @ac.guilds(Config.guilds['debug'].id)
@ac.guilds(*Config.guild_ids)
@ac.checks.cooldown(1, 30.0, key=lambda i: (i.channel.id, i.user.id))
async def waifu(interaction: discord.Interaction, category: Choice[str] = None):
    async with aiohttp.ClientSession() as session:
        if category is None:
            category = Choice(name='隨機', value='waifu')
        url = urljoin(waifu_pics_url, f'sfw/{category.value}')

        async with session.get(url) as response:
            try:
                img_url = (await response.json())['url']
                embed = discord.Embed(
                    color=discord.Color.random(),
                    description=f'老婆類型: {category.name}',
                    type='image',
                    timestamp=datetime.now(),
                )
                embed.set_image(url=img_url)
                await interaction.response.send_message(embed=embed)
            except:
                await interaction.response.send_message('醒 你沒老婆')


@ac.command(description='可以色色...', nsfw=True)
@ac.describe(category='你今天想要哪種色色')
@ac.rename(category='色色類型')
@ac.choices(category=[Choice(name=k, value=v) for k, v in categories['nsfw'].items()])
# @ac.guilds(Config.guilds['debug'].id)
@ac.guilds(*Config.guild_ids)
async def horny(interaction: discord.Interaction, category: Choice[str] = None):
    async with aiohttp.ClientSession() as session:
        if category is None:
            category = Choice(name='隨機', value='waifu')
        url = urljoin(waifu_pics_url, f'nsfw/{category.value}')

        async with session.get(url) as response:
            try:
                img_url = (await response.json())['url']
                embed = discord.Embed(
                    color=discord.Color.random(),
                    description=f'色色類型: {category.name}',
                    type='image',
                    timestamp=datetime.now(),
                )
                embed.set_image(url=img_url)
                await interaction.response.send_message(embed=embed)
            except:
                await interaction.response.send_message('不可以色色')


async def setup(bot: commands.Bot) -> None:
    bot.tree.add_command(waifu)
    bot.tree.add_command(horny)
