# -*- coding:utf-8 -*-
import random
from datetime import datetime
from typing import Optional

from linebot.v3.messaging import Sender
from linebot.v3.messaging.models import PostbackAction, TextMessage

from .sticker_util import STICKER

EMPTY_POSTBACK_ACTION = PostbackAction(
    label=" ", data="null", displayText=None, inputOption=None, fillInText=None
)


def get_sender(name: Optional[str] = None) -> Sender:
    """
    Get sender information with a random sticker as the icon.

    Args:
        name (str, optional): The name of the sender.

    Returns:
        A Sender object with the name and iconUrl.
    """

    return Sender(
        name=name,
        iconUrl=random.choice(STICKER.STICKER_LIST) if STICKER.STICKER_LIST else None,
    )


def instruction() -> list[TextMessage]:
    """Provides instructions on how to use a Line messaging platform bot."""

    mes_sender = get_sender("進階魔法師")
    last_year = datetime.now().year - 1

    text_title = "使用說明："

    id_text = "\n".join(
        [
            "輸入「學生 {學號}」查詢學生",
            "輸入「學生 {姓名}」查詢學生",
            "輸入「科系 {系名}」查詢系代碼",
            "輸入「系代碼 {系代碼}」查詢系名",
            "輸入「學年 {入學年份}」後選科系查學生名單",
        ]
    )

    course_text = "\n".join(
        [
            "輸入「課程 {課程名}」尋找課程",
            "輸入「教師 {教師名}」尋找教師開的課",
        ]
    )

    contact_text = "\n".join(
        [
            "輸入「聯繫 {單位/姓名}」尋找聯繫方式",
        ]
    )

    text_note = "\n".join(
        [
            "PS 符號{}中的部分要換成實際值",
            "PPS 學生相關功能已無113學年後的資料",
        ]
    )

    example_title = "範例："

    id_example = "\n".join(
        [
            "學號：`學生 412345678`",
            "姓名：`學生 小明` or `學生 林小明`",
            "系名：`科系 資工系` or `科系 資訊工程學系`",
            "系代碼：`系代碼 85`",
            f"入學年：`學年 {last_year - 1911}` or `學年 {last_year}`",
        ]
    )

    course_example = "\n".join(
        [
            "課程：`課程 程式設計`",
            "教師：`教師 李小美`",
        ]
    )

    contact_example = "\n".join(
        [
            "聯繫：`聯繫 資工系`",
        ]
    )

    example_note = "\n".join(
        [
            "PS 符號``中的部分是實際要輸入的",
        ]
    )

    return [
        TextMessage(
            text="\n\n".join(
                [
                    text_title,
                    id_text,
                    course_text,
                    contact_text,
                    text_note,
                ]
            ),
            sender=mes_sender,
            quickReply=None,
            quoteToken=None,
        ),
        TextMessage(
            text="\n\n".join(
                [
                    example_title,
                    id_example,
                    course_example,
                    contact_example,
                    example_note,
                ]
            ),
            sender=mes_sender,
            quickReply=None,
            quoteToken=None,
        ),
        TextMessage(
            text="部分內容是由相關資料推斷\n不一定為正確資訊",
            sender=mes_sender,
            quickReply=None,
            quoteToken=None,
        ),
        TextMessage(
            text="資料來源：國立臺北大學\n數位學苑2.0(已無新資料)\n校園聯絡簿\n課程查詢系統",
            sender=mes_sender,
            quickReply=None,
            quoteToken=None,
        ),
    ]
