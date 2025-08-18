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

import requests, os, re, datetime, json

PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"   # 注意：參數名是 scheduleNo（不是 scheduleId）
MELON_COOKIE = os.environ.get("MELON_COOKIE")  # 建議設為 GitHub Secret

def fetch_seat_info():
    url = "https://ticket.melon.com/tktapi/product/block/summary.json"
    params = {"v": "1"}  # 端點需要帶 v=1
    form = {
        "prodId": PRODUCT_ID,
        "scheduleNo": SCHEDULE_NO,
        # 下列欄位視場次而定，有就帶：perfDate, seatGradeNo, pocCode, corpCodeNo
        # "perfDate": "20250101",
        # "seatGradeNo": "",
        # "pocCode": "",
        # "corpCodeNo": ""
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://ticket.melon.com",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
        "Accept": "*/*",
    }
    if MELON_COOKIE:
        headers["Cookie"] = MELON_COOKIE

    r = requests.post(url, params=params, data=form, headers=headers, timeout=15)
    r.raise_for_status()

    # 這支回的是 JSONP，如：getBlockSummaryCountCallBack({...})
    m = re.search(r"getBlockSummaryCountCallBack\\((.*)\\)\\s*;?\\s*$", r.text)
    if not m:
        raise RuntimeError("Unexpected response (no JSONP callback)")

    payload = json.loads(m.group(1))
    summary = payload.get("summary", [])

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"🎫 *Melon 票務查詢*（{now}）"]
    found = False
    for item in summary:
        # 常見欄位：floorName/areaName/realSeatCnt(或 realSeatCntlk)
        cnt = item.get("realSeatCnt")
        if cnt is None:
            cnt = item.get("realSeatCntlk", 0)
        area = f'{item.get("floorName","")}-{item.get("areaName","")}'.strip("-")
        if (cnt or 0) > 0:
            lines.append(f"✅ {area}：{cnt} 張可售")
            found = True
    if not found:
        lines.append("❌ 目前無可售座位區")

    message = "\\n".join(lines)
    print(message)
    send_telegram_message(message)


if __name__ == "__main__":
    fetch_seat_info()
