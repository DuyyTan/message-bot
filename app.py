from flask import Flask, request
import requests
import os
import schedule
import time
import threading

app = Flask(__name__)

# Lấy token và ID từ biến môi trường
VERIFY_TOKEN = os.environ.get("VERIFY_TOKEN")
PAGE_ACCESS_TOKEN = os.environ.get("PAGE_ACCESS_TOKEN")
USER_ID = os.environ.get("USER_ID")

# ======= HÀM GỬI TIN NHẮC ==========
def reply(recipient_id, text):
    if not PAGE_ACCESS_TOKEN:
        print("❌ Thiếu PAGE_ACCESS_TOKEN")
        return
    url = "https://graph.facebook.com/v17.0/me/messages"
    params = {"access_token": PAGE_ACCESS_TOKEN}
    headers = {"Content-Type": "application/json"}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": text}
    }
    try:
        response = requests.post(url, params=params, headers=headers, json=data)
        print("✅ Gửi tin nhắn, status:", response.status_code)
        print("📨 Phản hồi từ Facebook:", response.text)
    except Exception as e:
        print("❌ Lỗi khi gửi request:", e)

def send_reminders_from_txt():
    print("🔁 Đang chạy send_reminders_from_txt()")
    if not USER_ID:
        print("❌ USER_ID chưa được set.")
        return
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line:
                print(f"📌 Đang gửi: {line}")
                reply(USER_ID, f"📌 Nhắc nè: {line}")
    except Exception as e:
        print(f"❌ Lỗi khi đọc/gửi từ reminders.txt: {e}")

# ====== LỊCH GỬI NHẮC ======
def run_schedule():
    schedule.every(2).minutes.do(send_reminders_from_txt)
    while True:
        print("⏳ Đợi tới lịch gửi...")
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    thread = threading.Thread(target=run_schedule)
    thread.daemon = True
    thread.start()

# ========== FB WEBHOOK ============
@app.route('/', methods=['GET'])
def verify():
    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        print("✅ Xác minh webhook thành công.")
        return challenge
    print("❌ Sai VERIFY_TOKEN")
    return 'Invalid verification token', 403

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print("📩 Dữ liệu từ Facebook:", data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            messaging = entry.get("messaging", [])
            for message_event in messaging:
                sender_id = message_event["sender"]["id"]
                if "message" in message_event:
                    message_text = message_event["message"].get("text")
                    if message_text:
                        reply(sender_id, f"🤖 Bot nhận được: {message_text}")
    return "ok", 200

# ========== CHẠY APP ============
if __name__ == "__main__":
    print("🚀 Đang khởi chạy bot ở môi trường:", os.environ.get("FLASK_ENV", "production"))
    start_scheduler()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
