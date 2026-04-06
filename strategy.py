from alpaca_client import AlpacaClient
from config import *
import logging

logger = logging.getLogger(__name__)

class ORBStrategy:
    """Opening Range Breakout for MNQ"""

    def __init__(self):
        self.client = AlpacaClient()
        self.orb = None          # {"high": x, "low": y}
        self.trade_placed = False

    def setup_orb(self) -> bool:
        """取得 ORB 高低點，成功回傳 True"""
        candle = self.client.get_orb_candle(MNQ_SYMBOL, ORB_MINUTES)
        if candle:
            self.orb = candle
            logger.info(f"ORB 設定完成 | High: {candle['high']} | Low: {candle['low']}")
            return True
        return False

    def check_signal(self) -> str | None:
        """
        回傳 'long' / None
        目前策略只做突破高點做多
        """
        if not self.orb or self.trade_placed:
            return None

        price = self.client.get_latest_price(MNQ_SYMBOL)
        logger.info(f"Current price: {price} | ORB High: {self.orb['high']}")

        if price > self.orb["high"]:
            return "long"

        return None

    def execute_long(self) -> dict:
        """進場做多，帶 TP/SL"""
        entry = self.client.get_latest_price(MNQ_SYMBOL)
        tp = entry + TARGET_POINTS
        sl = entry - STOP_POINTS

        logger.info(f"進場 LONG | Entry≈{entry} | TP={tp} | SL={sl}")
        result = self.client.place_bracket_order(
            symbol=MNQ_SYMBOL,
            side="buy",
            qty=CONTRACT_QTY,
            take_profit=tp,
            stop_loss=sl,
        )
        self.trade_placed = True
        return {
            "entry": entry,
            "tp": tp,
            "sl": sl,
            "order": result,
        }
