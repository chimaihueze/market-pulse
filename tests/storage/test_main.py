import unittest
from unittest.mock import AsyncMock, patch

from app.storage import main as storage_main


class StorageMainTest(unittest.IsolatedAsyncioTestCase):
    async def test_main_creates_clickhouse_table_before_starting_consumer(self):
        calls = []

        repository = AsyncMock()
        repository.create_table.side_effect = lambda: calls.append("create_table")

        consumer = AsyncMock()
        consumer.start.side_effect = lambda: calls.append("consumer_start")
        consumer.run.side_effect = lambda handler: calls.append("consumer_run")

        processor = AsyncMock()
        processor.flush = AsyncMock(side_effect=lambda: calls.append("flush"))

        with (
            patch.object(storage_main, "ClickHouseRepository", return_value=repository),
            patch.object(storage_main, "TradeStorageProcessor", return_value=processor),
            patch.object(storage_main, "KafkaConsumer", return_value=consumer),
        ):
            await storage_main.main()

        self.assertEqual(
            calls,
            ["create_table", "consumer_start", "consumer_run", "flush"],
        )
