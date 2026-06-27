import asyncio

from loguru import logger

from app.config.settings import settings
from app.storage.processor import TradeStorageProcessor
from app.storage.repository import ClickHouseRepository
from app.streaming.kafka_consumer import KafkaConsumer
from app.streaming.topics import Topics
from observability.logger import setup_logger


async def main():
    logger.info("starting storage service")

    repository = ClickHouseRepository()
    await repository.create_table()

    processor = TradeStorageProcessor(repository)

    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_url,
        topic=Topics.MARKET_TRADES,
        group_id=settings.kafka_storage_group_id,
    )
    await consumer.start()
    try:
        await consumer.run(processor.process)
    finally:
        await processor.flush()

if __name__ == "__main__":
    setup_logger()
    asyncio.run(main())
