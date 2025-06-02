import schedule
import time
import threading

from app import reply

USER_ID = "24101809476121217"

def send_reminders_from_txt():
    try:
        with open("reminders.txt", "r", encoding="utf-8") as f:
            lines = f.readlines()

        for line in lines:
            line = line.strip()
            if line:
                reply(USER_ID, f"📌 Nhắc nè: {line}")
    except Exception as e:
        print(f"Lỗi khi gửi nhắc: {e}")

def run_schedule():
    schedule.every().day.at("09:00").do(send_reminders_from_txt)
    schedule.every().day.at("22:25").do(send_reminders_from_txt)

    while True:
        schedule.run_pending()
        time.sleep(60)

def start_scheduler():
    threading.Thread(target=run_schedule).start()