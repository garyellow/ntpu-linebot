# -*- coding:utf-8 -*-
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
from sanic import (
    HTTPResponse,
    Request,
    Sanic,
    ServiceUnavailable,
    Unauthorized,
    redirect,
    text,
)

from ntpu_linebot import (
    LINE_API_UTIL,
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
        HTTPResponse: An HTTP response with status code 200 if all services are healthy.
        If any service is not healthy, an exception with status code 503 will be raised.
    """

    if not await STICKER.is_healthy(request.app):
        raise ServiceUnavailable("Sticker Unavailable")

    if not await ntpu_id.healthz(request.app):
        raise ServiceUnavailable("ID Unavailable")

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

    try:
        events = LINE_API_UTIL.get_webhook_parser().parse(
            request.body.decode(),
            request.headers.get("X-Line-Signature"),
        )

        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessageContent):
                    await handle_text_message(event, request.app)

                elif isinstance(event.message, StickerMessageContent):
                    await handle_sticker_message(event, request.app)

            elif isinstance(event, PostbackEvent):
                await handle_postback_event(event, request.app)

            elif isinstance(event, (FollowEvent, JoinEvent, MemberJoinedEvent)):
                await handle_follow_join_event(event, request.app)

        return text("OK")

    except InvalidSignatureError as exc:
        raise Unauthorized("Invalid signature") from exc
