from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class MetricEvent(BaseModel):
    event_version: int = 1
    event_type: str = "metric"

    event_id: str

    symbol: str
    metric_name: str
    value: Decimal
    window_seconds: int

    computed_at: datetime
    trade_count: int
