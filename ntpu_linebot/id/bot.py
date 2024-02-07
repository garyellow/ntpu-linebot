# -*- coding:utf-8 -*-
import math
import time
from typing import List

from linebot.v3.messaging.models import (
    ButtonsTemplate,
    ConfirmTemplate,
    MessageAction,
    PostbackAction,
    QuickReply,
    QuickReplyItem,
    TemplateMessage,
    TextMessage,
)

from ntpu_linebot.abs_bot import Bot
from ntpu_linebot.id.request import get_students_by_year_and_department, student_list
from ntpu_linebot.id.util import (
    DEPARTMENT_CODE,
    DEPARTMENT_NAME,
    FULL_DEPARTMENT_CODE,
    FULL_DEPARTMENT_NAME,
    Order,
    student_info_format,
)
from ntpu_linebot.line_bot_util import get_sender, instruction, reply_message


class IDBot(Bot):
    SPILT_CODE = "@"
    SENDER_NAME = "學號魔法師"
    ALL_DEPARTMENT_CODE = "所有系代碼"

    def college_postback(self, college_name: str, year: str) -> PostbackAction:
        """製作學院 postback action"""

        return PostbackAction(
            label=college_name,
            display_text=college_name,
            data=year + self.SPILT_CODE + college_name,
            input_option="closeRichMenu",
        )

    def department_postback(self, department_code: str, year: str) -> PostbackAction:
        """製作科系 postback action"""

        return PostbackAction(
            label=FULL_DEPARTMENT_NAME[department_code],
            display_text=f"正在搜尋{year}學年度"
            + ("法律系" if department_code[0:2] == DEPARTMENT_CODE["法律"] else "")
            + DEPARTMENT_NAME[department_code]
            + ("組" if department_code[0:2] == DEPARTMENT_CODE["法律"] else "系"),
            data=year + self.SPILT_CODE + department_code,
            input_option="closeRichMenu",
        )

    async def handle_text_message(self, payload: str, reply_token: str) -> bool:
        """處理文字訊息"""

        if payload.isdecimal():
            if payload in FULL_DEPARTMENT_NAME:
                messages = [
                    TextMessage(
                        text=FULL_DEPARTMENT_NAME[payload],
                        quick_reply=QuickReply(
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

                await reply_message(reply_token, messages)

            elif 2 <= len(payload) <= 4:
                year = int(payload) if int(payload) < 1911 else int(payload) - 1911

                messages: List
                if year > time.localtime(time.time()).tm_year - 1911:
                    messages = [
                        TextMessage(
                            text="你未來人？(⊙ˍ⊙)",
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]
                elif year < 90:
                    messages = [
                        TextMessage(
                            text="學校都還沒蓋好(￣▽￣)",
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]
                elif year < 95:
                    messages = [
                        TextMessage(
                            text="數位學苑還沒出生喔~~",
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]
                else:
                    messages = [
                        TemplateMessage(
                            alt_text="確認學年度",
                            template=ConfirmTemplate(
                                text=f"是否要搜尋 {year} 學年度的學生",
                                actions=[
                                    PostbackAction(
                                        label="哪次不是",
                                        display_text="哪次不是",
                                        data=f"{year}{self.SPILT_CODE}搜尋全系",
                                        input_option="openRichMenu",
                                    ),
                                    PostbackAction(
                                        label="我在想想",
                                        display_text="再啦乾ಠ_ಠ",
                                        data="兇",
                                        input_option="openKeyboard",
                                    ),
                                ],
                            ),
                            sender=get_sender(self.SENDER_NAME),
                        )
                    ]

                await reply_message(reply_token, messages)

            elif 8 <= len(payload) <= 9:
                students = student_info_format(
                    payload,
                    order=[Order.YEAR, Order.FULL_DEPARTMENT, Order.NAME],
                    space=2,
                )

                if not students:
                    messages = [
                        TextMessage(
                            text=f"學號 {payload} 不存在OAO",
                            sender=get_sender(self.SENDER_NAME),
                        ),
                    ]

                    await reply_message(reply_token, messages)
                    return

                messages = [
                    TextMessage(
                        text=students,
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

                if payload[0] == "4":
                    over_99 = len(payload) == 9
                    year = payload[1 : over_99 + 3]

                    department = payload[over_99 + 3 : over_99 + 5]
                    if department in [
                        DEPARTMENT_CODE["法律"],
                        DEPARTMENT_CODE["社學"][0:2],
                    ]:
                        department += payload[over_99 + 5]

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
                                    display_text=f"正在{show_text}",
                                    data=year + self.SPILT_CODE + department,
                                    input_option="closeRichMenu",
                                ),
                            ),
                        ],
                    )

                await reply_message(reply_token, messages)

            else:
                return False

        else:
            if payload in ["使用說明", "help"]:
                await instruction(reply_token)

            elif payload == self.ALL_DEPARTMENT_CODE:
                students = "\n".join(
                    [f"{x}系 -> {y}" for x, y in DEPARTMENT_CODE.items()]
                )
                messages = [
                    TextMessage(
                        text=students,
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

                await reply_message(reply_token, messages)

            elif payload.strip("系") in DEPARTMENT_CODE:
                messages = [
                    TextMessage(
                        text=DEPARTMENT_CODE[payload.strip("系")],
                        quick_reply=QuickReply(
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

                await reply_message(reply_token, messages)

            elif payload in FULL_DEPARTMENT_CODE:
                messages = [
                    TextMessage(
                        text=FULL_DEPARTMENT_CODE[payload],
                        quick_reply=QuickReply(
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

                await reply_message(reply_token, messages)

            else:
                students = []
                for key, value in student_list.items():
                    if payload in value:
                        students.append((key, value))

                if students:
                    students = sorted(students, key=lambda x: (not x[0], int(x[0])))

                    messages = []
                    for i in range(min(math.ceil(len(students) / 100), 5), 0, -1):
                        students_info = "\n".join(
                            [
                                student_info_format(x[0], x[1])
                                for x in students[
                                    -i * 100 : -(i - 1) * 100 if i - 1 else None
                                ]
                            ]
                        )

                        messages.append(
                            TextMessage(
                                text=students_info,
                                sender=get_sender(self.SENDER_NAME),
                            )
                        )

                    await reply_message(reply_token, messages)

                else:
                    return False

        return True

    async def handle_postback_event(self, payload: str, reply_token: str) -> None:
        """處理回傳事件"""

        if payload == "使用說明":
            await instruction(reply_token)

        elif payload == "兇":
            messages = [
                TextMessage(
                    text="泥好兇喔~~இ௰இ",
                    sender=get_sender(self.SENDER_NAME),
                ),
            ]

            await reply_message(reply_token, messages)

        else:
            year, data = payload.split(self.SPILT_CODE)

            messages: List
            if data == "搜尋全系":
                messages = [
                    TemplateMessage(
                        alt_text="選擇學院群",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://new.ntpu.edu.tw/assets/logo/ntpu_logo.png",
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

            elif data in ["文法商", "公社電資"]:
                messages = [
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

            elif data == "人文學院":
                messages = [
                    TemplateMessage(
                        alt_text="選擇科系",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://walkinto.in/upload/-192z7YDP8-JlchfXtDvI.JPG",
                            title="選擇科系",
                            text="請選擇要查詢的科系",
                            actions=[
                                self.department_postback(DEPARTMENT_CODE["中文"], year),
                                self.department_postback(DEPARTMENT_CODE["應外"], year),
                                self.department_postback(DEPARTMENT_CODE["歷史"], year),
                            ],
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            elif data == "法律學院":
                messages = [
                    TemplateMessage(
                        alt_text="選擇組別",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://walkinto.in/upload/byupdk9PvIZyxupOy9Dw8.JPG",
                            title="選擇組別",
                            text="請選擇要查詢的組別",
                            actions=[
                                self.department_postback(DEPARTMENT_CODE["法學"], year),
                                self.department_postback(DEPARTMENT_CODE["司法"], year),
                                self.department_postback(DEPARTMENT_CODE["財法"], year),
                            ],
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            elif data == "商學院":
                messages = [
                    TemplateMessage(
                        alt_text="選擇科系",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://walkinto.in/upload/ZJum7EYwPUZkedmXNtvPL.JPG",
                            title="選擇科系",
                            text="請選擇科系 (休運系請直接點圖片)",
                            default_action=self.department_postback(
                                DEPARTMENT_CODE["休運"], year
                            ),
                            actions=[
                                self.department_postback(DEPARTMENT_CODE["企管"], year),
                                self.department_postback(DEPARTMENT_CODE["金融"], year),
                                self.department_postback(DEPARTMENT_CODE["會計"], year),
                                self.department_postback(DEPARTMENT_CODE["統計"], year),
                            ],
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            elif data == "公共事務學院":
                messages = [
                    TemplateMessage(
                        alt_text="選擇科系",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://walkinto.in/upload/ZJhs4wEaDIWklhiVwV6DI.jpg",
                            title="選擇科系",
                            text="請選擇要查詢的科系",
                            actions=[
                                self.department_postback(DEPARTMENT_CODE["公行"], year),
                                self.department_postback(DEPARTMENT_CODE["不動"], year),
                                self.department_postback(DEPARTMENT_CODE["財政"], year),
                            ],
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            elif data == "社會科學學院":
                messages = [
                    TemplateMessage(
                        alt_text="選擇科系",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://walkinto.in/upload/WyPbshN6DIZ1gvZo2NTvU.JPG",
                            title="選擇科系",
                            text="請選擇科系",
                            actions=[
                                self.department_postback(DEPARTMENT_CODE["經濟"], year),
                                self.department_postback(DEPARTMENT_CODE["社學"], year),
                                self.department_postback(DEPARTMENT_CODE["社工"], year),
                            ],
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            elif data == "電機資訊學院":
                messages = [
                    TemplateMessage(
                        alt_text="選擇科系",
                        template=ButtonsTemplate(
                            thumbnail_image_url="https://walkinto.in/upload/bJ9zWWHaPLWJg9fW-STD8.png",
                            title="選擇科系",
                            text="請選擇科系",
                            actions=[
                                self.department_postback(DEPARTMENT_CODE["電機"], year),
                                self.department_postback(DEPARTMENT_CODE["資工"], year),
                                self.department_postback(DEPARTMENT_CODE["通訊"], year),
                            ],
                        ),
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            else:
                students = get_students_by_year_and_department(year, data)

                students_info: str
                if students:
                    students_info = "\n".join(
                        [
                            student_info_format(x, y, [Order.ID, Order.NAME], 3)
                            for x, y in students.items()
                        ]
                    )

                    students_info += (
                        f"\n\n{year}學年度"
                        + ("法律系" if data[0:2] == DEPARTMENT_CODE["法律"] else "")
                        + DEPARTMENT_NAME[data]
                        + ("組" if data[0:2] == DEPARTMENT_CODE["法律"] else "系")
                        + f"共有{len(students)}位學生"
                    )

                else:
                    students_info = (
                        f"{year}學年度"
                        + ("法律系" if data[0:2] == DEPARTMENT_CODE["法律"] else "")
                        + DEPARTMENT_NAME[data]
                        + ("組" if data[0:2] == DEPARTMENT_CODE["法律"] else "系")
                        + "好像沒有人耶OAO"
                    )

                messages = [
                    TextMessage(
                        text=students_info,
                        sender=get_sender(self.SENDER_NAME),
                    ),
                ]

            await reply_message(reply_token, messages)


ID_BOT = IDBot()
