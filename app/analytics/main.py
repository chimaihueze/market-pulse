import asyncio

from loguru import logger

from app.analytics.processor import TradeAnalyticsProcessor
from app.config.settings import settings
from app.streaming.kafka_consumer import KafkaConsumer
from app.streaming.kafka_producer import KafkaProducer
from app.streaming.topics import Topics
from observability.logger import setup_logger


async def main():
    logger.info("starting analytics service")

    producer = KafkaProducer(settings.kafka_url)
    processor = TradeAnalyticsProcessor(producer=producer)

    consumer = KafkaConsumer(
        bootstrap_servers=settings.kafka_url,
        topic=Topics.MARKET_TRADES,
        group_id=settings.kafka_analytics_group_id,
    )

    await producer.start()
    try:
        await consumer.start()
        await consumer.run(processor.process)
    finally:
        await producer.stop()


if __name__ == "__main__":
    setup_logger()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("shutting down cleanly")
