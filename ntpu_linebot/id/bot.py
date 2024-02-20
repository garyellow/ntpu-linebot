# -*- coding:utf-8 -*-
from datetime import datetime
from math import ceil
from typing import Optional

from linebot.v3.messaging.models import (
    ButtonsTemplate,
    ConfirmTemplate,
    Message,
    MessageAction,
    PostbackAction,
    QuickReply,
    QuickReplyItem,
    TemplateMessage,
    TextMessage,
)

from ntpu_linebot.abs_bot import Bot
from ntpu_linebot.id.util import (
    DEPARTMENT_CODE,
    DEPARTMENT_NAME,
    FULL_DEPARTMENT_CODE,
    FULL_DEPARTMENT_NAME,
    Order,
    search_students_by_name,
    search_students_by_year_and_department,
    student_info_format,
)
from ntpu_linebot.line_bot_util import get_sender, instruction


class IDBot(Bot):
    SPILT_CODE = "@"
    SENDER_NAME = "學號魔法師"
    ALL_DEPARTMENT_CODE = "所有系代碼"
    HELP_COMMANDS = ["使用說明", "help"]
    COLLAGES = [
        "人文學院",
        "法律學院",
        "商學院",
        "公共事務學院",
        "社會科學學院",
        "電機資訊學院",
    ]

    def college_postback(self, college_name: str, year: str) -> PostbackAction:
        """
        Creates a postback action for a college in the Line messaging platform.

        Args:
            college_name (str): The name of the college.
            year (str): The year for which the action is being created.

        Returns:
            PostbackAction: A postback action object that represents the college in the Line messaging platform.
        """

        data = year + self.SPILT_CODE + college_name
        return PostbackAction(
            label=college_name,
            displayText=college_name,
            data=data,
            inputOption="closeRichMenu",
        )

    def department_postback(self, department_code: str, year: str) -> PostbackAction:
        """
        Creates a postback action object for a specific department and year in the Line messaging platform.

        Args:
            department_code (str): The code of the department.
            year (str): The year for which the action is being created.

        Returns:
            PostbackAction: A postback action object that represents the department in the Line messaging platform.
        """

        full_name = FULL_DEPARTMENT_NAME[department_code]

        display_text = f"正在搜尋{year}學年度"

        if department_code[0:2] == DEPARTMENT_CODE["法律"]:
            display_text += "法律系"

        display_text += DEPARTMENT_NAME[department_code]

        if department_code[0:2] == DEPARTMENT_CODE["法律"]:
            display_text += "組"
        else:
            display_text += "系"

        data = year + self.SPILT_CODE + department_code

        return PostbackAction(
            label=full_name,
            displayText=display_text,
            data=data,
            inputOption="closeRichMenu",
        )

    def choose_department_message(
        self,
        year: str,
        image_url: str,
        department_names: list[str],
        extra_department: Optional[str] = None,
        is_law: bool = False,
    ) -> TemplateMessage:
        """
        Creates a template message with a button template for selecting a department.

        Args:
            year (str): The year for which the department is being selected.
            image_url (str): The URL of the image to be displayed in the template message.
            department_names (list[str]): A list of department names to be displayed as buttons in the template message.

        Returns:
            TemplateMessage: A template message with a button template for selecting a department.
        """

        department_class = "組別" if is_law else "科系"

        actions = [
            self.department_postback(DEPARTMENT_CODE[name], year)
            for name in department_names
        ]

        default_action = (
            self.department_postback(DEPARTMENT_CODE[extra_department], year)
            if extra_department
            else None
        )

        template = ButtonsTemplate(
            thumbnailImageUrl=image_url,
            title=f"選擇{department_class}",
            text=f"請選擇要查詢的{department_class}",
            defaultAction=default_action,
            actions=actions,
        )

        return TemplateMessage(
            alt_text=f"選擇{department_class}",
            template=template,
            sender=get_sender(self.SENDER_NAME),
        )

    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> list[Message]:
        """處理文字訊息"""

        if payload.isdecimal():
            if payload in FULL_DEPARTMENT_NAME:
                return [
                    TextMessage(
                        text=FULL_DEPARTMENT_NAME[payload],
                        quickReply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label=self.ALL_DEPARTMENT_CODE,
                                        text=self.ALL_DEPARTMENT_CODE,
                                    ),
                                ),
                            ]
                        ),
                        sender=get_sender(self.SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

            if 2 <= len(payload) <= 4:
                year = int(payload) if int(payload) < 1911 else int(payload) - 1911

                if year > datetime.now().year - 1911:
                    return [
                        TextMessage(
                            text="你未來人？(⊙ˍ⊙)",
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]
                if year < 90:
                    return [
                        TextMessage(
                            text="學校都還沒蓋好(￣▽￣)",
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]
                if 90 <= year < 95:
                    return [
                        TextMessage(
                            text="數位學苑還沒出生喔~~",
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]

                return [
                    TemplateMessage(
                        alt_text="確認學年度",
                        template=ConfirmTemplate(
                            text=f"是否要搜尋 {year} 學年度的學生",
                            actions=[
                                PostbackAction(
                                    label="哪次不是",
                                    displayText="哪次不是",
                                    data=f"{year}{self.SPILT_CODE}搜尋全系",
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
                        sender=get_sender(self.SENDER_NAME),
                    )
                ]

            if 8 <= len(payload) <= 9:
                students = await student_info_format(
                    payload,
                    order=[Order.YEAR, Order.FULL_DEPARTMENT, Order.NAME],
                    space=2,
                )

                if not students:
                    return [
                        TextMessage(
                            text=f"學號 {payload} 不存在OAO",
                            sender=get_sender(self.SENDER_NAME),
                            quoteToken=quote_token,
                        ),
                    ]

                messages = [
                    TextMessage(
                        text=students,
                        sender=get_sender(self.SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

                if payload[0] == "4":
                    is_over_99 = len(payload) == 9
                    year = payload[1 : is_over_99 + 3]

                    department = payload[is_over_99 + 3 : is_over_99 + 5]
                    if department in [
                        DEPARTMENT_CODE["法律"],
                        DEPARTMENT_CODE["社學"][0:2],
                    ]:
                        department += payload[is_over_99 + 5]

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
                                    displayText=f"正在{show_text}",
                                    data=year + self.SPILT_CODE + department,
                                    inputOption="closeRichMenu",
                                ),
                            ),
                        ],
                    )

                return messages

        else:
            if payload in self.HELP_COMMANDS:
                return instruction()

            if payload == self.ALL_DEPARTMENT_CODE:
                students = "\n".join(
                    [f"{x}系 -> {y}" for x, y in DEPARTMENT_CODE.items()]
                )

                return [
                    TextMessage(
                        text=students,
                        sender=get_sender(self.SENDER_NAME),
                        quoteToken=quote_token,
                    ),
                ]

            if payload.rstrip("系") in DEPARTMENT_CODE:
                return [
                    TextMessage(
                        text=DEPARTMENT_CODE[payload.rstrip("系")],
                        quickReply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label=self.ALL_DEPARTMENT_CODE,
                                        text=self.ALL_DEPARTMENT_CODE,
                                    )
                                ),
                            ]
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            if payload in FULL_DEPARTMENT_CODE:
                return [
                    TextMessage(
                        text=FULL_DEPARTMENT_CODE[payload],
                        quickReply=QuickReply(
                            items=[
                                QuickReplyItem(
                                    action=MessageAction(
                                        label=self.ALL_DEPARTMENT_CODE,
                                        text=self.ALL_DEPARTMENT_CODE,
                                    )
                                ),
                            ]
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            students = search_students_by_name(payload)
            if students:
                students = sorted(students, key=lambda x: (not x[0], int(x[0])))

                messages = list[TextMessage]()
                for i in range(min(ceil(len(students) / 100), 5), 0, -1):
                    students_info = "\n".join(
                        [
                            await student_info_format(x[0], x[1])
                            for x in students[
                                -i * 100 : -(i - 1) * 100 if i - 1 else None
                            ]
                        ]
                    )

                    messages.append(
                        TextMessage(
                            text=students_info,
                            sender=get_sender(self.SENDER_NAME),
                            quoteToken=quote_token,
                        )
                    )

                return messages

        return list[Message]()

    async def handle_postback_event(self, payload: str) -> None:
        """處理回傳事件"""

        if payload in self.HELP_COMMANDS:
            return instruction()

        if payload == "兇":
            return [
                TextMessage(
                    text="泥好兇喔~~இ௰இ",
                    sender=get_sender(self.SENDER_NAME),
                ),
            ]

        year, data = payload.split(self.SPILT_CODE)
        if data == "搜尋全系":
            return [
                TemplateMessage(
                    alt_text="選擇學院群",
                    template=ButtonsTemplate(
                        thumbnailImageUrl="https://new.ntpu.edu.tw/assets/logo/ntpu_logo.png",
                        title="選擇學院群",
                        text="請選擇科系所屬學院群",
                        actions=[
                            self.college_postback("文法商", year),
                            self.college_postback("公社電資", year),
                        ],
                    ),
                    sender=get_sender(self.SENDER_NAME),
                ),
            ]

        if data in ["文法商", "公社電資"]:
            return [
                TemplateMessage(
                    alt_text="選擇學院",
                    template=ButtonsTemplate(
                        title="選擇學院",
                        text="請選擇科系所屬學院",
                        actions=(
                            [
                                self.college_postback("人文學院", year),
                                self.college_postback("法律學院", year),
                                self.college_postback("商學院", year),
                            ]
                            if data == "文法商"
                            else [
                                self.college_postback("公共事務學院", year),
                                self.college_postback("社會科學學院", year),
                                self.college_postback("電機資訊學院", year),
                            ]
                        ),
                    ),
                    sender=get_sender(self.SENDER_NAME),
                ),
            ]

        if data in self.COLLAGES:
            department_message = {
                "人文學院": self.choose_department_message(
                    year,
                    "https://walkinto.in/upload/-192z7YDP8-JlchfXtDvI.JPG",
                    ["中文", "應外", "歷史"],
                ),
                "法律學院": self.choose_department_message(
                    year,
                    "https://walkinto.in/upload/byupdk9PvIZyxupOy9Dw8.JPG",
                    ["法學", "司法", "財法"],
                    is_law=True,
                ),
                "商學院": self.choose_department_message(
                    year,
                    "https://walkinto.in/upload/ZJum7EYwPUZkedmXNtvPL.JPG",
                    ["企管", "金融", "會計", "統計"],
                    "休運",
                ),
                "公共事務學院": self.choose_department_message(
                    year,
                    "https://walkinto.in/upload/ZJhs4wEaDIWklhiVwV6DI.jpg",
                    ["公行", "不動", "財政"],
                ),
                "社會科學學院": self.choose_department_message(
                    year,
                    "https://walkinto.in/upload/WyPbshN6DIZ1gvZo2NTvU.JPG",
                    ["經濟", "社學", "社工"],
                ),
                "電機資訊學院": self.choose_department_message(
                    year,
                    "https://walkinto.in/upload/bJ9zWWHaPLWJg9fW-STD8.png",
                    ["電機", "資工", "通訊"],
                ),
            }

            return [department_message[data]]

        return [
            TextMessage(
                text=await search_students_by_year_and_department(year, data),
                sender=get_sender(self.SENDER_NAME),
            ),
        ]


ID_BOT = IDBot()
