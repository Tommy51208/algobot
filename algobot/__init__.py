"""Initialization file for the :mod:`algobot` package."""

from __future__ import annotations

from algobot.helpers import get_current_version, get_latest_version, get_logger

MAIN_LOGGER = get_logger(log_file='algobot', logger_name='algobot')

CURRENT_VERSION = get_current_version()
LATEST_VERSION = get_latest_version()

try:  # pragma: no cover - exercised indirectly during imports
    from binance import Client  # type: ignore
except ModuleNotFoundError:  # pragma: no cover - dependency not available in tests
    Client = None  # type: ignore

if Client is not None:
    try:  # pragma: no cover - requires network access
        BINANCE_CLIENT = Client()
    except Exception as e:  # pragma: no cover - defensive programming
        MAIN_LOGGER.exception(repr(e))
        BINANCE_CLIENT = None
else:
    BINANCE_CLIENT = None

__all__ = [
    "BINANCE_CLIENT",
    "CURRENT_VERSION",
    "LATEST_VERSION",
    "MAIN_LOGGER",
]
