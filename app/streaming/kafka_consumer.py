import json

from aiokafka import AIOKafkaConsumer
from loguru import logger


class KafkaConsumer:
    def __init__(self, bootstrap_servers: str, topic: str, group_id: str) -> None:
        self.bootstrap_servers = bootstrap_servers
        self.topic = topic
        self.group_id = group_id
        self.consumer = None

    async def start(self):
        self.consumer = AIOKafkaConsumer(
            self.topic,
            bootstrap_servers=self.bootstrap_servers,
            group_id=self.group_id,
            value_deserializer=lambda m: json.loads(m.decode('utf-8'))
        )

        await self.consumer.start()
        logger.info(f"Kafka Consumer started for {self.topic}")

    async def run(self, handler):
        try:
            async for msg in self.consumer:
                await handler(msg.value)
        finally:
            await self.consumer.stop()