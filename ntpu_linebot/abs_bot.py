# -*- coding:utf-8 -*-
from abc import abstractmethod
from typing import Optional


class Bot:
    """Abstract class for creating bots"""

    @abstractmethod
    async def handle_text_message(
        self,
        payload: str,
        quote_token: Optional[str] = None,
    ) -> bool:
        """
        Handle text messages received by the bot.

        Args:
            payload (str): The text message.
            quote_token (str): Token used for quoting the message.

        Returns:
            bool: True if the message is successfully handled, False otherwise.
        """

    @abstractmethod
    async def handle_postback_event(self, payload: str) -> None:
        """
        Handle postback events received by the bot.

        Args:
            payload (str): The payload of the event.
        """
