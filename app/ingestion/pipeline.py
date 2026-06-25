from loguru import logger

from app.normalizers.binance_trade import normalize_trade
from app.schema.trade_event import TradeEvent
from app.shared.result import Result
from app.streaming.topics import Topics


class TradePipeline:
    def __init__(self, validator, publisher):
        self.validator = validator
        self.publisher = publisher


    async def process(self, msg) -> bool:

        normalized = self._normalize(msg)
        if not normalized.ok or normalized.value is None:
            return False

        trade = normalized.value

        validated = self._validate(trade)

        if not validated.ok or validated.value is None:
            return False

        trade = validated.value

        published = await self._publish(trade)
        if not published.ok:
            return False

        return True

    def _normalize(self, msg) -> Result[TradeEvent]:
        try:
            trade = normalize_trade(msg["data"])
            return Result.success(trade)
        except Exception as e:
            logger.error(
                "normalize error",
                extra={"error": str(e), "raw": msg}
            )
            return Result.fail(str(e))

    def _validate(self, trade: TradeEvent) -> Result[TradeEvent]:
        result = self.validator.validate(trade)

        if not result.valid:
            logger.warning(
                "invalid trade dropped",
                extra={"trade_id": trade.trade_id, "errors": result.errors}
            )
            return Result.fail("validation failed")

        return Result.success(trade)


    async def _publish(self, trade: TradeEvent) -> Result[TradeEvent]:
        try:
            await self.publisher.publish(
                topic=Topics.MARKET_TRADES,
                key=trade.symbol,
                value=trade.model_dump()
            )
            return Result.success(trade)
        except Exception as e:
            logger.error(
                "Failed to publish trade", extra={"trade_id": trade.trade_id, "errors": str(e)}
            )
            return Result.fail(str(e))