"""Universe object: it runs time and physics."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
import time
import threading

class Universe:
    def __init__(self):
        logger.info("Spawning a new universe (but not starting it yet)")
        self.diagnostic_number = 0.0  # A toy example for now
        self.grid = np.zeros((100, 100))  # A toy example grid
        self.lock = threading.Lock()

    def start_universe(self):
        """Starting the universe."""
        logger.info("Starting the time in the universe!")
        def update_universe():
            while True:
                with self.lock:
                    self.diagnostic_number += random.uniform(-0.01, 0.01)
                    self.grid = (np.random.uniform(low=0, high=1, size=(100, 100)) < 0.01)*1
                time.sleep(0.05)

        thread = threading.Thread(target=update_universe, daemon=True)
        thread.start()
