# -*- coding:utf-8 -*-
from abc import abstractmethod


class Bot:
    """Abstract class for creating bots"""

    @abstractmethod
    async def handle_text_message(self, payload: str, reply_token: str) -> bool:
        """
        Handle text messages received by the bot.

        Args:
            payload (str): The text message.
            reply_token (str): Token used for replying to the message.

        Returns:
            bool: True if the message is successfully handled, False otherwise.
        """

    @abstractmethod
    async def handle_postback_event(self, payload: str, reply_token: str) -> None:
        """
        Handle postback events received by the bot.

        Args:
            payload (str): The payload of the event.
            reply_token (str): Token used for replying to the event.
        """
