import asyncio
import random

from loguru import logger

from app.config.settings import settings
from app.consmer.pipeline import TradePipeline
from app.ingestion.binance_ws_client import BinanceWSClient
from app.validators.trade_validator import TradeValidator
from app.producers.kafka_producer import KafkaProducer


class Backoff:
    def __init__(self, base=settings.backoff_base, cap=settings.backoff_cap):
        self.base = base
        self.cap = cap
        self.attempt = 0

    def next_delay(self) -> float:
        exp = float(min(self.cap, self.base * (2 ** self.attempt)))
        jitter = exp * 0.2 * random.random()
        return exp + jitter

    def success(self):
        self.attempt = max(0, self.attempt - 1)

    def failure(self):
        self.attempt += 1


async def run_consumer():
    ws_client = BinanceWSClient(
        url=settings.binance_ws_url,
        ping_interval=settings.ws_ping_interval,
        ping_timeout=settings.ws_ping_timeout,
    )

    validator = TradeValidator(settings)

    producer = KafkaProducer(settings.kafka_url)
    await producer.start()

    pipeline = TradePipeline(validator=validator, publisher=producer, logger=logger)

    backoff = Backoff()

    try:
        async for raw in ws_client.connect():

            try:

                await pipeline.process(raw)

                backoff.success()

            except Exception as e:
                logger.error(f"Processing error: {e}")

                backoff.failure()
                await asyncio.sleep(backoff.next_delay())

    finally:
        await producer.stop()
        logger.info("Consumer shutdown complete")