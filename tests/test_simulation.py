"""Tests for the lightweight crypto trading simulation module."""

import pytest

from algobot.simulation import CryptoTradingSimulation


def test_simulation_generates_expected_profit():
    simulation = CryptoTradingSimulation(starting_balance=1000, trading_fee=0.001)
    prices = [10, 11, 12]
    signals = ["BUY", "HOLD", "SELL"]

    result = simulation.run(prices=prices, signals=signals)

    assert len(result.trades) == 2
    assert result.trades[0].action == "BUY"
    assert result.trades[-1].action == "SELL"
    assert result.final_coin_holdings == pytest.approx(0.0)
    assert result.final_balance == pytest.approx(1197.6012, rel=1e-6)
    assert result.net_worth == pytest.approx(1197.6012, rel=1e-6)
    assert result.profit == pytest.approx(197.6012, rel=1e-6)
    assert result.return_percentage == pytest.approx(19.76012, rel=1e-6)


def test_simulation_ignores_redundant_signals():
    simulation = CryptoTradingSimulation(starting_balance=500, trading_fee=0)
    prices = [10, 9, 8, 7]
    signals = ["BUY", "BUY", "HOLD", "SELL"]

    result = simulation.run(prices=prices, signals=signals)

    assert len(result.trades) == 2
    assert result.trades[0].quantity == pytest.approx(50)
    assert result.final_balance == pytest.approx(350)
    assert result.total_fees_paid == pytest.approx(0)


def test_simulation_with_strategy_callable():
    simulation = CryptoTradingSimulation(starting_balance=100)
    prices = [10, 8, 6, 12]

    def simple_strategy(step: int, price: float, sim: CryptoTradingSimulation) -> str:
        if step == 0:
            return "BUY"
        if price >= 12 and sim.coin > 0:
            return "SELL"
        return "HOLD"

    result = simulation.run(prices=prices, strategy=simple_strategy)

    assert len(result.trades) == 2
    assert result.trades[0].action == "BUY"
    assert result.trades[1].action == "SELL"
    assert result.final_balance > simulation.starting_balance


def test_simulation_requires_signals_or_strategy():
    simulation = CryptoTradingSimulation(starting_balance=100)
    prices = [10, 11]

    with pytest.raises(ValueError, match="must be provided"):
        simulation.run(prices=prices)

    with pytest.raises(ValueError, match="Only one"):
        simulation.run(prices=prices, signals=["HOLD", "HOLD"], strategy=lambda *_: "HOLD")

    with pytest.raises(ValueError, match="must match length"):
        simulation.run(prices=prices, signals=["BUY"])

    with pytest.raises(ValueError, match="Unsupported signal"):
        simulation.run(prices=prices, signals=["BUY", "INVALID"])
