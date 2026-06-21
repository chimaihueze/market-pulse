from app.normalizers.binance_trade import normalize_trade
from app.streams.topics import Topics


class TradePipeline:
    def __init__(self, validator, publisher, logger):
        self.validator = validator
        self.publisher = publisher
        self.logger = logger


    async def process(self, msg) -> bool:

        trade = normalize_trade(msg["data"])

        if not await self._validate(trade):
            return False

        if not await self._publish(msg, trade):
            return False

        return True


    async def _validate(self, trade) -> bool:
        result = self.validator.validate(trade)

        if result.valid: return True

        self.logger.warning(
            "invalid trade dropped", extra={"trade_id": trade.trade_id, "errors": result.errors}
        )
        return False


    async def _publish(self, msg, trade) -> bool:
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