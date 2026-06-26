import asyncio
import websockets
from websockets.exceptions import ConnectionClosed
from loguru import logger

from app.core.backoff import Backoff


class BinanceWSClient:
    def __init__(self, url: str, ping_interval: int, ping_timeout: int):
        self.url = url
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout
        self.backoff = Backoff()

    async def connect(self):
        while True:
            try:
                async with websockets.connect(
                    self.url,
                    ping_interval=self.ping_interval,
                    ping_timeout=self.ping_timeout,
                ) as ws:

                    logger.info("binance websocket connected")
                    self.backoff.success()

                    async for raw in ws:
                        yield raw

            except ConnectionClosed as e:
                logger.exception(f"binance websocket closed: {e}")
                self.backoff.failure()
                delay = self.backoff.next_delay()
                await asyncio.sleep(delay)

            except Exception as e:
                logger.exception(f"binance websocket error: {e}")
                self.backoff.failure()
                delay = self.backoff.next_delay()
                await asyncio.sleep(delay)