"""High level utilities for running lightweight trading simulations.

This module exposes a small, dependency free simulation engine that can be
used in tests, examples or documentation without requiring access to the
Binance API.  The existing :class:`algobot.traders.simulation_trader
SimulationTrader` class offers a rich feature set that mirrors the real
trading flow.  Unfortunately it depends on the :class:`algobot.data.Data`
object which in turn connects to Binance in order to fetch tick data.

The helper classes below provide an alternative that operates purely on a
sequence of prices.  They are intentionally simple – the goal is to make it
easy to experiment with strategies or to create deterministic unit tests that
exercise trading logic without performing any network requests.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from statistics import mean
from typing import Dict, Iterable, List, MutableMapping, Sequence


# ---------------------------------------------------------------------------
# Strategy helpers
# ---------------------------------------------------------------------------


class SimulationStrategy:
    """Small protocol style base class for simulation strategies.

    A strategy is expected to examine the historical prices and emit a trading
    signal for the current step.  Implementations must return one of the
    supported actions: ``"buy"``, ``"sell"`` or ``"hold"``.  The base class
    also exposes :meth:`reset` which allows strategies that keep internal
    state to reset that state before a new simulation run begins.
    """

    ACTIONS = {"buy", "sell", "hold"}

    def reset(self) -> None:
        """Reset any state stored by the strategy.

        Sub-classes can safely ignore this method if they operate in a purely
        functional manner.
        """

    def get_signal(self, history: Sequence[float]) -> str:
        """Return the action to take for the current timestep.

        :param history: Prices leading up to and including the current step.
        :return: One of ``"buy"``, ``"sell"`` or ``"hold"``.
        """

        raise NotImplementedError("Strategies must implement `get_signal`.")


@dataclass
class MovingAverageCrossStrategy(SimulationStrategy):
    """Tiny moving average crossover strategy used for demonstrations.

    The strategy goes long when the fast moving average crosses above the slow
    moving average.  It exits the position once the fast average drops below
    the slow one again.
    """

    fast_period: int = 3
    slow_period: int = 5
    _in_position: bool = field(default=False, init=False)

    def reset(self) -> None:  # pragma: no cover - trivial one liner
        self._in_position = False

    def get_signal(self, history: Sequence[float]) -> str:
        if len(history) < self.slow_period:
            return "hold"

        fast_average = mean(history[-self.fast_period :])
        slow_average = mean(history[-self.slow_period :])

        if not self._in_position and fast_average > slow_average:
            self._in_position = True
            return "buy"

        if self._in_position and fast_average < slow_average:
            self._in_position = False
            return "sell"

        return "hold"


# ---------------------------------------------------------------------------
# Core simulation engine
# ---------------------------------------------------------------------------


@dataclass
class TradingSimulation:
    """A lightweight trading simulation engine.

    Parameters
    ----------
    prices:
        Iterable of prices that make up the market data.  The engine processes
        the values in the order in which they are provided.
    strategy:
        A :class:`SimulationStrategy` instance used to generate trading
        signals.
    starting_balance:
        Balance the simulation should begin with.  All trades use the full
        available balance in order to keep the implementation compact.
    trading_fee:
        Percentage based fee applied to both the entry and exit legs of a
        trade.  ``0.001`` corresponds to ``0.1%`` which roughly matches the
        default Binance spot trading fees.
    """

    prices: Iterable[float]
    strategy: SimulationStrategy
    starting_balance: float = 1_000.0
    trading_fee: float = 0.001

    def run(self) -> MutableMapping[str, object]:
        """Execute the simulation and return a report dictionary.

        The report contains the executed trades, the equity curve and a couple
        of convenience metrics that make the result easy to inspect.
        """

        prices = list(self.prices)
        if not prices:
            raise ValueError("`prices` must contain at least one value.")

        self.strategy.reset()

        cash_balance = self.starting_balance
        coin_balance = 0.0
        trades: List[Dict[str, float]] = []
        equity_curve: List[float] = []

        for index, price in enumerate(prices):
            history = prices[: index + 1]
            signal = self.strategy.get_signal(history).lower()

            if signal not in SimulationStrategy.ACTIONS:
                raise ValueError(f"Unknown trading signal: {signal}")

            if signal == "buy" and cash_balance > 0:
                fee = cash_balance * self.trading_fee
                investable = cash_balance - fee
                coin_balance += investable / price
                cash_balance = 0.0
                trades.append(self._create_trade_record(index, signal, price, cash_balance, coin_balance))

            elif signal == "sell" and coin_balance > 0:
                gross = coin_balance * price
                fee = gross * self.trading_fee
                cash_balance += gross - fee
                coin_balance = 0.0
                trades.append(self._create_trade_record(index, signal, price, cash_balance, coin_balance))

            equity_curve.append(cash_balance + coin_balance * price)

        ending_balance = cash_balance + coin_balance * prices[-1]
        return_percentage = ((ending_balance / self.starting_balance) - 1) * 100

        return {
            "starting_balance": self.starting_balance,
            "ending_balance": ending_balance,
            "return_pct": return_percentage,
            "trades": trades,
            "equity_curve": equity_curve,
        }

    @staticmethod
    def _create_trade_record(index: int, action: str, price: float, cash: float, coin: float) -> Dict[str, float]:
        net_worth = cash + coin * price
        return {
            "index": index,
            "action": action,
            "price": price,
            "cash_balance": cash,
            "coin_balance": coin,
            "net_worth": net_worth,
        }


__all__ = [
    "MovingAverageCrossStrategy",
    "SimulationStrategy",
    "TradingSimulation",
]

