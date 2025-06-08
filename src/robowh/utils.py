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
        padded_name = f"{levelname:<5}"  # Left aligned, padded to 8 chars
        if levelname == 'INFO':
            record.levelname = f'{self.BLUE}{padded_name}{self.RESET}'
        elif levelname == 'WARNING':
            record.levelname = f'{self.YELLOW}{padded_name}{self.RESET}'
        elif levelname == 'ERROR':
            record.levelname = f'{self.RED}{padded_name}{self.RESET}'
        elif levelname == 'DEBUG':
            record.levelname = f'{padded_name}' # No color change

        funcName = record.funcName
        funcName = f"{funcName:<12.12}"
        record.funcName = f'{self.PALEGRAY}{funcName}{self.RESET}'
        return super().format(record)

# A dictionary of codes used to represent the WH on a grid.
# To change the colors for these, you'll need to go to the UI html and change them there.
grid_codes = {
    'empty':0,
    'shelf':1,
    'robot':2,
    'operation':3,
    'confused':4,
    'item':5
}
