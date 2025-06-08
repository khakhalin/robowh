import pytest
from unittest.mock import MagicMock
import numpy as np

from robowh.shelves import Shelves
from robowh.utils import grid_codes


@pytest.fixture(autouse=True)
def universe(monkeypatch):
    mock = MagicMock()
    mock.grid = np.zeros((5, 5), dtype=int)

    monkeypatch.setattr(
        "robowh.strategies.Universe.get_universe",
        lambda: mock
    )
    return mock

def test_add_shelf(universe):
    sh = Shelves("main")
    assert sh.name == "main"
    assert len(sh.coords) == 0
    sh.add_shelf((2,2), empty=True)
    assert sh.n_items == 0
    assert len(sh.coords) == 1
    assert sh.coords[0] == (2,2)
    assert sh.inventory[0] is None


def test_place_stuff(universe):
    sh = Shelves()
    for i in range(5):
        sh.add_shelf((2,i), empty=True)
    assert sh.n_items == 0
    assert len(sh.coords) == 5

    sh.place_at(2, "product2")
    sh.place_at(0, "product0")

    assert sh.n_items == 2
    assert len(sh.records) == 2
    assert sh.records["product2"] == 2
    assert sh.inventory[2] == "product2"
    assert sh.coords[2] == (2,2)
    assert universe.grid[2,2] == grid_codes['item']


def test_clear_shelf(universe):
    sh = Shelves()
    for i in range(5):
        sh.add_shelf((2,i), empty=True)
        sh.place_at(i, str(i))
    assert sh.n_items == 5
    assert len(sh.coords) == 5

    sh.clear(2)
    assert sh.n_items == 4
    assert len(sh.records) == 4
    assert sh.records["3"] == 3
    assert "2" not in sh.records
    assert sh.inventory[2] is None
    assert universe.grid[2,2] == grid_codes['shelf']


def test_place_optimally(universe):
    sh = Shelves()
    for i in range(5):
        sh.add_shelf((2,i), empty=True)
        if i in [2,3]:  # But not 0, 1 or 4!
            sh.place_at(i, str(i))
    assert [int(p is not None) for p in sh.inventory] == [0, 0, 1, 1, 0]
    sh.place_optimally("product0")
    assert [int(p is not None) for p in sh.inventory] == [1, 0, 1, 1, 0]
    sh.place_optimally("product1")
    assert [int(p is not None) for p in sh.inventory] == [1, 1, 1, 1, 0]
    sh.place_optimally("product2")
    assert [int(p is not None) for p in sh.inventory] == [1, 1, 1, 1, 1]
