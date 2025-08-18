import requests
import os
import datetime
import json
import re

# 環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MELON_COOKIE = os.environ.get("MELON_COOKIE")  # 建議設為 GitHub Secret

PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"

# 送 Telegram
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

# 查票
def fetch_seat_info():
    url = "https://tkglobal.melon.com/tktapi/product/seat/seatMapList.json"
    params = {
        "v": "1",
        "callback": "getSeatListCallBack",
        "prodId": PRODUCT_ID,
        "scheduleNo": SCHEDULE_NO
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
        "Origin": "https://ticket.melon.com",
        "Accept": "*/*",
        "Cookie": MELON_COOKIE
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code == 403:
            raise RuntimeError("❌ Cookie 無效或無法訪問座位資料 (403 Forbidden)")
        r.raise_for_status()

        # 解析 JSONP
        m = re.search(r"getSeatListCallBack\((.*)\)\s*;?\s*$", r.text)
        if not m:
            raise RuntimeError("❌ 查票失敗：回傳非預期格式或無票")
        payload = json.loads(m.group(1))

        # 解析座位資訊
        seats = payload.get("seatMapList", [])
        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"🎫 *Melon 票務查詢*（{now}）"]
        found = False
        for block in seats:
            for seat in block.get("seatList", []):
                if seat.get("status") == "N":  # N 表示可售
                    lines.append(f"✅ {block.get('sectionName','')}-{seat.get('seatName','')} 可售")
                    found = True

        if found:
            message = "\n".join(lines)
            print(message)
            send_telegram_message(message)
        else:
            print("❌ 目前無可售座位")
    except Exception as e:
        print(f"[錯誤] {e}")

if __name__ == "__main__":
    fetch_seat_info()
