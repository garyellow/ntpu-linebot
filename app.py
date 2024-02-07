# -*- coding:utf-8 -*-
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

from ntpu_linebot import (
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
    ntpu_id,
    parser,
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

    if not ntpu_id.healthz():
        raise HTTPException(503, "Service Unavailable")

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
