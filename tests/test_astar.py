import pytest
from unittest.mock import MagicMock
import numpy as np

from robowh.strategies import AStarStrategy



@pytest.fixture(autouse=True)
def universe(monkeypatch):
    mock = MagicMock()
    mock.grid = np.zeros((5, 5), dtype=int)

    monkeypatch.setattr(
        "robowh.strategies.Universe.get_universe",
        lambda: mock
    )
    return mock


@pytest.fixture
def clear_grid():
    return np.zeros((5, 5), dtype=int)

@pytest.fixture
def blocked_grid():
    grid = np.zeros((5, 5), dtype=int)
    grid[0:5, 2] = 1  # Complete Vertical wall
    return grid

@pytest.fixture
def partially_blocked():
    grid = np.zeros((5, 5), dtype=int)
    grid[0:3, 2] = 1  # partial
    return grid

def test_clear_path():
    path = AStarStrategy.calculate_path((0,0), (2,2), until_touch=False)
    assert len(path) == 4
    assert path == [(1,0), (1,0), (0,1), (0,1)]

def test_blocked_path(blocked_grid, universe):
    universe.grid = blocked_grid
    path = AStarStrategy.calculate_path((0,0), (4,4), until_touch=False)
    assert path == []

def test_complex_path(partially_blocked, universe):
    universe.grid = partially_blocked
    path = AStarStrategy.calculate_path((0,0), (0,4), until_touch=False)
    assert len(path) == 10
    # I'm too lazy to write it down completely, but here's an approximation
    assert len([m for m in path if m==(0,1)]) == 4
    assert len([m for m in path if m==(1,0)]) == 3
    assert len([m for m in path if m==(-1,0)]) == 3

def test_partial_steps():
    path = AStarStrategy.calculate_path((0,0), (4,4), n_steps=3, until_touch=False)
    assert len(path) == 3
    assert path == [(1,0), (1,0), (1,0)]

def test_same_position():
    path = AStarStrategy.calculate_path((2,2), (2,2), until_touch=False)
    assert path == []

def test_invalid_start():
    path = AStarStrategy.calculate_path((-1,0), (4,4), until_touch=False)
    assert path == []

def test_invalid_target():
    path = AStarStrategy.calculate_path((0,0), (9,9), until_touch=False)
    assert path == []