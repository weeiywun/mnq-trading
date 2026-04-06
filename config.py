# =============================================
# 所有參數集中管理，敏感資訊用環境變數
# =============================================
import os

# Alpaca Paper Trading
ALPACA_API_KEY    = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]
ALPACA_BASE_URL   = "https://paper-api.alpaca.markets"

# 合約設定（每次換月需更新，格式：MNQ + 月份代碼 + 年）
# H=3月 M=6月 U=9月 Z=12月
MNQ_SYMBOL = os.environ.get("MNQ_SYMBOL", "MNQM25")  # 2025 June

# 策略參數
ORB_MINUTES     = 5        # 開盤區間分鐘數
TARGET_POINTS   = 100      # 目標點數
STOP_POINTS     = 100      # 停損點數（1:1）
CONTRACT_QTY    = 1        # 口數

# 風控參數
MAX_DAILY_LOSS_USD   = 500   # 每日最大虧損（美元）
MAX_CONSECUTIVE_LOSS = 3     # 連敗熔斷次數
TRADE_ONCE_PER_DAY   = True  # 每日只交易一次

# LINE Bot
LINE_CHANNEL_TOKEN = os.environ["LINE_CHANNEL_TOKEN"]
LINE_USER_ID       = os.environ["LINE_USER_ID"]  # 推播對象的 userId

# GAS Webhook（記錄到 Google Sheets）
GAS_WEBHOOK_URL = os.environ["GAS_WEBHOOK_URL"]

# 時區
TIMEZONE = "America/New_York"
