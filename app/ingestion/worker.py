import asyncio
import json
import random

from loguru import logger

from app.config.settings import settings


class Backoff:
    def __init__(self, base=settings.backoff_base, cap=settings.backoff_cap):
        self.base = base
        self.cap = cap
        self.attempt = 0

    def next_delay(self) -> float:
        exp = float(min(self.cap, self.base * (2 ** self.attempt)))
        jitter = exp * 0.2 * random.random()
        return exp + jitter

    def success(self):
        self.attempt = max(0, self.attempt - 1)

    def failure(self):
        self.attempt += 1

class Worker:
    def __init__(self, ws_client, pipeline):
        self.ws_client = ws_client
        self.pipeline = pipeline


    async def run(self):


        backoff = Backoff()

        async for raw in self.ws_client.connect():

            try:

                msg = json.loads(raw)

                await self.pipeline.process(msg)

                backoff.success()

            except Exception as e:
                logger.error(f"Processing error: {e}")

                backoff.failure()
                await asyncio.sleep(backoff.next_delay())

