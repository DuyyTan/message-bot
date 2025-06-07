from flask import Flask, request
import requests
import schedule
import time
import threading
import os

app = Flask(__name__)

VERIFY_TOKEN = "duyytan123"
PAGE_ACCESS_TOKEN = "EAAKldfttpFUBO2q8iL8gmOyzNaqi7qq4bPXHumzwckf33gYDUD22XyFeLxYOmkUbs9b9mQx0CectodFoqlFlyFQtZChZAneEkAthNW47CsubZADSuH3Jt6ieLmH8gAb4dl6xqDmqffldk6ttj5v7gPbLlu1ZAWB9r2bj6Jd0IaqJYjltVDDWujxRpsCsWTVWZBvRJ"
USER_ID = 24101809476121217

def send_reminders_from_txt():
    print("📤 Bắt đầu gửi tin nhắn nhắc nhở...")
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()
            for line in lines:
                message = line.strip()
                if message:
                    send_message(USER_ID, message)
    except Exception as e:
        print("Lỗi khi gửi nhắc:", e)

def send_message(recipient_id, message_text):
    url = 'https://graph.facebook.com/v18.0/me/messages'
    headers = {"Content-Type": "application/json"}
    params = {"access_token": PAGE_ACCESS_TOKEN}
    data = {
        "recipient": {"id": recipient_id},
        "message": {"text": message_text}
    }
    response = requests.post(url, headers=headers, params=params, json=data)
    print("Đã gửi:", message_text, "| Phản hồi:", response.text)

@app.route('/', methods=['GET', 'HEAD'])
def verify():
    if request.method == 'HEAD':
        return "✅ OK", 200

    token_sent = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")
    if token_sent == VERIFY_TOKEN:
        return challenge or ''
    return 'Sai verify token'

@app.route('/', methods=['POST'])
def webhook():
    data = request.get_json()
    print("🟢 Đã nhận sự kiện:", data)

    if data.get("object") == "page":
        for entry in data.get("entry", []):
            for messaging_event in entry.get("messaging", []):
                if messaging_event.get("message"):
                    sender_id = messaging_event["sender"]["id"]
                    message_text = messaging_event["message"].get("text", "")
                    reply = f"Đã nhận được: {message_text}"
                    send_message(sender_id, reply)
    return "ok", 200

@app.route("/ping")
def ping():
    return "", 204
    
def run_schedule():
    # Cập nhật lại lịch 9h sáng và 6h tối
    schedule.every().day.at("08:30").do(send_reminders_from_txt)
    schedule.every().day.at("14:00").do(send_reminders_from_txt)
    schedule.every().day.at("18:00").do(send_reminders_from_txt)
    while True:
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    print("🚀 Đã khởi động scheduler!")
    thread = threading.Thread(target=run_schedule, daemon=True)
    thread.start()

if __name__ == '__main__':
    start_scheduler()
    app.run(host='0.0.0.0', port=int(os.environ.get("PORT", 5000)))
