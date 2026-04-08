import os
import time
import requests
from config import LINE_CHANNEL_TOKEN, LINE_USER_ID

# 預設關閉；確認 Alpaca 連線正常後，請將 NOTIFY_ENABLED 設為 "true" 再重啟
NOTIFY_ENABLED = os.environ.get("NOTIFY_ENABLED", "false").lower() == "true"
_ERROR_COOLDOWN_FILE = "/tmp/last_error_notify.txt"
_ERROR_COOLDOWN_SECS = 3600  # 同樣的錯誤 1 小時內只發一次

def push_line(message: str):
    if not NOTIFY_ENABLED:
        return
    requests.post(
        "https://api.line.me/v2/bot/message/push",
        headers={
            "Authorization": f"Bearer {LINE_CHANNEL_TOKEN}",
            "Content-Type": "application/json",
        },
        json={
            "to": LINE_USER_ID,
            "messages": [{
                "type": "flex",
                "altText": message[:100],
                "contents": _build_flex(message),
            }]
        }
    )

def _build_flex(text: str) -> dict:
    return {
        "type": "bubble",
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {"type": "text", "text": "📊 MNQ 交易通知",
                 "weight": "bold", "color": "#0F6E56", "size": "md"},
                {"type": "separator", "margin": "md"},
                {"type": "text", "text": text, "wrap": True,
                 "margin": "md", "size": "sm"},
            ]
        }
    }

def notify_entry(signal: str, entry: float, tp: float, sl: float):
    msg = (f"方向：{'做多 🟢' if signal == 'long' else '做空 🔴'}\n"
           f"進場：{entry:.2f}\n目標：{tp:.2f}（+{tp-entry:.0f}pts）\n"
           f"停損：{sl:.2f}（-{entry-sl:.0f}pts）")
    push_line(msg)

def notify_blocked(reason: str):
    push_line(f"⛔ 今日停止交易\n原因：{reason}")

def notify_error(err: str):
    # 防止相同錯誤在短時間內重複發送
    try:
        if os.path.exists(_ERROR_COOLDOWN_FILE):
            with open(_ERROR_COOLDOWN_FILE) as f:
                last_ts, last_err = f.read().split("\n", 1)
            if err.strip() == last_err.strip() and time.time() - float(last_ts) < _ERROR_COOLDOWN_SECS:
                return
    except Exception:
        pass
    try:
        with open(_ERROR_COOLDOWN_FILE, "w") as f:
            f.write(f"{time.time()}\n{err}")
    except Exception:
        pass
    push_line(f"❗ 系統異常\n{err}")
