import json

from app.normalizers.binance_trade import normalize_trade
from app.streams.topics import Topics


class TradePipeline:
    def __init__(self, validator, publisher, logger):
        self.validator = validator
        self.publisher = publisher
        self.logger = logger

    async def process(self, raw_message) -> bool:

        msg = json.loads(raw_message)

        trade = normalize_trade(msg["data"])

        result = self.validator.validate(trade)

        if not result.valid:
            self.logger.warning("invalid trade dropped", extra={"trade_id": trade.trade_id, "errors": result.errors})
            return False

        try:
            await self.publisher.publish(
                topic=Topics.MARKET_TRADES,
                key=trade.symbol,
                value=trade.model_dump()
            )
            return True
        except Exception as e:
            self.logger.error(
                "Failed to publish trade", extra={"trade_id": trade.trade_id, "errors": str(e)}
            )
            return False