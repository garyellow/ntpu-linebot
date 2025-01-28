# -*- coding:utf-8 -*-
import random
from asyncio import sleep
from datetime import datetime
from enum import Enum, auto, unique

from sanic import Sanic

from .course import Course, SimpleCourse
from .request import COURSE_REQUEST


async def healthz(app: Sanic, force: bool = False) -> bool:
    """
    Perform a health check on a URL.

    Args:
        app (Sanic): The Sanic application.
        force (bool, optional): Whether to force the renew. Defaults to False.

    Returns:
        bool: True if the health check is successful, False otherwise.
    """

    if await COURSE_REQUEST.check_url():
        return True

    if force or await COURSE_REQUEST.change_base_url():
        await app.cancel_task("load_course_dict", raise_exception=False)
        app.add_task(load_course_dict(), name="load_course_dict")

        return True

    return False


async def load_course_dict() -> None:
    """Updates the course dict for each year."""

    cur_year = datetime.now().year - 1911
    for year in range(cur_year, cur_year - 3, -1):
        await sleep(random.uniform(15, 25))
        await COURSE_REQUEST.get_simple_courses_by_year(year)


async def search_course_by_uid(uid: str) -> Course:
    """
    Asynchronously searches for course by UID.

    Args:
        uid (str): The unique identifier of the course to search for.

    Returns:
        Course: The course corresponding to the given UID.
    """

    return await COURSE_REQUEST.get_course_by_uid(uid)


@unique
class SearchKind(Enum):
    """Enumeration representing the search arguments."""

    NO = auto()
    TITLE = auto()
    TEACHER = auto()
    STRICT_TEACHER = auto()


def search_simple_courses_by_criteria_and_kind(
    criteria: str,
    kind: SearchKind,
    limit: int = 30,
) -> list[SimpleCourse]:
    """
    Function to search courses by a given value and condition, with an optional limit.

    Args:
        criteria (str): The value to search for.
        kind (SearchKind): The kind of search to perform.
        limit (int, optional): The maximum number of results to return. Defaults to 30.

    Returns:
        list[SimpleCourse]: A list of courses matching the criteria, up to the specified limit.
    """

    criteria_set = set(criteria.lower())
    match kind:
        case SearchKind.NO:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                if criteria in course.no
            ]

        case SearchKind.TITLE:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                if criteria_set.issubset(course.title.lower())
            ]

        case SearchKind.TEACHER:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                for teacher in course.teachers
                if criteria_set.issubset(teacher.lower())
            ]

        case SearchKind.STRICT_TEACHER:
            courses = [
                course
                for course in COURSE_REQUEST.COURSE_DICT.values()
                if criteria in course.teachers
            ]

        case _:
            raise ValueError("Invalid SearchArgument")

    return sorted(courses, key=lambda c: (-c.year, c.term, c.no))[:limit]
