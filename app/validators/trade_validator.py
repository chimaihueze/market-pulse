from datetime import timezone, datetime

from app.config.settings import Settings
from app.schema.trade_event import TradeEvent
from app.validators.validation_result import ValidationResult



class TradeValidator:

    def __init__(self, settings: Settings):
        self.settings = settings


    def validate(self, trade: TradeEvent) -> ValidationResult:
        errors = []

        errors.extend(self._validate_required_fields(trade))

        errors.extend(self._validate_quantity(trade))

        errors.extend(self._validate_price(trade))

        errors.extend(self._validate_timestamp(trade))

        return ValidationResult(valid = len(errors) == 0, errors = errors)


    def _validate_required_fields(self, trade: TradeEvent) -> list[str]:

        errors = []

        if not trade.event_id:
            errors.append("missing event id")

        if not trade.trade_id:
            errors.append("missing trade id")

        if not trade.symbol:
            errors.append("missing symbol")

        if not trade.exchange:
            errors.append("missing exchange")

        return errors

    def _validate_price(self, trade: TradeEvent) -> list[str]:

        errors = []

        if trade.price <= 0:
            errors.append(f"invalid price: {trade.price}")

        return errors

    def _validate_quantity(self, trade: TradeEvent) -> list[str]:
        errors = []
        if trade.quantity <= 0:
            errors.append(f"invalid quantity: {trade.quantity}")
        return errors


    def _validate_timestamp(self, trade: TradeEvent,) -> list[str]:

        errors = []

        now = datetime.now(timezone.utc)

        drift = abs((now - trade.trade_timestamp).total_seconds())

        if drift > self.settings.max_clock_drift_seconds:
            errors.append(f"timestamp drift too large: {drift}")

        return errors
