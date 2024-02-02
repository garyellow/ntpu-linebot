# -*- coding:utf-8 -*-
import os
import random
import sys
import time
from abc import abstractmethod
from typing import List

from linebot.v3 import WebhookParser
from linebot.v3.messaging.api.async_messaging_api import AsyncMessagingApi
from linebot.v3.messaging.async_api_client import AsyncApiClient
from linebot.v3.messaging.configuration import Configuration
from linebot.v3.messaging.models import (
    Message,
    ReplyMessageRequest,
    Sender,
    TextMessage,
)

from .stickerUtil import stickers

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


# 回覆者資訊
def get_sender(name: str | None = None) -> Sender:
    return Sender(
        name=name,
        iconUrl=random.choice(stickers),
    )


# 回覆訊息
async def reply_message(reply_token: str, message: List[Message]) -> None:
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=message,
        ),
    )


# 使用說明
async def instruction(reply_token: str) -> None:
    mes_sender = get_sender()
    messages = [
        TextMessage(
            text="輸入學號可查詢姓名\n輸入姓名可查詢學號\n輸入系名可查詢系代碼\n輸入系代碼可查詢系名\n輸入入學學年再選科系獲取學生名單",
            sender=mes_sender,
        ),
        TextMessage(
            text="For example~~\n學號：412345678\n姓名：林某某 or 某某\n系名：資工系 or 資訊工程學系\n系代碼：85\n"
            + "入學學年："
            + str(time.localtime(time.time()).tm_year - 1911)
            + " or "
            + str(time.localtime(time.time()).tm_year),
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
