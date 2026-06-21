from datetime import datetime, timezone

from app.schema.trade_event import TradeEvent


def normalize_trade(data: dict) -> TradeEvent:

    return TradeEvent(
        event_id = f"binance-{data['s']}-{data['t']}",

        exchange = "binance",
        symbol = data["s"],

        trade_id=data["t"],

        price = data["p"],

        quantity = data["q"],

        trade_timestamp = datetime.fromtimestamp(data["T"] / 1000, tz=timezone.utc),

        ingest_timestamp=datetime.now(tz=timezone.utc),

        is_buyer_maker=data["m"],
    )