import requests
import os
import datetime

# 讀取環境變數
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
MELON_COOKIE = os.environ.get("MELON_COOKIE")  # GitHub Secret

# MELON 參數
PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"

# API 回傳訊息對照中文
API_MESSAGE_MAP = {
    "구역별 잔여좌석 정보를 확인 할 수 없습니다.": "❌ 目前無可售座位區（尚未開賣或已售罄）"
}

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

    try:
        r = requests.post(url, params=params, data=form, headers=headers, timeout=15)
        r.raise_for_status()
        data = r.json()

        now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        lines = [f"🎫 *Melon 票務查詢*（{now}）"]

        code = data.get("code")
        if code != 0:
            msg = data.get("message", "無法取得座位資訊")
            # 翻譯成中文友善訊息
            msg_cn = API_MESSAGE_MAP.get(msg, f"❌ {msg}")
            lines.append(msg_cn)
        else:
            summary = data.get("summary", [])
            found = False
            for item in summary:
                cnt = item.get("realSeatCnt") or item.get("realSeatCntlk") or 0
                area = f'{item.get("floorName","")}-{item.get("areaName","")}'.strip("-")
                if cnt > 0:
                    lines.append(f"✅ {area}：{cnt} 張可售")
                    found = True
            if not found:
                lines.append("❌ 目前無可售座位區（尚未開賣或已售罄）")

        message = "\n".join(lines)
        print(message)
        send_telegram_message(message)

    except Exception as e:
        print(f"[錯誤] 查詢失敗: {e}")
        send_telegram_message(f"⚠️ MELON 查詢失敗: {e}")

if __name__ == "__main__":
    fetch_seat_info()
