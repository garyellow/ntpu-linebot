# -*- coding:utf-8 -*-
from abc import abstractmethod
from typing import Optional

from linebot.v3.messaging.models import Message


class Bot:
    """Abstract class for creating bots"""

    @abstractmethod
    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> list[Message]:
        """
        Handle text messages received by the bot.

        Args:
            payload (str): The text message payload received by the bot.
            quote_token (Optional[str]): An optional quote token used for quoting the message.

        Returns:
            List[Message]: A list of Message objects representing the bot's response to the text message.
        """

    @abstractmethod
    async def handle_postback_event(self, payload: str) -> list[Message]:
        """
        Handle a postback event and return a list of messages as a response.

        Args:
            payload (str): The payload received by the bot representing a postback event.

        Returns:
            list[Message]: A list of Message objects representing the bot's response to the postback event.
        """
