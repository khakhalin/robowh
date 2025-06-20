import logging
logger = logging.getLogger(__name__)

from flask import Flask, jsonify, send_from_directory, request
import threading



# Suppress console logging for selected Viewer interfaces
class NoGetNumber(logging.Filter):
    def filter(self, record):
        # Suppress two specific GET requests (should be enough for our purposes)
        msg = record.getMessage()
        return not ("GET /get_kpis" in msg or "GET /get_grid" in msg)

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

        @self.app.route('/get_kpis')  # Toy example
        def get_kpis():
            return jsonify({
                "n_tasks": self.universe.observer.n_tasks,
                "n_shelves": self.universe.shelves.n_items,
                "n_bay": self.universe.bays.n_items,
                "sh_blocked": 100 * self.universe.observer.n_blocked / self.universe.N_ROBOTS
                })

        @self.app.route('/get_grid')
        def get_grid():
            # No need to lock, as we are only reading here.
            # We're flipping the grid, to have the Y axis go from top to bottom
            return jsonify({"grid": self.universe.grid[::-1, :].copy().tolist()})

        @self.app.route('/set_mode', methods=['POST'])
        def set_mode():
            # Parse JSON data from the request
            data = request.get_json()
            mode = data.get('mode')  # e.g., "store", "both", "pick"

            self.universe.orchestrator.mode = mode
            logger.warning(f"Orchestrator is now in [{self.universe.orchestrator.mode}] mode")

            # Return a simple confirmation response
            return jsonify({"status": "ok", "mode": mode})


    def run(self):
        self.app.run(port=5000)