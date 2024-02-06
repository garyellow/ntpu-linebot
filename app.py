# -*- coding:utf-8 -*-
import threading

import requests
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import PlainTextResponse, RedirectResponse
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    Event,
    FollowEvent,
    JoinEvent,
    MemberJoinedEvent,
    MessageEvent,
    PostbackEvent,
    StickerMessageContent,
    TextMessageContent,
)

import src.bot_routes as routes
from src.id_request import check_url
from src.line_bot_util import handler
from src.student_util import renew_student_list

app = FastAPI()

url_state = False
renew_thread: threading.Thread


@app.head("/")
@app.get("/")
def index() -> RedirectResponse:
    """導向至專案 GitHub 頁面"""

    return RedirectResponse(
        status_code=302, url="https://github.com/garyellow/ntpu-linebot"
    )


@app.head("/healthz")
@app.get("/healthz")
def healthz() -> PlainTextResponse:
    """健康檢查"""

    global url_state, renew_thread

    if not url_state:
        if not check_url():
            raise HTTPException(status_code=503, detail="Service Unavailable")

        renew_thread = threading.Thread(target=renew_student_list)
        renew_thread.start()

        url_state = True

    return PlainTextResponse(status_code=200, content="OK")


@app.post("/callback")
async def callback(request: Request) -> PlainTextResponse:
    """處理 LINE Bot 的 Webhook"""

    global url_state

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = await request.body()
    body = body.decode()

    # handle webhook body
    try:
        handler.handle(body, signature)

    except InvalidSignatureError as exc:
        raise HTTPException(status_code=400, detail="Invalid signature") from exc

    except requests.exceptions.Timeout as exc:
        url_state = False
        raise HTTPException(status_code=408, detail="Request Timeout") from exc

    return PlainTextResponse(status_code=200, content="OK")


@handler.add(MessageEvent, TextMessageContent)
async def handle_text_message(event: MessageEvent) -> None:
    """處理文字訊息"""

    await routes.handle_text_message(event)


@handler.add(PostbackEvent)
async def handle_postback_event(event: PostbackEvent) -> None:
    """處理回傳事件"""

    await routes.handle_postback_event(event)


@handler.add(MessageEvent, StickerMessageContent)
async def handle_sticker_message(event: MessageEvent) -> None:
    """處理貼圖訊息"""

    await routes.handle_sticker_message(event)


@handler.add(FollowEvent)
@handler.add(JoinEvent)
@handler.add(MemberJoinedEvent)
async def handle_follow_join_event(event: Event) -> None:
    """處理加入好友與加入群組事件"""

    await routes.handle_follow_join_event(event)
