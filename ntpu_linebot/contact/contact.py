# -*- coding:utf-8 -*-
from typing import Optional
from urllib.parse import quote


class Contact:
    SANXIA_NORMAL_PHONE = "0286741111"
    TAIPEI_NORMAL_PHONE = "0225024654"
    SANXIA_EMERGENCY_PHONE = "0226711234"
    TAIPEI_EMERGENCY_PHONE = "0225023671"
    SANXIA_24H_PHONE = "0226731949"
    __SEARCH_URL = "https://sea.cc.ntpu.edu.tw/pls/ld/CAMPUS_DIR_M.pq?q="

    def __init__(self, uid: str, name: str) -> None:
        self.__uid = uid
        self.__name = name if name else uid

    @property
    def uid(self) -> str:
        """Getter for uid"""
        return self.__uid

    @property
    def name(self) -> str:
        """Getter for name"""
        return self.__name

    @property
    def search_url(self) -> str:
        """Getter for search_url"""
        try:
            return self.__SEARCH_URL + quote(self.__name, encoding="big5")
        except UnicodeEncodeError:
            return ""


class Individual(Contact):
    def __init__(
        self,
        name: str,
        organization: str,
        title: str,
        extension: str,
        email: str,
    ) -> None:
        super().__init__(organization + title + name, name)
        self.__organization = organization
        self.__title = title
        self.__extension = extension
        self.__email = email

    @property
    def organization(self) -> str:
        """Getter for orginization"""
        return self.__organization

    @property
    def title(self) -> str:
        """Getter for title"""
        return self.__title

    @property
    def extension(self) -> str:
        """Getter for extension"""
        return self.__extension

    @property
    def email(self) -> str:
        """Getter for email"""
        return self.__email

    @property
    def email_url(self) -> Optional[str]:
        """Getter for email_url"""
        return f"mailto:{self.__email}" if self.__email else None

    @property
    def phone(self) -> Optional[str]:
        """Getter for phone"""
        return (
            f"{super().SANXIA_NORMAL_PHONE},{self.__extension[:5]}"
            if len(self.__extension) >= 5
            else None
        )

    @property
    def phone_url(self) -> Optional[str]:
        """Getter for phone_url"""
        sp = super().SANXIA_NORMAL_PHONE
        return (
            f"tel:+886-{sp[1]}-{sp[2:6]}-{sp[6:10]},{self.__extension[:5]}"
            if len(self.__extension) >= 5
            else None
        )


class Organization(Contact):
    def __init__(
        self,
        name: str,
        superior: str,
        location: str,
        website: str,
        members: list[Individual],
    ) -> None:
        super().__init__(superior + name, name)
        self.__superior = superior
        self.__location = location
        self.__website = website
        self.__members = members

    @property
    def superior(self) -> str:
        """Getter for superior"""
        return self.__superior

    @property
    def location(self) -> str:
        """Getter for location"""
        return self.__location

    @property
    def website(self) -> str:
        """Getter for website"""
        return self.__website

    @property
    def members(self) -> list[Individual]:
        """Getter for members"""
        return self.__members
