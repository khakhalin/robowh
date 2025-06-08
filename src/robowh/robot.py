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

    def __init__(self, name:str, strategy):
        logger.debug(f"Spawning a new robot: {name}")
        self.name = name
        self.strategy = strategy
        self.x = None
        self.y = None
        self.task = 'idle' # idle, reposition, transfer
        self.origin = None
        self.destination = None
        self.action_stack = []  # A stack of actions into which tasks are broken down
        self.substate = 'moving'  # moving, confused, loading - related to subtasks

        self.next_moves = []  # Placeholder for a sequence of steps in the queue

        self._set_position(universe.random_empty_position())

    def _set_position(self, position: tuple):
        """Set the robot's position in the universe. Teleportation."""
        if not isinstance(position, tuple) or len(position) != 2:
            raise ValueError("Position must be a tuple of (x, y) coordinates.")
        self.x, self.y = position
        universe.grid[self.x, self.y] = grid_codes['robot']
        logger.debug(f"Robot {self.name} teleported to ({self.x}, {self.y})")

    def move(self) -> None:
        """Request a random move."""
        # Check if we are out of ideas for next moves, in which case, think
        if len(self.next_moves) == 0:
            self.next_moves = self.strategy.calculate_path(
                (self.x, self.y), (0,0), n_steps=10
                )
            # TODO: Here I requested a default number of steps, which is dangerous.

        movement = self.next_moves.pop(0)  # Next element (reading L to R)
        new_x = self.x + movement[0]
        new_y = self.y + movement[1]

        # Check for collisions and move if possible.
        # Technically reaching into the grid directly from the robot is a very questionable
        # design choice, but let's consider it a case of bare-bones "observer pattern";
        # we're just communicating the change to the universe. Maybe we'll refactor it to
        # something slightly more elegant later.
        if universe.grid_is_free(new_x, new_y):  # Can move
            universe.grid[self.x, self.y] = grid_codes['empty']
            self.x, self.y = new_x, new_y
            universe.grid[self.x, self.y] = grid_codes['robot']
            self.substate = 'moving'
        else:  # Cannot move, think
            universe.grid[self.x, self.y] = grid_codes['confused']
            self.substate = 'confused'
            # Depending on the strategy, it could be a good point to replan from scratch.
            # TODO: introduce some flexibility here. Always replan? Sometimes replan?


    def assign_task(self, task_type: str, origin: tuple=None, destination: tuple=None) -> None:
        """Assign a task to the robot.

        task_type can be:
        - 'reposition': Move to a new position
        - 'transfer': A sequence of actions: go, pick, go, drop
        - 'idle': No task, do nothing in place
        """
        logger.info(f"Robot {self.name} assigned task: {task_type} from {origin} to {destination}")
        if task_type=="reposition":
            if destination is None:
                raise ValueError("Reposition task must have a destination.")
            origin = (self.x, self.y) if origin is None else origin
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
        self.action_stack.insert(0, (action, target))
        logger.debug(f"Robot {self.name} assigned action: {action} to {target}")