import sys
print(sys.path)

import pytest
import numpy as np

from robowh.universe import Universe


def test_random_empty_position():
    universe = Universe()
    # Test that the random_empty_position returns a position within bounds
    universe.grid = np.random.randint(0, 2, (100, 100))  # Fill the grid with random values (0 or 1)
    universe.grid[0,0] = 0  # Create one empty position just in case
    x, y = universe.random_empty_position()
    assert 0 <= x < 100
    assert 0 <= y < 100

    # Test that the position is empty in the grid
    assert universe.grid[x, y] == 0


def test_grid_is_free():
    universe = Universe()
    # Fill the grid with random values (0 or 1)
    universe.grid[11,11] = 1  # Create a non-empty position
    universe.grid[10, 10] = 0  # Create a surely free position

    assert universe.grid_is_free(10, 10) is True
    assert universe.grid_is_free(11, 11) is False