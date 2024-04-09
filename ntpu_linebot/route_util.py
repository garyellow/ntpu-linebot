# -*- coding:utf-8 -*-
from re import sub

from linebot.v3.messaging import ImageMessage, Message, TextMessage
from linebot.v3.webhooks import (
    FollowEvent,
    JoinEvent,
    MemberJoinedEvent,
    MessageEvent,
    PostbackEvent,
)

from .contact import CONTACT_BOT
from .course import COURSE_BOT
from .id import ID_BOT
from .line_api_util import LINE_API_UTIL
from .line_bot_util import get_sender, instruction

__HELP_COMMANDS = ["使用說明", "help"]
__PUNCTUATION_REGEX = r"[][!\"#$%&'()*+,./:;<=>?@\\^_`{|}~-]"


async def handle_text_message(event: MessageEvent) -> None:
    """
    Process the text message contained in the event.

    Args:
        event (MessageEvent): The event triggered by a text message.
    """

    # Change whitespace and remove punctuation characters from the message text
    payload = sub(r"\s", " ", event.message.text)
    payload = sub(__PUNCTUATION_REGEX, "", payload)
    if payload == "":
        return

    messages = list[Message]()
    if payload in __HELP_COMMANDS:
        messages += instruction()

    else:
        messages += await ID_BOT.handle_text_message(payload, event.message.quote_token)
        messages += await CONTACT_BOT.handle_text_message(
            payload, event.message.quote_token
        )
        messages += await COURSE_BOT.handle_text_message(
            payload, event.message.quote_token
        )

    if messages:
        await LINE_API_UTIL.reply_message(event.reply_token, messages[:5])


async def handle_postback_event(event: PostbackEvent) -> None:
    """
    Process the postback event triggered by the user.

    Args:
        event (PostbackEvent): The PostbackEvent object representing the postback event.
    """

    payload = event.postback.data

    messages = list[Message]()
    if payload in __HELP_COMMANDS:
        messages += instruction()

    else:
        messages += await ID_BOT.handle_postback_event(payload)
        messages += await CONTACT_BOT.handle_postback_event(payload)
        messages += await COURSE_BOT.handle_postback_event(payload)

    if messages:
        await LINE_API_UTIL.reply_message(event.reply_token, messages[:5])


async def handle_sticker_message(event: MessageEvent) -> None:
    """
    Handle sticker messages in a Line bot.

    Args:
        event (MessageEvent): The event object containing information about the sticker message.
    """

    msg_sender = get_sender()

    image_message = ImageMessage(
        originalContentUrl=msg_sender.icon_url,
        previewImageUrl=msg_sender.icon_url,
        sender=msg_sender,
    )

    await LINE_API_UTIL.reply_message(event.reply_token, [image_message])


async def handle_follow_join_event(
    event: FollowEvent | JoinEvent | MemberJoinedEvent,
) -> None:
    """
    Handles the follow, join, and member joined events in a Line bot.
    Sends a series of text messages to the user, introducing the bot and providing instructions on how to use it.

    Args:
        event (FollowEvent | JoinEvent | MemberJoinedEvent): The event object representing the follow, join, or member joined event.
    """

    mes_sender = get_sender("初階魔法師")
    messages = [
        TextMessage(
            text="泥好~~我是北大查詢小工具🔍",
            sender=mes_sender,
        ),
        TextMessage(
            text="詳細使用說明請點選下方選單\n或輸入「使用說明」",
            sender=mes_sender,
        ),
        TextMessage(
            text="有疑問可以先去看常見問題\n若無法解決或有發現 Bug\n可以到 GitHub 提出",
            sender=mes_sender,
        ),
        TextMessage(
            text="部分內容是由相關資料推斷\n不一定為正確資訊",
            sender=mes_sender,
        ),
        TextMessage(
            text="資料來源：\n國立臺北大學數位學苑 2.0\n國立臺北大學校園聯絡簿\n國立臺北大學課程查詢系統",
            sender=mes_sender,
        ),
    ]

    await LINE_API_UTIL.reply_message(event.reply_token, messages)
