import json

from aiokafka import AIOKafkaProducer


class KafkaProducer:
    def __init__(self, bootstrap_servers: str):
        self.bootstrap_servers = bootstrap_servers
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(bootstrap_servers=self.bootstrap_servers,
                                         value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                                         enable_idempotence=True)
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def publish(self, topic: str, key: str, value: dict):
        await self.producer.send_and_wait(topic=topic, key=key.encode(), value=value)