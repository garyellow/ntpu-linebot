# -*- coding:utf-8 -*-
import random

from linebot.v3.messaging.models import ImageMessage, Sender, TextMessage
from linebot.v3.webhooks import MessageEvent, PostbackEvent

from .idBot import IDBot
from .lineBotUtil import get_sender, reply_message

from .stickerUtil import stickers


async def handle_text_message(event: MessageEvent) -> None:
    await IDBot.handle_text_message(event)


async def handle_postback_event(event: PostbackEvent) -> None:
    await IDBot.handle_postback_event(event)


async def handle_sticker_message(event: MessageEvent) -> None:
    sticker = random.choice(stickers)

    messages = [
        ImageMessage(
            original_content_url=sticker,
            preview_image_url=sticker,
            sender=Sender(iconUrl=sticker),
        ),
    ]

    await reply_message(event.reply_token, messages)


async def handle_follow_join_event(event) -> None:
    mes_sender = get_sender()

    messages = [
        TextMessage(
            text="泥好~~我是北大查詢小工具🔍\n可以用學號查詢到姓名\n也可以用姓名查詢到學號",
            sender=mes_sender,
        ),
        TextMessage(
            text="詳細使用說明請點選下方選單\n或輸入「使用說明」", sender=mes_sender
        ),
        TextMessage(
            text="有疑問可以先去看常見問題\n若無法解決或有發現 Bug\n可以到 GitHub 提出",
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

    await reply_message(event.reply_token, messages)
