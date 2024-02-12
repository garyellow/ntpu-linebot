# -*- coding:utf-8 -*-
import asyncio
from typing import List

from aiohttp import ClientSession
from bs4 import BeautifulSoup as Bs4
from sanic import Sanic

stickers: List[str] = []

SPY_FAMILY_URLS = [
    "https://spy-family.net/tvseries/special/special1_season1.php",
    "https://spy-family.net/tvseries/special/special2_season1.php",
    "https://spy-family.net/tvseries/special/special9_season1.php",
    "https://spy-family.net/tvseries/special/special13_season1.php",
    "https://spy-family.net/tvseries/special/special16_season1.php",
    "https://spy-family.net/tvseries/special/special17_season1.php",
    "https://spy-family.net/tvseries/special/special3.php",
]

ICHIGO_PRODUCTION_URL = "https://ichigoproduction.com/special/present_icon.html"


async def is_healthy(app: Sanic) -> bool:
    """檢查貼圖是否可用"""

    if len(stickers) == 0:
        app.add_task(load_stickers)

        return False

    return True


async def load_stickers():
    """載入貼圖(爬蟲)"""

    async with ClientSession() as session:
        for url in SPY_FAMILY_URLS:
            async with session.get(url) as response:
                text = await response.text()
                soup = Bs4(text, "lxml")
                temp = soup.select("ul.icondlLists > li > a > img")

                for i in temp:
                    stickers.append(f"https://spy-family.net/{i['src'][3:]}")

            await asyncio.sleep(0.05)

        async with session.get(ICHIGO_PRODUCTION_URL) as response:
            text = await response.text()
            soup = Bs4(text, "lxml")
            temp = soup.select("ul.tp5 > li > div.ph > a")

            for i in temp:
                stickers.append(f"https://ichigoproduction.com/{i['href'][3:]}")
