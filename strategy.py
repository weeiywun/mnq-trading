from alpaca_client import AlpacaClient
from config import SYMBOL, ORB_MINUTES, SHARE_QTY
import logging

logger = logging.getLogger(__name__)

class ORBStrategy:
    """Opening Range Breakout for QQQ"""

    def __init__(self):
        self.client      = AlpacaClient()
        self.orb         = None
        self.trade_placed = False

    def setup_orb(self) -> bool:
        candle = self.client.get_orb_candle(SYMBOL, ORB_MINUTES)
        if candle:
            self.orb = candle
            orb_range = round(candle["high"] - candle["low"], 2)
            logger.info(f"ORB 完成 | High: {candle['high']} | Low: {candle['low']} | Range: {orb_range}")
            return True
        return False

    def check_signal(self) -> str | None:
        if not self.orb or self.trade_placed:
            return None

        price = self.client.get_latest_price(SYMBOL)
        logger.info(f"現價: {price} | ORB High: {self.orb['high']}")

        if price > self.orb["high"]:
            return "long"

        return None

    def execute_long(self) -> dict:
        entry     = self.client.get_latest_price(SYMBOL)
        orb_range = self.orb["high"] - self.orb["low"]

        # TP/SL 依 ORB range 計算（1:1）
        tp = round(entry + orb_range, 2)
        sl = round(entry - orb_range, 2)

        logger.info(f"進場 LONG | Entry≈{entry} | TP={tp} | SL={sl} | Range={orb_range:.2f}")

        result = self.client.place_bracket_order(
            symbol=SYMBOL,
            side="buy",
            qty=SHARE_QTY,
            take_profit=tp,
            stop_loss=sl,
        )

        self.trade_placed = True
        return {
            "entry":     entry,
            "tp":        tp,
            "sl":        sl,
            "orb_range": round(orb_range, 2),
            "order":     result,
        }
