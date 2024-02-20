# -*- coding:utf-8 -*-
from fastapi import (
    BackgroundTasks,
    Body,
    FastAPI,
    Header,
    HTTPException,
    Request,
    status,
)
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
from pydantic import BaseModel

from ntpu_linebot import (
    PARSER,
    STICKER,
    handle_follow_join_event,
    handle_postback_event,
    handle_sticker_message,
    handle_text_message,
    ntpu_id,
)

app = FastAPI()


@app.head("/")
@app.get("/")
async def index() -> RedirectResponse:
    """
    Redirects to the project GitHub page

    Returns:
        RedirectResponse: The redirect response that redirects the user to the GitHub page.
    """

    github_url = "https://github.com/garyellow/ntpu-linebot"
    return RedirectResponse(url=github_url, status_code=status.HTTP_302_FOUND)


@app.head("/healthz")
@app.get("/healthz")
async def healthz(background_tasks: BackgroundTasks) -> PlainTextResponse:
    """
    Checks the health status.

    Args:
        background_tasks (BackgroundTasks): The FastAPI BackgroundTasks object.

    Returns:
        PlainTextResponse: An HTTP response with status code 200 if all services are healthy.
        If any service is not healthy, an HTTP response with status code 503 will be returned.
    """

    if not await STICKER.is_healthy(background_tasks):
        return PlainTextResponse(
            "Sticker Unavailable",
            status.HTTP_503_SERVICE_UNAVAILABLE,
            background=background_tasks,
        )

    if not await ntpu_id.healthz(background_tasks):
        return PlainTextResponse(
            "ID Unavailable",
            status.HTTP_503_SERVICE_UNAVAILABLE,
            background=background_tasks,
        )

    return PlainTextResponse("OK")


class LineWebhookPayload(BaseModel):
    """
    The payload of the LINE Bot webhook.
    """

    destination: str
    events: list


@app.post("/callback")
async def callback(
    request: Request,
    _: LineWebhookPayload = Body(...),
    x_line_signature: str = Header(...),
) -> PlainTextResponse:
    """
    Handle LINE Bot webhook events.

    Args:
        body (LineWebhookPayload): The body of the LINE Bot webhook, containing the destination and events.
        x_line_signature (str): The signature of the webhook request.

    Returns:
        PlainTextResponse: The response object indicating the success of the callback function.
    """

    try:
        events = PARSER.parse((await request.body()).decode(), x_line_signature)

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

        return PlainTextResponse("OK")

    except InvalidSignatureError as exc:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid signature") from exc
