# -*- coding:utf-8 -*-
import requests
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    FollowEvent,
    JoinEvent,
    MemberJoinedEvent,
    MessageEvent,
    PostbackEvent,
    StickerMessageContent,
    TextMessageContent,
)
from sanic import HTTPResponse, Request, Sanic, SanicException, redirect, text

from ntpu_linebot import (
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
    ntpu_id,
    parser,
)


app = Sanic("app")


@app.route("/", methods=["HEAD", "GET"])
async def index(request: Request) -> HTTPResponse:
    """導向至專案 GitHub 頁面"""

    return redirect("https://github.com/garyellow/ntpu-linebot")


@app.route("/healthz", methods=["HEAD", "GET"])
async def healthz(request: Request) -> HTTPResponse:
    """健康檢查"""

    if not ntpu_id.healthz(request.app):
        raise SanicException("Service Unavailable", 503)

    return text("OK")


@app.post("/callback")
async def callback(request: Request) -> HTTPResponse:
    """處理 LINE Bot 的 Webhook"""

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.body.decode()

    # handle webhook body
    try:
        events = parser.parse(body, signature)

    except InvalidSignatureError as exc:
        raise SanicException("Invalid signature", 401) from exc

    except requests.exceptions.Timeout as exc:
        raise SanicException("Request Timeout", 408) from exc

    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessageContent):
                await handle_text_message(event)
            if isinstance(event.message, StickerMessageContent):
                await handle_sticker_message(event)

        elif isinstance(event, PostbackEvent):
            await handle_postback_event(event)

        elif isinstance(event, (FollowEvent, JoinEvent, MemberJoinedEvent)):
            await handle_follow_join_event(event)

    return text("OK")
