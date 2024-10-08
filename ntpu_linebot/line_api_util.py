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
    ShowLoadingAnimationRequest,
)


class LineAPIUtil:
    __parser: Optional[WebhookParser] = None
    __line_bot_api: Optional[AsyncMessagingApi] = None

    @property
    def line_bot_api(self) -> AsyncMessagingApi:
        """
        Retrieves an instance of the AsyncMessagingApi class.

        Returns:
            AsyncMessagingApi: An instance of the AsyncMessagingApi class.
        """

        if self.__line_bot_api is None:
            if channel_access_token := getenv("LINE_CHANNEL_ACCESS_TOKEN"):
                self.__line_bot_api = AsyncMessagingApi(
                    AsyncApiClient(
                        Configuration(access_token=channel_access_token),
                        pool_threads=2,
                    )
                )

            else:
                sys.exit("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")

        return self.__line_bot_api

    @property
    def parser(self) -> WebhookParser:
        """
        Retrieves an instance of the WebhookParser class.

        Returns:
            WebhookParser: An instance of the WebhookParser class.
        """

        if self.__parser is None:
            if channel_secret := getenv("LINE_CHANNEL_SECRET"):
                self.__parser = WebhookParser(channel_secret)

            else:
                sys.exit("Specify LINE_CHANNEL_SECRET as environment variable.")

        return self.__parser

    async def reply_message(self, reply_token: str, messages: list[Message]) -> None:
        """
        Create and send reply messages in the Line messaging platform.

        Args:
            reply_token (str): The token for replying to a specific message.
            messages (list[Message]): The list of messages to be sent as a reply.
        """

        await self.line_bot_api.reply_message(
            ReplyMessageRequest(
                replyToken=reply_token,
                messages=messages,
            )
        )

    async def loading_message(self, user_id: str) -> None:
        """
        Send a loading message in the Line messaging platform.

        Args:
            user_id (str): The user ID of the message sender.
        """

        await self.line_bot_api.show_loading_animation(
            ShowLoadingAnimationRequest(chatId=user_id, loadingSeconds=10)
        )


LINE_API_UTIL = LineAPIUtil()
