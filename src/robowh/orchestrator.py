"""The Orchestrator rules the WH, manages the inventory, assigns tasks to robots."""

import logging
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING
import random

from robowh.robot import Robot
from robowh.universe import Universe


class Orchestrator:
    """The Orchestrator is the main controller of the Robotic Warehouse Simulator."""

    def __init__(self, universe: Universe):
        logger.info("Starting the Orchestrator")
        self.universe = universe
        self.idle_robots = []  # A list of idling robots (not IDs, but object references)

        self.target_inventory = 1  # Will be updated during racks creation; can be changed later


    def process_request_for_service(self, robot: Robot):
        """A robot has become idle and is asking for a new job."""
        logger.info(f"{robot.name} requesting a new task")
        # For now, let's just give them orders to move to random parts of the WH,
        # to test the movement logic.

        self.create_delivery_task(robot)

        # This part is currently unreachable, as for now we immediately give tasks to all robots
        # But once we move to actual operations, we'll start coin-tossing in scheduler, and then
        # some robots will become idle.
        if robot not in self.idle_robots:
            logger.info(f"{robot.name} is set to idle")
            self.idle_robots.append(robot)
            return


    def create_delivery_task(self, robot: Robot):
        """Create a random store or retrieval task."""
        # Pseudocode:
        # 1. Check with the Scheduler if there are orders in the queue.
        #   If there's an order, assign it to the robot.
        #   (Although we could also check the coordinates, and sometimes take the bettss, that
        #   maybe a beter robot, with better coordinates, will become idle soon.)
        # 2. If no ready orders, we could consider moving the robot to a more advantagious position
        #   (e.g., closer to the docks, or to a more central position).
        # 3. If no need to move, register the robot as idle and wait for the next order.
        if self.universe.shelves.n_items < self.target_inventory:
            # Create a storage order
            self.create_random_movement_task(robot)
        else:
            # Create a retrieval order
            # Pick
            product = random.choice([k for k in self.universe.shelves.records.keys()])
            shelf_id = self.universe.shelves.records[product]
            x,y = self.universe.shelves.coords[shelf_id]
            logger.warning(f"{product}, {x}, {y}")
            robot.assign_task("reposition", origin=None, destination=(x,y))


    def create_random_movement_task(self, robot: Robot):
        """Pick a random position within the WH and move the robot there."""
        random_position = self.universe.random_empty_position()
        robot.assign_task("reposition", origin=None, destination=random_position)
        return


    def find_idle_robot(self):
        """Find one idle robot from the stack."""
        # TODO: Make it adaptive to the coordinates of where the robot is needed.
        return random.choice(self.idle_robots) if self.idle_robots else None