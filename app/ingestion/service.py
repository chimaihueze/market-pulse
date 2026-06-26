import asyncio

from loguru import logger

from app.core.service import Service
from app.ingestion.worker import Worker
from app.streaming.kafka_producer import KafkaProducer


class IngestionService(Service):
    def __init__(self, producer: KafkaProducer, worker: Worker,):
        self.producer = producer
        self.worker = worker

    async def start(self):

        started = False

        for i in range(3):
            try:
                await self.producer.start()
                started = True
                logger.info("kafka connected")
                break
            except Exception as e:
                logger.error(f"kafka retry {i}", extra={"error": str(e)})
                await asyncio.sleep(2 ** i)

        if not started:
            logger.critical("kafka unavailable - shutting down service")
            await self.producer.stop()

    async def run(self):
        await self.worker.run()

    async def stop(self):
        logger.info("stopping ingestion service")
        await self.producer.stop()