"""Simplified Binance client stub for unit tests."""

from __future__ import annotations

from typing import Any, Dict, List


class Client:  # pylint: disable=too-few-public-methods
    """Very small subset of the Binance client used in the tests."""

    def __init__(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        self._tickers: List[Dict[str, Any]] = []

    # The real client exposes these helpers; tests patch them with mocks.
    def get_all_tickers(self):  # type: ignore[no-untyped-def]
        return list(self._tickers)

    def get_symbol_info(self, symbol):  # type: ignore[no-untyped-def]
        raise RuntimeError("get_symbol_info is not implemented in the test stub")

    def get_historical_klines(self, *args, **kwargs):  # type: ignore[no-untyped-def]
        raise RuntimeError("get_historical_klines is not implemented in the test stub")
