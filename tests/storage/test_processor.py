from datetime import datetime, timezone
from decimal import Decimal
import unittest
from unittest.mock import AsyncMock

from app.schema.trade_event import TradeEvent
from app.storage.processor import TradeStorageProcessor


def trade_payload(trade_id: int) -> dict:
    return {
        "event_version": 1,
        "event_type": "trade",
        "event_id": f"binance-ETHUSDT-{trade_id}",
        "exchange": "binance",
        "symbol": "ETHUSDT",
        "trade_id": trade_id,
        "price": "2500.12000000",
        "quantity": "0.50000000",
        "trade_timestamp": "2026-01-01 00:00:00+00:00",
        "ingest_timestamp": "2026-01-01 00:00:01+00:00",
        "is_buyer_maker": False,
    }


class TradeStorageProcessorTest(unittest.IsolatedAsyncioTestCase):
    async def test_process_validates_payload_and_saves_trade(self):
        repository = AsyncMock()
        processor = TradeStorageProcessor(repository, batch_size=1)

        result = await processor.process(trade_payload(42))

        self.assertTrue(result)
        repository.save_many.assert_awaited_once()

        saved_trades = repository.save_many.await_args.args[0]
        self.assertEqual(len(saved_trades), 1)
        saved_trade = saved_trades[0]
        self.assertIsInstance(saved_trade, TradeEvent)
        self.assertEqual(saved_trade.price, Decimal("2500.12000000"))
        self.assertEqual(saved_trade.quantity, Decimal("0.50000000"))
        self.assertEqual(
            saved_trade.trade_timestamp,
            datetime(2026, 1, 1, tzinfo=timezone.utc),
        )

    async def test_process_flushes_when_batch_size_reached(self):
        repository = AsyncMock()
        processor = TradeStorageProcessor(repository, batch_size=2)

        await processor.process(trade_payload(1))
        repository.save_many.assert_not_awaited()

        await processor.process(trade_payload(2))
        repository.save_many.assert_awaited_once_with(
            [
                TradeEvent.model_validate(trade_payload(1)),
                TradeEvent.model_validate(trade_payload(2)),
            ]
        )

    async def test_flush_writes_remaining_buffered_trades(self):
        repository = AsyncMock()
        processor = TradeStorageProcessor(repository, batch_size=1000)

        await processor.process(trade_payload(7))
        repository.save_many.assert_not_awaited()

        await processor.flush()
        repository.save_many.assert_awaited_once()
        self.assertEqual(len(repository.save_many.await_args.args[0]), 1)
