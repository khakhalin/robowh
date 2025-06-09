"""Storage shelves."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
from typing import List, Tuple, Optional

from robowh.universe import Universe
from robowh.utils import grid_codes


class Shelves():

    def __init__(self, name=None, deep=False):
        logger.info("Shelves object created")
        self.name:Optional[str] = name
        self.deep:bool = deep  # Deep shelves store more than one item in a cell

        self.n_items:int = 0
        self.records:dict[str:int] = {}  # To search shelves by product
        self.coords:List[Tuple[int]] = []  # Coordinates of every shelf
        self.inventory:List[List[str]] = []  # What is stored in every shelf
        self.lock:list[bool] = []  # Cells are locked for placement and picking to avoid conflicts

        self.universe:Universe = Universe.get_universe()

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
        self.inventory.append([])
        self.lock.append(False)
        if not empty and np.random.uniform() > 0.5:
            item_code = self.universe.new_code()
            self.place_at(cell_id, item_code)


    def place_at(self, index:int, product:str):
        """Place item (hash) product at index index."""
        logger.info(f"Product {product} is placed at index {index} on {self.name}")
        # Check if the shelf exists
        if index >= len(self.coords):
            raise ValueError(f"Requested index {index} is out of bounds ({len(self.coords)}) " +
                             f"for shelves {self.name}")

        # Check if there's space on the shelf (not deep shelves, and something is there already)
        if (not self.deep) and (self.inventory[index]):
            raise ValueError(f"Index {index} at shelves {self.name} is already taken.")

        # Check if product is unique
        # TODO: There are obviously better ways to handle that, but for now let's just fail
        if product in self.records:
            raise ValueError(f"Product {product} is already present in shelves {self.name}")

        # Check if grid is in an illegal state (strictly speaking grid's problem, but let's check)
        x,y = self.coords[index]
        if (not self.deep) and (self.universe.grid[x,y] != grid_codes['shelf']):
            raise ValueError(f"Even though pos {index} at shelf {self.name} is empty, " +
                             f"it's marked non-empty on the map!")

        self.inventory[index].append(product)  # We always store lists of strings, not bare strings
        self.n_items += 1
        self.records[product] = index
        self.universe.grid[x,y] = grid_codes['item']
        self.lock[index] = False


    def remove(self, index:int, product:str):
        """Place item (hash) product at index index."""
        logger.info(f"Clear index {index} in shelf {self.name}")
        if index >= len(self.coords):
            raise ValueError(f"Index {index} out of bounds ({len(self.coords)}) for {self.name}")
        if not self.inventory[index]:  # Empty list
            raise ValueError(f"Can't clear {product} from {self.name} #{index}: it's empty.")
        if product not in self.inventory[index]:
            raise ValueError(f"Can't find {product} in {index} of {self.name}")

        x,y = self.coords[index]
        if self.universe.grid[x,y] != grid_codes['item']:
            raise ValueError(f"Even though pos {index} at shelf {self.name} is taken, " +
                             f"it's marked empty on the map!")

        self.inventory[index].remove(product)
        self.n_items -= 1
        del self.records[product]
        if not self.inventory[index]:  # The shelf is empty now
            self.universe.grid[x,y] = grid_codes['shelf']
        self.lock[index] = False


    def place_optimally(self, product:str):
        """Find the closest empty number and store there."""
        logger.debug(f"Product {product} stored optimally at shelves {self.name}")
        try:
            index = self.inventory.index([])  # Find the first position with an empty list in it
        except ValueError:
            raise ValueError(f"The shelf {self.name} is full, cannot find an empty slot")
        self.place_at(index, product)


    def pick_random_product_for_delivery(self):
        """IRL it would not be a good method, but for us it's a substitute for realistic orders."""
        products = [self.inventory[i] for i in range(len(self.inventory)) if not self.lock[i]]
        products = [p for sublist in products for p in sublist]
        if not products:
            logger.warning(f"Requesting a random object off {self.name}, but the shelf is empty.")
            return None
        return random.choice(products)