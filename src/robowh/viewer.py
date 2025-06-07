from flask import Flask, jsonify, send_from_directory
import random
import time
import threading

import logging

# Suppress console logging for selected Viewer interfaces
class NoGetNumber(logging.Filter):
    def filter(self, record):
        # Suppress two specific GET requests (should be enough for our purposes)
        msg = record.getMessage()
        return not ("GET /get_number" in msg or "GET /get_image" in msg)

# Add the filter to the werkzeug logger
logging.getLogger('werkzeug').addFilter(NoGetNumber())


class Viewer:
    def __init__(self):
        self.app = Flask(__name__, static_folder='static')
        self.diagnostic_number = 0.0  # A toy example for now
        self.lock = threading.Lock()

        self._setup_routes()
        self._start_number_updater()


    def _setup_routes(self):
        """External interfaces."""
        @self.app.route('/get_number')
        def get_number():
            with self.lock:
                return jsonify({'number': self.diagnostic_number})

        @self.app.route('/')
        def index():
            # Serve the HTML file from the static directory
            return send_from_directory(self.app.static_folder, 'index.html')


    def _start_number_updater(self):
        def update_number():
            while True:
                with self.lock:
                    self.diagnostic_number += random.uniform(-0.01, 0.01)
                time.sleep(0.05)

        thread = threading.Thread(target=update_number, daemon=True)
        thread.start()

    def run(self):
        self.app.run(port=5000)