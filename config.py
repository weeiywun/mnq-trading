import os

# Alpaca Paper Trading
ALPACA_API_KEY    = os.environ["ALPACA_API_KEY"]
ALPACA_SECRET_KEY = os.environ["ALPACA_SECRET_KEY"]
ALPACA_BASE_URL   = "https://paper-api.alpaca.markets"

# 商品設定
SYMBOL = "QQQ"

# 策略參數
ORB_MINUTES   = 5      # 開盤區間分鐘數
SHARE_QTY     = 10     # 股數（可調整）

# TP/SL 用 ORB 區間大小動態計算（1:1）
# 不設固定點數，依當日 ORB range 決定

# 風控參數
MAX_DAILY_LOSS_USD   = 300   # 每日最大虧損（美元）
MAX_CONSECUTIVE_LOSS = 3     # 連敗熔斷
TRADE_ONCE_PER_DAY   = True  # 每日只交易一次

# LINE Bot
LINE_CHANNEL_TOKEN = os.environ["LINE_CHANNEL_TOKEN"]
LINE_USER_ID       = os.environ["LINE_USER_ID"]

# GAS Webhook
GAS_WEBHOOK_URL = os.environ["GAS_WEBHOOK_URL"]

# 時區
TIMEZONE = "America/New_York"
