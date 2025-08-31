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

def create_quote_image(text, output_path="/tmp/output.png"):
    # 画像サイズ
    width, height = 800, 400
    img = Image.new("RGB", (width, height), color=(0,0,0))
    draw = ImageDraw.Draw(img)

    # フォント（デフォルト）
    font = ImageFont.load_default()

    # テキスト自動改行
    lines = []
    max_chars_per_line = 40
    for i in range(0, len(text), max_chars_per_line):
        lines.append(text[i:i+max_chars_per_line])
    
    y = 50
    for line in lines:
        draw.text((50, y), line, font=font, fill="white")
        y += 40

    # 枠を描く
    draw.rectangle([40, 40, width-40, y], outline="white", width=2)

    img.save(output_path)
    print("画像保存完了:", output_path)
    return output_path

def send_image(room_id, filepath):
    if not os.path.exists(filepath):
        print("ファイルが存在しません:", filepath)
        return
    url = f"https://api.chatwork.com/v2/rooms/{room_id}/files"
    headers = {"X-ChatWorkToken": API_TOKEN}
    params = {"message": "引用画像を生成しました！"}
    with open(filepath, "rb") as f:
        res = requests.post(url, headers=headers, params=params, files={"file": f})
    print("送信結果:", res.status_code, res.text)
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

        img_path = create_quote_image(text)
        send_image(ROOM_ID, img_path)

    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


    return jsonify({"status": "ok"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

