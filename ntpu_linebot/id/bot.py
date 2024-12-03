# -*- coding:utf-8 -*-
from datetime import datetime
from math import ceil
from re import IGNORECASE, search
from typing import Optional

from linebot.v3.messaging.models import (
    ButtonsTemplate,
    CarouselColumn,
    CarouselTemplate,
    ConfirmTemplate,
    ImageMessage,
    Message,
    MessageAction,
    PostbackAction,
    QuickReply,
    QuickReplyItem,
    TemplateMessage,
    TextMessage,
)

from ..abs_bot import Bot
from ..line_bot_util import EMPTY_POSTBACK_ACTION, get_sender
from ..normal_util import list_to_regex, partition
from .util import (
    DEPARTMENT_CODE,
    DEPARTMENT_NAME,
    FULL_DEPARTMENT_CODE,
    FULL_DEPARTMENT_NAME,
    Order,
    search_student_by_uid,
    search_students_by_name,
    search_students_by_year_and_department,
    student_info_format,
)


class IDBot(Bot):
    __SENDER_NAME = "學號魔法師"
    __VALID_DEPARTMENT_STR = [
        "dep",
        "department",
        "系",
        "所",
        "系所",
        "科系",
        "系名",
        "系所名",
        "科系名",
        "系所名稱",
        "科系名稱",
    ]
    __VALID_DEPARTMENT_CODE_STR = [
        "depCode",
        "departmentCode",
        "系代碼",
        "系所代碼",
        "科系代碼",
        "系編號",
        "系所編號",
        "科系編號",
    ]
    __VALID_YEAR_STR = [
        "year",
        "年份",
        "學年",
        "年度",
        "學年度",
        "入學年",
        "入學學年",
        "入學年度",
    ]
    __VALID_STUDENT_STR = [
        "student",
        "name",
        "學生",
        "姓名",
        "學生姓名",
        "學號",
        "學生編號",
    ]
    __DEPARTMENT_REGEX = list_to_regex(__VALID_DEPARTMENT_STR)
    __DEPARTMENT_CODE_REGEX = list_to_regex(__VALID_DEPARTMENT_CODE_STR)
    __YEAR_REGEX = list_to_regex(__VALID_YEAR_STR)
    __STUDENT_REGEX = list_to_regex(__VALID_STUDENT_STR)
    __ALL_DEPARTMENT_CODE = "所有系代碼"
    __COLLEGE_NAMES = [
        "人文學院",
        "法律學院",
        "商學院",
        "公共事務學院",
        "社會科學學院",
        "電機資訊學院",
    ]

    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> list[Message]:
        """處理文字訊息"""

        if payload == self.__ALL_DEPARTMENT_CODE:
            department_info = "\n".join(
                [f"{x}系 -> {y}" for x, y in DEPARTMENT_CODE.items()]
            )

            return [
                TextMessage(
                    text=department_info,
                    sender=get_sender(self.__SENDER_NAME),
                    quoteToken=quote_token,
                ),
            ]

        if match := search(self.__DEPARTMENT_REGEX, payload, IGNORECASE):
            criteria = match.group()

            if department_code := DEPARTMENT_CODE.get(criteria.rstrip("系")):
                return [
                    TextMessage(
                        text=department_code,
                        quickReply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label=self.__ALL_DEPARTMENT_CODE,
                                        text=self.__ALL_DEPARTMENT_CODE,
                                    )
                                ),
                            ]
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

            if full_department_code := FULL_DEPARTMENT_CODE.get(criteria):
                return [
                    TextMessage(
                        text=full_department_code,
                        quickReply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label=self.__ALL_DEPARTMENT_CODE,
                                        text=self.__ALL_DEPARTMENT_CODE,
                                    )
                                ),
                            ]
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

            return [
                TextMessage(
                    text="請輸入正確的系名",
                    sender=get_sender(self.__SENDER_NAME),
                    quoteToken=quote_token,
                ),
            ]

        if match := search(self.__DEPARTMENT_CODE_REGEX, payload, IGNORECASE):
            criteria = match.group()

            if full_department_name := FULL_DEPARTMENT_NAME.get(criteria):
                return [
                    TextMessage(
                        text=full_department_name,
                        quickReply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label=self.__ALL_DEPARTMENT_CODE,
                                        text=self.__ALL_DEPARTMENT_CODE,
                                    ),
                                ),
                            ]
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

            return [
                TextMessage(
                    text="請輸入正確的系代碼",
                    sender=get_sender(self.__SENDER_NAME),
                    quoteToken=quote_token,
                ),
            ]

        if match := search(self.__YEAR_REGEX, payload, IGNORECASE):
            criteria = match.group()

            if 2 <= len(criteria) <= 4:
                year = int(criteria) if int(criteria) < 1911 else int(criteria) - 1911

                if year > datetime.now().year - 1911:
                    return [
                        TextMessage(
                            text="你未來人？(⊙ˍ⊙)",
                            sender=get_sender(self.__SENDER_NAME),
                            quoteToken=quote_token,
                        )
                    ]
                if year >= 113:
                    sender = get_sender(self.__SENDER_NAME)
                    image_url = "https://raw.githubusercontent.com/garyellow/ntpu-linebot/main/assets/rip.png"

                    return [
                        TextMessage(
                            text="數位學苑 2.0 已停止使用，無法取得資料",
                            sender=sender,
                            quoteToken=quote_token,
                        ),
                        ImageMessage(
                            originalContentUrl=image_url,
                            previewImageUrl=image_url,
                            sender=sender,
                            quoteToken=quote_token,
                        ),
                    ]
                if year < 90:
                    return [
                        TextMessage(
                            text="學校都還沒蓋好(￣▽￣)",
                            sender=get_sender(self.__SENDER_NAME),
                            quoteToken=quote_token,
                        )
                    ]
                if 90 <= year < 95:
                    return [
                        TextMessage(
                            text="數位學苑還沒出生喔~~",
                            sender=get_sender(self.__SENDER_NAME),
                            quoteToken=quote_token,
                        )
                    ]

                return [
                    TemplateMessage(
                        altText="確認學年度",
                        template=ConfirmTemplate(
                            text=f"是否要搜尋 {year} 學年度的學生",
                            actions=[
                                PostbackAction(
                                    label="哪次不是",
                                    displayText="哪次不是",
                                    data=f"搜尋全系{self.split_char}{year}",
                                    inputOption="openRichMenu",
                                ),
                                PostbackAction(
                                    label="我在想想",
                                    displayText="再啦乾ಠ_ಠ",
                                    data="兇",
                                    inputOption="openKeyboard",
                                ),
                            ],
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                    )
                ]

            return [
                TextMessage(
                    text="請輸入正確的年份",
                    sender=get_sender(self.__SENDER_NAME),
                    quoteToken=quote_token,
                ),
            ]

        if match := search(self.__STUDENT_REGEX, payload, IGNORECASE):
            criteria = match.group()

            if criteria.isdecimal() and 8 <= len(criteria) <= 9:
                if (student_info := await search_student_by_uid(criteria)) is None:
                    return [
                        TextMessage(
                            text=f"學號 {criteria} 不存在OAO",
                            sender=get_sender(self.__SENDER_NAME),
                            quoteToken=quote_token,
                        ),
                    ]

                messages = [
                    TextMessage(
                        text=student_info_format(
                            criteria,
                            student_info,
                            order=[Order.YEAR, Order.FULL_DEPARTMENT, Order.NAME],
                            space=2,
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

                if criteria[0] == "4":
                    is_over_99 = len(criteria) == 9
                    year = int(criteria[1 : is_over_99 + 3])

                    department = criteria[is_over_99 + 3 : is_over_99 + 5]
                    if department in [
                        DEPARTMENT_CODE["法律"],
                        DEPARTMENT_CODE["社學"][0:2],
                    ]:
                        department += criteria[is_over_99 + 5]

                    if department[0:2] == DEPARTMENT_CODE["法律"]:
                        show_text = (
                            f"搜尋{year}學年度法律系{DEPARTMENT_NAME[department]}組"
                        )
                    else:
                        show_text = f"搜尋{year}學年度{DEPARTMENT_NAME[department]}系"

                    messages[0].quick_reply = QuickReply(
                        items=[
                            QuickReplyItem(
                                action=PostbackAction(
                                    label=show_text,
                                    displayText=f"{show_text}",
                                    data=f"{year}{self.split_char}{department}",
                                    inputOption="closeRichMenu",
                                ),
                            ),
                        ],
                    )

                return messages

            if student_list := search_students_by_name(criteria):
                student_list = sorted(student_list, key=lambda s: int(s[0]))[-500:]

                messages: list[Message] = []
                for i in range(0, ceil(len(student_list) / 100)):
                    students_info = "\n".join(
                        [
                            student_info_format(student_id, student_name)
                            for student_id, student_name in student_list[
                                i * 100 : (i + 1) * 100
                            ]
                        ]
                    )

                    messages.append(
                        TextMessage(
                            text=students_info,
                            sender=get_sender(self.__SENDER_NAME),
                            quoteToken=quote_token,
                        )
                    )

                return messages

            return [
                TextMessage(
                    text="查無學生",
                    sender=get_sender(self.__SENDER_NAME),
                    quoteToken=quote_token,
                ),
            ]

        return []

    async def handle_postback_event(self, payload: str) -> list[Message]:
        """處理回傳事件"""

        if payload == "兇":
            return [
                TextMessage(
                    text="泥好兇喔~~இ௰இ",
                    sender=get_sender(self.__SENDER_NAME),
                ),
            ]

        if self.split_char in payload:
            data, year = payload.split(self.split_char)

            if data == "搜尋全系":
                return [
                    TemplateMessage(
                        altText="選擇學院群",
                        template=ButtonsTemplate(
                            thumbnailImageUrl="https://new.ntpu.edu.tw/assets/logo/ntpu_logo.png",
                            title="選擇學院群",
                            text="請選擇科系所屬學院群",
                            actions=[
                                self.__college_postback("文法商", year),
                                self.__college_postback("公社電資", year),
                            ],
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                    ),
                ]

            if data in ["文法商", "公社電資"]:
                return [
                    TemplateMessage(
                        altText="選擇學院",
                        template=ButtonsTemplate(
                            title="選擇學院",
                            text="請選擇科系所屬學院",
                            actions=(
                                [
                                    self.__college_postback("人文學院", year),
                                    self.__college_postback("法律學院", year),
                                    self.__college_postback("商學院", year),
                                ]
                                if data == "文法商"
                                else [
                                    self.__college_postback("公共事務學院", year),
                                    self.__college_postback("社會科學學院", year),
                                    self.__college_postback("電機資訊學院", year),
                                ]
                            ),
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                    ),
                ]

            if data in self.__COLLEGE_NAMES:
                department_message = {
                    "人文學院": self.__choose_department_message(
                        year,
                        "https://walkinto.in/upload/-192z7YDP8-JlchfXtDvI.JPG",
                        ["中文", "應外", "歷史"],
                    ),
                    "法律學院": self.__choose_department_message(
                        year,
                        "https://walkinto.in/upload/byupdk9PvIZyxupOy9Dw8.JPG",
                        ["法學", "司法", "財法"],
                        is_law=True,
                    ),
                    "商學院": self.__choose_department_message(
                        year,
                        "https://walkinto.in/upload/ZJum7EYwPUZkedmXNtvPL.JPG",
                        ["企管", "金融", "會計", "統計", "休運"],
                    ),
                    "公共事務學院": self.__choose_department_message(
                        year,
                        "https://walkinto.in/upload/ZJhs4wEaDIWklhiVwV6DI.jpg",
                        ["公行", "不動", "財政"],
                    ),
                    "社會科學學院": self.__choose_department_message(
                        year,
                        "https://walkinto.in/upload/WyPbshN6DIZ1gvZo2NTvU.JPG",
                        ["經濟", "社學", "社工"],
                    ),
                    "電機資訊學院": self.__choose_department_message(
                        year,
                        "https://walkinto.in/upload/bJ9zWWHaPLWJg9fW-STD8.png",
                        ["電機", "資工", "通訊"],
                    ),
                }

                return [
                    TemplateMessage(
                        altText=f"選擇{"組別" if data == "法律學院" else "科系"}",
                        template=department_message[data],
                        sender=get_sender(self.__SENDER_NAME),
                    )
                ]

            if data in DEPARTMENT_NAME:
                return [
                    TextMessage(
                        text=await search_students_by_year_and_department(
                            int(year), data
                        ),
                        sender=get_sender(self.__SENDER_NAME),
                    )
                ]

        return []

    def __college_postback(self, college_name: str, year: str) -> PostbackAction:
        """
        Creates a postback action for a college.

        Args:
            college_name (str): The name of the college.
            year (str): The year for which the action is being created.

        Returns:
            PostbackAction: A postback action object that represents the college.
        """

        data = f"{college_name}{self.split_char}{year}"
        return PostbackAction(
            label=college_name,
            displayText=college_name,
            data=data,
            inputOption="closeRichMenu",
        )

    def __department_postback(
        self, department_code: str, year: str, is_law: bool = False
    ) -> PostbackAction:
        """
        Creates a postback action object for a department.

        Args:
            department_code (str): The code of the department.
            year (str): The year for which the action is being created.
            is_law (bool): Optional parameter indicating if the department is a law department.

        Returns:
            PostbackAction: A postback action object that represents the department.
        """

        full_name = FULL_DEPARTMENT_NAME[department_code]

        display_text = f"搜尋{year}學年度"

        if is_law:
            display_text += "法律系"

        display_text += DEPARTMENT_NAME[department_code]

        if is_law:
            display_text += "組"
        else:
            display_text += "系"

        data = f"{year}{self.split_char}{department_code}"

        return PostbackAction(
            label=full_name,
            displayText=display_text,
            data=data,
            inputOption="closeRichMenu",
        )

    def __choose_department_message(
        self,
        year: str,
        image_url: str,
        departments: list[str],
        is_law: bool = False,
    ) -> ButtonsTemplate | CarouselTemplate:
        """
        Creates a template with a button or carousel template for selecting a department.

        Args:
            year (str): The year for which the department is being selected.
            image_url (str): The URL of the image to be displayed in the template message.
            departments (list[str]): A list of department names to be displayed as buttons.
            is_law (bool): Optional parameter indicating if the department is a law department.

        Returns:
            CarouselTemplate: A template for selecting a department.
        """

        department_class = "組別" if is_law else "科系"

        actions = [
            self.__department_postback(DEPARTMENT_CODE[name], year, is_law)
            for name in departments
        ]

        while len(actions) > 4 and len(actions) % 3 != 0:
            actions.append(EMPTY_POSTBACK_ACTION)

        if len(actions) <= 4:
            template = ButtonsTemplate(
                thumbnailImageUrl=image_url,
                title=f"選擇{department_class}",
                text=f"請選擇要查詢的{department_class}",
                actions=actions,
            )
        else:
            template = CarouselTemplate(
                columns=[
                    CarouselColumn(
                        thumbnailImageUrl=image_url,
                        title=f"選擇{department_class}",
                        text=f"請選擇要查詢的{department_class}",
                        actions=action_group,
                    )
                    for action_group in partition(actions, 3)
                ]
            )

        return template


ID_BOT = IDBot()
