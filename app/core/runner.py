from loguru import logger


class ServiceRunner:
    def __init__(self, service):
        self.service = service

    async def run(self):

        try:
            logger.info(f"Starting {self.service.__class__.__name__}")

            await self.service.start()
            await self.service.run()
        except Exception as e:
            logger.exception(f"service crashed: {e}")

        finally:
            logger.info("shutting down service")
            await self.service.stop()
