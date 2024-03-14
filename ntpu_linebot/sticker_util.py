# -*- coding:utf-8 -*-
from asyncio import sleep

from aiohttp import ClientSession
from bs4 import BeautifulSoup as Bs4
from fake_useragent import UserAgent
from sanic import Sanic


class StickerUtil:
    __SPY_FAMILY_URLS = [
        "https://spy-family.net/tvseries/special/special1_season1.php",
        "https://spy-family.net/tvseries/special/special2_season1.php",
        "https://spy-family.net/tvseries/special/special9_season1.php",
        "https://spy-family.net/tvseries/special/special13_season1.php",
        "https://spy-family.net/tvseries/special/special16_season1.php",
        "https://spy-family.net/tvseries/special/special17_season1.php",
        "https://spy-family.net/tvseries/special/special3.php",
    ]
    __ICHIGO_PRODUCTION_URL = "https://ichigoproduction.com/special/present_icon.html"
    __UA = UserAgent(min_percentage=2.5)
    STICKER_LIST = list[str]()

    async def is_healthy(self, app: Sanic, force: bool = False) -> bool:
        """
        Check if the application is healthy.

        Args:
            app (Sanic): The Sanic application.
            force (bool, optional): Whether to force the renew. Defaults to False.

        Returns:
            bool: True if the application is healthy, False otherwise.
        """

        if force:
            await app.cancel_task("load_stickers", raise_exception=False)
            app.add_task(self.load_stickers, name="load_stickers")
            return True

        if len(self.STICKER_LIST) == 0:
            await app.cancel_task("load_stickers", raise_exception=False)
            app.add_task(self.load_stickers, name="load_stickers")
            return False

        return True

    async def load_stickers(self) -> None:
        """
        Loads stickers by scraping the specified URLs using aiohttp and BeautifulSoup.
        Appends the URLs of the stickers to the stickers list.
        """

        headers = {
            "User-Agent": self.__UA.random,
        }

        async with ClientSession() as session:
            for url in self.__SPY_FAMILY_URLS:
                async with session.get(url, headers=headers) as response:
                    soup = Bs4(await response.text(), "lxml")

                for i in soup.select("ul.icondlLists > li > a"):
                    if herf := i.get("herf"):
                        self.STICKER_LIST.append(
                            f"https://spy-family.net/tvseries/{herf[3:]}"
                        )

                await sleep(0.05)

            async with session.get(
                self.__ICHIGO_PRODUCTION_URL,
                headers=headers,
            ) as response:
                soup = Bs4(await response.text(), "lxml")

            for i in soup.select("ul.tp5 > li > div.ph > a"):
                if href := i.get("href"):
                    self.STICKER_LIST.append(
                        f"https://ichigoproduction.com/{href[3:]}"
                    )


STICKER = StickerUtil()
