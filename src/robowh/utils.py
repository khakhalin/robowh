"""Assorted technical utilities."""

import logging

class ColorFormatter(logging.Formatter):
    """Custom color formatter for logging messages."""
    BLUE = '\033[94m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PALEGRAY = '\033[38;5;245m'
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
        funcName = record.funcName
        record.funcName = f'{self.PALEGRAY}{funcName}{self.RESET}'
        return super().format(record)

# A dictionary of codes used to represent the WH on a grid.
# To change the colors for these, you'll need to go to the UI html and change them there.
grid_codes = {
    'empty':0,
    'rack':1,
    'robot':2,
    'operation':3,
    'confused':4,
    'payload':5
}
