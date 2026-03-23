import os
import io
import re
import json
import numpy as np
import cv2
import pytesseract
import gspread
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, ImageMessage, TextSendMessage
from PIL import Image
from oauth2client.service_account import ServiceAccountCredentials

app = Flask(__name__)

# --- Configuration ---
# แนะนำให้ตั้งค่าเหล่านี้ใน Render Dashboard (Environment Variables)
CHANNEL_ACCESS_TOKEN = os.getenv('CHANNEL_ACCESS_TOKEN')
CHANNEL_SECRET = os.getenv('CHANNEL_SECRET')

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(CHANNEL_SECRET)

# --- Google Sheets Setup ---
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    # วิธีที่ปลอดภัย: เก็บเนื้อหา JSON ใน Env Var ชื่อ GOOGLE_APPLICATION_CREDENTIALS_JSON
    creds_json = os.getenv('GOOGLE_APPLICATION_CREDENTIALS_JSON')
    if creds_json:
        info = json.loads(creds_json)
        creds = ServiceAccountCredentials.from_json_keyfile_dict(info, scope)
    else:
        # กรณีรันเทสในเครื่องที่มีไฟล์
        creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
    return gspread.authorize(creds)

# --- Routes ---
@app.route("/")
def home():
    return "Bot is running!"

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers.get('X-Line-Signature')
    body = request.get_data(as_text=True)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK'

@handler.add(MessageEvent, message=ImageMessage)
def handle_image(event):
    try:
        # 1. ดึงรูปภาพ
        message_content = line_bot_api.get_message_content(event.message.id)
        image_bytes = io.BytesIO(message_content.content)
        image = Image.open(image_bytes)

        # 2. Image Processing ด้วย OpenCV
        img_np = np.frombuffer(image_bytes.getvalue(), np.uint8)
        img = cv2.imdecode(img_np, cv2.IMREAD_GRAYSCALE)
        
        # เพิ่มความชัด (Thresholding)
        _, img_bin = cv2.threshold(img, 150, 255, cv2.THRESH_BINARY)

        # 3. OCR (บน Render ไม่ต้องกำหนด tesseract_cmd)
        # ระบุ lang='eng+tha' เพื่อให้อ่านภาษาไทยได้ด้วย
        text = pytesseract.image_to_string(img_bin, lang='eng+tha')

        # 4. หาเลข 7 หลัก
        numbers = re.findall(r'\b\d{7}\b', text)

        if numbers:
            # บันทึกลง Google Sheets
            client = get_gspread_client()
            sheet = client.open("LINE OCR DATA").sheet1
            
            for n in numbers:
                sheet.append_row([n])

            reply_text = "พบตัวเลข 7 หลัก:\n" + "\n".join(numbers)
        else:
            reply_text = "ไม่พบตัวเลข 7 หลักในรูปภาพ"

        line_bot_api.reply_message(event.reply_token, TextSendMessage(text=reply_text))

    except Exception as e:
        print(f"Error: {e}")
        line_bot_api.reply_message(event.reply_token, TextSendMessage(text="เกิดข้อผิดพลาดในการประมวลผล"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
