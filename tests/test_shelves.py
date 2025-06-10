import logging
logger = logging.getLogger(__name__)

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
    assert not sh.inventory[0] # Empty list


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
    assert sh.inventory[2][0] == "product2"
    assert sh.coords[2] == (2,2)
    assert universe.grid[2,2] == grid_codes['item']

    with pytest.raises(Exception):
        sh.place_at(1, "product2")  # This product already exists
    with pytest.raises(Exception):
        sh.place_at(2, "product_other")  # This place is already taken


def test_remove_from_shelf(universe):
    sh = Shelves()
    for i in range(5):
        sh.add_shelf((2,i), empty=True)
        sh.place_at(i, str(i))
    assert sh.n_items == 5
    assert len(sh.coords) == 5

    sh.remove(2, "2")
    assert sh.n_items == 4
    assert len(sh.records) == 4
    assert sh.records["3"] == 3
    assert "2" not in sh.records
    assert not sh.inventory[2]
    assert universe.grid[2,2] == grid_codes['shelf']


def test_place_optimally(universe):
    sh = Shelves()
    for i in range(5):
        sh.add_shelf((2,i), empty=True)
        if i in [2,3]:  # But not 0, 1 or 4!
            sh.place_at(i, str(i))
    assert [int(bool(p)) for p in sh.inventory] == [0, 0, 1, 1, 0]
    i = sh.request_optimal_placement()
    sh.place_at(i, "product0")
    assert [int(bool(p)) for p in sh.inventory] == [1, 0, 1, 1, 0]
    i = sh.request_optimal_placement()
    sh.place_at(i, "product1")
    assert [int(bool(p)) for p in sh.inventory] == [1, 1, 1, 1, 0]
    i = sh.request_optimal_placement()
    sh.place_at(i, "product2")
    assert [int(bool(p)) for p in sh.inventory] == [1, 1, 1, 1, 1]

    with pytest.raises(Exception):
        sh.place_optimally("product2")  # This product already exists


def test_deep_shelves(universe):
    sh = Shelves(deep=True)
    for i in range(5):
        sh.add_shelf((2,i), empty=True)

    sh.place_at(1, "product11")
    sh.place_at(1, "product12")
    sh.place_at(2, "product2")
    sh.place_at(3, "product3")
    assert sh.n_items == 4
    assert len(sh.inventory[1]) == 2

    sh.remove(sh.records["product11"], "product11")
    sh.remove(sh.records["product2"], "product2")
    assert sh.n_items == 2
    assert sh.inventory[1][0] == "product12"