import asyncio
import aiohttp
from random import choice
from bs4 import BeautifulSoup

starburst_images = []


async def starburst_session(session, link_starto):
    async with session.get(link_starto) as response:
        html = await response.text()
        imgs = BeautifulSoup(html, 'lxml').find(
            'div', class_='MSG-list8C').find_all('img')
        for img in imgs:
            starburst_images.append(img['data-src'])


async def get_starburst_images():
    creations_url = 'https://home.gamer.com.tw/creationDetail.php'
    sns = [4279438, 4443834, 4655069, 4848281, 5046574, 5190390, 5375874]
    links_starto = [f'{creations_url}?sn={sn}' for sn in sns]
    async with aiohttp.ClientSession() as session:
        aws = [starburst_session(session, l) for l in links_starto]
        print('獲取星爆圖中...')
        await asyncio.gather(*aws)


async def starburst_stream():
    if not starburst_images:
        await get_starburst_images()
    return choice(starburst_images)
