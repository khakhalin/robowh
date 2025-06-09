"""Pathfinding strategies for robots."""

import logging
logger = logging.getLogger(__name__)

import random
from abc import ABC, abstractmethod
from typing import List, Tuple

from robowh.universe import Universe
from robowh.utils import grid_codes
from robowh import astar

class StrategyLibary():
    """An instance of this class contains each strategy, as a class."""
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
    def calculate_path(cls, current_pos, target_pos, n_steps=1):
        # Random wiggling in place
        plan = []
        for i in range(n_steps):
            # We have to use random, as numpy is confused by a list of tuples
            random_movement = random.choice([(-1,0), (1,0), (0,-1), (0,1)])
            plan.append(random_movement)
        return plan


class AStarStrategy(MoveStrategy):
    @classmethod
    def calculate_path(cls, current_pos, target_pos, n_steps=20, until_touch=True):
        """Calculate a path from current to target, and return n_steps of it.

        Note that the default n_steps is set to 20, as our current implementation is that
        if the robot is blocked, a pixel-sized movement is wasted, and the robot continues
        with the NEXT step. It doesn't retry to step. Which means that they may end up in a wrong
        isle unless we recalculat the path every now and then.

        If `until_touch` is True, it's enough for the path to reach a pixel near the target pixel.
        It's true by default, so that robots could reach shelves and loading bays.
        """
        universe = Universe.get_universe()
        grid = universe.grid.copy()  # Get environment from singleton

        # Input validation
        if not cls._valid_pos(grid, current_pos):
            logger.warning(f"Current position {current_pos} is not valid for Astar!!")
            return []
        if not cls._valid_pos(grid, target_pos):
            logger.warning(f"Target position {target_pos} is not valid for Astar!")
            return []

        # Get path from A* core
        path = astar.find_path(grid, current_pos, target_pos, until_touch)
        if len(path)==0: # Astar didn't find a path
            logger.warning(f"A-star could not find a path from {current_pos} to {target_pos}!")

        # Convert to movement deltas
        deltas = cls._path_to_deltas(path)

        # Apply step limit
        return deltas[:n_steps] if n_steps > 0 else deltas

    @staticmethod
    def _path_to_deltas(path):
        return [
            (path[i][0]-path[i-1][0], path[i][1]-path[i-1][1])
            for i in range(1, len(path))
        ]

    @staticmethod
    def _valid_pos(grid, pos):
        y, x = pos
        # We accept all grid states as targets: even though we cannot travel inside a rack
        # or a robot, we may have to travel to it, and step one pixel early.
        return (0 <= y < grid.shape[0]) and (0 <= x < grid.shape[1])
