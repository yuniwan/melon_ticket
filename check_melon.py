import requests
import os
import datetime
import json

# 環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MELON_COOKIE = os.environ.get("MELON_COOKIE")

PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"  # 注意：Melon API 使用 scheduleNo

def send_telegram_message(message):
    if not BOT_TOKEN or not CHAT_ID:
        print("⚠️ 缺少 TELEGRAM_BOT_TOKEN 或 TELEGRAM_CHAT_ID")
        return
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try:
        requests.post(url, data=payload, timeout=10)
    except Exception as e:
        print(f"[傳送錯誤] {e}")

def fetch_seat_info():
    url = "https://tkglobal.melon.com/tktapi/product/seat/seatMapList.json?v=1"
    params = {
        "callback": "getSeatListCallBack",
        "prodId": PRODUCT_ID,
        "scheduleNo": SCHEDULE_NO
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/139.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "zh-TW,zh;q=0.9,en;q=0.8",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
        "Origin": "https://ticket.melon.com",
        "Connection": "keep-alive",
        "Cookie": MELON_COOKIE
    }

    try:
        r = requests.get(url, headers=headers, params=params, timeout=15)
        if r.status_code != 200:
            raise requests.HTTPError(f"{r.status_code} {r.reason}")
    except Exception as e:
        send_telegram_message(f"❌ 查票失敗: {e}")
        return

    text = r.text.strip()
    # 解析 JSONP
    if text.startswith("getSeatListCallBack(") and text.endswith(")"):
        json_str = text[len("getSeatListCallBack("):-1]
        data = json.loads(json_str)
    else:
        send_telegram_message("❌ Cookie 無效或無法訪問座位資料")
        return

    # 解析可售座位
    seats = []
    for floor in data.get("floorList", []):
        for area in floor.get("areaList", []):
            cnt = area.get("realSeatCnt", 0)
            if cnt > 0:
                seats.append(f"{floor.get('floorName','')}-{area.get('areaName','')}：{cnt}張可售")

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if seats:
        message = f"🎫 *Melon 票務查詢*（{now}）\n" + "\n".join(["✅ " + s for s in seats])
    else:
        message = f"🎫 *Melon 票務查詢*（{now}）\n❌ 目前無可售座位區"

    print(message)
    send_telegram_message(message)

if __name__ == "__main__":
    fetch_seat_info()
