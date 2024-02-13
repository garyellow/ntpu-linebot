# -*- coding:utf-8 -*-
from re import sub

from linebot.v3.messaging import ImageMessage, TextMessage
from linebot.v3.webhooks import (
    FollowEvent,
    JoinEvent,
    MemberJoinedEvent,
    MessageEvent,
    PostbackEvent,
)

from ntpu_linebot.id import ID_BOT
from ntpu_linebot.line_bot_util import get_sender, reply_message


async def handle_text_message(event: MessageEvent) -> None:
    """
    Process the text message contained in the event.

    Args:
        event (MessageEvent): The event triggered by a text message.

    Returns:
        None
    """

    # Remove all whitespace and punctuation characters from the text message
    payload = sub(r"\s|[][!\"#$%&'()*+,./:;<=>?@\\^_`{|}~-]", "", event.message.text)

    await ID_BOT.handle_text_message(
        payload,
        event.reply_token,
        event.message.quote_token,
    )


async def handle_postback_event(event: PostbackEvent) -> None:
    """
    Process the postback event triggered by the user.

    Args:
        event (PostbackEvent): The PostbackEvent object representing the postback event.

    Returns:
        None
    """

    await ID_BOT.handle_postback_event(event.postback.data, event.reply_token)


async def handle_sticker_message(event: MessageEvent) -> None:
    """
    Handle sticker messages in a Line bot.

    Args:
        event (MessageEvent): The event object containing information about the sticker message.

    Returns:
        None
    """

    msg_sender = get_sender()

    image_message = ImageMessage(
        originalContentUrl=msg_sender.icon_url,
        previewImageUrl=msg_sender.icon_url,
        sender=msg_sender,
    )

    await reply_message(event.reply_token, [image_message])


async def handle_follow_join_event(
    event: FollowEvent | JoinEvent | MemberJoinedEvent,
) -> None:
    """
    Handles the follow, join, and member joined events in a Line bot.
    Sends a series of text messages to the user, introducing the bot and providing instructions on how to use it.

    Args:
        event (FollowEvent | JoinEvent | MemberJoinedEvent): The event object representing the follow, join, or member joined event.

    Returns:
        None
    """

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
            text="部分資訊是由相關資料推斷\n不一定為正確資訊", sender=mes_sender
        ),
        TextMessage(
            text="資料來源：\n國立臺北大學數位學苑 2.0\n國立臺北大學學生資訊系統\n國立臺北大學課程查詢系統",
            sender=mes_sender,
        ),
    ]

    await reply_message(event.reply_token, messages)
