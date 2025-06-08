"""Universe object: it runs time and physics."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
import time
import threading

from robowh.utils import grid_codes
from robowh.strategies import StrategyLibary
from robowh.scheduler import Scheduler
from robowh.orchestrator import Orchestrator

class Universe:
    """A singleton Universe object."""
    _instance = None

    def __new__(cls, *args, **kwargs):
        """CLassic singleton pattern."""
        if cls._instance is None:
            cls._instance = super(Universe, cls).__new__(cls)
            cls._instance._init()
        return cls._instance

    @classmethod
    def get_universe(cls):
        return cls._instance or cls()

    # TODO: Move these constants to some config file
    MAX_UPDATE_TIME = 0.1  # 10 ms
    GRID_SIZE = 100
    N_ROBOTS = 70
    RACK_SPACING = 15

    def _init(self):
        logger.info("Spawning a new universe (but not starting it yet)")
        self.lock = threading.Lock()

        # Connect global objects here
        self.strategy_library = StrategyLibary()
        self.scheduler = Scheduler(self)
        self.orchestrator = Orchestrator(self)

        # Create the structure of the WH
        self.grid = self.create_racks()

        # Robots
        self.robots = []
        from robowh.robot import Robot  # Deferred import to avoid circular dependency
        for i in range(self.N_ROBOTS):
            robot = Robot(
                name=f"Robot_{i+1}",
                strategy=self.strategy_library.random
                )
            self.robots.append(robot)

        # Set tracking numbers (temporary? Should go to the Observer class?)
        self.diagnostic_number = 0.0  # A toy example for now


    def create_racks(self):
        """Create a grid with empty positions and racks."""
        logger.info("Creating the grid of racks")
        grid = np.full((self.GRID_SIZE, self.GRID_SIZE), grid_codes['empty'], dtype=int)

        # Set up racks as vertical lines padded by empty spaces, and equally spaced.
        # We have some magic numbers here, to make the picture prettier. Sorry!
        for j in range(self.RACK_SPACING, self.GRID_SIZE, self.RACK_SPACING):
            if j + 1 < self.GRID_SIZE:
                for i in range(self.RACK_SPACING*2, self.GRID_SIZE - self.RACK_SPACING):
                    grid[i, j] = grid_codes['rack']
        return grid

    def start_universe(self):
        """Starting the universe."""
        logger.info("Starting the time in the universe!")
        def update_universe():
            while True:
                start_time = time.time()

                # Update diagnostic number
                with self.lock:
                    self.diagnostic_number += random.uniform(-0.01, 0.01)

                # Rearrange robots randomly, to not have favorites during bottlenecking
                sequence = random.sample(range(len(self.robots)), len(self.robots))
                for i in sequence:
                    if time.time() - start_time < self.MAX_UPDATE_TIME:
                        robot = self.robots[i]
                        with self.lock:
                            robot.move()

                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.MAX_UPDATE_TIME - elapsed_time)
                time.sleep(sleep_time)

        thread = threading.Thread(target=update_universe, daemon=True)
        thread.start()

    def random_empty_position(self):
        """Get a random empty position in the grid."""
        with self.lock:
            empty_positions = np.argwhere(self.grid == grid_codes['empty'])
            if empty_positions.size == 0:
                raise ValueError("No empty positions available in the grid.")
            position = random.choice(empty_positions)
            return tuple(position)

    def grid_is_free(self, x, y):
        """Try to move robot to new position. Return success/failure."""
        if (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE):
            if self.grid[x, y] == grid_codes['empty']:
                return True
        return False