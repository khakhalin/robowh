"""Storage shelves."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
from typing import List, Tuple, Optional, Set

from robowh.universe import Universe
from robowh.utils import grid_codes


class Shelves():

    def __init__(self, name=None, deep=False) -> None:
        logger.info("Shelves object created")
        self.name:Optional[str] = name
        self.deep:bool = deep  # Deep shelves store more than one item in a cell

        self.n_items:int = 0
        self.records:dict[str:int] = {}  # To search shelves by product
        self.coords:List[Tuple[int]] = []  # Coordinates of every shelf
        self.inventory:List[List[str]] = []  # What is stored in every shelf
        self.locked_indices:list[bool] = []  # Cells are booked for r/w to avoid conflicts
        self.locked_products:Set[str] = set({})  # Products that were promised for picking

        self.universe:Universe = Universe.get_universe()

    def add_shelf(self, point: Tuple[int], empty=False) -> None:
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
        self.locked_indices.append(False)
        if not empty and np.random.uniform() > 0.5:
            item_code = self.universe.new_code()
            self.place_at(cell_id, item_code)


    def place_at(self, index:int, product:str) -> None:
        """Place item (hash) product at index index."""
        logger.info(f"Product {product} is placed at index {index} on {self.name}")
        # Check if the shelf exists
        if index >= len(self.coords):
            raise ValueError(f"Requested index {index} is out of bounds ({len(self.coords)}) " +
                             f"for shelves {self.name}")

        # Check if there's space on the shelf (not deep shelves, and something is there already)
        if (not self.deep) and (self.inventory[index]):
            cell_content = self.inventory[index]
            raise ValueError(f"Index {index} at shelves {self.name} is already taken " +
                             f"by product {cell_content}")

        # Check if product is unique
        # TODO: There are obviously better ways to handle that, but for now let's just fail
        if product in self.records:
            raise ValueError(f"Product {product} is already present in shelves {self.name}")

        # Check if grid is in an illegal state (strictly speaking grid's problem, but let's check)
        x,y = self.coords[index]
        if (not self.deep) and (self.universe.grid[x,y] != grid_codes['shelf']):
            raise ValueError(f"Even though pos {index} at shelf {self.name} is empty, " +
                             f"it's marked as occupied on the map.")

        self.inventory[index].append(product)  # We always store lists of strings, not bare strings
        self.n_items += 1
        self.records[product] = index
        self.universe.grid[x,y] = grid_codes['item']
        self.unlock(index)


    def remove(self, index:int, product:str) -> None:
        """Place item (hash) product at index index."""
        logger.info(f"Remove {product} from shelf {self.name} pos {index}")
        if index >= len(self.coords):
            raise ValueError(f"Index {index} out of bounds ({len(self.coords)}) for {self.name}")
        if not self.inventory[index]:  # Empty list
            raise ValueError(f"Can't clear {product} from {self.name} #{index}: it's empty.")
        if product not in self.inventory[index]:
            raise ValueError(f"Can't find {product} in {index} of {self.name}")

        x,y = self.coords[index]
        if self.universe.grid[x,y] != grid_codes['item']:
            raise ValueError(f"Even though pos {index} at shelf {self.name} is occupied, " +
                             f"it's marked empty on the map.")

        self.inventory[index].remove(product)
        self.n_items -= 1
        del self.records[product]
        if not self.inventory[index]:  # The shelf is empty now
            self.universe.grid[x,y] = grid_codes['shelf']
        self.unlock(index, product)

    def request_optimal_placement(self) -> int:
        """Find the closest empty number and store there."""
        logger.debug(f"Requesting optimal location at shelves {self.name}")
        try:
            # Find the first UNLOCKED position with an empty list in it.
            # As two simple python lists are involved, it's not a very effective operation.
            # The awkward construction below helps somewhat, but it looks too complex.
            index = next(
                (
                    i
                    for i, (inv, lck)
                    in enumerate(zip(self.inventory, self.locked_indices))
                    if not inv and not lck
                ),
                None
            )
            # We're assuming here that shelves are created in a correct order, starting from
            # loading bays and going away from them. Could be a differet logic of course.
        except ValueError:
            raise ValueError(f"The shelf {self.name} is full, cannot find an empty slot")
        return index

    def pick_random_product_for_delivery(self) -> str:
        """IRL it would not be a good method, but for us it's a substitute for realistic orders."""
        products = [p for pl in self.inventory for p in pl if p not in self.locked_products]
        if not products:
            logger.warning(f"Requesting a random object off {self.name}, but the shelf is empty.")
            return None
        return random.choice(products)

    def lock(self, index:int, product:str=None) -> None:
        """Lock a cell (index) and (optionally) a product for task creation."""
        logger.debug(f"Locking cell {self.name} pos {index}")
        self.locked_indices[index] = True
        if product is not None:
            self.locked_products.add(product)

    def unlock(self, index:int, product:str=None) -> None:
        """Unlock a cell (index) for operations."""
        logger.debug(f"Unlocking cell {self.name} pos {index}")
        self.locked_indices[index] = False
        if product is not None:
            if product in self.locked_products:
                self.locked_products.remove(product)
            else:
                logger.debug("Requested to unlock {product} from {self.name}, but it's not locked.")