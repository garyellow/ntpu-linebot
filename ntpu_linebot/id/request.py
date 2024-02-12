# -*- coding:utf-8 -*-
import asyncio
import random
from collections import defaultdict
from typing import Dict

from aiohttp import ClientSession, ClientError
from bs4 import BeautifulSoup as Bs4
from asyncache import cached
from cachetools import TTLCache

base_url = ""
STUDENT_SEARCH_URL = "/portfolio/search.php?fmScope=2"
student_list = defaultdict(str)


async def is_healthy() -> bool:
    """
    檢查網址是否可用

    若網址無法連線，則嘗試使用其他網址
    """

    global base_url

    try:
        async with ClientSession() as session:
            async with session.head(base_url):
                pass

    except ClientError:
        ip_url = "http://120.126.197.52"
        ips_url = "https://120.126.197.52"
        real_url = "https://lms.ntpu.edu.tw"

        for url in [ip_url, ips_url, real_url]:
            try:
                async with ClientSession() as session:
                    async with session.head(url):
                        base_url = url
                        break

            except ClientError:
                base_url = ""

    return base_url != ""


@cached(TTLCache(maxsize=9999, ttl=60 * 60 * 24 * 7))
async def get_student_by_id(number: str) -> str:
    """取得單一學生的資料(快取一週)"""

    global base_url

    if student_list[number] == "":
        url = f"{base_url}{STUDENT_SEARCH_URL}&page=1&fmKeyword={number}"

        try:
            async with ClientSession() as session:
                async with session.get(url) as res:
                    text = await res.text("utf-8")
                    soup = Bs4(text, "lxml")
                    student = soup.find("div", {"class": "bloglistTitle"})

                    if student is not None:
                        student_list[number] = student.find("a").text
                    else:
                        return ""

        except ClientError:
            base_url = ""
            return ""

    return student_list[number]


@cached(TTLCache(maxsize=99, ttl=60 * 60 * 24 * 7))
async def get_students_by_year_and_department(
    year: str, department: str
) -> Dict[str, str]:
    """取得某年某系(限大學日間部)學生名單(快取一週)"""

    global base_url

    students: Dict[str, str] = {}
    url = f"{base_url}{STUDENT_SEARCH_URL}&page=1&fmKeyword=4{year}{department}"

    try:
        async with ClientSession() as session:
            async with session.get(url) as res:
                text = await res.text("utf-8")
                data = Bs4(text, "lxml")
                pages = len(data.find_all("span", {"class": "item"}))
                await asyncio.sleep(random.uniform(0.1, 0.2))

                for i in range(1, pages):
                    url = f"{base_url}{STUDENT_SEARCH_URL}&page={i}&fmKeyword=4{year}{department}"

                    async with session.get(url) as res:
                        text = await res.text("utf-8")
                        data = Bs4(text, "lxml")

                        for item in data.find_all("div", {"class": "bloglistTitle"}):
                            name = item.find("a").text
                            number = item.find("a").get("href").split("/")[-1]
                            students[number] = name
                            student_list[number] = name

                    await asyncio.sleep(random.uniform(0.1, 0.2))

    except ClientError:
        base_url = ""
        return {}

    return students
