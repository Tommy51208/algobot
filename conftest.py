"""Pytest configuration for the project."""
import socket
from typing import Callable, Optional, Type

import pytest

_ORIGINAL_SOCKET: Optional[Type[socket.socket]] = None
_ORIGINAL_CREATE_CONNECTION: Optional[Callable[..., socket.socket]] = None
_ORIGINAL_GETADDRINFO: Optional[Callable[..., list]] = None
_SOCKET_DISABLED = False


class SocketAccessBlocked(RuntimeError):
    """Error raised when socket access is blocked during testing."""


def _disable_socket_access():
    global _ORIGINAL_SOCKET, _ORIGINAL_CREATE_CONNECTION, _ORIGINAL_GETADDRINFO, _SOCKET_DISABLED
    if _SOCKET_DISABLED:
        return
    _ORIGINAL_SOCKET = socket.socket
    _ORIGINAL_CREATE_CONNECTION = socket.create_connection
    _ORIGINAL_GETADDRINFO = socket.getaddrinfo

    class GuardedSocket(_ORIGINAL_SOCKET):  # type: ignore[misc,valid-type]
        def __new__(cls, *args, **kwargs):  # type: ignore[no-untyped-def]
            raise SocketAccessBlocked(
                "Network access is disabled by the --disable-socket option."
            )

    def guarded_create_connection(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise SocketAccessBlocked("Network access is disabled by the --disable-socket option.")

    def guarded_getaddrinfo(*args, **kwargs):  # type: ignore[no-untyped-def]
        raise SocketAccessBlocked("Network access is disabled by the --disable-socket option.")

    socket.socket = GuardedSocket  # type: ignore[assignment]
    socket.create_connection = guarded_create_connection  # type: ignore[assignment]
    socket.getaddrinfo = guarded_getaddrinfo  # type: ignore[assignment]
    _SOCKET_DISABLED = True


def _enable_socket_access():
    global _SOCKET_DISABLED
    if not _SOCKET_DISABLED:
        return
    assert _ORIGINAL_SOCKET is not None
    assert _ORIGINAL_CREATE_CONNECTION is not None
    assert _ORIGINAL_GETADDRINFO is not None
    socket.socket = _ORIGINAL_SOCKET  # type: ignore[assignment]
    socket.create_connection = _ORIGINAL_CREATE_CONNECTION  # type: ignore[assignment]
    socket.getaddrinfo = _ORIGINAL_GETADDRINFO  # type: ignore[assignment]
    _SOCKET_DISABLED = False


@pytest.hookimpl(tryfirst=True)
def pytest_addoption(parser):
    """Register custom CLI options for pytest."""
    parser.addoption(
        "--disable-socket",
        action="store_true",
        default=False,
        help="Disable network access during test runs.",
    )


def pytest_configure(config):  # type: ignore[no-untyped-def]
    """Disable socket access if requested by pytest.ini."""
    if config.getoption("--disable-socket"):
        _disable_socket_access()


def pytest_unconfigure(config):  # type: ignore[no-untyped-def]
    """Restore socket functions after the test session completes."""
    if config.getoption("--disable-socket"):
        _enable_socket_access()
