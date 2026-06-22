from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from loguru import logger

from app.config.settings import settings
from app.streams.topics import Topics


async def create_topics():
    admin = AIOKafkaAdminClient(
        bootstrap_servers=settings.kafka_url,
    )

    await admin.start()

    try:
        await admin.create_topics(
            [
                NewTopic(
                    name=Topics.MARKET_TRADES,
                    num_partitions=settings.kafka_partition_number,
                    replication_factor=settings.kafka_replication_factor
                )
            ]
        )
    except Exception as e:
        logger.error(f"create_topics error: {e}")

    finally:
        await admin.close()