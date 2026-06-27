from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from loguru import logger

from app.config.settings import settings
from app.streaming.topics import Topics


async def create_topics(kafka_url, kafka_partition_number, kafka_replication_factor):
    admin = AIOKafkaAdminClient(
        bootstrap_servers=kafka_url,
    )

    await admin.start()

    try:
        await admin.create_topics(
            [
                NewTopic(
                    name=Topics.MARKET_TRADES,
                    num_partitions=kafka_partition_number,
                    replication_factor=kafka_replication_factor,
                )
            ]
        )
    except Exception as e:
        logger.error(f"create_topics error: {e}")

    finally:
        await admin.close()