# -*- coding:utf-8 -*-
from typing import Optional

from httpx import AsyncClient, HTTPError
from asyncache import cached
from bs4 import BeautifulSoup as Bs4
from cachetools import TTLCache
from fake_useragent import UserAgent


class IDRequest:
    __base_url = ""
    __URLS = [
        "http://120.126.197.52",
        "https://120.126.197.52",
        "https://lms.ntpu.edu.tw",
    ]
    __STUDENT_SEARCH_URL = "/portfolio/search.php"
    __UA = UserAgent(min_percentage=0.01)
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

        if not url:
            return False

        try:
            async with AsyncClient(headers={"User-Agent": self.__UA.random}) as client:
                await client.head(url)

        except HTTPError:
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

    @cached(TTLCache(maxsize=9, ttl=60 * 60 * 24 * 7))
    async def get_student_by_uid(self, uid: str) -> str:
        """
        Asynchronously gets a student by their ID.

        Args:
            uid (str): The unique ID of the student.

        Returns:
            str: The name of the student, if found. Otherwise, throws an exception.
        """

        url = self.__base_url + self.__STUDENT_SEARCH_URL

        params = {
            "fmScope": "2",
            "page": "1",
            "fmKeyword": uid,
        }

        try:
            async with AsyncClient(headers={"User-Agent": self.__UA.random}) as client:
                res = await client.get(url, params=params)
                soup = Bs4(res.text, "lxml")

            if student := soup.find("div", {"class": "bloglistTitle"}):
                name = student.find("a").text
                self.STUDENT_DICT[uid] = name
                return name

        except HTTPError:
            self.__base_url = ""

        raise ValueError("Student not found.")

    @cached(TTLCache(maxsize=9, ttl=60 * 60 * 24 * 7))
    async def get_students_by_year_and_department(
        self,
        year: int,
        department: str,
    ) -> dict[str, str]:
        """
        Async function to retrieve students by year and department.

        Args:
            year (int): The year for which to retrieve students.
            department (str): The department for which to retrieve students.

        Returns:
            dict[str, str]: A dictionary of student numbers and names, or throws an exception if not found.
        """

        students = dict[str, str]()
        url = self.__base_url + self.__STUDENT_SEARCH_URL
        params = {
            "fmScope": "2",
            "page": "1",
            "fmKeyword": f"4{year}{department}",
        }
        headers = {
            "User-Agent": self.__UA.random,
        }

        try:
            async with AsyncClient(headers={"User-Agent": self.__UA.random}) as client:
                res = await client.get(url, params=params)
                data = Bs4(res.text, "lxml")
                pages = len(data.find_all("span", {"class": "item"}))

                for i in range(1, pages):
                    params["page"] = str(i)
                    res = await client.get(url, params=params)
                    data = Bs4(res.text, "lxml")

                    for item in data.find_all("div", {"class": "bloglistTitle"}):
                        name = item.find("a").text
                        number = item.find("a").get("href").split("/")[-1]
                        self.STUDENT_DICT[number] = name
                        students[number] = name

        except HTTPError as exc:
            self.__base_url = ""
            raise ValueError("An error occurred while fetching students.") from exc

        return students


ID_REQUEST = IDRequest()
