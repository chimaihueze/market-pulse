import asyncio
import json
import random

import websockets
from loguru import logger
from websockets.exceptions import ConnectionClosed
from app.config import settings
from app.normalizers.binance_trade import normalize_trade
from app.validators.trade_validator import TradeValidator


class Backoff:
    def __init__(self, base: int = settings.backoff_base, cap: int = settings.backoff_cap):
        self.base = base
        self.cap = cap
        self.attempt = 0
        self.last_success = None

    def next_delay(self):
        exp: int = min(self.cap, self.base * (2 ** self.attempt))
        jitter: float | int= random.uniform(0, exp * 0.2)
        return exp + jitter
    
    def success(self):
        self.last_success = asyncio.get_event_loop().time()
        if self.attempt > 0:
            self.attempt -= 1
    
    def failure(self):
        self.attempt += 1


async def consume():
    backoff = Backoff()
    validator = TradeValidator(settings)

    try:
        while True:
            try:
                async with websockets.connect(settings.binance_ws_url, ping_interval=settings.ws_ping_interval,
                                              ping_timeout=settings.ws_ping_timeout) as ws:

                    async for raw in ws:

                        try:
                            msg = json.loads(raw)
                            stream = msg.get("stream")
                            data = msg.get("data")

                            trade = normalize_trade(data)

                            result = validator.validate(trade)

                            if not result.valid:

                                logger.warning(
                                    "Trade validation failed",
                                    extra={
                                        "errors": result.errors,
                                        "trade_id": trade.trade_id,
                                    }
                                )
                                continue

                            backoff.success()
                        except Exception as e:
                            logger.error(f"trade processing failed: {e}")

            except ConnectionClosed as e:
                logger.error(f"Connection closed: {e}")
                backoff.failure()

            except asyncio.CancelledError:
                raise

            except Exception as e:
                logger.error(f"Unexpected Error: {e}")
                backoff.failure()

            delay = backoff.next_delay()
            logger.warning(f"Reconnecting in {delay:.2f}s")
            await asyncio.sleep(delay)

    except asyncio.CancelledError:
        logger.error("Consumer cancelled cleanly")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        logger.error("Shutting down consumer...")