"""Robot class."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random

from robowh.universe import Universe
from robowh.utils import grid_codes
from robowh.strategies import MoveStrategy

class Robot:
    """A robot in the universe."""

    def __init__(self, name:str, strategy: MoveStrategy):
        logger.debug(f"Spawning a new robot: {name}")
        self.name = name
        self.strategy = strategy
        self.x = None
        self.y = None
        self.task = 'idle' # idle, reposition, transfer
        self.origin = None
        self.destination = None
        self.action_stack = []  # A stack of actions into which tasks are broken down
        self.current_action = None  # A tuple (action, target). actions: 'go', 'pick', 'drop'
        self.state = 'idling'  # idling, moving, blocked, loading etc. (TODO: full ontology)
        self.next_moves = []  # Placeholder for a sequence of steps in the queue

        self.universe = Universe.get_universe()
        self._set_position(self.universe.random_empty_position())  # Teleport
        self._report_for_service()


    def _set_position(self, position: tuple) -> None:
        """Set the robot's position in the universe. Teleportation."""
        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Position must be a tuple of (x, y) coordinates.")
        self.x, self.y = position
        self.universe.grid[self.x, self.y] = grid_codes['robot']
        logger.debug(f"{self.name} teleported to ({self.x}, {self.y})")


    def _report_for_service(self) -> None:
        """Robot finished a task and is ready to pick up a new one, or become idle."""
        self.universe.orchestrator.process_request_for_service(self)

    def act(self) -> None:
        """Perform an action for this turn, whatever it is."""
        # Pseudocode:
        # 1. Check if we are in a no action state. If no action, pop(0) from the action stack
        # 2. If we have an ongoing action, perform this action
        # 3. Otherwise, idle
        if not self.current_action:
            if len(self.action_stack)>0:
                self.current_action = self.action_stack.pop(0)
            else: # We can only idle
                self._report_for_service()
                return

        if self.current_action[0] == 'go':
            target = self.current_action[1]
            if (self.x==target[0]) & (self.y==target[1]): #  We are at destination
                self.current_action = None
                logger.debug(f"{self.name} Arrived at destination")
            else:
                self.move()
        else:
            raise ValueError(f"Action {self.current_action} is not implemented")


    def move(self) -> None:
        """Request a random move."""
        # Check if we are out of ideas for next moves, in which case, think
        if len(self.next_moves) == 0:
            logger.debug(f"{self.name} recalculating path (at {self.x}, {self.y})")
            self.next_moves = self.strategy.calculate_path(
                (self.x, self.y), self.current_action[1]
                )

        if len(self.next_moves) ==0: # Calculation failed
            self.universe.grid[self.x, self.y] = grid_codes['confused']
            self.state = 'blocked'
            return

        movement = self.next_moves.pop(0)  # Next element (reading L to R)
        new_x = self.x + movement[0]
        new_y = self.y + movement[1]

        # Check for collisions and whether the move is possible.
        # Technically reaching into the grid directly from the robot is a very questionable
        # design choice, but let's consider it a case of bare-bones "observer pattern";
        # we're just communicating the change to the universe. Maybe we'll refactor it to
        # something slightly more elegant later.
        if self.universe.grid_is_free(new_x, new_y):  # Can move
            self.universe.grid[self.x, self.y] = grid_codes['empty']
            self.x, self.y = new_x, new_y
            self.universe.grid[self.x, self.y] = grid_codes['robot']
            self.state = 'moving'
        else:  # Cannot move, think
            self.universe.grid[self.x, self.y] = grid_codes['confused']
            # logger.debug(f"{self.name} stumbled at ({self.x}, {self.y})")
            self.state = 'blocked'
            # Depending on the strategy, it could be a good point to replan from scratch.
            # TODO: introduce some flexibility here. Always replan? Sometimes replan?


    def assign_task(self, task_type: str, origin: tuple=None, destination: tuple=None) -> None:
        """Assign a task to the robot.

        task_type can be:
        - 'reposition': Move to a new position
        - 'transfer': A sequence of actions: go, pick, go, drop
        - 'idle': No task, do nothing in place
        """
        if task_type=="reposition":
            origin = (self.x, self.y) if origin is None else origin
            logger.info(f"{self.name} asked to reposition from {origin} to {destination}")
            if destination is None:
                raise ValueError("Reposition task must have a destination.")
            self._assign_action("go", destination)
        else:
            raise ValueError(f"Unknown task type: {task_type}. Supported: 'reposition'.")

        # Register the task
        self.task = task_type
        self.origin = origin
        self.destination = destination


    def _assign_action(self, action: str, target: tuple) -> None:
        """Add an action to the queue of actions."""
        if action not in ["go", "pick", "drop"]:
            raise ValueError(f"Unknown action: {action}. Supported: 'go', 'pick', 'drop'.")
        logger.debug(f"{self.name} assigned action: {action} to {target}")
        self.action_stack.append((action, target))
