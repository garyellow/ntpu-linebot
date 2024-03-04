# -*- coding:utf-8 -*-
import random
from asyncio import sleep
from datetime import datetime
from enum import Enum, auto, unique
from typing import Optional

from asyncache import cached
from cachetools import TTLCache
from sanic import Sanic

from .course import Course, SimpleCourse
from .request import COURSE_REQUEST


async def healthz(app: Sanic) -> bool:
    """
    Perform a health check on a URL.

    Args:
        app (Sanic): An instance of the Sanic class representing the Sanic application.

    Returns:
        bool: True if the health check is successful, False otherwise.
    """

    if not await COURSE_REQUEST.check_url():
        if await COURSE_REQUEST.change_base_url():
            await app.cancel_task("renew_course_dict", raise_exception=False)
            app.add_task(renew_course_dict, name="renew_course_dict")

        return False

    return True


async def renew_course_dict() -> None:
    """Updates the course dict for each year."""

    cur_year = datetime.now().year - 1911
    for year in range(cur_year, cur_year - 5, -1):
        await COURSE_REQUEST.get_simple_courses_by_year(year)
        await sleep(random.uniform(10, 20))


async def search_course_by_uid(uid: str) -> Optional[Course]:
    """
    Asynchronously searches for course by UID.

    Args:
        uid (str): The unique identifier of the course to search for.

    Returns:
        Optional[Course]: The course corresponding to the given UID, or None if not found.
    """

    return await COURSE_REQUEST.get_course_by_uid(uid)


@unique
class SearchArgument(Enum):
    """Enumeration representing the search arguments."""

    NO = auto()
    TITLE = auto()
    TEACHER = auto()


@cached(TTLCache(maxsize=99, ttl=60 * 60))
def search_simple_courses_by_condition(
    criteria: str,
    condition: SearchArgument,
    limit: int = 30,
) -> list[SimpleCourse]:
    """
    Function to search courses by a given value and condition, with an optional limit.

    Args:
        value (str): The value to search for.
        condition (SearchArgument): The condition to apply to the search.
        limit (int, optional): The maximum number of results to return. Defaults to 30.

    Returns:
        list[SimpleCourse]: A list of courses matching the criteria, up to the specified limit.
    """

    match condition:
        case SearchArgument.NO:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                if criteria in course.no
            ]

        case SearchArgument.TITLE:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                if set(criteria).issubset(set(course.title))
            ]

        case SearchArgument.TEACHER:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                for teacher in course.teachers
                if set(criteria).issubset(set(teacher))
            ]

        case _:
            raise ValueError("Invalid SearchArgument")

    return sorted(courses, key=lambda course: (-course.year, course.term, course.no))[
        :limit
    ]
