import requests
from config import LINE_CHANNEL_TOKEN, LINE_USER_ID

def push_line(message: str):
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
    push_line(f"❗ 系統異常\n{err}")
