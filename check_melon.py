import requests
import datetime
import re
import os

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
PRODUCT_ID = "211510"
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
    url = f"https://tkglobal.melon.com/performance/index.htm?prodId={PRODUCT_ID}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers, timeout=10)
    r.raise_for_status()
    
    # 解析公開區域資訊
    pattern = re.compile(r'"seatGradeName":"(.*?)","seatRemainCnt":(\d+)')
    matches = pattern.findall(r.text)
    
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"🎫 *Melon 票務查詢*（{now}）"]
    found = False
    
    for name, count in matches:
        if SEAT_SECTION_KEYWORD.upper() in name.upper():
            count = int(count)
            status = f"{count} 張可售" if count > 0 else "售罄"
            icon = "✅" if count > 0 else "❌"
            lines.append(f"{icon} {name}：{status}")
            found = True
    
    if not found:
        lines.append(f"❌ 找不到含「{SEAT_SECTION_KEYWORD}」的座位區或無票")
    
    message = "\n".join(lines)
    print(message)
    send_telegram_message(message)

if __name__ == "__main__":
    fetch_seat_info()
