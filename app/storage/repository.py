from collections.abc import Callable

from asynch import Connection

from app.config.settings import settings
from app.schema.trade_event import TradeEvent
from app.storage.queries import CREATE_TRADES_TABLE_SQL, INSERT_TRADE_SQL


class ClickHouseRepository:
    def __init__(
        self,
        host: str = settings.clickhouse_host,
        port: int = settings.clickhouse_port,
        user: str = settings.clickhouse_user,
        password: str = settings.clickhouse_password,
        database: str = settings.clickhouse_database,
        table_name: str = settings.clickhouse_trades_table,
        connection_factory: Callable[..., Connection] = Connection,
    ):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.database = database
        self.table_name = table_name
        self.connection_factory = connection_factory

    async def create_table(self) -> None:
        connection = self.connection_factory(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        async with connection:
            cursor = connection.cursor()
            try:
                await cursor.execute(
                    CREATE_TRADES_TABLE_SQL.format(table_name=self.table_name)
                )
            finally:
                await cursor.close()

    async def save_many(self, trades: list[TradeEvent]) -> None:
        if not trades:
            return

        connection = self.connection_factory(
            host=self.host,
            port=self.port,
            user=self.user,
            password=self.password,
            database=self.database,
        )
        async with connection:
            cursor = connection.cursor()
            try:
                await cursor.execute(
                    INSERT_TRADE_SQL.format(table_name=self.table_name),
                    [self._trade_to_row(trade) for trade in trades],
                )
            finally:
                await cursor.close()

    async def save(self, trade: TradeEvent) -> None:
        await self.save_many([trade])

    def _trade_to_row(self, trade: TradeEvent) -> tuple:
        return (
            trade.event_version,
            trade.event_type,
            trade.event_id,
            trade.exchange,
            trade.symbol,
            trade.trade_id,
            trade.price,
            trade.quantity,
            trade.trade_timestamp,
            trade.ingest_timestamp,
            trade.is_buyer_maker,
        )
