import requests, os, re, datetime, json

PRODUCT_ID = "211510"
SCHEDULE_NO = "100001"
MELON_COOKIE = os.environ.get("MELON_COOKIE")  # GitHub Secret

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

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
    url = "https://ticket.melon.com/tktapi/product/block/summary.json"
    params = {"v": "1"}
    form = {"prodId": PRODUCT_ID, "scheduleNo": SCHEDULE_NO}
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Origin": "https://ticket.melon.com",
        "Referer": f"https://ticket.melon.com/performance/index.htm?prodId={PRODUCT_ID}",
    }
    if MELON_COOKIE:
        headers["Cookie"] = MELON_COOKIE

    try:
        r = requests.post(url, params=params, data=form, headers=headers, timeout=15)
        r.raise_for_status()
    except requests.HTTPError as e:
        send_telegram_message(f"⚠️ MELON Cookie 無效或無法訪問 ({e})")
        return
    except Exception as e:
        send_telegram_message(f"⚠️ 查詢失敗 ({e})")
        return

    # 檢查是否為 JSONP 回傳
    m = re.search(r"getBlockSummaryCountCallBack\((.*)\)\s*;?\s*$", r.text)
    if not m:
        send_telegram_message("⚠️ MELON Cookie 無效或查票資料無法取得")
        return

    payload = json.loads(m.group(1))
    summary = payload.get("summary", [])

    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [f"🎫 *Melon 票務查詢*（{now}）"]

    found = False
    for item in summary:
        cnt = item.get("realSeatCnt") or item.get("realSeatCntlk", 0)
        area = f'{item.get("floorName","")}-{item.get("areaName","")}'
