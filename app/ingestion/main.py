import asyncio

from loguru import logger

from app.config.settings import settings
from app.core.runner import ServiceRunner
from app.ingestion.binance_ws_client import BinanceWSClient
from app.ingestion.pipeline import TradePipeline
from app.ingestion.service import IngestionService
from app.ingestion.worker import Worker
from app.streaming.kafka_producer import KafkaProducer
from app.validators.trade_validator import TradeValidator
from observability.logger import setup_logger


async def main():
    logger.info("starting ingestion service")

    validator = TradeValidator(settings)
    producer = KafkaProducer(settings.kafka_url)

    pipeline = TradePipeline(
        validator=validator,
        publisher=producer,
    )

    ws_client = BinanceWSClient(
        url=settings.binance_ws_url,
        ping_interval=settings.ws_ping_interval,
        ping_timeout=settings.ws_ping_timeout,
    )

    worker = Worker(ws_client=ws_client, pipeline=pipeline)

    service = IngestionService(
        producer=producer,
        worker=worker,
    )

    runner = ServiceRunner(service)
    await runner.run()


if __name__ == "__main__":
    setup_logger()
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warning("shutting down cleanly")
