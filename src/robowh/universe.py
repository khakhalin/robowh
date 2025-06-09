"""Universe object: it runs time and physics."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
import time
import threading

from robowh.utils import grid_codes

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
    GRID_SIZE = 30
    N_ROBOTS = 3
    RACK_SPACING = 7

    def _init(self):
        logger.info("Spawning a new universe (but not starting it yet)")
        self.lock = threading.Lock()

        # Ugly deferred imports to avoid circular dependencies
        from robowh.robot import Robot  # Deferred import to avoid circular dependency
        from robowh.strategies import StrategyLibary
        from robowh.scheduler import Scheduler
        from robowh.orchestrator import Orchestrator
        from robowh.shelves import Shelves

        # Connect global objects here
        self.strategy_library = StrategyLibary()
        self.scheduler = Scheduler(self)
        self.orchestrator = Orchestrator(self)

        # Create the structure of the WH
        self.grid = np.full((self.GRID_SIZE, self.GRID_SIZE), grid_codes['empty'], dtype=int)
        self.shelves = Shelves("racks")
        self.setup_shelves()
        self.bays = Shelves("bays", deep=True)
        self.setup_loading_bays()

        # Robots
        self.robots = []
        for i in range(self.N_ROBOTS):
            robot = Robot(
                name=f"R{i+1:03d}",
                strategy=self.strategy_library.astar
                )
            self.robots.append(robot)

        # Set tracking numbers (temporary? Should go to the Observer class?)
        self.diagnostic_number = 0.0  # A toy example for now


    def setup_shelves(self):
        """Create a grid of storage racks."""
        logger.info("Creating the grid of racks")
        # Set up racks as vertical lines padded by empty spaces, and equally spaced.
        # We have some magic numbers here, to make the picture prettier. Sorry!
        gap = self.RACK_SPACING // 2
        for j in range(gap, self.GRID_SIZE, self.RACK_SPACING):
            if j < self.GRID_SIZE-gap:
                for i in range(self.RACK_SPACING + gap, self.GRID_SIZE - gap):
                    self.shelves.add_shelf((i, j))
                    self.shelves.add_shelf((i, j+1))

        # Remember current stock, and make the orchestrator try to maintain it
        self.orchestrator.target_inventory = self.shelves.n_items


    def setup_loading_bays(self):
        """Create a line of loading bays."""
        logger.info("Creating the grid of loading bays")
        gap = self.RACK_SPACING // 2
        for j in range(gap, self.GRID_SIZE, gap):
            if j < self.GRID_SIZE-gap*0.7:
                self.bays.add_shelf((0, j), empty=True)


    def start_universe(self):
        """Starting the universe."""
        logger.info("Big bang: kicking-off timeline in the universe!")
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
                            robot.act()

                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.MAX_UPDATE_TIME - elapsed_time)
                time.sleep(sleep_time)

        thread = threading.Thread(target=update_universe, daemon=True)
        thread.start()

    def random_empty_position(self):
        """Get a random empty position in the grid."""
        empty_positions = np.argwhere(self.grid == grid_codes['empty'])
        if empty_positions.size == 0:
            raise ValueError("No empty positions available in the grid.")
        position = random.choice(empty_positions)
        position = [int(c) for c in position] # Numpy integers are annoying, cast to int
        return tuple(position)

    def grid_is_free(self, x, y):
        """Try to move robot to new position. Return success/failure."""
        if (0 <= x < self.GRID_SIZE and 0 <= y < self.GRID_SIZE):
            if self.grid[x, y] == grid_codes['empty']:
                return True
        return False