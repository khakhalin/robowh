"""Robot class."""

import logging
logger = logging.getLogger(__name__)

from typing import List, Tuple, Literal, Optional, cast, TypeAlias

from robowh.custom_types import RobotAction, Product, Coords
from robowh.universe import Universe
from robowh.utils import grid_codes
from robowh.strategies import MoveStrategy


RobotState: TypeAlias = Literal["idling", "moving", "blocked"]

class Robot:
    """A robot in the universe."""

    def __init__(self, name:str, strategy: MoveStrategy):
        logger.debug(f"Spawning a new robot: {name}")
        self.name:str = name
        self.strategy:MoveStrategy = strategy
        self.x:int = -1
        self.y:int = -1
        self.task:Literal["idle", "reposition", "transfer"] = 'idle'
        self.origin:Optional[Coords] = None
        self.destination:Optional[Coords] = None
        # Action is a sequence of action proper + optional coords, product
        self.current_action:Optional[RobotAction] = None # None in-between actions or while idling
        self.action_queue:List[RobotAction] = []  # A queue of scheduled actions
        self.state:RobotState = "idling"
        self.next_moves:List[Tuple[int]] = []  # Placeholder for a sequence of steps in the queue
        self.load = None  # What the robot is carrying

        self.universe:Universe = Universe.get_universe()

        # Teleport to a good position:
        self._set_position(self.universe.random_empty_position())  # Teleport
        # We don't want to report for service right upon creation, let's wait for initialization
        # to be over, and for time to start.


    def _set_position(self, position: Coords) -> None:
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

        if self.current_action is None:
            if len(self.action_queue) > 0:
                self.current_action = self.action_queue.pop(0)
            else: # We can only idle
                self._report_for_service()
                return

        # Semaphore for action types
        if self.current_action[0] == "go":
            target = cast(Coords, self.current_action[1])
            if abs(self.x-target[0]) + abs(self.y-target[1]) <= 1: #  We are at destination
                logger.debug(f"{self.name} Arrived at destination")
                self.current_action = None  # Reset action
                return
            else:
                self.move()

        elif self.current_action[0] == "pick":
            x,y = cast(Coords, self.current_action[1])
            product = self.current_action[2]
            scan_result = self.universe.scan(x, y)
            if not scan_result:
                raise SystemError(f"No shelf can be reached from {self.x}, {self.y}")
            # We don't need to check if the product is there, as we'll just crash at picking
            shelf, index = scan_result
            logger.info(f"{self.name} picking {product} from {shelf.name} pos {index}")
            shelf.remove(index, product)
            self.current_action = None  # Reset action

        elif self.current_action[0] == "drop":
            x,y = cast(Coords, self.current_action[1])
            product = self.current_action[2]
            # TODO: Here the robot could check if it is in fact carrying product
            scan_result = self.universe.scan(x, y)  # Scan for the presence of a bay
            if not scan_result:
                raise SystemError(f"No shelf can be reached from {self.x}, {self.y}")
            shelf, index = scan_result
            logger.info(f"{self.name} storing {product} at {shelf.name} pos {index}")
            shelf.place_at(index, product)
            self.current_action = None  # Reset action

        else:
            raise ValueError(f"Action {self.current_action} is not implemented")


    def move(self) -> None:
        """Perform a single one-pixel move (if possible)."""
        # Check if we are out of ideas for next moves, in which case, think
        if len(self.next_moves) == 0:
            logger.debug(f"{self.name} recalculating path (at {self.x}, {self.y})")
            self.next_moves = self.strategy.calculate_path(
                (self.x, self.y), self.current_action[1]
                )

        if len(self.next_moves) ==0: # If it's still zero, then the calculation above failed
            self.set_state("blocked")
            return

        movement = self.next_moves.pop(0)  # Next element (reading L to R)
        new_x = self.x + movement[0]
        new_y = self.y + movement[1]

        # Check for collisions and whether the move is possible.
        # Technically reaching into the grid directly from the robot is a very questionable
        # design choice, but let's consider it a case of bare-bones "observer pattern";
        # we're just communicating the change to the universe. Maybe we'll refactor it to
        # something slightly more elegant later.
        if self.universe.grid_is_free(new_x, new_y):  # Can move to this pixel
            self.universe.grid[self.x, self.y] = grid_codes['empty']
            self.x, self.y = new_x, new_y
            self.set_state("moving")
        else:  # Cannot move
            self.set_state("blocked")
            # Depending on the strategy, it could be a reasonable point to replan from scratch.
            # TODO: introduce some flexibility here. Always replan? Sometimes replan?


    def set_state(self, new_state:RobotState):
        """Set state, but also report this change to the Observer."""
        if new_state != "blocked":
            # Nice moving robot
            self.universe.grid[self.x, self.y] = grid_codes['robot']
            if self.state == "blocked":  # Just got unblocked
                self.universe.observer.n_blocked -= 1
                # logger.warning(f"Unblocking {self.name}")
        if new_state == "blocked":
            # Confused robot
            # logger.debug(f"{self.name} stumbled at ({self.x}, {self.y})")
            self.universe.grid[self.x, self.y] = grid_codes['confused']
            if self.state != "blocked":  # Just got confused
                self.universe.observer.n_blocked += 1
                # logger.error(f"Blocking {self.name}")
        self.state = new_state


    def assign_task(
            self, task_type:str, origin:Coords=None, destination:Coords=None, product:Product=None
            ) -> None:
        """Assign a task to the robot.

        task_type can be:
        - 'reposition': Move to a new position
        - 'transfer': A sequence of actions: go, pick, go, drop
        - 'idle': No task, do nothing in place
        """

        if task_type=="reposition":
            origin = (self.x, self.y) if origin is None else origin
            if destination is None:
                raise ValueError("Reposition task must have a destination.")
            logger.info(f"{self.name} asked to reposition from {origin} to {destination}")
            self._assign_action("go", destination)

        elif task_type=="transfer":
            if origin is None:
                raise ValueError("Transfer task must have an origin.")
            if destination is None:
                raise ValueError("Transfer task must have a destination.")
            logger.info(f"{self.name} asked to bring {product} from {origin} to {destination}")
            pre_origin = (self.x, self.y)
            self._assign_action("go", origin)
            self._assign_action("pick", origin, product)
            self._assign_action("go", destination)
            self._assign_action("drop", destination, product)

        elif task_type=="idle":
            logger.info(f"{self.name} asked to idle for a while")

        else:
            raise ValueError(f"Unknown task type: {task_type}. Supported: 'reposition'.")

        # Register the task
        self.task = task_type
        self.origin = origin
        self.destination = destination


    def _assign_action(self, action:str, target:Coords, product:str=Product) -> None:
        """Add an action to the queue of actions."""
        if action not in ["go", "pick", "drop"]:
            raise ValueError(f"Unknown action: {action}. Supported: 'go', 'pick', 'drop'.")
        logger.debug(f"{self.name} assigned action: {action} to {target}")
        self.action_queue.append((action, target, product))
