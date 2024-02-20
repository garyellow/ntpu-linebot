# -*- coding:utf-8 -*-
import random
import sys
from os import getenv
from typing import Optional

from linebot.v3 import WebhookParser
from linebot.v3.messaging import (
    AsyncApiClient,
    AsyncMessagingApi,
    Configuration,
    Message,
    ReplyMessageRequest,
    Sender,
)

from ntpu_linebot.sticker_util import STICKER

# get channel_secret and channel_access_token from your environment variable
CHANNEL_SECRET = getenv("LINE_CHANNEL_SECRET", None)
CHANNEL_ACCESS_TOKEN = getenv("LINE_CHANNEL_ACCESS_TOKEN", None)

if CHANNEL_SECRET is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if CHANNEL_ACCESS_TOKEN is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

PARSER = WebhookParser(CHANNEL_SECRET)
CONFIGURATION = Configuration(access_token=CHANNEL_ACCESS_TOKEN)
ASYNC_API_CLIENT = AsyncApiClient(CONFIGURATION)
LINE_BOT_API = AsyncMessagingApi(ASYNC_API_CLIENT)


def get_sender(name: Optional[str] = None) -> Sender:
    """
    Get sender information with a random sticker as the icon.

    Args:
        name (str, optional): The name of the sender.

    Returns:
        A Sender object with the name and iconUrl.
    """

    return Sender(name=name, iconUrl=random.choice(STICKER.STICKER_LIST))


async def reply_message(reply_token: str, messages: list[Message]) -> None:
    """
    Create and send reply messages in the Line messaging platform.

    Args:
        reply_token (str): The token for replying to a specific message.
        messages (list[Message]): The list of messages to be sent as a reply.

    Returns:
        None
    """

    await LINE_BOT_API.reply_message(
        ReplyMessageRequest(
            replyToken=reply_token,
            messages=messages,
        ),
    )
