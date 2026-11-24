import pricing_engine
from .node import MarketDataNode, CalculationNode


class EuropeanOption:
    """
    Wires a single option into the DAG:
      - 1 Heavy CalculationNode calling the compiled C++ pricing_engine
      - 6 Lightweight Extractor Nodes (price, delta, gamma, vega, theta, rho)
    """
    def __init__(
        self,
        name: str,
        spot_node: MarketDataNode,
        strike_node: MarketDataNode,
        time_node: MarketDataNode,
        rate_node: MarketDataNode,
        vol_node: MarketDataNode,
        option_type: pricing_engine.OptionType = pricing_engine.OptionType.Call,
        quantity: float = 1.0,
    ):
        self.name = name
        self.quantity = quantity
        self.option_type = option_type

        # 1. Heavy Math Node (C++ single-pass Black-Scholes)
        def _cpp_pricer(S: float, K: float, T: float, r: float, sigma: float):
            return pricing_engine.calculate_black_scholes(
                S, K, T, r, sigma, self.option_type
            )

        self.pricer_node = CalculationNode(
            f"{name}_CPP_Engine",
            _cpp_pricer,
            spot_node,
            strike_node,
            time_node,
            rate_node,
            vol_node,
        )

        # 2. Lightweight Extractor Nodes (zero transcendental math, scaled by position size)
        q = self.quantity
        self.price_node = CalculationNode(f"{name}_Price", lambda m: m.price * q, self.pricer_node)
        self.delta_node = CalculationNode(f"{name}_Delta", lambda m: m.delta * q, self.pricer_node)
        self.gamma_node = CalculationNode(f"{name}_Gamma", lambda m: m.gamma * q, self.pricer_node)
        self.vega_node  = CalculationNode(f"{name}_Vega",  lambda m: m.vega  * q, self.pricer_node)
        self.theta_node = CalculationNode(f"{name}_Theta", lambda m: m.theta * q, self.pricer_node)
        self.rho_node   = CalculationNode(f"{name}_Rho",   lambda m: m.rho   * q, self.pricer_node)