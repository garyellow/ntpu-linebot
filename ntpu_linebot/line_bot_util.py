# -*- coding:utf-8 -*-
import random
from typing import Optional

from linebot.v3.messaging import Sender

from ntpu_linebot.sticker_util import STICKER


def get_sender(name: Optional[str] = None) -> Sender:
    """
    Get sender information with a random sticker as the icon.

    Args:
        name (str, optional): The name of the sender.

    Returns:
        A Sender object with the name and iconUrl.
    """

    return Sender(name=name, iconUrl=random.choice(STICKER.STICKER_LIST))
