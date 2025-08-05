# -*- coding:utf-8 -*-
from argparse import Action
from random import sample
from re import IGNORECASE, fullmatch, match, search
from typing import Optional, cast

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
from ..normal_util import list_to_regex
from .course import ALL_EDU_CODE, Course, SimpleCourse
from .util import (
    SearchKind,
    search_course_by_uid,
    search_simple_courses_by_criteria_and_kind,
)


class CourseBot(Bot):
    __SENDER_NAME = "課程魔法師"
    __VALID_CLASS_STR = [
        "class",
        "course",
        "課",
        "課程",
        "科目",
        "課名",
        "課程名",
        "課程名稱",
        "科目",
        "科目名",
        "科目名種",
    ]
    __VALID_TEACHER_STR = [
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
    __UID_REGEX = r"\d{3,4}[" + "".join(ALL_EDU_CODE) + r"]\d{4}"
    __SEARCH_REGEX = r"|".join(__VALID_CLASS_STR + __VALID_TEACHER_STR)
    __CLASS_REGEX = list_to_regex(__VALID_CLASS_STR)
    __TEACHER_REGEX = list_to_regex(__VALID_TEACHER_STR)

    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> list[Message]:
        """處理文字訊息"""

        if match(self.__SEARCH_REGEX, payload, IGNORECASE):
            kind = SearchKind.NONE
            criteria = ""

            if m := search(self.__CLASS_REGEX, payload, IGNORECASE):
                criteria = m.group()
                kind = SearchKind.TITLE

            if m := search(self.__TEACHER_REGEX, payload, IGNORECASE):
                criteria = m.group()
                kind = SearchKind.TEACHER

            if courses := search_simple_courses_by_criteria_and_kind(criteria, kind):
                return [
                    TemplateMessage(
                        altText="請選擇要查詢的課程",
                        template=self.__choose_course_message(courses),
                        sender=get_sender(self.__SENDER_NAME),
                        quickReply=None,
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
                    quickReply=None,
                )
            ]

        return []

    async def handle_postback_event(self, payload: str) -> list[Message]:
        """處理回傳事件"""

        if payload.startswith("授課課程"):
            payload = payload.split(self.split_char)[1]
            if courses := search_simple_courses_by_criteria_and_kind(
                payload,
                SearchKind.STRICT_TEACHER,
            ):
                return [
                    TemplateMessage(
                        altText="請選擇要查詢的課程",
                        template=self.__choose_course_message(courses),
                        sender=get_sender(self.__SENDER_NAME),
                        quickReply=None,
                    )
                ]

            return [
                TextMessage(
                    text=f"查無授課教師為「{payload}」的課程",
                    sender=get_sender(self.__SENDER_NAME),
                    quickReply=None,
                    quoteToken=None,
                )
            ]

        if fullmatch(self.__UID_REGEX, payload, IGNORECASE):
            if course := await search_course_by_uid(payload):
                return [
                    TemplateMessage(
                        altText=f"{course.title}的課程資訊",
                        template=self.__course_info_message(course),
                        sender=get_sender(self.__SENDER_NAME),
                        quickReply=None,
                    )
                ]

            return [
                TextMessage(
                    text=f"查無 uid 為「{payload}」的課程",
                    sender=get_sender(self.__SENDER_NAME),
                    quickReply=None,
                    quoteToken=None,
                )
            ]

        return []

    def __course_info_message(self, course: Course) -> ButtonsTemplate:
        """
        Generate message containing course information and actions for the LINE chatbot.

        Args:
            course (Course): The course object containing information about the course.

        Returns:
            ButtonsTemplate: The message template containing course information and actions.
        """
        teacher_actions: list[Action] = cast(
            list[Action],
            [
                URIAction(label=f"教師課表({name})"[:20], uri=url, altUri=None)
                for (name, url) in course.teachers_name_url
            ],
        )

        if len(teacher_actions) == 1:
            teacher_actions.append(
                cast(
                    Action,
                    PostbackAction(
                        label="查看教師資訊",
                        data=f"查看資訊{self.split_char}{course.teachers[0]}",
                        displayText=None,
                        inputOption=None,
                        fillInText=None,
                    ),
                )
            )

        elif len(teacher_actions) > 2:
            teacher_actions = sample(teacher_actions, 2)

        actions = [
            URIAction(label="課程大綱", uri=course.detail_url, altUri=None),
            URIAction(label="課程查詢系統", uri=course.course_query_url, altUri=None),
            *teacher_actions,
        ]

        texts = [
            f"教師：{', '.join(course.teachers)}",
            f"時間：{', '.join(course.times)}",
            f"地點：{', '.join(course.locations)}",
        ]

        if course.note:
            texts.append(f"\n備註：{course.note}")

        if len(text := "\n".join(texts)) > 60:
            text = text[:59] + "…"

        return ButtonsTemplate(
            title=course.title,
            text=text,
            actions=actions,
            thumbnailImageUrl=None,
            imageAspectRatio=None,
            imageBackgroundColor=None,
            imageSize=None,
            defaultAction=None,
        )

    def __generate_course_text(self, course: SimpleCourse) -> str:
        """
        Generate a text representation of the given SimpleCourse object.

        Args:
            course (SimpleCourse): The SimpleCourse object for which to generate the text.

        Returns:
            str: The text representation of the SimpleCourse object.
        """

        texts = [
            f"課程：{course.title if len(course.title) <= 15 else course.title[:14] + '…'}",
            f"教師：{', '.join(course.teachers)}",
            f"時間：{course.year}"
            + ("上" if course.term == 1 else "下")
            + f" {', '.join(course.times)}",
        ]

        if len(text := "\n".join(texts)) > 34:
            text = text[:33] + "…"

        return text

    def __choose_course_message(self, courses: list[SimpleCourse]) -> CarouselTemplate:
        """
        Generates a carousel template with the details of the given courses for the LINE chatbot.

        Args:
            courses (list[SimpleCourse]): The list of courses to be displayed in the carousel.

        Returns:
            CarouselTemplate: The carousel template containing the course details for display.
        """

        texts = [self.__generate_course_text(course) for course in courses]
        actions = [
            PostbackAction(
                label=course.title[:20],
                displayText=f"查詢 {course.title} 的課程資訊",
                data=course.uid,
                inputOption=None,
                fillInText=None,
            )
            for course in courses
        ]

        while len(actions) % 3 != 0:
            actions.append(EMPTY_POSTBACK_ACTION)

        return CarouselTemplate(
            columns=[
                CarouselColumn(
                    text="選擇要查詢的課程：\n\n"
                    + "\n\n".join(texts[i * 3 : (i + 1) * 3]),
                    actions=actions[i * 3 : (i + 1) * 3],
                    thumbnailImageUrl=None,
                    imageBackgroundColor=None,
                    defaultAction=None,
                )
                for i in range(len(actions) // 3)
            ],
            imageAspectRatio=None,
            imageSize=None,
        )


COURSE_BOT = CourseBot()
