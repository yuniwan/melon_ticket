import requests
import os
import datetime

# 讀取環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

# MELON 參數
PRODUCT_ID = "211510"
SCHEDULE_ID = "100001"
SEAT_SECTION_KEYWORD = "S"

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ 缺少 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[傳送錯誤] {e}")

def fetch_seat_info():
    URL = f"https://ticket.melon.com/performance/api/performanceInfo.json?prodId={PRODUCT_ID}&scheduleId={SCHEDULE_ID}"
    HEADERS = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://tkglobal.melon.com/performance/index.htm?prodId={PRODUCT_ID}"
    }

    try:
        r = requests.get(URL, headers=HEADERS)
        r.raise_for_status()
        data = r.json()

        seats = data.get("seatGradeList", [])
        available = []

        for seat in seats:
            name = seat.get("seatGradeName", "")
            count = seat.get("seatRemainCnt", 0)
            if SEAT_SECTION_KEYWORD.upper() in name.upper():
                available.append((name, count))

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = [f"🎫 *Melon 票務查詢*（{now}）"]

        if not available:
            message.append(f"找不到含「{SEAT_SECTION_KEYWORD}」的座位區")
        else:
            for name, count in available:
                status = f"{count} 張票" if count > 0 else "售罄"
                icon = "✅" if count > 0 else "❌"
                message.append(f"{icon} {name}：{status}")

        full_message = "\n".join(message)
        print(full_message)
        send_telegram_message(full_message)

    except Exception as e:
        print(f"[錯誤] 查詢失敗: {e}")
        send_telegram_message(f"⚠️ MELON 查詢失敗: {e}")

if __name__ == "__main__":
    fetch_seat_info()
