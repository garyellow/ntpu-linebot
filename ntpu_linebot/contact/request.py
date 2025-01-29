# -*- coding:utf-8 -*-
from typing import Optional
from urllib.parse import quote

from httpx import AsyncClient, HTTPError
from asyncache import cached
from bs4 import BeautifulSoup as Bs4
from bs4 import NavigableString
from cachetools import TTLCache
from fake_useragent import UserAgent

from .contact import Contact, Individual, Organization


class ContactRequest:
    __base_url = ""
    __URLS = [
        "http://120.126.197.7",
        "https://120.126.197.7",
        "https://sea.cc.ntpu.edu.tw",
    ]
    __UA = UserAgent(min_percentage=0.01)
    __ALL_ADMINISTATIVE_URL = "/pls/ld/CAMPUS_DIR_M.p1?kind=1"
    __ALL_ACADEMIC_URL = "/pls/ld/CAMPUS_DIR_M.p1?kind=2"
    __SEARCH_URL = "/pls/ld/CAMPUS_DIR_M.pq?q="
    CONTACT_DICT = dict[str, Contact]()

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
            async with AsyncClient(
                headers={"User-Agent": self.__UA.random}
            ) as client:
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

    async def get_contacts_by_url(self, url: str) -> list[Contact]:
        """
        Asynchronously gets contacts by URL.

        Args:
            url (str): The URL to fetch contacts from.

        Returns:
            list[Contact]: A list of contacts, or throws an exception if the request fails.
        """

        contacts: list[Contact] = []

        try:
            async with AsyncClient(
                headers={"User-Agent": self.__UA.random}
            ) as client:
                res = await client.get(url)
                soup = Bs4(res.text, "lxml")

                for organization in soup.find_all(
                    "div", {"class": "alert alert-info mt-0 mb-0"}
                ):
                    org_names = organization.find_all(
                        "a", {"class": "lang lang-zh-Hant mx-2"}
                    )
                    if len(org_names) == 1:
                        superior = ""
                        org_name = org_names[0].text
                    else:
                        superior = org_names[0].text
                        org_name = org_names[1].text

                    org_datas = organization.find_all("li")
                    location = org_datas[2].text.split("：")[1]
                    website = org_datas[3].find("a").text

                    members: list[Individual] = []
                    member_data = organization.next_sibling.next_sibling
                    if member_data.get("class") == ["w100"]:
                        for data in member_data.find("tbody").find_all("tr"):
                            member_datas = data.find_all("td")
                            member_name = member_datas[0].find("span").text
                            title = member_datas[1].text.strip()
                            extension = member_datas[2].find("span").text
                            email = ""
                            for child in member_datas[4].find("span").children:
                                if isinstance(child, NavigableString):
                                    email += child
                                elif child.name == "img":
                                    email += "@"

                            contact = Individual(
                                name=member_name,
                                organization=org_name,
                                title=title,
                                extension=extension,
                                email=email,
                            )

                            print(member_name, org_name, title, extension, email)
                            members.append(contact)
                            contacts.append(contact)
                            self.CONTACT_DICT[contact.uid] = contact

                    organization = Organization(
                        name=org_name,
                        superior=superior,
                        location=location,
                        website=website,
                        members=members,
                    )

                    contacts.append(organization)
                    self.CONTACT_DICT[organization.uid] = organization

        except HTTPError as exc:
            self.__base_url = ""
            raise ValueError("An error occurred while fetching contacts.") from exc

        return contacts

    async def get_contact_pages_by_url(self, url: str) -> list[Contact]:
        """
        An asynchronous function to retrieve contact pages by URL.

        Args:
            url (str): The URL for which contact pages are to be retrieved.

        Returns:
            list[Contact]: A list of contact pages if found, otherwise throws an exception.
        """

        contacts: list[Contact] = []

        try:
            async with AsyncClient(
                headers={"User-Agent": self.__UA.random}
            ) as client:
                res = await client.get(url)
                soup = Bs4(res.text, "lxml")

                for department in soup.find_all("div", {"class": "card-header"}):
                    url = f"{self.__base_url}/pls/ld/{department.find("a")["href"]}"
                    contacts += await self.get_contacts_by_url(url)

        except HTTPError as exc:
            self.__base_url = ""
            raise ValueError("An error occurred while fetching contacts.") from exc

        return contacts

    async def get_administrative_contacts(self) -> list[Contact]:
        """
        Asynchronously gets administrative contacts.

        Returns:
            list[Contact]: A list of administrative contacts.
        """

        url = self.__base_url + self.__ALL_ADMINISTATIVE_URL
        return await self.get_contact_pages_by_url(url)

    async def get_academic_contacts(self) -> list[Contact]:
        """
        Asynchronously gets academic contacts.

        Returns:
            list[Contact]: A list of academic contacts.
        """

        url = self.__base_url + self.__ALL_ACADEMIC_URL
        return await self.get_contact_pages_by_url(url)

    @cached(TTLCache(maxsize=9, ttl=60 * 60 * 24 * 7))
    async def get_contacts_by_criteria(self, criteria: str) -> list[Contact]:
        """
        Asynchronously retrieves contacts by the given criteria and returns a list of Contact objects.

        Args:
            criteria (str): The criteria for searching contacts.

        Returns:
            list[Contact]: A list of Contact objects if found.
        """

        criteria = quote(criteria, encoding="big5")
        url = self.__base_url + self.__SEARCH_URL + criteria
        return await self.get_contacts_by_url(url)


CONTACT_REQUEST = ContactRequest()
