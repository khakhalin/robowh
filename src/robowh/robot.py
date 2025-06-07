"""Robot class."""

import logging
logger = logging.getLogger(__name__)

import numpy as np

from robowh.utils import grid_codes

class Robot:
    """A robot in the universe."""

    def __init__(self, name, universe):
        logger.debug(f"Spawning a new robot: {name}")
        self.name = name
        self.universe = universe
        self.x, self.y = self.universe.random_empty_position()
        self.universe.grid[self.x, self.y] = grid_codes['robot']

    def move(self):
        """Request a random move."""
        new_x = self.x + np.random.randint(-1, 2)
        new_y = self.y + np.random.randint(-1, 2)

        if self.universe.grid_is_free(new_x, new_y):
            self.universe.grid[self.x, self.y] = grid_codes['empty']
            self.x, self.y = new_x, new_y
            self.universe.grid[self.x, self.y] = grid_codes['robot']
            # Technically reaching into the grid directly from the robot is a questionable
            # design choice, but let's consider it a case of bare-bones "observer pattern";
            # we're just communicating the change to the universe.
