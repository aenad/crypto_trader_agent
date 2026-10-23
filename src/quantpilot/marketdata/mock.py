"""Deterministic mock public service, without network or credentials."""

from datetime import datetime
from typing import Any


class MockPublic:
    source = "synthetic"

    def __init__(self, now: datetime):
        self.now = now
        self.calls: list[str] = []

    async def request(self, kind: str, args: dict[str, Any]) -> Any:
        self.calls.append(kind)
        if kind == "markets":
            return {
                "result": {
                    "markets": [
                        {
                            "symbol": "BTCUSDT",
                            "base_asset": "BTC",
                            "quote_asset": "USDT",
                            "is_spot": True,
                        }
                    ]
                }
            }
        if kind == "candles":
            from .normalize import RESOLUTIONS

            stamps = list(range(args["from"], args["to"] + 1, RESOLUTIONS[args["resolution"]]))
            return {
                "s": "ok",
                "t": stamps,
                **{
                    k: [value] * len(stamps)
                    for k, value in {
                        "o": "100",
                        "h": "102",
                        "l": "99",
                        "c": "101",
                        "v": "3.5",
                    }.items()
                },
            }
        if kind == "trades":
            return {
                "result": {
                    "latestTrades": [
                        {
                            "symbol": args["symbol"],
                            "price": "100",
                            "quantity": "0.01",
                            "timestamp": self.now.isoformat(),
                            "isBuyOrder": True,
                        }
                    ]
                }
            }
        if kind == "book":
            return {
                "result": {
                    "bid": [{"price": "99", "quantity": "1"}],
                    "ask": [{"price": "101", "quantity": "1"}],
                }
            }
        raise ValueError("Mock supports public reads only")
