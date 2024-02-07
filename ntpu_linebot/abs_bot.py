# -*- coding:utf-8 -*-
from abc import abstractmethod


class Bot:
    """機器人抽象類別"""

    @abstractmethod
    async def handle_text_message(self, payload: str, reply_token: str) -> bool:
        """處理文字訊息"""

    @abstractmethod
    async def handle_postback_event(self, payload: str, reply_token: str) -> None:
        """處理回傳事件"""
