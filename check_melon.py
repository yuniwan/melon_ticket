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
    except Excep
