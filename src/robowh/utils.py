"""Assorted technical utilities."""

import logging

class ColorFormatter(logging.Formatter):
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'

    def format(self, record):
        levelname = record.levelname
        if levelname == 'INFO':
            record.levelname = f'{self.BLUE}{levelname}{self.RESET}'
        elif levelname == 'WARNING':
            record.levelname = f'{self.YELLOW}{levelname}{self.RESET}'
        elif levelname == 'ERROR':
            record.levelname = f'{self.RED}{levelname}{self.RESET}'
        # DEBUG: no color
        return super().format(record)

