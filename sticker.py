# -*- coding:utf-8 -*-
import time
from typing import List

import requests
from bs4 import BeautifulSoup as BS4

stickers: List[str] = []

SPY_FAMILY_URLS = [
    "https://spy-family.net/tvseries/special/special13.php",
    "https://spy-family.net/tvseries/special/special17.php",
    "https://spy-family.net/tvseries/special/special16.php",
    "https://spy-family.net/tvseries/special/special9.php",
]

ICHIGOPRODUCTION_URL = "https://ichigoproduction.com/special/present_icon.html"


# 載入貼圖(爬蟲)
def load_stickers() -> None:
    for url in SPY_FAMILY_URLS:
        response = requests.get(url)
        soup = BS4(response.text, "html.parser")
        temp = soup.select("ul.icondlLists > li > a > img")

        for i in temp:
            stickers.append("https://spy-family.net/" + i["src"][3:])

        time.sleep(0.5)

    r = requests.get(ICHIGOPRODUCTION_URL)
    soup = BS4(r.text, "html.parser")
    temp = soup.select("a.img_link")

    for i in temp:
        stickers.append("https://ichigoproduction.com/" + i["href"][3:])
