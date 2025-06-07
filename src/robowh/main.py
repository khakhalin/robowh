# my-python-project/src/main.py

import logging
import sys
from robowh.utils import ColorFormatter

formatter = ColorFormatter(
    fmt="%(asctime)s: %(levelname)s: %(funcName)s: %(message)s", datefmt='%I:%M:%S')
hnd = logging.StreamHandler(stream=sys.stdout)

logger = logging.getLogger()
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
ch.setFormatter(formatter)
logger.addHandler(ch)



from robowh.viewer import Viewer
from robowh.universe import Universe

if __name__ == "__main__":
    logger.info("Welcome to the Robotic Warehouse Simulator!")
    universe = Universe.get_universe()
    viewer = Viewer(universe)

    try:
        viewer.run()
    except KeyboardInterrupt:
        print('\nServer stopped by user')