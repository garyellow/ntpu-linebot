# -*- coding:utf-8 -*-
import random
from datetime import datetime
from typing import Optional

from linebot.v3.messaging import Sender
from linebot.v3.messaging.models import TextMessage

from .sticker_util import STICKER


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

    mes_sender = get_sender()
    cur_year = datetime.now().year
    return [
        TextMessage(
            text="輸入學號可查詢姓名\n輸入姓名可查詢學號\n"
            + "輸入系名可查詢系代碼\n輸入系代碼可查詢系名\n輸入入學學年再選科系獲取學生名單",
            sender=mes_sender,
        ),
        TextMessage(
            text="For example~~\n學號：412345678\n姓名：林某某 or 某某\n"
            + f"系名：資工系 or 資訊工程學系\n系代碼：85\n入學學年：{cur_year - 1911} or {cur_year}",
            sender=mes_sender,
        ),
        TextMessage(
            text="部分資訊是由相關資料推斷\n不一定為正確資訊",
            sender=mes_sender,
        ),
        TextMessage(
            text="資料來源：\n國立臺北大學數位學苑 2.0\n國立臺北大學學生資訊系統\n國立臺北大學課程查詢系統",
            sender=mes_sender,
        ),
    ]
