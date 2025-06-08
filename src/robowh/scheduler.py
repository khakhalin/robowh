"""SCHEDULER: creates new orders for the WH, from a virtual order queue."""

import logging
logger = logging.getLogger(__name__)

class Scheduler:
    """Scheduler for the Robotic Warehouse Simulator."""

    def __init__(self, universe):
        logger.info("Starting the Scheduler")
        # IRL orders come from the ouside, but here we simulate them.
        # So we have to routinely ask the Orchestrator about our current inventory etc.
        self.universe = universe

    def add_order(self, task):
        """Add a new task to the task queue."""
        # IRL would be an important method. We don't need it however.
        pass

    def pop_order(self):
        """Pop an order from the task queue."""
        # Pseudocode for now:
        # 0. Toss a coin, and with some probability, return None. If this method is modeling
        #    getting an oder from a queue, then sometimes the queue should be empty, and
        #    robots requesting an task should receive no task, and get into idling.
        # 1. Check inventory with Scheduler, compare to target inventory. If a gap, only
        #   create orders of one type (store or retrieve) for a while (until the gap is closed).
        # 2. If no gap, toss a coin if it's a "store" or "retrieve" order
        # 3. If "store", create a load id, place it on a random dock.
        #   Tell Scheduler it needs to be stored. We assume that docks have infinite temp capacity.
        # 4. If "retrieve", ask Scheduler for inventory. Pick an id at random, pick a target
        #   dock at random, tell Scheduler the load needs to be broght to this dock.
        #   If no inventory, fizzle.
        pass