# -*- coding:utf-8 -*-
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

from src.botRoute import (
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
)
from src.lineBotUtil import parser
from src.requestUtil import check_url
from src.studentUtil import renew_student_list

app = FastAPI()

url_state = False
renew_thread: threading.Thread


@app.head("/")
@app.get("/")
def index() -> RedirectResponse:
    return RedirectResponse(
        status_code=302, url="https://github.com/garyellow/ntpu-linebot"
    )


@app.head("/healthz")
@app.get("/healthz")
def healthz() -> PlainTextResponse:
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
    global url_state

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = await request.body()
    body = body.decode()

    # handle webhook body
    try:
        events = parser.parse(body, signature)

    except InvalidSignatureError:
        raise HTTPException(status_code=500, detail="Invalid signature")

    except requests.exceptions.Timeout:
        url_state = False
        raise HTTPException(status_code=408, detail="Request Timeout")

    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessageContent):
                await handle_text_message(event)
            if isinstance(event.message, StickerMessageContent):
                await handle_sticker_message(event)

        elif isinstance(event, PostbackEvent):
            await handle_postback_event(event)

        elif (
            isinstance(event, FollowEvent)
            or isinstance(event, JoinEvent)
            or isinstance(event, MemberJoinedEvent)
        ):
            await handle_follow_join_event(event)

    return PlainTextResponse(status_code=200, content="OK")
