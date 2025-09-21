"""Tests for the lightweight trading simulation helpers."""

from typing import Sequence

import pytest

from algobot.simulation import (MovingAverageCrossStrategy, SimulationStrategy,
                                TradingSimulation)


class _IndexedSignalStrategy(SimulationStrategy):
    """Test helper that emits predefined signals at specific indices."""

    def __init__(self, buy_index: int, sell_index: int):
        self.buy_index = buy_index
        self.sell_index = sell_index

    def reset(self) -> None:
        self._has_bought = False
        self._has_sold = False

    def get_signal(self, history: Sequence[float]) -> str:
        index = len(history) - 1
        if not self._has_bought and index >= self.buy_index:
            self._has_bought = True
            return "buy"
        if self._has_bought and not self._has_sold and index >= self.sell_index:
            self._has_sold = True
            return "sell"
        return "hold"


class _HoldStrategy(SimulationStrategy):
    """Strategy that never trades and is used to test the idle path."""

    def get_signal(self, history: Sequence[float]) -> str:  # pragma: no cover - trivial
        return "hold"


def test_simulation_generates_expected_trades():
    prices = [100, 101, 102, 103, 110, 120]
    strategy = _IndexedSignalStrategy(buy_index=2, sell_index=5)
    simulation = TradingSimulation(prices=prices, strategy=strategy, trading_fee=0)

    report = simulation.run()

    assert report["starting_balance"] == 1000
    expected_balance = 1000 / prices[2] * prices[-1]
    assert report["ending_balance"] == pytest.approx(expected_balance)
    assert len(report["trades"]) == 2
    assert report["trades"][0]["action"] == "buy"
    assert report["trades"][0]["index"] == 2
    assert report["trades"][1]["action"] == "sell"
    assert report["trades"][1]["index"] == 5
    assert len(report["equity_curve"]) == len(prices)


def test_simulation_handles_no_signals():
    prices = [100, 99, 98]
    strategy = _HoldStrategy()
    simulation = TradingSimulation(prices=prices, strategy=strategy)

    report = simulation.run()

    assert report["trades"] == []
    assert report["ending_balance"] == pytest.approx(1000)
    assert report["return_pct"] == pytest.approx(0)


def test_moving_average_strategy_state_is_reset_between_runs():
    prices = [100, 101, 102, 98, 97, 96, 103, 110]
    strategy = MovingAverageCrossStrategy(fast_period=2, slow_period=3)
    simulation = TradingSimulation(prices=prices, strategy=strategy, trading_fee=0)

    first_report = simulation.run()
    second_report = simulation.run()

    assert first_report == second_report
    assert len(first_report["trades"]) >= 1


def test_simulation_rejects_unknown_signal():
    class _InvalidStrategy(SimulationStrategy):
        def get_signal(self, history: Sequence[float]) -> str:
            return "invalid"

    simulation = TradingSimulation(prices=[100, 101], strategy=_InvalidStrategy())

    with pytest.raises(ValueError):
        simulation.run()


def test_simulation_requires_prices():
    simulation = TradingSimulation(prices=[], strategy=_HoldStrategy())

    with pytest.raises(ValueError):
        simulation.run()

