import json
from loguru import logger


class Worker:
    def __init__(self, ws_client, pipeline):
        self.ws_client = ws_client
        self.pipeline = pipeline

    async def run(self):
        async for raw in self.ws_client.connect():
            try:

                msg = json.loads(raw)
                ok = await self.pipeline.process(msg)

                if not ok:
                    continue

            except Exception as e:
                logger.error(f"Processing error: {e}")
