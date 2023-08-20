# -*- coding:utf-8 -*-
import random
import string
import time
import threading
from typing import Dict
from copy import deepcopy

import requests
from bs4 import BeautifulSoup as BS4
from flask import Flask, Response, request, redirect
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.webhooks import (
    MessageEvent,
    PostbackEvent,
    TextMessageContent,
    StickerMessageContent,
    FollowEvent,
    JoinEvent,
    MemberJoinedEvent,
)
from linebot.v3.messaging.models import (
    Sender,
    QuickReply,
    QuickReplyItem,
    MessageAction,
    PostbackAction,
    TextMessage,
    ImageMessage,
    TemplateMessage,
    ConfirmTemplate,
    ButtonsTemplate,
)

from src.lineBotUtil import handler, reply_message
from src.sticker import stickers, load_stickers

app = Flask(__name__)

# 科系名稱 -> 科系代碼
DEPARTMENT_CODE = {
    "法律": "71",
    "法學": "712",
    "司法": "714",
    "財法": "716",
    "公行": "72",
    "經濟": "73",
    "社學": "742",
    "社工": "744",
    "財政": "75",
    "不動": "76",
    "會計": "77",
    "統計": "78",
    "企管": "79",
    "金融": "80",
    "中文": "81",
    "應外": "82",
    "歷史": "83",
    "休運": "84",
    "資工": "85",
    "通訊": "86",
    "電機": "87",
}

# 科系全名 -> 科系代碼
FULL_DEPARTMENT_CODE = {
    "法律學系": "71",
    "法學組": "712",
    "司法組": "714",
    "財經法組": "716",
    "公共行政暨政策學系": "72",
    "經濟學系": "73",
    "社會學系": "742",
    "社會工作學系": "744",
    "財政學系": "75",
    "不動產與城鄉環境學系": "76",
    "會計學系": "77",
    "統計學系": "78",
    "企業管理學系": "79",
    "金融與合作經營學系": "80",
    "中國文學系": "81",
    "應用外語學系": "82",
    "歷史學系": "83",
    "休閒運動管理學系": "84",
    "資訊工程學系": "85",
    "通訊工程學系": "86",
    "電機工程學系": "87",
}

# 科系代碼 -> 科系名稱
DEPARTMENT_NAME = {v: k for k, v in DEPARTMENT_CODE.items()}

# 科系代碼 -> 科系全名
FULL_DEPARTMENT_NAME = {v: k for k, v in FULL_DEPARTMENT_CODE.items()}

sticker_thread = threading.Thread(target=load_stickers)
sticker_thread.start()

search_url = ""


# 檢查網址是否還可用
def check_url():
    global search_url

    try:
        requests.get(search_url, timeout=1)
    except requests.exceptions.RequestException:
        ip_url = "http://120.126.197.52/"
        ip2_url = "https://120.126.197.52/"
        real_url = "https://lms.ntpu.edu.tw/"

        for url in [ip_url, ip2_url, real_url]:
            try:
                requests.get(url, timeout=1)
                search_url = url
                return Response(response="OK", status=200)
            except requests.exceptions.RequestException:
                continue

    return Response(response="Service Unavailable", status=503)


student_list: Dict[str, str] = {}


def renew_student() -> Response:
    global student_list

    cur_year = time.localtime(time.time()).tm_year - 1911
    new_student_list: Dict[str, str] = {}

    with requests.Session() as s:
        for year in range(cur_year - 6, cur_year + 1):
            for dep in DEPARTMENT_CODE.values():
                time.sleep(random.uniform(2.5, 5))
                url = (
                        search_url
                        + "portfolio/search.php?fmScope=2&page=1&fmKeyword=4"
                        + str(year)
                        + dep
                )
                raw_data = s.get(url)
                raw_data.encoding = "utf-8"

                data = BS4(raw_data.text, "html.parser")
                for item in data.find_all("div", {"class": "bloglistTitle"}):
                    name = item.find("a").text
                    number = item.find("a").get("href").split("/")[-1]
                    new_student_list[number] = name

                pages = len(data.find_all("span", {"class": "item"}))
                for i in range(2, pages):
                    time.sleep(random.uniform(2.5, 5))
                    url = (
                            search_url
                            + "portfolio/search.php?fmScope=2&page="
                            + str(i)
                            + "&fmKeyword=4"
                            + str(year)
                            + dep
                    )
                    raw_data = s.get(url)
                    raw_data.encoding = "utf-8"

                    data = BS4(raw_data.text, "html.parser")
                    for item in data.find_all("div", {"class": "bloglistTitle"}):
                        name = item.find("a").text
                        number = item.find("a").get("href").split("/")[-1]
                        new_student_list[number] = name

    student_list = deepcopy(new_student_list)
    return Response(response="OK", status=200)


renew_thread: threading.Thread

RENEW_USAGE = 1000
usage = RENEW_USAGE


@app.route("/")
def github() -> Response:
    return redirect("https://github.com/garyellow/ntpu-student-id-linebot")


@app.route("/check")
def healthy() -> Response:
    global usage, renew_thread

    if usage >= RENEW_USAGE:
        if check_url().response == "Service Unavailable":
            return Response(response="Service Unavailable", status=503)

        renew_thread = threading.Thread(target=renew_student)
        renew_thread.start()

    return Response(response="OK", status=200)


@app.route("/callback", methods=["POST"])
def callback() -> Response:
    global usage

    # get X-Line-Signature header value
    signature = request.headers["X-Line-Signature"]

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)

    except InvalidSignatureError:
        app.logger.info(
            "Invalid signature. Please check your channel access token/channel secret."
        )
        return Response(response="Internal Server Error", status=500)

    except requests.exceptions.Timeout:
        app.logger.info("Request Timeout.")
        usage = RENEW_USAGE
        return Response(response="Request Timeout", status=408)

    return Response(response="OK", status=200)


@handler.add(MessageEvent, message=TextMessageContent)
def handle_text_message(event: MessageEvent) -> None:
    global student_list

    receive_message = "".join(
        x for x in event.message.text if x not in string.whitespace + string.punctuation
    )

    if receive_message.isdecimal():
        if receive_message in FULL_DEPARTMENT_NAME:
            messages = [
                TextMessage(
                    text=FULL_DEPARTMENT_NAME[receive_message],
                    quick_reply=QuickReply(
                        items=[
                            QuickReplyItem(
                                action=MessageAction(label="所有系代碼", test="所有系代碼")
                            ),
                        ]
                    ),
                    sender=Sender(iconUrl=random.choice(stickers)),
                ),
            ]

            reply_message(event.reply_token, messages)

        elif 8 <= len(receive_message) <= 9:
            name = ""
            if receive_message in student_list:
                name = student_list[receive_message]
            else:
                url = (
                        search_url
                        + "portfolio/search.php?fmScope=2&page=1&fmKeyword="
                        + receive_message
                )
                web = requests.get(url)
                web.encoding = "utf-8"

                html = BS4(web.text, "html.parser")
                person = html.find("div", {"class": "bloglistTitle"})

                if person is not None:
                    name = str(person.find("a").text)
                else:
                    messages = [
                        TextMessage(
                            text="學號" + receive_message + "不存在OAO",
                            sender=Sender(iconUrl=random.choice(stickers)),
                        ),
                    ]

                    reply_message(event.reply_token, messages)
                    return

            messages = [
                TextMessage(
                    text=name,
                    sender=Sender(iconUrl=random.choice(stickers)),
                ),
            ]

            if receive_message[0] == "4":
                over_99 = len(receive_message) == 9
                year = receive_message[1: over_99 + 3]

                department = receive_message[over_99 + 3: over_99 + 5]
                if department in [
                    DEPARTMENT_CODE["法律"],
                    DEPARTMENT_CODE["社學"][0:2],
                ]:
                    department += receive_message[over_99 + 5]

                if department[0:2] == DEPARTMENT_CODE["法律"]:
                    show_text = (
                            "搜尋" + year + "學年度法律系" + DEPARTMENT_NAME[department] + "組"
                    )
                else:
                    show_text = "搜尋" + year + "學年度" + DEPARTMENT_NAME[department] + "系"

                messages[0].quick_reply = QuickReply(
                    items=[
                        QuickReplyItem(
                            action=PostbackAction(
                                label=show_text,
                                display_text="正在" + show_text,
                                data=year + " " + department,
                                input_option="closeRichMenu",
                            ),
                        ),
                    ],
                )

            reply_message(event.reply_token, messages)

        elif 2 <= len(receive_message) <= 4:
            year = (
                int(receive_message)
                if int(receive_message) < 1911
                else int(receive_message) - 1911
            )

            messages = []
            if year > time.localtime(time.time()).tm_year - 1911:
                messages.append(
                    TextMessage(
                        text="你未來人？(⊙ˍ⊙)",
                        sender=Sender(iconUrl=random.choice(stickers)),
                    )
                )
            elif year < 90:
                messages.append(
                    TextMessage(
                        text="學校都還沒蓋好(￣▽￣)",
                        sender=Sender(iconUrl=random.choice(stickers)),
                    )
                )
            elif year < 95:
                messages.append(
                    TextMessage(
                        text="數位學苑還沒出生",
                        sender=Sender(iconUrl=random.choice(stickers)),
                    )
                )
            else:
                messages.append(
                    TemplateMessage(
                        alt_text="確認學年度",
                        template=ConfirmTemplate(
                            text="是否要搜尋 " + str(year) + " 學年度的學生",
                            actions=[
                                PostbackAction(
                                    label="哪次不是",
                                    display_text="哪次不是",
                                    data="搜尋全系" + str(year),
                                    input_option="openRichMenu",
                                ),
                                PostbackAction(
                                    label="我在想想",
                                    display_text="再啦ㄍಠ_ಠ",
                                    data="兇",
                                    input_option="openKeyboard",
                                ),
                            ],
                        ),
                        sender=Sender(iconUrl=random.choice(stickers)),
                    )
                )

            reply_message(event.reply_token, messages)

    elif receive_message == "所有系代碼":
        message = "\n".join([x + "系 -> " + y for x, y in DEPARTMENT_CODE.items()])
        messages = [
            TextMessage(
                text=message,
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif receive_message.strip("系") in DEPARTMENT_CODE:
        messages = [
            TextMessage(
                text=DEPARTMENT_CODE[receive_message.strip("系")],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyItem(
                            action=MessageAction(label="所有系代碼", text="所有系代碼")
                        ),
                    ]
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif receive_message in FULL_DEPARTMENT_CODE:
        messages = [
            TextMessage(
                text=FULL_DEPARTMENT_CODE[receive_message],
                quick_reply=QuickReply(
                    items=[
                        QuickReplyItem(
                            action=MessageAction(label="所有系代碼", text="所有系代碼")
                        ),
                    ]
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif receive_message in student_list.values():
        message = ""
        for key, value in student_list:
            if value == receive_message:
                if message != "":
                    message += "\n"

                over_99 = len(key) == 9

                year = key[1: over_99 + 3]
                message += year + " "

                department = key[over_99 + 3: over_99 + 5]
                if department in [
                    DEPARTMENT_CODE["法律"],
                    DEPARTMENT_CODE["社學"][0:2],
                ]:
                    department += key[over_99 + 5]

                if department[0:2] == DEPARTMENT_CODE["法律"]:
                    message += "法律系 " + DEPARTMENT_NAME[department] + "組 "
                elif department[0:2] == DEPARTMENT_CODE["社學"][0:2]:
                    message += DEPARTMENT_NAME[department] + "系 "
                else:
                    message += DEPARTMENT_NAME[department] + "系 "

                message += key

        messages = [
            TextMessage(
                text=message,
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif receive_message[0] in string.ascii_letters or len(receive_message) < 6:
        if not student_list:
            messages = [
                TextMessage(
                    text="資料未建檔，請稍後再試😅",
                    sender=Sender(iconUrl=random.choice(stickers)),
                ),
            ]

            reply_message(event.reply_token, messages)
            return

        temp = []
        for key, value in student_list.items():
            if receive_message in value:
                temp.append(key.ljust(11, " ") + value)

        if temp:
            messages = [
                TextMessage(
                    text="\n".join(temp if len(temp) < 250 else temp[-250:]),
                    sender=Sender(iconUrl=random.choice(stickers)),
                ),
            ]

            reply_message(event.reply_token, messages)


@handler.add(MessageEvent, message=StickerMessageContent)
def handle_sticker_message(event: MessageEvent):
    sticker = random.choice(stickers)

    messages = [
        ImageMessage(
            original_content_url=sticker,
            preview_image_url=sticker,
            sender=Sender(iconUrl=sticker),
        ),
    ]

    reply_message(event.reply_token, messages)


@handler.add(PostbackEvent)
def handle_postback(event: PostbackEvent):
    if event.postback.data == "使用說明":
        mes_sender = Sender(iconUrl=random.choice(stickers))
        messages = [
            TextMessage(
                text="輸入學號可查詢姓名\n輸入姓名可查詢學號\n輸入系名可查詢系代碼\n輸入系代碼可查詢系名\n輸入入學學年再選科系獲取學生名單",
                sender=mes_sender,
            ),
            TextMessage(
                text="For example~~\n學號：412345678\n姓名：林某某 or 某某\n系名：資工系 or 資訊工程學系\n系代碼：85\n"
                     + "入學學年："
                     + str(time.localtime(time.time()).tm_year - 1911)
                     + " or "
                     + str(time.localtime(time.time()).tm_year),
                sender=mes_sender,
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data == "兇":
        messages = [
            TextMessage(
                text="泥好兇喔~~இ௰இ",
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("搜尋全系"):
        year = event.postback.data.split("搜尋全系")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇學院群",
                template=ButtonsTemplate(
                    thumbnail_imageUrl="https://new.ntpu.edu.tw/assets/logo/ntpu_logo.png",
                    title="選擇學院群",
                    text="請選擇科系所屬學院群",
                    actions=[
                        PostbackAction(
                            label="文法商", display_text="文法商", data="文法商" + year, input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="公社電資", display_text="公社電資", data="公社電資" + year,
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("文法商"):
        year = event.postback.data.split("文法商")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇學院",
                template=ButtonsTemplate(
                    title="選擇學院",
                    text="請選擇科系所屬學院",
                    actions=[
                        PostbackAction(
                            label="人文學院", display_text="人文學院", data="人文學院" + year,
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="法律學院", display_text="法律學院", data="法律學院" + year,
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="商學院", display_text="商學院", data="商學院" + year, input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("公社電資"):
        year = event.postback.data.split("公社電資")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇學院",
                template=ButtonsTemplate(
                    title="選擇學院",
                    text="請選擇科系所屬學院",
                    actions=[
                        PostbackAction(
                            label="公共事務學院", display_text="公共事務學院", data="公共事務學院" + year,
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="社會科學學院", display_text="社會科學學院", data="社會科學學院" + year,
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="電機資訊學院", display_text="電機資訊學院", data="電機資訊學院" + year,
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("人文學院"):
        year = event.postback.data.split("人文學院")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇科系",
                template=ButtonsTemplate(
                    thumbnail_imageUrl='https://walkinto.in/upload/-192z7YDP8-JlchfXtDvI.JPG',
                    title="選擇科系",
                    text="請選擇要查詢的科系",
                    actions=[
                        PostbackAction(
                            label="中國文學系", display_text="中國文學系", data="中國文學系" + year,
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="應用外語學系", display_text="應用外語學系", data="應用外語學系" + year,
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="歷史學系", display_text="歷史學系", data="歷史學系" + year,
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("法律學院"):
        year = event.postback.data.split("法律學院")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇組別",
                template=ButtonsTemplate(
                    thumbnail_imageUrl="https://walkinto.in/upload/byupdk9PvIZyxupOy9Dw8.JPG",
                    title="選擇組別",
                    text="請選擇要查詢的組別",
                    actions=[
                        PostbackAction(
                            label="法學組",
                            display_text="正在搜尋" + year + "學年度法律系法學組",
                            data=year + " " + DEPARTMENT_CODE["法學"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="司法組",
                            display_text="正在搜尋" + year + "學年度法律系司法組",
                            data=year + " " + DEPARTMENT_CODE["司法"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="財經法組",
                            display_text="正在搜尋" + year + "學年度法律系財法組",
                            data=year + " " + DEPARTMENT_CODE["財法"],
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("商學院"):
        year = event.postback.data.split("商學院")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇科系",
                template=ButtonsTemplate(
                    thumbnail_imageUrl="https://walkinto.in/upload/ZJum7EYwPUZkedmXNtvPL.JPG",
                    title="選擇科系",
                    text="請選擇科系 (休運系請直接點圖片)",
                    default_action=PostbackAction(
                        label="休閒運動管理學系",
                        display_text="正在搜尋" + year + "學年度休運系",
                        data=year + " " + DEPARTMENT_CODE["休運"],
                        input_option="closeRichMenu",
                    ),
                    actions=[
                        PostbackAction(
                            label="企業管理學系",
                            display_text="正在搜尋" + year + "學年度企管系",
                            data=year + " " + DEPARTMENT_CODE["企管"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="金融與合作經營學系",
                            display_text="正在搜尋" + year + "學年度金融系",
                            data=year + " " + DEPARTMENT_CODE["金融"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="會計學系",
                            display_text="正在搜尋" + year + "學年度會計系",
                            data=year + " " + DEPARTMENT_CODE["會計"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="統計學系",
                            display_text="正在搜尋" + year + "學年度統計系",
                            data=year + " " + DEPARTMENT_CODE["統計"],
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("公共事務學院"):
        year = event.postback.data.split("公共事務學院")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇科系",
                template=ButtonsTemplate(
                    thumbnail_imageUrl="https://walkinto.in/upload/ZJhs4wEaDIWklhiVwV6DI.jpg",
                    title="選擇科系",
                    text="請選擇要查詢的科系",
                    actions=[
                        PostbackAction(
                            label="公共行政暨政策學系",
                            display_text="正在搜尋" + year + "學年度公行系",
                            data=year + " " + DEPARTMENT_CODE["公行"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="不動產與城鄉環境學系",
                            display_text="正在搜尋" + year + "學年度不動系",
                            data=year + " " + DEPARTMENT_CODE["不動"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="財政學系",
                            display_text="正在搜尋" + year + "學年度財政系",
                            data=year + " " + DEPARTMENT_CODE["財政"],
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("社會科學學院"):
        year = event.postback.data.split("社會科學學院")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇科系",
                template=ButtonsTemplate(
                    thumbnail_imageUrl="https://walkinto.in/upload/WyPbshN6DIZ1gvZo2NTvU.JPG",
                    title="選擇科系",
                    text="請選擇科系",
                    actions=[
                        PostbackAction(
                            label="經濟學系",
                            display_text="正在搜尋" + year + "學年度經濟系",
                            data=year + " " + DEPARTMENT_CODE["經濟"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="社會學系",
                            display_text="正在搜尋" + year + "學年度社學系",
                            data=year + " " + DEPARTMENT_CODE["社學"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="社會工作學系",
                            display_text="正在搜尋" + year + "學年度社工系",
                            data=year + " " + DEPARTMENT_CODE["社工"],
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    elif event.postback.data.startswith("電機資訊學院"):
        year = event.postback.data.split("電機資訊學院")[1]

        messages = [
            TemplateMessage(
                alt_text="選擇科系",
                template=ButtonsTemplate(
                    thumbnail_imageUrl="https://walkinto.in/upload/bJ9zWWHaPLWJg9fW-STD8.png",
                    title="選擇科系",
                    text="請選擇科系",
                    actions=[
                        PostbackAction(
                            label="電機工程學系",
                            display_text="正在搜尋" + year + "學年度電機系",
                            data=year + " " + DEPARTMENT_CODE["電機"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="資訊工程學系",
                            display_text="正在搜尋" + year + "學年度資工系",
                            data=year + " " + DEPARTMENT_CODE["資工"],
                            input_option="closeRichMenu",
                        ),
                        PostbackAction(
                            label="通訊工程學系",
                            display_text="正在搜尋" + year + "學年度通訊系",
                            data=year + " " + DEPARTMENT_CODE["通訊"],
                            input_option="closeRichMenu",
                        ),
                    ],
                ),
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)

    else:
        yd = "".join(event.postback.data.split(" "))
        temp = []

        if student_list:
            for key, value in student_list.items():
                if key.startswith("4" + yd):
                    temp.append(key.ljust(11, " ") + value)

        else:
            with requests.Session() as s:
                s.keep_alive = False

                url = (
                        search_url
                        + "portfolio/search.php?fmScope=2&page=1&fmKeyword=4"
                        + yd
                )
                web = s.get(url)
                web.encoding = "utf-8"

                html = BS4(web.text, "html.parser")
                for item in html.find_all("div", {"class": "bloglistTitle"}):
                    name = item.find("a").text
                    number = item.find("a").get("href").split("/")[-1]
                    temp.append(number.ljust(11, " ") + name)

                pages = len(html.find_all("span", {"class": "item"}))
                for i in range(2, pages):
                    time.sleep(random.uniform(0.05, 0.2))

                    url = (
                            search_url
                            + "portfolio/search.php?fmScope=2&page="
                            + str(i)
                            + "&fmKeyword=4"
                            + yd
                    )
                    web = s.get(url)
                    web.encoding = "utf-8"

                    html = BS4(web.text, "html.parser")
                    for item in html.find_all("div", {"class": "bloglistTitle"}):
                        name = item.find("a").text
                        number = item.find("a").get("href").split("/")[-1]
                        temp.append(number.ljust(11, " ") + name)

        message = "\n".join(temp)

        if event.postback.data.split(" ")[1][0:2] == DEPARTMENT_CODE["法律"]:
            message += (
                    "\n\n"
                    + event.postback.data.split(" ")[0]
                    + "學年度法律系"
                    + DEPARTMENT_NAME[event.postback.data.split(" ")[1]]
                    + "組共有"
                    + str(len(temp))
                    + "位學生"
            )
        else:
            message += (
                    "\n\n"
                    + event.postback.data.split(" ")[0]
                    + "學年度"
                    + DEPARTMENT_NAME[event.postback.data.split(" ")[1]]
                    + "系共有"
                    + str(len(temp))
                    + "位學生"
            )

        messages = [
            TextMessage(
                text=message,
                sender=Sender(iconUrl=random.choice(stickers)),
            ),
        ]

        reply_message(event.reply_token, messages)


@handler.add(FollowEvent)
@handler.add(JoinEvent)
@handler.add(MemberJoinedEvent)
def handle_follow_join(event):
    mes_sender = Sender(iconUrl=random.choice(stickers))

    messages = [
        TextMessage(
            text="泥好~~我是學號姓名查詢小工具🔍\n可以用學號查詢到姓名\n也可以用姓名查詢到學號\n詳細使用說明請點選下方選單",
            sender=mes_sender,
        ),
        TextMessage(
            text="有疑問可以先去看常見問題\n若無法解決或有發現 Bug\n可以再到 GitHub 提出", sender=mes_sender
        ),
        TextMessage(text="資料來源：國立臺北大學數位學苑2.0", sender=mes_sender),
    ]

    reply_message(event.reply_token, messages)


if __name__ == "__main__":
    sticker_thread.join()
    app.run(host="0.0.0.0", port=80)
