from datetime import UTC, datetime

from loguru import logger

from app.analytics.windows import SymbolWindows, WindowEntry
from app.config.settings import settings
from app.schema.metric_event import MetricEvent
from app.schema.trade_event import TradeEvent
from app.streaming.kafka_producer import KafkaProducer
from app.streaming.topics import Topics


class TradeAnalyticsProcessor:
    def __init__(
        self,
        producer: KafkaProducer,
        primary_window_seconds: int = settings.analytics_window_seconds,
        volume_window_seconds: int = settings.analytics_volume_window_seconds,
    ):
        self.producer = producer
        self.primary_window_seconds = primary_window_seconds
        self.volume_window_seconds = volume_window_seconds
        self._symbols: dict[str, SymbolWindows] = {}

    async def process(self, trade: dict) -> bool:
        trade_event = TradeEvent.model_validate(trade)
        symbol = trade_event.symbol

        if symbol not in self._symbols:
            self._symbols[symbol] = SymbolWindows(
                primary_window_seconds=self.primary_window_seconds,
                volume_window_seconds=self.volume_window_seconds,
            )

        entry = WindowEntry(
            timestamp=trade_event.trade_timestamp,
            price=trade_event.price,
            quantity=trade_event.quantity,
        )
        metrics = self._symbols[symbol].update(entry)
        computed_at = datetime.now(UTC)

        for metric in metrics:
            event = MetricEvent(
                event_id=(
                    f"metric-{symbol}-{metric.metric_name}-"
                    f"{trade_event.trade_id}-{computed_at.timestamp()}"
                ),
                symbol=symbol,
                metric_name=metric.metric_name,
                value=metric.value,
                window_seconds=metric.window_seconds,
                computed_at=computed_at,
                trade_count=metric.trade_count,
            )
            await self.producer.publish(
                topic=Topics.MARKET_METRICS,
                key=symbol,
                value=event.model_dump(),
            )

        logger.debug(
            "metrics computed",
            extra={
                "symbol": symbol,
                "metric_count": len(metrics),
                "trade_id": trade_event.trade_id,
            },
        )
        return True
