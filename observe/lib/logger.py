"""[summary]
"""
import logging
import os
import sys
from logging import Logger as L


class Logger(L):
    """[summary]
    Args:
        Logger ([type]): [description]
    """

    def __init__(self, name: str) -> None:
        """[summary]
        Args:
            name (str): [description]
        """
        super().__init__(name=name)
        self.setLevel(os.environ.get("LOG_LEVEL", logging.INFO))
        self.addHandler(logging.StreamHandler(sys.stdout))
