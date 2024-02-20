# -*- coding:utf-8 -*-
from http.client import SERVICE_UNAVAILABLE

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
from sanic import HTTPResponse, Request, Sanic, Unauthorized, redirect, text

from ntpu_linebot import (
    PARSER,
    STICKER,
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
    ntpu_id,
)

app = Sanic("app")


@app.route("/", methods=["HEAD", "GET"])
async def index(_: Request) -> HTTPResponse:
    """
    Redirects to the project GitHub page

    Args:
        request (Request): The request object representing the HTTP request made by the client.

    Returns:
        HTTPResponse: The redirect response that redirects the user to the GitHub page.
    """

    return redirect("https://github.com/garyellow/ntpu-linebot")


@app.route("/healthz", methods=["HEAD", "GET"])
async def healthz(request: Request) -> HTTPResponse:
    """
    Checks the health status.

    Args:
        request (Request): The Sanic request object representing the HTTP request.

    Returns:
        HTTPResponse: An HTTP response with  status code 200 if all services are healthy.
        If any service is not healthy, a SanicException with status code 503 will be raised.
    """

    if not await STICKER.is_healthy(request.app):
        return text("Sticker Unavailable", SERVICE_UNAVAILABLE)

    if not await ntpu_id.healthz(request.app):
        return text("ID Unavailable", SERVICE_UNAVAILABLE)

    return text("OK")


@app.post("/callback")
async def callback(request: Request) -> HTTPResponse:
    """
    Handle LINE Bot webhook events.

    Args:
        request (Request): The request object representing the incoming webhook request.

    Returns:
        HTTPResponse: The response object indicating the success of the callback function.
    """

    # Get the X-Line-Signature header value
    signature = request.headers.get("X-Line-Signature")

    # Get the request body as text
    body = request.body.decode()

    # Handle the webhook body
    try:
        events = PARSER.parse(body, signature)

    except InvalidSignatureError as exc:
        raise Unauthorized("Invalid signature") from exc

    # Process each event
    for event in events:
        if isinstance(event, MessageEvent):
            if isinstance(event.message, TextMessageContent):
                await handle_text_message(event)

            elif isinstance(event.message, StickerMessageContent):
                await handle_sticker_message(event)

        elif isinstance(event, PostbackEvent):
            await handle_postback_event(event)

        elif isinstance(event, (FollowEvent, JoinEvent, MemberJoinedEvent)):
            await handle_follow_join_event(event)

    return text("OK")
