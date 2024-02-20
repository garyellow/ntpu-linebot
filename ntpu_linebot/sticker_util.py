# -*- coding:utf-8 -*-
from asyncio import sleep

from aiohttp import ClientSession
from bs4 import BeautifulSoup as Bs4
from sanic import Sanic

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


class StickerUtil:
    STICKER_LIST = list[str]()

    async def is_healthy(self, app: Sanic) -> bool:
        """
        Checks if the `stickers` list is empty.

        If it is empty, adds the `load_stickers` task to the Sanic app and return False.
        Otherwise, returns True.
        """

        if not self.STICKER_LIST:
            await app.cancel_task("load_stickers", raise_exception=False)
            app.add_task(self.load_stickers, name="load_stickers")
            return False

        return True

    async def load_stickers(self) -> None:
        """
        Loads stickers by scraping the specified URLs using aiohttp and BeautifulSoup.
        Appends the URLs of the stickers to the stickers list.
        """

        async with ClientSession() as session:
            for url in SPY_FAMILY_URLS:
                async with session.get(url) as response:
                    text = await response.text()
                    soup = Bs4(text, "lxml")
                    temp = soup.select("ul.icondlLists > li > a > img")

                    for i in temp:
                        self.STICKER_LIST.append(
                            f"https://spy-family.net/{i['src'][3:]}"
                        )

                await sleep(0.05)

            async with session.get(ICHIGO_PRODUCTION_URL) as response:
                text = await response.text()
                soup = Bs4(text, "lxml")
                temp = soup.select("ul.tp5 > li > div.ph > a")

                for i in temp:
                    self.STICKER_LIST.append(
                        f"https://ichigoproduction.com/{i['href'][3:]}"
                    )


STICKER = StickerUtil()
