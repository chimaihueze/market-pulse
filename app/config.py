
class Settings:
    def __init__(self):
        self.binance_ws_url = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"
        self.ws_ping_interval = 20
        self.ws_ping_timeout = 20
        self.backoff_base = 1
        self.backoff_cap = 30

        self.symbol = ["btcusdt", "ethusdt"]

settings = Settings()