from aiokafka.admin import AIOKafkaAdminClient, NewTopic
from aiokafka.errors import TopicAlreadyExistsError
from loguru import logger

from app.streaming.topics import Topics


async def create_topics(
    kafka_url: str,
    kafka_partition_number: int,
    kafka_replication_factor: int,
) -> bool:
    admin = AIOKafkaAdminClient(
        bootstrap_servers=kafka_url,
    )

    await admin.start()

    try:
        required_topics = [
            NewTopic(
                name=Topics.MARKET_TRADES,
                num_partitions=kafka_partition_number,
                replication_factor=kafka_replication_factor,
            ),
            NewTopic(
                name=Topics.MARKET_METRICS,
                num_partitions=kafka_partition_number,
                replication_factor=kafka_replication_factor,
            ),
        ]
        existing_topics = await admin.list_topics()
        missing_topics = [
            topic for topic in required_topics if topic.name not in existing_topics
        ]

        if not missing_topics:
            logger.info("kafka topics already exist")
            return True

        await admin.create_topics(missing_topics)
        logger.info("kafka topics created")
        return True
    except TopicAlreadyExistsError:
        logger.info("kafka topics already exist")
        return True
    except Exception as e:
        logger.error(f"create_topics error: {e}")
        return False
    finally:
        await admin.close()