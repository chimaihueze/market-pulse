
class Settings:
    def __init__(self):
        self.binance_ws_url: str = "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade"
        self.kafka_url: str = "localhost:9092"
        self.ws_ping_interval: int = 20
        self.ws_ping_timeout: int = 20
        self.backoff_base: int = 1
        self.backoff_cap: int = 30

        self.max_clock_drift_seconds: int = 30

        self.symbol: list = ["btcusdt", "ethusdt"]

settings = Settings()