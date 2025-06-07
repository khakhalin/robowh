"""Robot class."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random

from robowh.universe import Universe
from robowh.utils import grid_codes

universe = Universe.get_universe()

class Robot:
    """A robot in the universe."""

    def __init__(self, name, strategy):
        logger.debug(f"Spawning a new robot: {name}")
        self.name = name
        self.strategy = strategy
        self.x = None
        self.y = None
        self.state = 'idle' # idle, working, error - related to task assignment
        self.substate = 'moving'  # moving, confused, loading - related to subtasks
        self.target = None
        self.program = []  # Placeholder for a sequence of steps in the queue

        self._set_position(universe.random_empty_position())

    def _set_position(self, position):
        """Set the robot's position in the universe."""
        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Position must be a tuple of (x, y) coordinates.")
        self.x, self.y = position
        universe.grid[self.x, self.y] = grid_codes['robot']
        logger.debug(f"Robot {self.name} set to position ({self.x}, {self.y})")

    def move(self):
        """Request a random move."""
        movement = self.strategy.calculate_path(
            current_pos=(self.x, self.y), target_pos=(0, 0), n_steps=1)[0]
        new_x = self.x + movement[0]
        new_y = self.y + movement[1]

        if universe.grid_is_free(new_x, new_y):
            universe.grid[self.x, self.y] = grid_codes['empty']
            self.x, self.y = new_x, new_y
            universe.grid[self.x, self.y] = grid_codes['robot']
            # Technically reaching into the grid directly from the robot is a questionable
            # design choice, but let's consider it a case of bare-bones "observer pattern";
            # we're just communicating the change to the universe.
            self.substate = 'moving'
        else:
            universe.grid[self.x, self.y] = grid_codes['confused']
            self.substate = 'confused'
