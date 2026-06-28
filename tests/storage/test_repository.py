from datetime import datetime, timezone
from decimal import Decimal
import unittest

from app.schema.trade_event import TradeEvent
from app.storage.queries import CREATE_TRADES_TABLE_SQL, INSERT_TRADE_SQL
from app.storage.repository import ClickHouseRepository


class FakeCursor:
    def __init__(self):
        self.queries = []
        self.args = []
        self.closed = False

    async def execute(self, query, args=None):
        self.queries.append(query)
        self.args.append(args)

    async def close(self):
        self.closed = True


class FakeConnection:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self.cursor_instance = FakeCursor()
        self.entered = False
        self.exited = False

    async def __aenter__(self):
        self.entered = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.exited = True

    def cursor(self):
        return self.cursor_instance


class ClickHouseRepositoryTest(unittest.IsolatedAsyncioTestCase):
    async def test_create_table_executes_expected_ddl(self):
        connections = []

        def connection_factory(**kwargs):
            connection = FakeConnection(**kwargs)
            connections.append(connection)
            return connection

        repository = ClickHouseRepository(
            host="clickhouse",
            port=9440,
            user="market",
            password="secret",
            database="analytics",
            table_name="trades",
            connection_factory=connection_factory,
        )

        await repository.create_table()

        self.assertEqual(
            connections[0].kwargs,
            {
                "host": "clickhouse",
                "port": 9440,
                "user": "market",
                "password": "secret",
                "database": "analytics",
            },
        )
        self.assertTrue(connections[0].entered)
        self.assertTrue(connections[0].exited)
        self.assertTrue(connections[0].cursor_instance.closed)
        self.assertEqual(
            connections[0].cursor_instance.queries,
            [CREATE_TRADES_TABLE_SQL.format(table_name="trades")],
        )

    async def test_save_inserts_trade_row(self):
        connections = []

        def connection_factory(**kwargs):
            connection = FakeConnection(**kwargs)
            connections.append(connection)
            return connection

        repository = ClickHouseRepository(
            table_name="trades",
            connection_factory=connection_factory,
        )
        trade = TradeEvent(
            event_id="binance-BTCUSDT-100",
            exchange="binance",
            symbol="BTCUSDT",
            trade_id=100,
            price=Decimal("65000.12345678"),
            quantity=Decimal("0.01000000"),
            trade_timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
            ingest_timestamp=datetime(2026, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
            is_buyer_maker=True,
        )

        await repository.save(trade)

        cursor = connections[0].cursor_instance
        self.assertEqual(
            cursor.queries,
            [INSERT_TRADE_SQL.format(table_name="trades")],
        )
        self.assertEqual(
            cursor.args,
            [
                [
                    (
                        1,
                        "trade",
                        "binance-BTCUSDT-100",
                        "binance",
                        "BTCUSDT",
                        100,
                        Decimal("65000.12345678"),
                        Decimal("0.01000000"),
                        datetime(2026, 1, 1, tzinfo=timezone.utc),
                        datetime(2026, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
                        True,
                    )
                ]
            ],
        )

    async def test_save_many_inserts_all_trade_rows_in_one_query(self):
        connections = []

        def connection_factory(**kwargs):
            connection = FakeConnection(**kwargs)
            connections.append(connection)
            return connection

        repository = ClickHouseRepository(
            table_name="trades",
            connection_factory=connection_factory,
        )
        trades = [
            TradeEvent(
                event_id=f"binance-BTCUSDT-{trade_id}",
                exchange="binance",
                symbol="BTCUSDT",
                trade_id=trade_id,
                price=Decimal("65000.12345678"),
                quantity=Decimal("0.01000000"),
                trade_timestamp=datetime(2026, 1, 1, tzinfo=timezone.utc),
                ingest_timestamp=datetime(2026, 1, 1, 0, 0, 1, tzinfo=timezone.utc),
                is_buyer_maker=True,
            )
            for trade_id in (100, 101)
        ]

        await repository.save_many(trades)

        cursor = connections[0].cursor_instance
        self.assertEqual(
            cursor.queries,
            [INSERT_TRADE_SQL.format(table_name="trades")],
        )
        self.assertEqual(len(cursor.args[0]), 2)
        self.assertEqual(cursor.args[0][0][5], 100)
        self.assertEqual(cursor.args[0][1][5], 101)
