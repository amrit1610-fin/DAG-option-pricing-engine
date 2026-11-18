from abc import ABC, abstractmethod
from typing import List, Any, Callable

class Node(ABC):
    "Abstract base class for node of a DAG"
    def __init__(self, name: str):
        self.name = name
        self.value: Any = None
        self.is_dirty: bool = None
        self.observers = List['Node'] = []

    def add_observer(self, node: 'Node') -> None:
        "Add an observer to a parent node"
        if node not in self.observers:
            self.observers.append(node)
        
    def notify_observers(self) -> None:
        "Pushes the 'dirty' state up the graph"
        for obs in self.observers:
            if not in obs.is_dirty:
                obs.mark_dirty()

    def mark_dirty(self) -> None:
        "Marks node for recalculation"
        self.is_dirty = True
        self.notify_observers()

    @abstractmethod
    def get_value(self) -> Any:
        "Returns node's value"
        pass

class MarketDataNode(Node):
    """
    Node representing market variables: spot, rates, volatility, etc.
    """
    def __init__(self, name: str, initial_value: float = 0.0):
        super().__init__(name)
        self.value = initial_value
        self.is_dirty = False

    def update_value(self, new_value: float) -> None:
        "Updates market data if needed"
        if self.value != new_value:
            self.value = new_value
            self.notify_observers()
        
    def get_value(self) -> float:
        return self.value


class CalculationNode(Node):
    """
    Class for performing calculations based on changed market variables
    Lazy evaluation: execution only occurs if a dependency is changed
    """
    def __init__(self, name: str, calc_func: Callable, *dependencies: Node):
        super().__init__(name)
        self.calc_func = calc_func
        self.dependencies = dependencies

        for dep in self.dependencies:
            dep.add_observer(self)

    def get_value(self) -> Any:
        if self.is_dirty:
            inputs = [dep.get_value() for dep in self.dependencies]
            self.value = self.calc_function(*inputs)
            self.is_dirty = False
        return self.value