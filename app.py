from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage, TextSendMessage

# ❌ ปิด pytesseract ไปก่อน
# import pytesseract

import cv2
import numpy as np
import io
import re
from PIL import Image

# import gspread
# from oauth2client.service_account import ServiceAccountCredentials

# LINE TOKEN
CHANNEL_ACCESS_TOKEN = "wL3e0IKFdezOLn9xLZEV9Lf1QY4KwoQPOx8yiWD6OKgoSqmZyXfgwogqiKXm8Mw2rta7F3dCYwLs9dBfUv9YRrDUb5nPW57+YuEcsZJJ/FKAy4uVrUeXW303tHtQINHpV+ASj01cymjtpBKw2aFlmQdB04t89/1O/w1cDnyilFU="
CHANNEL_SECRET = "d37d882dab0e0059f4fc23473fe8bd7d"

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

app = Flask(__name__)

# Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/drive"
]

# Google Sheets ปิดชั่วคราว
sheet = None


@app.route("/")
def home():
    return "I'm alive"


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    handler.handle(body, signature)

    return 'OK'


@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):

    message_content = line_bot_api.get_message_content(event.message.id)

    image_bytes = b''
    for chunk in message_content.iter_content():
        image_bytes += chunk

    image = Image.open(io.BytesIO(image_bytes))

    img = cv2.cvtColor(np.array(image), cv2.COLOR_BGR2GRAY)

    # ปรับภาพ
    img = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)[1]

    # ❌ ปิด OCR ชั่วคราว
    # text = pytesseract.image_to_string(img)

    text = "1234567 7654321"  # mock test

    numbers = re.findall(r'\b\d{7}\b', text)

    if numbers:
        for n in numbers:
            # sheet.append_row([n])

        reply_text = "\n".join(numbers)

        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=reply_text)
        )
    else:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text="ไม่พบตัวเลข")
        )


if __name__ == "__main__":
    app.run()
