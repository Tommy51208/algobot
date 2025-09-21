"""Utilities for running lightweight crypto trading simulations."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Iterable, List, Optional, Sequence


SignalGenerator = Callable[[int, float, "CryptoTradingSimulation"], str]


@dataclass
class Trade:
    """Represents a single trade executed by the simulation."""

    step: int
    action: str
    price: float
    quantity: float
    balance: float
    coin: float


@dataclass
class SimulationResult:
    """Summary of the simulation run."""

    starting_balance: float
    final_balance: float
    final_coin_holdings: float
    final_price: float
    trades: List[Trade]
    total_fees_paid: float

    @property
    def net_worth(self) -> float:
        """Return the total account value using the final market price."""
        return self.final_balance + self.final_coin_holdings * self.final_price

    @property
    def profit(self) -> float:
        """Return absolute profit or loss produced by the simulation."""
        return self.net_worth - self.starting_balance

    @property
    def return_percentage(self) -> float:
        """Return profit expressed as a percentage of the starting balance."""
        if self.starting_balance == 0:
            return 0.0
        return (self.profit / self.starting_balance) * 100


class CryptoTradingSimulation:
    """A minimal trading engine to simulate simple buy and sell signals."""

    VALID_SIGNALS = {"BUY", "SELL", "HOLD"}

    def __init__(self, starting_balance: float = 1000.0, trading_fee: float = 0.001):
        if starting_balance <= 0:
            raise ValueError("Starting balance must be greater than zero.")
        if trading_fee < 0:
            raise ValueError("Trading fee cannot be negative.")
        self.starting_balance = float(starting_balance)
        self.trading_fee = float(trading_fee)
        self.reset()

    def reset(self) -> None:
        """Reset the simulation to the initial state."""
        self.balance = float(self.starting_balance)
        self.coin = 0.0
        self.trades: List[Trade] = []
        self.total_fees_paid = 0.0

    def net_worth(self, price: float) -> float:
        """Return the account net worth for the provided price."""
        return self.balance + self.coin * price

    def run(
        self,
        prices: Sequence[float],
        signals: Optional[Iterable[str]] = None,
        strategy: Optional[SignalGenerator] = None,
    ) -> SimulationResult:
        """Run the simulation for the provided price series.

        Either ``signals`` or ``strategy`` must be supplied. ``signals`` can be an
        iterable of string instructions (``BUY``, ``SELL`` or ``HOLD``). ``strategy``
        can be used to dynamically create signals per step.
        """
        if not prices:
            raise ValueError("Price series must not be empty.")
        if signals is None and strategy is None:
            raise ValueError("Either 'signals' or 'strategy' must be provided.")
        if signals is not None and strategy is not None:
            raise ValueError("Only one of 'signals' or 'strategy' may be provided.")

        self.reset()
        actions_list: Optional[List[str]] = None
        if signals is not None:
            actions_list = [signal for signal in signals]
            if len(actions_list) != len(prices):
                raise ValueError("Length of signals must match length of prices.")

        for step, price in enumerate(prices):
            if strategy is not None:
                action = strategy(step, price, self)
            else:
                assert actions_list is not None
                action = actions_list[step]
            self._process_signal(step, float(price), action)

        final_price = float(prices[-1])
        return SimulationResult(
            starting_balance=self.starting_balance,
            final_balance=self.balance,
            final_coin_holdings=self.coin,
            final_price=final_price,
            trades=list(self.trades),
            total_fees_paid=self.total_fees_paid,
        )

    def _apply_fee(self, amount: float) -> float:
        fee = amount * self.trading_fee
        self.total_fees_paid += fee
        return fee

    def _process_signal(self, step: int, price: float, signal: str) -> None:
        action = signal.upper()
        if action not in self.VALID_SIGNALS:
            raise ValueError(f"Unsupported signal '{signal}'.")

        if action == "BUY":
            if self.balance <= 0:
                return
            fee = self._apply_fee(self.balance)
            quantity = (self.balance - fee) / price if price else 0.0
            self.balance = 0.0
            self.coin += quantity
            self.trades.append(
                Trade(
                    step=step,
                    action="BUY",
                    price=price,
                    quantity=quantity,
                    balance=self.balance,
                    coin=self.coin,
                )
            )
        elif action == "SELL":
            if self.coin <= 0:
                return
            proceeds = self.coin * price
            fee = self._apply_fee(proceeds)
            quantity = self.coin
            self.balance += proceeds - fee
            self.coin = 0.0
            self.trades.append(
                Trade(
                    step=step,
                    action="SELL",
                    price=price,
                    quantity=quantity,
                    balance=self.balance,
                    coin=self.coin,
                )
            )
        else:
            # HOLD action, nothing happens
            return
