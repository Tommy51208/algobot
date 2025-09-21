"""Simplified parser module providing :func:`parse` for tests."""
from __future__ import annotations

from datetime import datetime
from typing import Iterable

__all__ = ["parse"]

_KNOWN_FORMATS: Iterable[str] = (
    "%m/%d/%Y %I:%M %p",
    "%m/%d/%y %I:%M %p",
    "%m/%d/%Y",
    "%Y-%m-%d %H:%M:%S",
    "%Y-%m-%d %H:%M",
    "%Y-%m-%d",
)


def parse(value: str) -> datetime:
    """Parse ``value`` into a :class:`datetime` using common formats.

    This is a tiny subset of :mod:`dateutil.parser.parse` that is sufficient
    for the bundled tests. If no known format matches, ``datetime.fromisoformat``
    is used as a best-effort fallback.
    """
    for fmt in _KNOWN_FORMATS:
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue

    return datetime.fromisoformat(value)
