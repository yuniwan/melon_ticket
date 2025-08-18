import requests
import os
import datetime
import re
import json

# 讀取環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MELON_COOKIE = os.environ.get("MELON_COOKIE")  # GitHub Secret

# MELON 參數
PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"   # 注意：要確認正確

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
    url = "https://ticket.melon.com/tktapi/product/block/summary.json"
    params = {"v": "1"}
    form = {
        "prodId": PRODUCT_ID,
        "scheduleNo": SCHEDULE_NO
    }
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://ticket.melon.com",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
        "Accept": "*/*",
    }
    if MELON_COOKIE:
        headers["Cookie"] = MELON_COOKIE

    print("🔹 POST URL:", url)
    print("🔹 Form data:", form)
    if MELON_COOKIE:
        print("🔹 Using MELON_COOKIE:", MELON_COOKIE[:20], "...")

    try:
        r = requests.post(url, params=params, data=form, headers=headers, timeout=15)
        print("🔹 Status:", r.status_code)
        print("🔹 Response sample:", r.text[:300])

        r.raise_for_status()

        m = re.search(r"getBlockSummaryCountCallBack\((.*)\)\s*;?\s*$", r.text)
        if not m:
            raise RuntimeError("Unexpected response (no JSONP callback)")

        payload = json.loads(m.group(1))
        summary = payload.get("summary", [])

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"🎫 *Melon 票務查詢*（{now}）"]
        found = False
        for item in summary:
            cnt = item.get("realSeatCnt") or item.get("realSeatCntlk", 0)
            area = f'{item.get("floorName","")}-{item.get("areaName","")}'.strip("-")
            if cnt > 0:
                lines.append(f"✅ {area}：{cnt} 張可售")
                found = True
        if not found:
            lines.append("❌ 目前無可售座位區")

        message = "\n".join(lines)
        print(message)
        send_telegram_message(message)

    except Exception as e:
        err_msg = f"[錯誤] 查詢失敗: {e}"
        print(err_msg)
        send_telegram_message(f"⚠️ MELON 查詢失敗: {e}")

if __name__ == "__main__":
    fetch_seat_info()
