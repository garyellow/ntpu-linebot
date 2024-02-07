# -*- coding:utf-8 -*-
import time
from typing import List

import requests
from bs4 import BeautifulSoup as Bs4

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

# 載入貼圖(爬蟲)
for url in SPY_FAMILY_URLS:
    response = requests.get(url, timeout=5)
    soup = Bs4(response.text, "html.parser")
    temp = soup.select("ul.icondlLists > li > a > img")

    for i in temp:
        stickers.append(f"https://spy-family.net/{i['src'][3:]}")

    time.sleep(0.05)

response = requests.get(ICHIGO_PRODUCTION_URL, timeout=5)
soup = Bs4(response.text, "html.parser")
temp = soup.select("ul.tp5 > li > div.ph > a")

for i in temp:
    stickers.append(f"https://ichigoproduction.com/{i['href'][3:]}")
