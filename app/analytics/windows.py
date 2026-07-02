import math
from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from decimal import Decimal


@dataclass(frozen=True)
class WindowEntry:
    timestamp: datetime
    price: Decimal
    quantity: Decimal


class TradeWindow:
    def __init__(self, window_seconds: int):
        self.window_seconds = window_seconds
        self._entries: deque[WindowEntry] = deque()

    def add(self, entry: WindowEntry) -> None:
        self._entries.append(entry)
        self._evict(entry.timestamp)

    def _evict(self, now: datetime) -> None:
        cutoff = now - timedelta(seconds=self.window_seconds)
        while self._entries and self._entries[0].timestamp < cutoff:
            self._entries.popleft()

    @property
    def trade_count(self) -> int:
        return len(self._entries)

    @property
    def entries(self) -> deque[WindowEntry]:
        return self._entries


def compute_vwap(entries: deque[WindowEntry]) -> Decimal | None:
    if not entries:
        return None

    total_qty = sum(entry.quantity for entry in entries)
    if total_qty == 0:
        return None

    total_pv = sum(entry.price * entry.quantity for entry in entries)
    return total_pv / total_qty


def compute_volume(entries: deque[WindowEntry]) -> Decimal:
    return sum((entry.quantity for entry in entries), start=Decimal("0"))


def compute_sma(entries: deque[WindowEntry]) -> Decimal | None:
    if not entries:
        return None

    total_price = sum(entry.price for entry in entries)
    return total_price / len(entries)


def compute_volatility(entries: deque[WindowEntry]) -> Decimal | None:
    if len(entries) < 2:
        return None

    prices = [float(entry.price) for entry in entries]
    returns = [
        math.log(prices[index] / prices[index - 1])
        for index in range(1, len(prices))
    ]

    mean = sum(returns) / len(returns)
    variance = sum((value - mean) ** 2 for value in returns) / len(returns)
    return Decimal(str(math.sqrt(variance)))


@dataclass(frozen=True)
class ComputedMetric:
    metric_name: str
    value: Decimal
    window_seconds: int
    trade_count: int


class SymbolWindows:
    def __init__(self, primary_window_seconds: int, volume_window_seconds: int):
        self.primary = TradeWindow(primary_window_seconds)
        self.volume = TradeWindow(volume_window_seconds)
        self.primary_window_seconds = primary_window_seconds
        self.volume_window_seconds = volume_window_seconds

    def update(self, entry: WindowEntry) -> list[ComputedMetric]:
        self.primary.add(entry)
        self.volume.add(entry)

        metrics: list[ComputedMetric] = []

        vwap = compute_vwap(self.primary.entries)
        if vwap is not None:
            metrics.append(
                ComputedMetric(
                    metric_name="vwap",
                    value=vwap,
                    window_seconds=self.primary_window_seconds,
                    trade_count=self.primary.trade_count,
                )
            )

        sma = compute_sma(self.primary.entries)
        if sma is not None:
            metrics.append(
                ComputedMetric(
                    metric_name="sma",
                    value=sma,
                    window_seconds=self.primary_window_seconds,
                    trade_count=self.primary.trade_count,
                )
            )

        volatility = compute_volatility(self.primary.entries)
        if volatility is not None:
            metrics.append(
                ComputedMetric(
                    metric_name="volatility",
                    value=volatility,
                    window_seconds=self.primary_window_seconds,
                    trade_count=self.primary.trade_count,
                )
            )

        metrics.append(
            ComputedMetric(
                metric_name="volume",
                value=compute_volume(self.volume.entries),
                window_seconds=self.volume_window_seconds,
                trade_count=self.volume.trade_count,
            )
        )

        return metrics
