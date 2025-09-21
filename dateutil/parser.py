"""Lightweight substitute for :mod:`dateutil.parser` used in tests."""

from __future__ import annotations

from datetime import datetime
from typing import Iterable

_KNOWN_FORMATS: Iterable[str] = (
    "%Y-%m-%d",
    "%Y-%m-%d %H:%M:%S",
    "%m/%d/%Y",
    "%m/%d/%Y %H:%M:%S",
)


def parse(value: str) -> datetime:
    """Parse a datetime string using a set of known formats.

    The helper is intentionally small but perfectly adequate for the inputs
    used throughout the repository's test-suite.
    """

    value = value.strip()
    for fmt in _KNOWN_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    raise ValueError(f"Unsupported date format: {value}")


__all__ = ["parse"]

