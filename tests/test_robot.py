import pytest
from typing import Tuple
import numpy as np

from robowh.universe import Universe
from robowh.robot import Robot
from robowh.strategies import RandomMovementStrategy, AStarStrategy

@pytest.fixture
def universe() -> Universe:
    """Create a test universe instance."""
    universe = Universe.get_universe()
    universe.grid = np.zeros((10, 10), dtype=int)  # Small test grid
    return universe

@pytest.fixture
def robot(universe: Universe) -> Robot:
    """Create a test robot with random movement strategy."""
    return Robot(
        name="TestBot",
        strategy=RandomMovementStrategy
    )

@pytest.mark.parametrize("invalid_position", [(1,), (1, 2, 3), [1, 2], "12", None])
def test_set_position_invalid_input(robot: Robot, invalid_position: any) -> None:
    """Test that _set_position rejects invalid positions."""
    with pytest.raises(ValueError):
        robot._set_position(invalid_position)

@pytest.mark.parametrize("valid_position", [(0, 0), (1, 1)])
def test_set_position_valid_input(robot: Robot, valid_position: Tuple[int, int]) -> None:
    """Test that _set_position accepts valid positions."""
    robot._set_position(valid_position)
    assert robot.x == valid_position[0]
    assert robot.y == valid_position[1]

def test_robot_initialization(robot: Robot) -> None:
    """Test that robot is properly initialized."""
    assert isinstance(robot.name, str)
    assert robot.x is not None
    assert robot.y is not None
    assert 0 <= robot.x < robot.universe.grid.shape[0]
    assert 0 <= robot.y < robot.universe.grid.shape[1]
    assert robot.task == 'idle'
    assert robot.state == 'idling'
    assert isinstance(robot.next_moves, list)

@pytest.mark.parametrize("strategy_class", [
    RandomMovementStrategy,
    AStarStrategy
])
def test_robot_different_strategies(universe: Universe, strategy_class: type) -> None:
    """Test robot creation with different movement strategies."""
    robot = Robot(name="StrategyBot", strategy=strategy_class)
    assert robot.strategy == strategy_class
    assert callable(robot.strategy.calculate_path)

@pytest.mark.skip
def test_robot_movement_bounds(robot: Robot) -> None:
    """Test that robot stays within grid bounds."""
    initial_pos = (robot.x, robot.y)
    # TODO: Give this robot an action to move somewhere
    # Force many movements
    robot.strategy = RandomMovementStrategy

    # for _ in range(100):
    #     robot.act()
    #     assert 0 <= robot.x < 10 # TODO: add a normal check
    #     assert 0 <= robot.y < 10

    # Position should have changed after many moves
    # TODO: assert (robot.x, robot.y) != initial_pos
    assert True # temp haha

@pytest.mark.skip
def test_robot_collision_avoidance(universe: Universe, robot: Robot) -> None:
    """Test that robot doesn't move into obstacles."""
    # TODO: Make it run in a 2x2 universe with a single obstacle and random movement
    # Place an obstacle
    # obstacle_pos = (robot.x + 1, robot.y)
    # universe.grid[obstacle_pos] = 1  # Wall

    # # Try to move many times
    # for _ in range(10):
    #     robot.act()
    #     assert (robot.x, robot.y) != obstacle_pos
    assert True