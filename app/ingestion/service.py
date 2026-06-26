import asyncio

from loguru import logger

from app.core.backoff import Backoff
from app.core.service import Service
from app.ingestion.worker import Worker
from app.streaming.kafka_producer import KafkaProducer


class IngestionService(Service):
    def __init__(self, producer: KafkaProducer, worker: Worker,):
        self.producer = producer
        self.worker = worker
        self.backoff = Backoff()

    async def start(self):

        started = False

        for i in range(3):
            try:
                await self.producer.start()
                started = True
                logger.info("kafka connected")
                self.backoff.success()
                break
            except Exception as e:
                logger.error(f"kafka retry {i}", extra={"error": str(e)})
                self.backoff.failure()
                delay = self.backoff.next_delay()
                await asyncio.sleep(delay)

        if not started:
            logger.critical("kafka unavailable - shutting down service")
            await self.producer.stop()

    async def run(self):
        await self.worker.run()

    async def stop(self):
        logger.info("stopping ingestion service")
        await self.producer.stop()