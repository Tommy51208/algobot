"""Initialization file."""

try:  # pragma: no cover - optional dependency
    from binance import Client  # type: ignore
except Exception:  # pragma: no cover - binance not installed during tests
    Client = None  # type: ignore[assignment]

try:
    from algobot.helpers import get_current_version, get_latest_version, get_logger
except Exception:  # pragma: no cover - fall back when optional deps missing
    import logging

    def get_logger(log_file: str, logger_name: str):  # type: ignore[override]
        logger = logging.getLogger(logger_name)
        if not logger.handlers:
            handler = logging.StreamHandler()
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def get_current_version():
        return "unknown"

    def get_latest_version():
        return "unknown"

MAIN_LOGGER = get_logger(log_file='algobot', logger_name='algobot')

CURRENT_VERSION = get_current_version()
LATEST_VERSION = get_latest_version()

if Client is not None:
    try:  # pragma: no cover - requires external service
        BINANCE_CLIENT = Client()
    except Exception as e:  # pragma: no cover - log unexpected client errors
        MAIN_LOGGER.exception(repr(e))
        BINANCE_CLIENT = None
else:
    BINANCE_CLIENT = None
