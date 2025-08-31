from flask import Flask, request, jsonify
import requests
from PIL import Image, ImageDraw, ImageFont
import os

app = Flask(__name__)

API_TOKEN = os.getenv("CHATWORK_API_TOKEN")
ROOM_ID = os.getenv("CHATWORK_ROOM_ID")

def get_message(room_id, message_id):
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/messages/{message_id}"
    headers = {"X-ChatWorkToken": API_TOKEN}
    res = requests.get(url, headers=headers)
    return res.json()

def create_image(text, output_path="/tmp/output.png"):
    # 画像作成
    img = Image.new("RGB", (800, 400), color=(0,0,0))
    draw = ImageDraw.Draw(img)
    try:
        # デフォルトフォント使用（日本語は□になる場合あり）
        font = ImageFont.load_default()
    except:
        font = None
    draw.text((50, 150), text, font=font, fill="white")
    img.save(output_path)
    print("画像保存完了:", output_path)
    return output_path

def send_image(room_id, filepath):
    if not os.path.exists(filepath):
        print("ファイルが存在しません:", filepath)
        return
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/files"
    headers = {"X-ChatWorkToken": API_TOKEN}
    params = {"message": "画像を生成しました！"}
    with open(filepath, "rb") as f:
        res = requests.post(url, headers=headers, params=params, files={"file": f})
    print("Chatwork送信結果:", res.status_code, res.text)
    return res.json()

@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    body = data.get("webhook_event", {}).get("body", "")
    reply_id = data.get("webhook_event", {}).get("replyTo")

    print("Webhook受信:", body, "返信ID:", reply_id)

    if "めいく" in body and reply_id:
        msg_data = get_message(ROOM_ID, reply_id)
        text = msg_data.get("body", "")
        print("返信元メッセージ:", text)

        img_path = create_image(text)
        send_image(ROOM_ID, img_path)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

