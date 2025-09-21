"""Pytest configuration shared across the entire test suite."""

from __future__ import annotations

import socket
from typing import Callable

import pytest


def pytest_addoption(parser: pytest.Parser) -> None:
    """Register the ``--disable-socket`` option used in ``pytest.ini``."""

    parser.addoption(
        "--disable-socket",
        action="store_true",
        default=False,
        help="Disable network connectivity during tests.",
    )


@pytest.fixture(autouse=True)
def _enforce_socket_restriction(pytestconfig: pytest.Config) -> Callable[[], None]:
    """Disable real network calls when ``--disable-socket`` is set.

    The project relies on a number of network facing dependencies.  When the
    option is enabled (it is by default through ``pytest.ini``) we monkey patch
    ``socket.socket`` and ``socket.create_connection`` so that accidental
    network access results in a descriptive error.  The original functions are
    restored after each test in order to keep the monkey patch contained.
    """

    if not pytestconfig.getoption("--disable-socket"):
        return lambda: None

    original_socket = socket.socket
    original_create_connection = socket.create_connection

    def guard(*_args, **_kwargs):
        raise RuntimeError("Network access is disabled during tests.")

    socket.socket = guard  # type: ignore[assignment]
    socket.create_connection = guard  # type: ignore[assignment]

    def restore() -> None:
        socket.socket = original_socket  # type: ignore[assignment]
        socket.create_connection = original_create_connection  # type: ignore[assignment]

    return restore


def pytest_runtest_teardown(item: pytest.Item) -> None:  # pragma: no cover - exercised by pytest
    """Ensure any socket monkey patches created by :func:`_enforce_socket_restriction` are restored."""

    restore = item.funcargs.get("_enforce_socket_restriction")
    if callable(restore):
        restore()

