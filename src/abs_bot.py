# -*- coding:utf-8 -*-
from abc import abstractmethod

from linebot.v3.webhooks import MessageEvent, PostbackEvent


class Bot:
    """機器人抽象類別"""

    @abstractmethod
    async def handle_text_message(self, event: MessageEvent) -> None:
        """處理文字訊息"""

    @abstractmethod
    async def handle_postback_event(self, event: PostbackEvent) -> None:
        """處理回傳事件"""
