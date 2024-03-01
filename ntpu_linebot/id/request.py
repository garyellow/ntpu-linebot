# -*- coding:utf-8 -*-
from asyncio import sleep
from random import uniform
from typing import Optional

from aiohttp import ClientError, ClientSession
from asyncache import cached
from bs4 import BeautifulSoup as Bs4
from cachetools import TTLCache


class IDRequest:
    __base_url = ""
    __URLS = [
        "http://120.126.197.52",
        "https://120.126.197.52",
        "https://lms.ntpu.edu.tw",
    ]
    __STUDENT_SEARCH_URL = "/portfolio/search.php"
    STUDENT_DICT = dict[str, str]()

    async def check_url(self, url: Optional[str] = None) -> bool:
        """
        Check if a given URL is accessible by sending a HEAD request to the URL.

        Args:
            url (str, optional): The URL to be checked. Defaults to base_url.

        Returns:
            bool: True if the URL is accessible, False otherwise.
        """

        if url is None:
            url = self.__base_url

        try:
            async with ClientSession() as session:
                async with session.head(url):
                    pass

        except ClientError:
            return False

        return True

    async def change_base_url(self) -> bool:
        """
        Check if a given URL is accessible. If not, try alternative URLs until a valid one is found.
        Returns True if a valid URL is found, False otherwise.
        """

        for url in self.__URLS:
            if await self.check_url(url):
                self.__base_url = url
                return True

        self.__base_url = ""
        return False

    @cached(TTLCache(maxsize=99, ttl=60 * 60 * 24 * 7))
    async def get_student_by_id(self, uid: str) -> Optional[str]:
        """
        Asynchronously gets a student by their ID.

        Args:
            uid (str): The unique ID of the student.

        Returns:
            Optional[str]: The name of the student, if found. Otherwise, None.
        """

        url = self.__base_url + self.__STUDENT_SEARCH_URL
        params = {
            "fmScope": "2",
            "page": "1",
            "fmKeyword": uid,
        }

        try:
            async with ClientSession() as session:
                async with session.get(url, params=params) as res:
                    soup = Bs4(await res.text("utf-8"), "lxml")

            if student := soup.find("div", {"class": "bloglistTitle"}):
                name = student.find("a").text
                self.STUDENT_DICT[uid] = name
                return name

        except ClientError:
            self.__base_url = ""

        return None

    @cached(TTLCache(maxsize=9, ttl=60 * 60 * 24 * 7))
    async def get_students_by_year_and_department(
        self,
        year: str,
        department: str,
    ) -> Optional[dict[str, str]]:
        """
        Async function to retrieve students by year and department.

        Args:
            year (str): The year for which to retrieve students.
            department (str): The department for which to retrieve students.

        Returns:
            Optional[dict[str, str]]: A dictionary of student numbers and names, or None if an error occurs.
        """

        students = dict[str, str]()
        url = self.__base_url + self.__STUDENT_SEARCH_URL
        params = {
            "fmScope": "2",
            "page": "1",
            "fmKeyword": f"4{year}{department}",
        }

        try:
            async with ClientSession() as session:
                async with session.get(url, params=params) as res:
                    data = Bs4(await res.text("utf-8"), "lxml")
                    pages = len(data.find_all("span", {"class": "item"}))

                for i in range(1, pages):
                    await sleep(uniform(0.05, 0.15))

                    params["page"] = str(i)
                    async with session.get(url, params=params) as res:
                        data = Bs4(await res.text("utf-8"), "lxml")

                    for item in data.find_all("div", {"class": "bloglistTitle"}):
                        name = item.find("a").text
                        number = item.find("a").get("href").split("/")[-1]
                        self.STUDENT_DICT[number] = name
                        students[number] = name

        except ClientError:
            self.__base_url = ""
            return None

        return students


ID_REQUEST = IDRequest()
