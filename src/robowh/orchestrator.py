"""The Orchestrator rules the WH, manages the inventory, assigns tasks to robots."""

import logging
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING
import numpy as np
import random

from robowh.robot import Robot
from robowh.universe import Universe


class Orchestrator:
    """The Orchestrator is the main controller of the Robotic Warehouse Simulator."""

    def __init__(self, universe: Universe):
        logger.info("Starting the Orchestrator")
        self.universe = universe
        self.idle_robots = []  # A list of idling robots (not IDs, but object references)

        self.target_inventory:int = 1  # Will be updated during racks creation; can be changed later
        self.mode:str = 'both'  # both, pick, or store


    def process_request_for_service(self, robot: Robot):
        """A robot has become idle and is asking for a new job."""
        logger.info(f"{robot.name} requesting a new task")
        # For now, let's just give them orders to move to random parts of the WH,
        # to test the movement logic.

        success = self.create_delivery_task(robot)

        # The part below is only rechable if we run out of tasks (out of goods to move), and
        # we arrive here with `success` set to False
        if not success:
            if self.universe.scan(robot.x, robot.y):
                # We ran out of tasks near a rack. That's not good. Relocate! (anywhere else)
                logger.info(f"{robot.name} tried to idle near the rack, but thats prohibited.")
                self.create_random_movement_task(robot)
            else:
                if (robot not in self.idle_robots):
                    logger.info(f"{robot.name} is set to idle")
                    self.idle_robots.append(robot)


    def create_delivery_task(self, robot: Robot):
        """Create a random storage or retrieval task."""
        # Decide whether we pick or store, depending on the mode of operation
        # (coming from the JS UI).
        if self.mode == "both":
            if self.universe.shelves.n_items < self.target_inventory:
                operation = "store"
            else:
                operation = "pick"
        else:
            operation = self.mode

        if operation == "store":
            # Create a storage order
            product = self.universe.bays.pick_random_product_for_delivery()
            if product is None: # We failed to create an order
                return False  # Try to set the robot to idle

            bay_id = self.universe.bays.records[product]
            bx,by = self.universe.bays.coords[bay_id]
            self.universe.bays.lock(bay_id, product)  # Lock the product

            shelf_id = self.universe.shelves.request_optimal_placement()
            sx,sy = self.universe.shelves.coords[shelf_id]
            self.universe.shelves.lock(shelf_id, None)  # Lock the space

            robot.assign_task("transfer", origin=(bx,by), destination=(sx,sy), product=product)
            self.universe.observer.count_task()

        else:  # operation == "pick"
            # Create a retrieval order
            product = self.universe.shelves.pick_random_product_for_delivery()
            if product is None: # We failed to create an order
                return False  # Try to set the robot to idle

            shelf_id = self.universe.shelves.records[product]
            x,y = self.universe.shelves.coords[shelf_id]
            self.universe.shelves.lock(shelf_id, product)  # Lock the product

            bay_id = np.random.randint(len(self.universe.bays.inventory))
            bx,by = self.universe.bays.coords[bay_id]
            # No need to lock a bay - they are assumed to have infinite capacity

            robot.assign_task("transfer", origin=(x,y), destination=(bx,by), product=product)
            self.universe.observer.count_task()
            # We don't remove the product from loading bays afterwards,
            # we let it stay there. It's obviously not what's happening to products IRL,
            # but it's good enough for our purposes,  as we'll need to store something
            # from the bays to the shelves at some later point anyways.

        return True


    def create_random_movement_task(self, robot: Robot):
        """Pick a random position within the WH and move the robot there."""
        random_position = self.universe.random_empty_position()
        robot.assign_task("reposition", origin=None, destination=random_position)
        return


    def find_idle_robot(self):
        """Find one idle robot from the stack."""
        # TODO: Make it adaptive to the coordinates of where the robot is needed.
        return random.choice(self.idle_robots) if self.idle_robots else None