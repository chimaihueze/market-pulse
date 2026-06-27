CREATE_TRADES_TABLE_SQL = """
    CREATE TABLE IF NOT EXISTS {table_name} (
        event_version UInt16,
        event_type LowCardinality(String),
        event_id String,
        exchange LowCardinality(String),
        symbol LowCardinality(String),
        trade_id UInt64,
        price Decimal(18, 8),
        quantity Decimal(18, 8),
        trade_timestamp DateTime64(3, 'UTC'),
        ingest_timestamp DateTime64(3, 'UTC'),
        is_buyer_maker Bool
    )
    ENGINE = MergeTree
    PARTITION BY toYYYYMM(trade_timestamp)
    ORDER BY (exchange, symbol, trade_timestamp, trade_id)
""".strip()

INSERT_TRADE_SQL = """
    INSERT INTO {table_name} (
        event_version,
        event_type,
        event_id,
        exchange,
        symbol,
        trade_id,
        price,
        quantity,
        trade_timestamp,
        ingest_timestamp,
        is_buyer_maker
    )
    VALUES
""".strip()
