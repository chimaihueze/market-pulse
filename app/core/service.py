from abc import ABC


class Service(ABC):
    async def start(self):
        """To be implemented"""
        pass

    async def run(self):
        """To be implemented"""
        pass

    async def stop(self):
        """To be implemented"""
        pass