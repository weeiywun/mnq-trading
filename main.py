import time, logging
from datetime import datetime
import pytz
import requests

from strategy import ORBStrategy
from risk_manager import RiskManager
from notifier import notify_entry, notify_blocked, notify_error
from alpaca_client import AlpacaClient
from config import GAS_WEBHOOK_URL, TIMEZONE, MNQ_SYMBOL

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

def log_to_sheets(payload: dict):
    try:
        requests.post(GAS_WEBHOOK_URL, json=payload, timeout=5)
    except Exception as e:
        logger.warning(f"Sheets 記錄失敗: {e}")

def wait_until_orb_done():
    """等到 9:35 AM ET（ORB 結束）"""
    tz = pytz.timezone(TIMEZONE)
    while True:
        now = datetime.now(tz)
        target = now.replace(hour=9, minute=35, second=5, microsecond=0)
        if now >= target:
            break
        wait_secs = (target - now).seconds
        logger.info(f"等待 ORB 結束，剩 {wait_secs}s")
        time.sleep(min(wait_secs, 30))

def main():
    tz = pytz.timezone(TIMEZONE)
    risk = RiskManager()
    strategy = ORBStrategy()

    # 1. 風控確認
    ok, reason = risk.can_trade()
    if not ok:
        notify_blocked(reason)
        logger.info(f"停止交易: {reason}")
        return

    # 2. 等 ORB 完成
    wait_until_orb_done()

    # 3. 設定 ORB 高低點
    if not strategy.setup_orb():
        notify_error("無法取得 ORB K 棒，請確認 Alpaca 數據連線")
        return

    # 4. 監控突破（最多等到 11:30 AM ET，超過不交易）
    logger.info("開始監控突破訊號...")
    while True:
        now = datetime.now(tz)
        if now.hour >= 11 and now.minute >= 30:
            logger.info("超過監控時間 11:30，今日結束")
            log_to_sheets({"date": str(now.date()), "result": "no_trade",
                           "symbol": MNQ_SYMBOL})
            return

        signal = strategy.check_signal()
        if signal == "long":
            try:
                result = strategy.execute_long()
                notify_entry("long", result["entry"], result["tp"], result["sl"])
                log_to_sheets({
                    "date": str(now.date()),
                    "symbol": MNQ_SYMBOL,
                    "side": "long",
                    "entry": result["entry"],
                    "tp": result["tp"],
                    "sl": result["sl"],
                    "orb_high": strategy.orb["high"],
                    "orb_low": strategy.orb["low"],
                    "result": "pending",
                    "order_id": result["order"].get("id", "")
                })
                # 此時 Alpaca bracket order 已掛好，可以結束腳本
                logger.info("訂單已送出，流程結束")
                return
            except Exception as e:
                notify_error(str(e))
                return

        time.sleep(10)  # 每 10 秒檢查一次

if __name__ == "__main__":
    main()
