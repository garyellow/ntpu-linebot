# -*- coding:utf-8 -*-
import imp
import threading

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
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

from src import id_request
from src.id_util import renew_student_list
from src.line_bot_util import parser
from src.route_util import (
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
)

app = FastAPI()


@app.head("/")
@app.get("/")
def index() -> RedirectResponse:
    """導向至專案 GitHub 頁面"""

    return RedirectResponse("https://github.com/garyellow/ntpu-linebot", 302)


@app.head("/healthz")
@app.get("/healthz")
def healthz() -> PlainTextResponse:
    """健康檢查"""

    if not id_request.base_url:
        if not id_request.check_url():
            raise HTTPException(503, "Service Unavailable")

        id_request.renew_thread = threading.Thread(target=renew_student_list)
        id_request.renew_thread.start()

    return PlainTextResponse("OK", 200)


@app.post("/callback")
async def callback(request: Request) -> PlainTextResponse:
    """處理 LINE Bot 的 Webhook"""

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = await request.body()
    body = body.decode()

    # handle webhook body
    try:
        events = parser.parse(body, signature)

    except InvalidSignatureError as exc:
        raise HTTPException(401, "Invalid signature") from exc

    except requests.exceptions.Timeout as exc:
        raise HTTPException(408, "Request Timeout") from exc

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

    return PlainTextResponse("OK", 200)
