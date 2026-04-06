from alpaca_client import AlpacaClient
from config import *
import json, os
import logging

logger = logging.getLogger(__name__)
STATE_FILE = "/tmp/risk_state.json"

class RiskManager:
    def __init__(self):
        self.client = AlpacaClient()
        self.state = self._load_state()

    def _load_state(self) -> dict:
        if os.path.exists(STATE_FILE):
            with open(STATE_FILE) as f:
                return json.load(f)
        return {"consecutive_loss": 0, "today_traded": False}

    def _save_state(self):
        with open(STATE_FILE, "w") as f:
            json.dump(self.state, f)

    def can_trade(self) -> tuple[bool, str]:
        """回傳 (可否交易, 原因)"""
        # 每日只交易一次
        if TRADE_ONCE_PER_DAY and self.state.get("today_traded"):
            return False, "今日已交易過"

        # 連敗熔斷
        if self.state["consecutive_loss"] >= MAX_CONSECUTIVE_LOSS:
            return False, f"連敗 {self.state['consecutive_loss']} 次，熔斷暫停"

        # 每日最大虧損
        today_pnl = self.client.get_today_pnl()
        if today_pnl <= -MAX_DAILY_LOSS_USD:
            return False, f"今日虧損 ${abs(today_pnl):.0f}，達上限"

        return True, "OK"

    def record_result(self, is_win: bool):
        if is_win:
            self.state["consecutive_loss"] = 0
        else:
            self.state["consecutive_loss"] += 1
        self.state["today_traded"] = True
        self._save_state()

    def reset_daily(self):
        """每日開盤前重置（GitHub Actions 排程呼叫）"""
        self.state["today_traded"] = False
        self._save_state()
