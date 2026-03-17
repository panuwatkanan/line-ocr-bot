from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.models import MessageEvent, ImageMessage, TextSendMessage

app = Flask(__name__)

# 🔐 ใช้ ENV (สำคัญ)
import os
CHANNEL_ACCESS_TOKEN = os.getenv("wL3e0IKFdezOLn9xLZEV9Lf1QY4KwoQPOx8yiWD6OKgoSqmZyXfgwogqiKXm8Mw2rta7F3dCYwLs9dBfUv9YRrDUb5nPW57+YuEcsZJJ/FKAy4uVrUeXW303tHtQINHpV+ASj01cymjtpBKw2aFlmQdB04t89/1O/w1cDnyilFU=")
CHANNEL_SECRET = os.getenv("d37d882dab0e0059f4fc23473fe8bd7d")

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

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
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text="รับรูปแล้ว 📸")
    )

if __name__ == "__main__":
    app.run()
