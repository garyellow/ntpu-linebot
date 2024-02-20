# -*- coding:utf-8 -*-
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
)


class LineAPIUtil:
    channel_secret: Optional[str] = None
    channel_access_token: Optional[str] = None
    parser: Optional[WebhookParser] = None
    configuration: Optional[Configuration] = None
    async_api_client: Optional[AsyncApiClient] = None
    line_bot_api: Optional[AsyncMessagingApi] = None

    def get_line_bot_api(self) -> AsyncMessagingApi:
        """
        Retrieves an instance of the AsyncMessagingApi class.

        Returns:
            AsyncMessagingApi: An instance of the AsyncMessagingApi class.
        """

        if self.line_bot_api is None:
            self.channel_access_token = getenv("LINE_CHANNEL_ACCESS_TOKEN")

            if self.channel_access_token is None:
                print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
                sys.exit(1)

            self.configuration = Configuration(access_token=self.channel_access_token)
            self.async_api_client = AsyncApiClient(self.configuration)
            self.line_bot_api = AsyncMessagingApi(self.async_api_client)

        return self.line_bot_api

    def get_webhook_parser(self) -> WebhookParser:
        """
        Retrieves an instance of the WebhookParser class.

        Returns:
            WebhookParser: An instance of the WebhookParser class.
        """

        if self.parser is None:
            self.channel_secret = getenv("LINE_CHANNEL_SECRET")

            if self.channel_secret is None:
                print("Specify LINE_CHANNEL_SECRET as environment variable.")
                sys.exit(1)

            self.parser = WebhookParser(self.channel_secret)

        return self.parser

    async def reply_message(self, reply_token: str, messages: list[Message]) -> None:
        """
        Create and send reply messages in the Line messaging platform.

        Args:
            reply_token (str): The token for replying to a specific message.
            messages (list[Message]): The list of messages to be sent as a reply.

        Returns:
            None
        """

        await self.get_line_bot_api().reply_message(
            ReplyMessageRequest(
                replyToken=reply_token,
                messages=messages,
            ),
        )


LINE_API_UTIL = LineAPIUtil()
