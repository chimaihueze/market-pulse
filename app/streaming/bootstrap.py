import asyncio
import sys

from loguru import logger

from app.config.settings import settings
from app.streaming.admin import create_topics
from observability.logger import setup_logger


async def main() -> None:
    logger.info("bootstrapping kafka topics")

    created = await create_topics(
        kafka_url=settings.kafka_url,
        kafka_partition_number=settings.kafka_partition_number,
        kafka_replication_factor=settings.kafka_replication_factor,
    )

    if not created:
        logger.error("kafka topic bootstrap failed")
        sys.exit(1)

    logger.info("kafka topic bootstrap complete")


if __name__ == "__main__":
    setup_logger()
    asyncio.run(main())
