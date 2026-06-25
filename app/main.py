import asyncio

from loguru import logger

from app.config.settings import settings
from app.ingestion.binance_ws_client import BinanceWSClient
from app.ingestion.consumer import Consumer
from app.pipelines.pipeline import TradePipeline
from app.producers.create_topics import create_topics
from app.producers.kafka_producer import KafkaProducer
from app.ingestion.worker import Worker
from app.validators.trade_validator import TradeValidator
from observability.logger import setup_logger


async def main():
    logger.info("starting market-pulse")

    await create_topics()

    producer = KafkaProducer(settings.kafka_url)

    started = False

    for i in range(3):
        try:
            await producer.start()
            started = True
            logger.info("kafka connected")
            break
        except Exception as e:
            logger.error(f"kafka retry {i}", extra={"error": str(e)})
            await asyncio.sleep(2 ** i)

    if not started:
        logger.critical("kafka unavailable - shutting down service")
        await producer.stop()
        return

    validator = TradeValidator(settings)

    pipeline = TradePipeline(
        validator=validator,
        publisher=producer
    )

    ws_client = BinanceWSClient(
        url=settings.binance_ws_url,
        ping_interval=settings.ws_ping_interval,
        ping_timeout=settings.ws_ping_timeout,
    )

    worker = Worker(
        ws_client=ws_client,
        pipeline=pipeline,
    )

    try:
        await worker.run()
    finally:
        logger.info("shutting down producer")
        await producer.stop()


if __name__ == "__main__":
    setup_logger()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("shutting down cleanly")