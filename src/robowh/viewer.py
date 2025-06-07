import logging
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, send_from_directory
import threading



# Suppress console logging for selected Viewer interfaces
class NoGetNumber(logging.Filter):
    def filter(self, record):
        # Suppress two specific GET requests (should be enough for our purposes)
        msg = record.getMessage()
        return not ("GET /get_number" in msg or "GET /get_grid" in msg)

# Add the filter to the werkzeug logger
logging.getLogger('werkzeug').addFilter(NoGetNumber())


class Viewer:
    def __init__(self, universe):
        logger.info("Starting the Viewer")
        self.app = Flask(__name__, static_folder='static')
        self.lock = threading.Lock()

        self._setup_routes()
        self.universe = universe
        self.universe.start_universe()


    def _setup_routes(self):
        """External interfaces."""
        @self.app.route('/')
        def index():
            # Serve the HTML file from the static directory
            return send_from_directory(self.app.static_folder, 'index.html')

        @self.app.route('/get_number')  # Toy example
        def get_number():
            # with self.lock:
            return jsonify({'number': self.universe.diagnostic_number})

        @self.app.route('/get_grid')
        def get_grid():
            # with self.lock:
            return jsonify({"grid": self.universe.grid.copy().tolist()})


    def run(self):
        self.app.run(port=5000)