from flask import Flask, request
import requests
import os
import schedule
import time
import threading

app = Flask(__name__)

VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")

# ======= HÀM GỬI TIN NHẮC ==========
def reply(recipient_id, text):
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    response = requests.post(url, params=params, headers=headers, json=data)
    print("Gửi tin nhắn, status:", response.status_code)
    print("Phản hồi từ Facebook:", response.text)

def send_reminders_from_txt():
    print("✅ Đang chạy send_reminders_from_txt()")
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line:
                print(f"👉 Đang gửi: {line}")
                reply(USER_ID, f"📌 Nhắc nè: {line}")
    except Exception as e:
        print(f"❌ Lỗi khi gửi nhắc: {e}")

def run_schedule():
    schedule.every(2).minutes.do(send_reminders_from_txt)
    while True:
        print("⏳ Đang chờ tới giờ gửi...")
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    threading.Thread(target=run_schedule).start()

# ========== WEBHOOK FB ============
@app.route('/', methods=['GET'])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge
    return 'Invalid verification token'

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print("Dữ liệu nhận được từ Facebook:", data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            messaging = entry.get("messaging", [])
            for message_event in messaging:
                sender_id = message_event["sender"]["id"]
                if "message" in message_event:
                    message = message_event["message"]
                    message_text = message.get("text")
                    if message_text:
                        reply(sender_id, f"Bot nhận được: {message_text}")
    return "ok", 200

# ========== CHẠY APP ============
if __name__ == "__main__":
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
