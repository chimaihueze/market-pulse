import sys
from loguru import logger


def setup_logger():
    logger.remove()

    log_format = (
        "{time:DD-MM-YYYYTHH:mm:ss} | "
        "{level} | "
        "{message}"
    )

    logger.add(
        sys.stdout,
        level="INFO",
        format=log_format,
    )

    logger.add(
        "logs/marketpulse.log",
        rotation="10 MB",
        retention="7 days",
        level="INFO",
        format=log_format,
    )

    return logger