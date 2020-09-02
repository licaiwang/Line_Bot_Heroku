# linebotTest1
# ngrok http 5000
import random
import re

from flask import Flask, abort, render_template, request
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (
    ImageSendMessage,
    LocationSendMessage,
    MessageAction,
    MessageEvent,
    QuickReply,
    QuickReplyButton,
    StickerSendMessage,
    TextMessage,
    LocationMessage,
    TextSendMessage,
)

import clawer
from weather import searchWeather, stickerSelect
from breakfast import selectBreakfast
from travel import allSight, searchShortlest


app = Flask(__name__)

line_bot_api = LineBotApi(
    "k/HVDioE+/cG+b24V2c0vLvYbe1CgtmVo5uAz3IDyC3MwwhRRUxqUrbGFwjiuW4seNE37jTFUdYGgQB+Zv9UJEkt4HchRR4mhwQSEhnJqVknTz/qHiYfCInpoQjg7JjFDrb7lq0Mh1M7V8ngDbiOfgdB04t89/1O/w1cDnyilFU="
)
handler = WebhookHandler("ff0138a40953ad704412fb621ebbee64")

# 接收 LINE 的資訊
@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # 獲得使用者輸入的訊息
    body = request.get_data(as_text=True)
    try:
        # 送出
        handler.handle(body, signature)
    except InvalidSignatureError:
        # 送出 Bad request (400)
        abort(400)
    # 回覆OK
    return "ok"


# Line 要回傳什麼


@handler.add(MessageEvent, message=LocationMessage)
def handle_loc(event):
    input_address = event.message.address
    input_latitude = event.message.latitude
    input_longitude = event.message.longitude
    token = event.reply_token
    loc = searchShortlest(input_address, input_latitude, input_longitude)
    if loc:
        message = [
            TextSendMessage(text="為您推薦最近景點"),
            LocationSendMessage(
                title=loc[0], address=loc[2], latitude=loc[1][0], longitude=loc[1][1],
            ),
        ]
    else:
        message = TextSendMessage(text="查無最近景點！")

    line_bot_api.reply_message(token, message)


@handler.add(MessageEvent, message=TextMessage)
# 加入一個 handle_message function
def handle_message(event):
    """
    處理所有問題並分發答案
    """
    input_text = event.message.text
    token = event.reply_token
    if isInvoice(input_text, token):
        return
    elif isTravel_2(input_text, token):
        return
    elif isWeather(input_text, token):
        return
    elif isTravel(input_text, token):
        return

    elif isBreakfast(input_text, token):
        return


def isInvoice(input_text, token) -> bool:
    """
    查看是否為發票相關問題，是就回答
    """
    if input_text == "@本期中獎號碼":
        line_bot_api.reply_message(token, TextSendMessage(text=clawer.askPrize(0)))
        return True
    if input_text == "@前期中獎號碼":
        line_bot_api.reply_message(token, TextSendMessage(text=clawer.askPrize(1)))
        return True
    if input_text == "發票獎金":
        line_bot_api.reply_message(token, TextSendMessage(text=clawer.PRIZE))
        return True
    else:
        number = re.sub("\\D", "", input_text)
        if number != "" and len(number) == 3:
            (isWin, content) = clawer.checkWinPrize(number)
            # 0 - 沒中， 1 當期有中 , 2 前期有中
            if isWin:
                try:
                    message = [
                        TextSendMessage(text=content),
                        TextSendMessage(text=clawer.askPrize(isWin - 1)),
                    ]
                    line_bot_api.reply_message(token, message)
                    return True
                except:
                    return False
            else:
                line_bot_api.reply_message(token, TextSendMessage(text=content))
                return True
    return False


def isWeather(input_text, token):
    """
    查看是否為天氣相關問題，是就回答
    """
    if "天氣" in input_text:
        if searchWeather(input_text):
            (loc, date, inf, tmp) = searchWeather(input_text)
            if "週" in input_text:
                res = ""
                for i in range(7):
                    res += f"{date[i]}：\n白天：{inf[i][0]}\n溫度{tmp[i][0]}\n晚上：{inf[i][1]}\n溫度{tmp[i][1]}\n\n"
                line_bot_api.reply_message(token, TextSendMessage(text=res))
                return True
            else:
                url = stickerSelect(inf[0][0])
                respone = [
                    TextSendMessage(
                        text=f"{loc}今天的天氣狀況：\n白天：{inf[0][0]}，溫度{tmp[0][0]}\n晚上：{inf[0][1]}，溫度{tmp[0][1]}"
                    ),
                    ImageSendMessage(original_content_url=url, preview_image_url=url),
                ]
            line_bot_api.reply_message(token, respone)
            return True

        elif "天氣" in input_text:
            chose = TextSendMessage(
                text="哪裡的天氣呢?",
                quick_reply=QuickReply(
                    items=[
                        QuickReplyButton(action=MessageAction(label="宜蘭", text="宜蘭天氣")),
                        QuickReplyButton(action=MessageAction(label="台北", text="台北天氣")),
                        QuickReplyButton(action=MessageAction(label="台南", text="台南天氣")),
                    ]
                ),
            )
            line_bot_api.reply_message(token, chose)
            return isTravel_2(input_text, token)
    return False


def isBreakfast(input_text, token):
    if "早餐" in input_text:
        line_bot_api.reply_message(token, TextSendMessage(text=selectBreakfast()))
        return True
    return False


def isTravel(input_text, token):
    (loc_1, loc_2) = allSight(input_text)
    if loc_2:
        recommand = random.choice(loc_2)
        message = [
            TextSendMessage(text="為您隨機推薦景點"),
            LocationSendMessage(
                title=recommand[0],
                address=recommand[2],
                latitude=recommand[1][0],
                longitude=recommand[1][1],
            ),
        ]
        line_bot_api.reply_message(token, message)
        return True
    elif loc_1:
        recommand = random.choice(loc_1)
        message = [
            TextSendMessage(text="為您隨機推薦景點"),
            LocationSendMessage(
                title=recommand[0],
                address=recommand[2],
                latitude=recommand[1][0],
                longitude=recommand[1][1],
            ),
        ]
        line_bot_api.reply_message(token, message)
        return True

    elif "景點" in input_text:
        chose = TextSendMessage(
            text="哪邊的景點呢?",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="北部", text="@北")),
                    QuickReplyButton(action=MessageAction(label="中部", text="@中")),
                    QuickReplyButton(action=MessageAction(label="南部", text="@南")),
                    QuickReplyButton(action=MessageAction(label="東部", text="@東")),
                    QuickReplyButton(action=MessageAction(label="離島", text="@離島")),
                ]
            ),
        )
        line_bot_api.reply_message(token, chose)
        return isTravel_2(input_text, token)
    return False


def isTravel_2(input_text, token):
    if "@北" in input_text:
        chose = TextSendMessage(
            text="北部地區",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="基隆", text="基隆")),
                    QuickReplyButton(action=MessageAction(label="台北", text="台北")),
                    QuickReplyButton(action=MessageAction(label="新北", text="新北")),
                    QuickReplyButton(action=MessageAction(label="桃園", text="桃園")),
                    QuickReplyButton(action=MessageAction(label="新竹", text="新竹")),
                    QuickReplyButton(action=MessageAction(label="苗栗", text="苗栗")),
                ]
            ),
        )
        line_bot_api.reply_message(token, chose)
        return True

    if "@中" in input_text:
        chose = TextSendMessage(
            text="中部地區",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="台中", text="台中")),
                    QuickReplyButton(action=MessageAction(label="彰化", text="彰化")),
                    QuickReplyButton(action=MessageAction(label="南投", text="南投")),
                ]
            ),
        )
        line_bot_api.reply_message(token, chose)
        return True
    if "@南" in input_text:
        chose = TextSendMessage(
            text="南部地區",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="雲林", text="雲林")),
                    QuickReplyButton(action=MessageAction(label="嘉義", text="嘉義")),
                    QuickReplyButton(action=MessageAction(label="台南", text="台南")),
                    QuickReplyButton(action=MessageAction(label="高雄", text="高雄")),
                    QuickReplyButton(action=MessageAction(label="屏東", text="屏東")),
                ]
            ),
        )
        line_bot_api.reply_message(token, chose)
        return True
    if "@東" in input_text:
        chose = TextSendMessage(
            text="東部地區",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="台東", text="台東")),
                    QuickReplyButton(action=MessageAction(label="花蓮", text="花蓮")),
                    QuickReplyButton(action=MessageAction(label="宜蘭", text="宜蘭")),
                ]
            ),
        )
        line_bot_api.reply_message(token, chose)
        return True
    if "@離島" in input_text:
        chose = TextSendMessage(
            text="外島地區",
            quick_reply=QuickReply(
                items=[
                    QuickReplyButton(action=MessageAction(label="澎湖", text="澎湖")),
                    QuickReplyButton(action=MessageAction(label="金門", text="金門")),
                    QuickReplyButton(action=MessageAction(label="馬祖", text="連江")),
                ]
            ),
        )
        line_bot_api.reply_message(token, chose)
        return True


if __name__ == "__main__":
    app.run()
