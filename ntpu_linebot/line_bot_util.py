# -*- coding:utf-8 -*-
import os
import random
import sys
import time
from typing import List

from linebot.v3 import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    Message,
    ReplyMessageRequest,
    Sender,
    TextMessage,
)

from ntpu_linebot.sticker_util import stickers

# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

parser = WebhookParser(channel_secret)
configuration = Configuration(access_token=channel_access_token)
async_api_client = AsyncApiClient(configuration)
line_bot_api = AsyncMessagingApi(async_api_client)


def get_sender(name: str | None = None) -> Sender:
    """
    取得回覆者資訊

    icon 使用隨機貼圖
    """

    return Sender(
        name=name,
        iconUrl=random.choice(stickers),
    )


async def reply_message(reply_token: str, messages: List[Message]) -> None:
    """製作回覆訊息並發送"""

    await line_bot_api.reply_message(
        ReplyMessageRequest(
            replyToken=reply_token,
            messages=messages,
        ),
    )


async def instruction(reply_token: str) -> None:
    """使用說明"""

    mes_sender = get_sender()
    cur_year = time.localtime(time.time()).tm_year
    messages = [
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

    await reply_message(reply_token, messages)
