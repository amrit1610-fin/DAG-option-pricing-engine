# reactive_pricing_engine/test_integration.py

import pricing_engine
from dag_engine.node import MarketDataNode
from dag_engine.instruments import EuropeanOption
from dag_engine.portfolio import PortfolioBook

# 1. Shared Market Data Nodes
rate      = MarketDataNode("RiskFreeRate", 0.05)
aapl_spot = MarketDataNode("AAPL_Spot", 150.0)
tsla_spot = MarketDataNode("TSLA_Spot", 250.0)

# 2. Build Two Independent Option Positions
aapl_call = EuropeanOption(
    name="AAPL_155C",
    spot_node=aapl_spot,
    strike_node=MarketDataNode("AAPL_K", 155.0),
    time_node=MarketDataNode("AAPL_T", 30 / 365.0),
    rate_node=rate,
    vol_node=MarketDataNode("AAPL_Vol", 0.20),
    option_type=pricing_engine.OptionType.Call,
    quantity=100.0,
)

tsla_put = EuropeanOption(
    name="TSLA_240P",
    spot_node=tsla_spot,
    strike_node=MarketDataNode("TSLA_K", 240.0),
    time_node=MarketDataNode("TSLA_T", 45 / 365.0),
    rate_node=rate,
    vol_node=MarketDataNode("TSLA_Vol", 0.45),
    option_type=pricing_engine.OptionType.Put,
    quantity=50.0,
)

# 3. Wire into Portfolio Book
book = PortfolioBook("Tech_Derivatives")
book.add_option(aapl_call)
book.add_option(tsla_put)

print("--- 1. Initial Valuation (Both C++ nodes execute once) ---")
print(book.get_snapshot())
print(f"C++ eval counts -> AAPL: {aapl_call.pricer_node.eval_count}, TSLA: {tsla_put.pricer_node.eval_count}")

print("\n--- 2. AAPL Spot Ticks to 152.50 (Only AAPL should recalculate) ---")
aapl_spot.update_value(152.50)
print(book.get_snapshot())
print(f"C++ eval counts -> AAPL: {aapl_call.pricer_node.eval_count}, TSLA: {tsla_put.pricer_node.eval_count}")