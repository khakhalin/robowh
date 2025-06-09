
import logging
logger = logging.getLogger(__name__)

from typing import TYPE_CHECKING
import numpy as np
import random

from robowh.robot import Robot
from robowh.universe import Universe


class Observer():
    """For collecting all sorts of statistics."""

    def __init__(self):
        self.n_tasks:int = 0

    def count_task(self):
        self.n_tasks += 1