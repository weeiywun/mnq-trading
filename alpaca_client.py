import requests
from datetime import datetime, timedelta
import pytz
from config import ALPACA_API_KEY, ALPACA_SECRET_KEY, ALPACA_BASE_URL, TIMEZONE

class AlpacaClient:
    def __init__(self):
        self.headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
        }
        self.base      = ALPACA_BASE_URL
        self.data_base = "https://data.alpaca.markets"

    def get_orb_candle(self, symbol: str, orb_minutes: int = 5) -> dict | None:
        """取得今日開盤第一根 N 分鐘 K 棒"""
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        orb_end     = market_open + timedelta(minutes=orb_minutes)

        if now < orb_end:
            return None

        resp = requests.get(
            f"{self.data_base}/v2/stocks/{symbol}/bars",
            headers=self.headers,
            params={
                "timeframe":  f"{orb_minutes}Min",
                "start":      market_open.isoformat(),
                "end":        orb_end.isoformat(),
                "limit":      1,
                "feed":       "iex",     # 免費 feed
                "adjustment": "raw",
            }
        )
        bars = resp.json().get("bars", [])
        if not bars:
            return None

        bar = bars[0]
        return {
            "high":  bar["h"],
            "low":   bar["l"],
            "open":  bar["o"],
            "close": bar["c"],
        }

    def get_latest_price(self, symbol: str) -> float:
        """取得最新成交價"""
        resp = requests.get(
            f"{self.data_base}/v2/stocks/{symbol}/trades/latest",
            headers=self.headers,
            params={"feed": "iex"}
        )
        return resp.json()["trade"]["p"]

    def place_bracket_order(self, symbol: str, side: str,
                             qty: int, take_profit: float, stop_loss: float) -> dict:
        """下 bracket order（含 TP/SL）"""
        payload = {
            "symbol":        symbol,
            "qty":           str(qty),
            "side":          side,
            "type":          "market",
            "time_in_force": "day",
            "order_class":   "bracket",
            "take_profit":   {"limit_price": str(round(take_profit, 2))},
            "stop_loss":     {"stop_price":  str(round(stop_loss, 2))},
        }
        resp = requests.post(
            f"{self.base}/v2/orders",
            headers=self.headers,
            json=payload
        )
        return resp.json()

    def get_today_pnl(self) -> float:
        """取得今日損益"""
        resp = requests.get(
            f"{self.base}/v2/account/portfolio/history",
            headers=self.headers,
            params={"period": "1D", "timeframe": "1Min"}
        )
        data = resp.json()
        pl = data.get("profit_loss", [0])
        return pl[-1] if pl else 0.0
