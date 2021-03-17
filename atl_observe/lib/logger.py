"""This module defines a basic logging.Logger
"""
import logging
import os
import sys
from logging import Logger as L


class Logger(L):
    """The Logger is a wrap around logging.Logger with a basic setup.
    """

    def __init__(self, name: str) -> None:
        """Initializes the Logger.

        Note: reads from os to determine LOG_LEVEL
        """
        super().__init__(name=name)
        self.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))
        self.addHandler(logging.StreamHandler(sys.stdout))
