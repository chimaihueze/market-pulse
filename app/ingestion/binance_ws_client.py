import asyncio
import websockets
from websockets.exceptions import ConnectionClosed
from loguru import logger


class BinanceWSClient:
    def __init__(self, url: str, ping_interval: int, ping_timeout: int):
        self.url = url
        self.ping_interval = ping_interval
        self.ping_timeout = ping_timeout

    async def connect(self):
        while True:
            try:
                async with websockets.connect(
                    self.url,
                    ping_interval=self.ping_interval,
                    ping_timeout=self.ping_timeout,
                ) as ws:

                    logger.info("Connected to Binance WebSocket")

                    async for raw in ws:
                        yield raw

            except ConnectionClosed as e:
                logger.warning(f"WebSocket closed: {e}")
                await asyncio.sleep(2)

            except Exception as e:
                logger.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)