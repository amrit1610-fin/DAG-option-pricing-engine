# reactive_pricing_engine/dag_engine/portfolio.py

from typing import List, Dict
from .node import CalculationNode, Node


class PortfolioRiskNode(CalculationNode):
    """
    A specialized aggregator node representing a single portfolio risk metric.
    It sums up the values (e.g., Prices, Deltas, Gammas) of all child position nodes.
    """
    def __init__(self, name: str, position_nodes: List[Node]):
        def sum_positions(*node_values):
            return sum(node_values)

        super().__init__(name, sum_positions, *position_nodes)
        self.position_nodes = list(position_nodes)

    def add_position(self, node: Node) -> None:
        """Dynamically adds a new position to the portfolio DAG."""
        if node not in self.position_nodes:
            self.position_nodes.append(node)
            self.dependencies = tuple(self.position_nodes)
            node.add_observer(self)
            self.mark_dirty()

    def get_risk_summary(self) -> Dict[str, float]:
        """Forces evaluation and returns the total aggregated value."""
        return {
            "portfolio_name": self.name,
            "total_value": self.get_value(),
            "position_count": len(self.position_nodes),
        }


class PortfolioBook:
    """
    Manages the six independent treetop PortfolioRiskNodes (NPV + 5 Greeks)
    so incompatible financial units are never mixed.
    """
    def __init__(self, name: str):
        self.name = name
        self.positions = []

        self.npv_node   = PortfolioRiskNode(f"{name}_NPV",   [])
        self.delta_node = PortfolioRiskNode(f"{name}_Delta", [])
        self.gamma_node = PortfolioRiskNode(f"{name}_Gamma", [])
        self.vega_node  = PortfolioRiskNode(f"{name}_Vega",  [])
        self.theta_node = PortfolioRiskNode(f"{name}_Theta", [])
        self.rho_node   = PortfolioRiskNode(f"{name}_Rho",   [])

    def add_option(self, option) -> None:
        """Wires an option's extractor nodes into the portfolio's risk treetops."""
        self.positions.append(option)
        self.npv_node.add_position(option.price_node)
        self.delta_node.add_position(option.delta_node)
        self.gamma_node.add_position(option.gamma_node)
        self.vega_node.add_position(option.vega_node)
        self.theta_node.add_position(option.theta_node)
        self.rho_node.add_position(option.rho_node)

    def get_snapshot(self) -> Dict[str, float]:
        """Lazily evaluates only dirty branches and returns full portfolio risk."""
        return {
            "NPV":   self.npv_node.get_value(),
            "Delta": self.delta_node.get_value(),
            "Gamma": self.gamma_node.get_value(),
            "Vega":  self.vega_node.get_value(),
            "Theta": self.theta_node.get_value(),
            "Rho":   self.rho_node.get_value(),
        }