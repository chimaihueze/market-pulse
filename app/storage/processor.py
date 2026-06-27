from loguru import logger

from app.config.settings import settings
from app.schema.trade_event import TradeEvent
from app.storage.repository import ClickHouseRepository


class TradeStorageProcessor:
    def __init__(
        self,
        repository: ClickHouseRepository,
        batch_size: int = settings.clickhouse_batch_size,
    ):
        self.repository = repository
        self.batch_size = batch_size
        self._buffer: list[TradeEvent] = []

    async def process(self, trade: dict):
        trade_event = TradeEvent.model_validate(trade)
        self._buffer.append(trade_event)

        if len(self._buffer) >= self.batch_size:
            await self._flush()

        return True

    async def flush(self) -> None:
        await self._flush()

    async def _flush(self) -> None:
        if not self._buffer:
            return

        batch = self._buffer
        self._buffer = []

        logger.info("storing trades", extra={"count": len(batch)})
        await self.repository.save_many(batch)
