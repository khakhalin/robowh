"""Storage shelves."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
from typing import List, Tuple, Optional
import uuid

from robowh.universe import Universe
from robowh.utils import grid_codes
from robowh.strategies import MoveStrategy


class Shelves():

    def __init__(self, name=None):
        logger.info("Shelves object created")
        self.name:Optional[str] = name
        self.records:dict[str:int] = {}  # To search shelves by product
        self.coords:List[Tuple[int]] = []  # Coordinates of every shelf
        self.inventory:List = []  # What is stored in every shelf
        self.n_items = 0

        self.universe = Universe.get_universe()

    def add_shelf(self, point: Tuple[int], empty=False):
        """Create a shelf at given coordinates.

        By default, we'll be creating shelves that are filled in 50% of cases. It's not a perfect
        sepataion of concerns, but it's useful in practice.
        """
        logger.debug(f"Creating a shelf at {point}")
        x,y = point[0], point[1]
        if self.universe.grid[x, y] != 0:
            logger.error(f"Cannot create a shelf: point {point} is occupied!")
            return

        self.coords.append(point)
        cell_id = len(self.coords)-1
        # Create  shelf
        self.universe.grid[x, y] = grid_codes['shelf']
        self.inventory.append(None)
        if not empty and np.random.uniform() > 0.5:
            item_code = uuid.uuid4().hex[:8]  # Generate hex-based ID (32 characters)
            self.place_at(cell_id, item_code)


    def place_at(self, index:int, product:str):
        """Place item (hash) product at index index."""
        logger.info(f"Product {product} is placed at index {index} on {self.name}")
        if index >= len(self.coords):
            raise ValueError(f"Requested index {index} is out of bounds ({len(self.coords)}) " +
                             f"for shelves {self.name}")
        if self.inventory[index] is not None:
            raise ValueError(f"Index {index} at shelves {self.name} is already taken.")
        if product in self.records:
            # TODO: There should be a better way to handle that, but for now let's just fail
            raise ValueError(f"Product {product} is already present in shelves {self.name}")
        x,y = self.coords[index]
        if self.universe.grid[x,y] != grid_codes['shelf']:
            raise ValueError(f"Even though pos {index} at shelf {self.name} is empty, " +
                             f"it's marked non-empty on the map!")

        self.inventory[index] = product
        self.n_items += 1
        self.records[product] = index
        self.universe.grid[x,y] = grid_codes['item']


    def clear(self, index:int):
        """Place item (hash) product at index index."""
        logger.info(f"Clear index {index} in shelf {self.name}")
        if index >= len(self.coords):
            raise ValueError(f"Index {index} out of bounds ({len(self.coords)}) for {self.name}")
        if self.inventory[index] is None:
            raise ValueError(f"Can't clear {index} at shelves {self.name}: it's empty.")

        x,y = self.coords[index]
        if self.universe.grid[x,y] != grid_codes['item']:
            raise ValueError(f"Even though pos {index} at shelf {self.name} is taken, " +
                             f"it's marked empty on the map!")

        product = self.inventory[index]
        self.inventory[index] = None
        self.n_items -= 1
        del self.records[product]
        self.universe.grid[x,y] = grid_codes['shelf']


    def place_optimally(self, product:str):
        """Find the closest empty number and store there."""
        logger.debug(f"Product {product} stored optimally at shelves {self.name}")
        try:
            index = self.inventory.index(None)
        except ValueError:
            raise ValueError(f"The shelf {self.name} is full, cannot find an empty slot")
        self.place_at(index, product)