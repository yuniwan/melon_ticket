import requests
import os
import datetime
import json
import re

# 環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MELON_COOKIE = os.environ.get("MELON_COOKIE")

# MELON 參數
PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"  # 這是 scheduleNo 參數

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
    url = "https://tkglobal.melon.com/tktapi/product/seat/seatMapList.json"
    params = {
        "v": "1",
        "callback": "getSeatListCallBack",
        "prodId": PRODUCT_ID,
        "scheduleNo": SCHEDULE_NO
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
    }
    if MELON_COOKIE:
        headers["Cookie"] = MELON_COOKIE

    try:
        r = requests.get(url, params=params, headers=headers, timeout=15)
        r.raise_for_status()
        # 解析 JSONP
        m = re.search(r"getSeatListCallBack\((.*)\)", r.text)
        if not m:
            raise RuntimeError("無法取得座位資料或 Cookie 無效")

        data = json.loads(m.group(1))
        seats = data.get("seatList", [])
        available_seats = []
        for s in seats:
            count = s.get("realSeatCnt", 0) or s.get("realSeatCntlk", 0)
            area = f"{s.get('floorName','')}-{s.get('areaName','')}".strip("-")
            if count > 0:
                available_seats.append(f"{area}：{count} 張可售")

        if available_seats:
            now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"🎫 *Melon 票務查詢*（{now}）\n" + "\n".join(f"✅ {a}" for a in available_seats)
            print(message)
            send_telegram_message(message)
        else:
            print("❌ 目前無可售座位，不發送通知")

    except Exception as e:
        error_msg = f"⚠️ 查票失敗: {e}"
        print(error_msg)
        send_telegram_message(error_msg)

if __name__ == "__main__":
    fetch_seat_info()
