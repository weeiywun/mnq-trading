import requests
import pandas as pd
from datetime import datetime, timedelta
import pytz
from config import *

class AlpacaClient:
    def __init__(self):
        self.headers = {
            "APCA-API-KEY-ID": ALPACA_API_KEY,
            "APCA-API-SECRET-KEY": ALPACA_SECRET_KEY,
        }
        self.base = ALPACA_BASE_URL
        self.data_base = "https://data.alpaca.markets"

    def get_orb_candle(self, symbol: str, orb_minutes: int = 5) -> dict | None:
        """取得今日開盤第一根 N 分鐘 K 棒"""
        tz = pytz.timezone(TIMEZONE)
        now = datetime.now(tz)
        market_open = now.replace(hour=9, minute=30, second=0, microsecond=0)
        orb_end = market_open + timedelta(minutes=orb_minutes)

        # 等 ORB 結束後才能取資料
        if now < orb_end:
            return None

        start = market_open.isoformat()
        end   = orb_end.isoformat()

        resp = requests.get(
            f"{self.data_base}/v1beta1/futures/bars",
            headers=self.headers,
            params={
                "symbols": symbol,
                "timeframe": f"{orb_minutes}Min",
                "start": start,
                "end": end,
                "limit": 1,
            }
        )
        data = resp.json()
        bars = data.get("bars", {}).get(symbol, [])
        if not bars:
            return None

        bar = bars[0]
        return {
            "high": bar["h"],
            "low":  bar["l"],
            "open": bar["o"],
            "close": bar["c"],
        }

    def get_latest_price(self, symbol: str) -> float:
        resp = requests.get(
            f"{self.data_base}/v1beta1/futures/quotes/latest",
            headers=self.headers,
            params={"symbols": symbol}
        )
        return resp.json()["quotes"][symbol]["ap"]  # ask price

    def place_bracket_order(self, symbol: str, side: str,
                             qty: int, take_profit: float, stop_loss: float) -> dict:
        """下單含 TP/SL 的 bracket order"""
        payload = {
            "symbol": symbol,
            "qty": str(qty),
            "side": side,
            "type": "market",
            "time_in_force": "day",
            "order_class": "bracket",
            "take_profit": {"limit_price": str(round(take_profit, 2))},
            "stop_loss":   {"stop_price":  str(round(stop_loss, 2))},
        }
        resp = requests.post(
            f"{self.base}/v2/orders",
            headers=self.headers,
            json=payload
        )
        return resp.json()

    def get_open_positions(self) -> list:
        resp = requests.get(f"{self.base}/v2/positions", headers=self.headers)
        return resp.json()

    def get_today_pnl(self) -> float:
        """取得今日已實現損益"""
        resp = requests.get(
            f"{self.base}/v2/account/portfolio/history",
            headers=self.headers,
            params={"period": "1D", "timeframe": "1Min"}
        )
        data = resp.json()
        profit_loss = data.get("profit_loss", [0])
        return profit_loss[-1] if profit_loss else 0.0
