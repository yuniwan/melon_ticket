import requests
import os
import datetime
import json

# 環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MELON_COOKIE = os.environ.get("MELON_COOKIE")

# Melon 參數
PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"

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

def is_cookie_valid():
    """檢查 Cookie 是否有效"""
    url = f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": MELON_COOKIE
    }
    try:
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return False
        # 如果頁面內容包含 "performance" 或其他票務資訊，視為有效
        if "performance" in r.text or "block" in r.text:
            return True
        return False
    except:
        return False

def fetch_seat_info():
    url = "https://ticket.melon.com/tktapi/product/block/summary.json"
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
        "Cookie": MELON_COOKIE
    }
    form = {
        "prodId": PRODUCT_ID,
        "scheduleNo": SCHEDULE_NO
    }

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"🎫 *Melon 票務查詢*（{now}）"]

    # 先檢查 Cookie
    if not is_cookie_valid():
        lines.append("❌ Cookie 無效或無法訪問座位資料")
        message = "\n".join(lines)
        print(message)
        send_telegram_message(message)
        return

    try:
        r = requests.post(url, headers=headers, data=form, timeout=15)
        r.raise_for_status()
        data = r.json()

        if data.get("code") == "9990":
            lines.append("❌ Cookie 無效或無法訪問座位資料")
        else:
            summary = data.get("summary", [])
            found = False
            for item in summary:
                cnt = item.get("realSeatCnt") or item.get("realSeatCntlk", 0)
                area = f'{item.get("floorName","")}-{item.get("areaName","")}'.strip("-")
                if cnt > 0:
                    lines.append(f"✅ {area}：{cnt} 張可售")
                    found = True
            if not found:
                lines.append("❌ 目前無可售座位區")
    except Exception as e:
        lines.append(f"⚠️ 查票失敗: {e}")

    message = "\n".join(lines)
    print(message)
    send_telegram_message(message)

if __name__ == "__main__":
    fetch_seat_info()
