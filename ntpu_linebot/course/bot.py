# -*- coding:utf-8 -*-
from re import IGNORECASE, fullmatch, match, search
from typing import Optional

from linebot.v3.messaging.models import (
    ButtonsTemplate,
    CarouselColumn,
    CarouselTemplate,
    Message,
    PostbackAction,
    TemplateMessage,
    TextMessage,
    URIAction,
)

from ..abs_bot import Bot
from ..line_bot_util import EMPTY_POSTBACK_ACTION, get_sender
from .course import ALL_COURSE_CODE, Course, SimpleCourse
from .util import (
    SearchKind,
    search_course_by_uid,
    search_simple_courses_by_criteria_and_kind,
)


def course_info_message(course: Course) -> ButtonsTemplate:
    """
    Generate message containing course information and actions for the LINE chatbot.

    Args:
        course (Course): The course object containing information about the course.

    Returns:
        ButtonsTemplate: The message template containing course information and actions.
    """

    actions = [
        URIAction(label="課程大綱", uri=course.detail_url),
        *[
            URIAction(label=f"教師課表({name})", uri=url)
            for (name, url) in course.teachers_name_url
        ],
        URIAction(label="課程查詢系統", uri=course.course_query_url),
    ]

    text = "\n".join(
        [
            f"教師：{', '.join(course.teachers)}",
            f"時間：{', '.join(course.times)}",
            f"地點：{', '.join(course.locations)}",
        ]
    )

    if course.note:
        text += f"\n備註：{course.note}"

    if len(text) > 60:
        text = text[:59] + "…"

    return ButtonsTemplate(title=course.title, text=text, actions=actions)


def generate_course_text(course: SimpleCourse) -> str:
    """
    Generate a text representation of the given SimpleCourse object.

    Args:
        course (SimpleCourse): The SimpleCourse object for which to generate the text.

    Returns:
        str: The text representation of the SimpleCourse object.
    """

    text = "\n".join(
        [
            f"課程：{course.title if len(course.title) <= 15 else course.title[:14] + '…'}",
            f"教師：{', '.join(course.teachers)}",
            f"時間：{course.year}"
            + ("上" if course.term == 1 else "下")
            + f" {', '.join(course.times)}",
        ]
    )

    if len(text) > 34:
        text = text[:33] + "…"

    return text


def choose_course_message(courses: list[SimpleCourse]) -> CarouselTemplate:
    """
    Generates a carousel template with the details of the given courses for the LINE chatbot.

    Args:
        courses (list[SimpleCourse]): The list of courses to be displayed in the carousel.

    Returns:
        CarouselTemplate: The carousel template containing the course details for display.
    """

    texts = [generate_course_text(course) for course in courses]
    actions = [
        PostbackAction(
            label=course.title,
            displayText=f"正在查詢 {course.title} 的課程資訊",
            data=course.uid,
        )
        for course in courses
    ]

    while len(actions) % 3 != 0:
        actions.append(EMPTY_POSTBACK_ACTION)

    return CarouselTemplate(
        columns=[
            CarouselColumn(
                text="選擇要查詢的課程：\n\n" + "\n\n".join(texts[i * 3 : (i + 1) * 3]),
                actions=actions[i * 3 : (i + 1) * 3],
            )
            for i in range(len(actions) // 3)
        ]
    )


class CourseBot(Bot):
    __SENDER_NAME = "課程魔法師"
    __VALID_CLASS_STR = [
        "class",
        "course",
        "課",
        "課程",
        "課名",
        "課程名",
        "課程名稱",
        "科目",
        "科目名",
        "科目名種",
    ]
    __TEACHER_STR_LIST = [
        "dr",
        "prof",
        "teacher",
        "professor",
        "doctor",
        "師",
        "老師",
        "教師",
        "教授",
        "老師名",
        "教師名",
        "教授名",
        "老師名稱",
        "教師名稱",
        "教授名稱",
        "授課教師",
        "授課老師",
        "授課教授",
    ]
    __UID_REGEX = r"\d{3,4}[" + "".join(ALL_COURSE_CODE) + r"]\d{4}"
    __SEARCH_REGEX = r"|".join(__VALID_CLASS_STR + __TEACHER_STR_LIST)
    __TITLE_REGEX = (
        r"(?<=(" + r"|".join(rf"(?<={c})" for c in __VALID_CLASS_STR) + r")[ +]).*"
    )
    __TEACHER_REGEX = (
        r"(?<=(" + r"|".join(rf"(?<={s})" for s in __TEACHER_STR_LIST) + r")[ +]).*"
    )

    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> list[Message]:
        """處理文字訊息"""

        if fullmatch(self.__UID_REGEX, payload, IGNORECASE):
            if course := await search_course_by_uid(payload):
                return [
                    TemplateMessage(
                        altText=f"{course.title}的課程資訊",
                        template=course_info_message(course),
                        sender=get_sender(self.__SENDER_NAME),
                    )
                ]

        if match(self.__SEARCH_REGEX, payload, IGNORECASE):
            if m := search(self.__TITLE_REGEX, payload, IGNORECASE):
                criteria = m.group()
                kind = SearchKind.TITLE

            if m := search(self.__TEACHER_REGEX, payload, IGNORECASE):
                criteria = m.group()
                kind = SearchKind.TEACHER

            if courses := search_simple_courses_by_criteria_and_kind(criteria, kind):
                return [
                    TemplateMessage(
                        altText="請選擇要查詢的課程",
                        template=choose_course_message(courses),
                        sender=get_sender(self.__SENDER_NAME),
                    )
                ]

            match kind:
                case SearchKind.TITLE:
                    condition_str = "名稱"
                case SearchKind.TEACHER:
                    condition_str = "授課教師姓名"
                case _:
                    condition_str = "未知"

            return [
                TextMessage(
                    text=f"查無{condition_str}含有「{criteria}」的課程，請重新輸入",
                    sender=get_sender(self.__SENDER_NAME),
                    quoteToken=quote_token,
                )
            ]

        return list[Message]()

    async def handle_postback_event(self, payload: str) -> list[Message]:
        """處理回傳事件"""

        if fullmatch(self.__UID_REGEX, payload, IGNORECASE):
            if course := await search_course_by_uid(payload):
                return [
                    TemplateMessage(
                        altText=f"{course.title}的課程資訊",
                        template=course_info_message(course),
                        sender=get_sender(self.__SENDER_NAME),
                    )
                ]

        return list[Message]()


COURSE_BOT = CourseBot()
