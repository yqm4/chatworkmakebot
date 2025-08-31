from flask import Flask, request, jsonify
import requests
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

API_TOKEN = os.getenv("CHATWORK_API_TOKEN")
ROOM_ID = os.getenv("CHATWORK_ROOM_ID")
FONT_PATH = "NotoSansJP-Bold.otf"

def get_message(room_id, message_id):
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages/{message_id}"
    headers = {"X-ChatWorkToken": API_TOKEN}
    res = requests.get(url, headers=headers)
    return res.json()

def create_image(text, output_path="output.png"):
    img = Image.new("RGB", (800, 400), color=(0,0,0))
    draw = ImageDraw.Draw(img)
    font = ImageFont.truetype(FONT_PATH, 36)
    draw.text((50, 150), text, font=font, fill="white")
    img.save(output_path)
    return output_path

def send_image(room_id, filepath):
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/files"
    headers = {"X-ChatWorkToken": API_TOKEN}
    params = {"message": "画像を生成しました！"}
    files = {"file": open(filepath, "rb")}
    res = requests.post(url, headers=headers, params=params, files=files)
    return res.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json

    # webhookからメッセージ本文と返信先を取得
    body = data.get("webhook_event", {}).get("body", "")
    reply_id = data.get("webhook_event", {}).get("replyTo")

    # 本文に「めいく」が含まれる場合だけ実行
    if "めいく" in body and reply_id:
        msg_data = get_message(ROOM_ID, reply_id)
        text = msg_data.get("body", "")

        # 画像化
        img_path = create_image(text)

        # 投稿
        send_image(ROOM_ID, img_path)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
