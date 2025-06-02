from flask import Flask, request
import requests

app = Flask(__name__)

VERIFY_TOKEN = "duyytan123"
PAGE_ACCESS_TOKEN = "EAAKldfttpFUBOxomTE3qmIAULmIZCkx6Otnr0s9tR7b6rOdZBjRAYurt1vuFerGPhqezrM4UbyrZCp98EpAkz4hzyvRjNNywwalZAU1hggZAi4DXZCtoRyEdqKQnEKB2ZAYZCUiJNYHGs1nm8NCq3clZASg9kVuH3ndQhiCOCs7L73IAFEM6hfr2eQ1iXReWeDx6OFRGzHAZDZD"

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
                        print(f"Đang phản hồi lại: {message_text}")
                        reply(sender_id, f"Bot nhận được: {message_text}")
    return "ok", 200

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

if __name__ == '__main__':
    app.run(port=5000)
