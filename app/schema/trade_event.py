from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class TradeEvent(BaseModel):
    event_version: int = 1
    event_type: str = "trade"

    event_id: str

    exchange: str
    symbol: str

    trade_id: int

    price: Decimal
    quantity: Decimal

    trade_timestamp: datetime
    ingest_timestamp: datetime

    is_buyer_maker: bool