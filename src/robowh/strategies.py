"""Pathfinding strategies for robots."""

from abc import ABC, abstractmethod
from typing import List, Tuple
import random

class StrategyLibary():
    """An instance of this class would contain an each strategy."""
    def __init__(self):
        _strategies = {
            'astar': AStarStrategy,
            'random': RandomMovementStrategy
        }
        for name, strategy in _strategies.items():
            setattr(self, name, strategy)


class MoveStrategy(ABC):
    @classmethod
    @abstractmethod
    def calculate_path(cls,
        current_pos: Tuple[int, int], target_pos: Tuple[int, int], n_steps: int = 0
        ) -> List[Tuple[int, int]]:
        pass

    def __init__(self):
        pass


class RandomMovementStrategy(MoveStrategy):
    @classmethod
    def calculate_path(cls,current_pos, target_pos, n_steps=1):
        # Random wiggling in place
        plan = []
        for i in range(n_steps):
            # We have to use random, as numpy is confused by a list of tuples
            random_movement = random.choice([(-1,0), (1,0), (0,-1), (0,1)])
            plan.append(random_movement)
        return plan


class AStarStrategy(MoveStrategy):
    @classmethod
    def calculate_path(cls, current_pos, target_pos, n_steps=0):
        return [(0,0), (1,1)]  # Stub

