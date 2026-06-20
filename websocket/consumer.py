import asyncio
import json
import random
import websockets
from websockets.exceptions import ConnectionClosed
from settings import settings


class Backoff:
    def __init__(self, base=1, cap=30):
        self.base = base
        self.cap = cap
        self.attempt = 0
        self.last_success = None

    def next_delay(self):
        exp = min(self.cap, self.base * (2 ** self.attempt))
        jitter = random.uniform(0, exp * 0.2)
        return exp * jitter
    
    def success(self):
        self.last_success = asyncio.get_event_loop().time()
        if self.attempt > 0:
            self.attempt -= 1
    
    def failure(self):
        self.attempt += 1


async def consume():
    backoff = Backoff()

    try:
        while True:
            try:
                async with websockets.connect(settings.binance_ws_url, ping_interval=settings.ws_ping_interval,
                                              ping_timeout=settings.ws_ping_timeout) as ws:

                    async for raw in ws:
                        msg = json.loads(raw)
                        stream = msg.get("stream")
                        data = msg.get("data")

                        print(f"{stream}: {data}")

                        backoff.success()

            except ConnectionClosed as e:
                print(f"Connection closed: {e}")
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print(f"Unexpected Error: {e}")
                backoff.failure()

            delay = backoff.next_delay()
            print(f"Reconnecting in {delay:.2f}s")
            await asyncio.sleep(delay)

    except asyncio.CancelledError:
        print("Consumer cancelled cleanly")
        raise


if __name__ == "__main__":
    try:
        asyncio.run(consume())
    except KeyboardInterrupt:
        print("Shutting down consumer...")