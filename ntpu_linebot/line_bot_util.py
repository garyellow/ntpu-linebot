# -*- coding:utf-8 -*-
import random
from datetime import datetime
from typing import Optional

from linebot.v3.messaging import Sender
from linebot.v3.messaging.models import PostbackAction, TextMessage

from .sticker_util import STICKER

EMPTY_POSTBACK_ACTION = PostbackAction(label=" ", data="null")


def get_sender(name: Optional[str] = None) -> Sender:
    """
    Get sender information with a random sticker as the icon.

    Args:
        name (str, optional): The name of the sender.

    Returns:
        A Sender object with the name and iconUrl.
    """

    return Sender(name=name, iconUrl=random.choice(STICKER.STICKER_LIST))


def instruction() -> list[TextMessage]:
    """Provides instructions on how to use a Line messaging platform bot."""

    mes_sender = get_sender("進階魔法師")
    last_year = datetime.now().year - 1

    id_text = "\n".join(
        [
            "輸入「學號」可查詢姓名",
            "輸入「姓名」可查詢學號",
            "輸入「系名」可查詢系代碼",
            "輸入「系代碼」可查詢系名",
            "輸入「入學年」後選科系獲取學生名單",
        ]
    )

    id_example = "\n".join(
        [
            "學號：`412345678`",
            "姓名：`林某某` or `某某`",
            "系名：`資工系` or `資訊工程學系`",
            "系代碼：`85`",
            f"入學年：`{last_year - 1911}` or `{last_year}`",
        ]
    )

    course_text = "\n".join(
        [
            "輸入課程「年份學期代號」可查詢課程",
            "輸入「『課程』+課程名」可尋找課程",
            "輸入「『教師』+教師名」可尋找教師開的課",
        ]
    )

    course_example = "\n".join(
        [
            f"年份學期代號：`{last_year - 1911}2U1237`",
            "課程：`課程 程式設計`",
            "教師：`教師 林某某`",
        ]
    )

    example_note = "\n".join(
        [
            "P.S. 符號``中間的字代表實際要輸入的",
        ]
    )

    return [
        TextMessage(
            text="\n\n".join(
                [
                    id_text,
                    course_text,
                ]
            ),
            sender=mes_sender,
        ),
        TextMessage(
            text="\n\n".join(
                [
                    id_example,
                    course_example,
                    example_note,
                ]
            ),
            sender=mes_sender,
        ),
        TextMessage(
            text="部分內容是由相關資料推斷\n不一定為正確資訊",
            sender=mes_sender,
        ),
        TextMessage(
            text="資料來源：\n國立臺北大學數位學苑 2.0\n國立臺北大學課程查詢系統",
            sender=mes_sender,
        ),
    ]
