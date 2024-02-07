# -*- coding:utf-8 -*-
from ntpu_linebot import id as ntpu_id
from ntpu_linebot.line_bot_util import parser
from ntpu_linebot.route_util import (
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
)
