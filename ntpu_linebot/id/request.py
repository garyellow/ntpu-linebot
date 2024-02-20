# -*- coding:utf-8 -*-
import random
from asyncio import sleep

from aiohttp import ClientError, ClientSession
from asyncache import cached
from bs4 import BeautifulSoup as Bs4
from cachetools import TTLCache


class IDRequest:
    base_url = ""
    STUDENT_SEARCH_URL = "/portfolio/search.php"
    STUDENT_DICT = dict[str, str]()

    async def is_healthy(self) -> bool:
        """
        Check if a given URL is accessible. If not, try alternative URLs until a valid one is found.
        Returns True if a valid URL is found, False otherwise.
        """

        async def check_url(url: str) -> bool:
            try:
                async with ClientSession() as session:
                    async with session.head(url):
                        return True

            except ClientError:
                return False

        URLS = [
            "http://120.126.197.52",
            "https://120.126.197.52",
            "https://lms.ntpu.edu.tw",
        ]

        for url in URLS:
            if await check_url(url):
                self.base_url = url
                return True

        self.base_url = ""
        return False

    @cached(TTLCache(maxsize=9999, ttl=60 * 60 * 24 * 7))
    async def get_student_by_id(self, uid: str) -> str:
        """
        Retrieves information about a student by their ID.

        Args:
            uid (str): The ID of the student.

        Returns:
            str: The information of the student with the provided ID. If the student is not found or an error occurs, an empty string is returned.
        """

        url = self.base_url + self.STUDENT_SEARCH_URL
        params = {
            "fmScope": "2",
            "page": "1",
            "fmKeyword": uid,
        }

        try:
            async with ClientSession() as session:
                async with session.get(url, params=params) as res:
                    text = await res.text("utf-8")
                    soup = Bs4(text, "lxml")
                    student = soup.find("div", {"class": "bloglistTitle"})

                    if student is not None:
                        self.STUDENT_DICT[uid] = student.find("a").text
                    else:
                        return ""

        except ClientError:
            self.base_url = ""
            return ""

        return self.STUDENT_DICT[uid]

    @cached(TTLCache(maxsize=99, ttl=60 * 60 * 24 * 7))
    async def get_students_by_year_and_department(
        self,
        year: str,
        department: str,
    ) -> dict[str, str]:
        """
        Retrieves a dict of students by year and department from a website.
        Uses caching to store the results for a week and makes asynchronous HTTP requests to fetch the data.

        Args:
            year (str): The year of the students to retrieve.
            department (str): The department of the students to retrieve.

        Returns:
            Dict[str, str]: A dictionary containing the student numbers as keys and their corresponding names as values.
        """

        students = dict[str, str]()
        url = self.base_url + self.STUDENT_SEARCH_URL
        params = {
            "fmScope": "2",
            "page": "1",
            "fmKeyword": f"4{year}{department}",
        }

        try:
            async with ClientSession() as session:
                async with session.get(url, params=params) as res:
                    text = await res.text("utf-8")
                    data = Bs4(text, "lxml")
                    pages = len(data.find_all("span", {"class": "item"}))
                    await sleep(random.uniform(0.1, 0.2))

                    for i in range(1, pages):
                        params["page"] = str(i)

                        async with session.get(url, params=params) as res:
                            text = await res.text("utf-8")
                            data = Bs4(text, "lxml")

                            for item in data.find_all(
                                "div", {"class": "bloglistTitle"}
                            ):
                                name = item.find("a").text
                                number = item.find("a").get("href").split("/")[-1]
                                students[number] = name
                                self.STUDENT_DICT[number] = name

                        await sleep(random.uniform(0.1, 0.2))

        except ClientError:
            self.base_url = ""
            return {}

        return students


ID_REQUEST = IDRequest()
