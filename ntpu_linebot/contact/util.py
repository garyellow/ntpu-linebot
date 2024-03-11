# -*- coding:utf-8 -*-
import random
from asyncio import sleep
from typing import Optional

from sanic import Sanic

from ntpu_linebot.contact.contact import Contact, Organization

from .request import CONTACT_REQUEST


async def healthz(app: Sanic) -> bool:
    """
    Perform a health check on a URL.

    Args:
        app (Sanic): An instance of the Sanic class representing the Sanic application.

    Returns:
        bool: True if the health check is successful, False otherwise.
    """

    if not await CONTACT_REQUEST.check_url():
        if await CONTACT_REQUEST.change_base_url():
            await app.cancel_task("renew_contact_dict", raise_exception=False)
            app.add_task(renew_contact_dict, name="renew_contact_dict")

        return False

    return True


async def renew_contact_dict() -> None:
    """Updates the contact dict for each year."""

    await sleep(random.uniform(20, 40))
    await CONTACT_REQUEST.get_administrative_contacts()
    await sleep(random.uniform(20, 40))
    await CONTACT_REQUEST.get_academic_contacts()


def search_contact_by_uid(uid: str) -> Optional[Contact]:
    """
    Search for a contact by its unique identifier.

    Args:
        uid (str): The unique identifier of the contact.

    Returns:
        Optional[Contact]: The contact object if found, otherwise None.
    """

    return CONTACT_REQUEST.CONTACT_DICT.get(uid)


def search_contacts_by_name(name: str) -> list[Contact]:
    """
    Search contacts by name and return a list of Contact objects.

    Args:
        name (str): The name to search for in the contacts.

    Returns:
        list[Contact]: A list of Contact objects with the matching name.
    """

    return [
        contact
        for contact in CONTACT_REQUEST.CONTACT_DICT.values()
        if name == contact.name
        or isinstance(contact, Organization)
        and name == contact.superior
    ]


async def search_contacts_by_criteria(criteria: str) -> Optional[list[Contact]]:
    """
    Asynchronously searches contacts by the specified criteria and returns a list of contacts or None.

    Args:
        criteria (str): The criteria used for searching contacts.

    Returns:
        Optional[list[Contact]]: A list of contacts matching the criteria, or None if no contacts are found.
    """

    if contacts := [
        contact
        for contact in CONTACT_REQUEST.CONTACT_DICT.values()
        if set(criteria).issubset(contact.name)
        or isinstance(contact, Organization)
        and set(criteria).issubset(contact.superior)
    ]:
        return contacts

    return await CONTACT_REQUEST.get_contacts_by_criteria(criteria)
