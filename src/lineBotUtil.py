# -*- coding:utf-8 -*-
import os
import sys
from typing import List

from linebot.v3 import WebhookParser
from linebot.v3.messaging.api.async_messaging_api import AsyncMessagingApi
from linebot.v3.messaging.async_api_client import AsyncApiClient
from linebot.v3.messaging.configuration import Configuration
from linebot.v3.messaging.models import Message, ReplyMessageRequest

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


async def reply_message(reply_token: str, message: List[Message]) -> None:
    await line_bot_api.reply_message(
        ReplyMessageRequest(
            reply_token=reply_token,
            messages=message,
        ),
    )
