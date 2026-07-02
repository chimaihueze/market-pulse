
import os


class Settings:
    def __init__(self):
        self.binance_ws_url: str = os.getenv(
            "BINANCE_WS_URL",
            "wss://stream.binance.com:9443/stream?streams=btcusdt@trade/ethusdt@trade",
        )

        # kafka
        self.kafka_url: str = os.getenv("KAFKA_URL", "localhost:9092")
        self.kafka_partition_number: int = int(os.getenv("KAFKA_PARTITION_NUMBER", "3"))
        self.kafka_replication_factor: int = int(os.getenv("KAFKA_REPLICATION_FACTOR", "1"))
        self.kafka_storage_group_id: str = os.getenv(
            "KAFKA_STORAGE_GROUP_ID",
            "storage-service",
        )
        self.kafka_analytics_group_id: str = os.getenv(
            "KAFKA_ANALYTICS_GROUP_ID",
            "analytics-service",
        )

        # analytics
        self.analytics_window_seconds: int = int(
            os.getenv("ANALYTICS_WINDOW_SECONDS", "300")
        )
        self.analytics_volume_window_seconds: int = int(
            os.getenv("ANALYTICS_VOLUME_WINDOW_SECONDS", "60")
        )

        # clickhouse
        self.clickhouse_host: str = os.getenv("CLICKHOUSE_HOST", "localhost")
        self.clickhouse_port: int = int(os.getenv("CLICKHOUSE_PORT", "9000"))
        self.clickhouse_user: str = os.getenv("CLICKHOUSE_USER", "admin")
        self.clickhouse_password: str = os.getenv("CLICKHOUSE_PASSWORD", "admin")
        self.clickhouse_database: str = os.getenv("CLICKHOUSE_DATABASE", "default")
        self.clickhouse_trades_table: str = os.getenv(
            "CLICKHOUSE_TRADES_TABLE",
            "market_trades",
        )
        self.clickhouse_batch_size: int = int(
            os.getenv("CLICKHOUSE_BATCH_SIZE", "1000")
        )

        # websocket
        self.ws_ping_interval: int = int(os.getenv("WS_PING_INTERVAL", "20"))
        self.ws_ping_timeout: int = int(os.getenv("WS_PING_TIMEOUT", "20"))
        self.backoff_base: int = int(os.getenv("BACKOFF_BASE", "1"))
        self.backoff_cap: int = int(os.getenv("BACKOFF_CAP", "30"))

        self.max_clock_drift_seconds: int = int(
            os.getenv("MAX_CLOCK_DRIFT_SECONDS", "30")
        )

        self.symbol: list = os.getenv("SYMBOLS", "btcusdt,ethusdt").split(",")

settings = Settings()
