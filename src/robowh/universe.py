"""Universe object: it runs time and physics."""

import logging
logger = logging.getLogger(__name__)

import numpy as np
import random
import time
import threading

class Universe:
    MAX_UPDATE_TIME = 0.05  # 50 ms

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
                start_time = time.time()

                with self.lock:
                    self.diagnostic_number += random.uniform(-0.01, 0.01)

                    # First update - always happens
                    if time.time() - start_time < self.MAX_UPDATE_TIME:
                        self.grid = (np.random.uniform(low=0, high=1, size=(100, 100)) < 0.01)*1

                    # Second update - only if time permits
                    if time.time() - start_time < self.MAX_UPDATE_TIME:
                        self.grid = (np.random.uniform(low=0, high=1, size=(100, 100)) < 0.01)*1

                    # Third update - only if time permits
                    if time.time() - start_time < self.MAX_UPDATE_TIME:
                        self.grid = (np.random.uniform(low=0, high=1, size=(100, 100)) < 0.01)*1

                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.MAX_UPDATE_TIME - elapsed_time)
                time.sleep(sleep_time)

        thread = threading.Thread(target=update_universe, daemon=True)
        thread.start()
