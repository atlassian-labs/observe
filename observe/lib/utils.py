"""This module provides utils for the @observe operator, to keep the actual implementation maintainable and readable.
"""
import logging
from typing import Tuple

from observe.lib.logger import Logger


class Provider:
    """The Provider defines methods to find a client or default to one.
    """
    @staticmethod
    def get_logger(*args: Tuple) -> logging.Logger:
        """Searches the parameter list *args for an instance of logging.Logger.

        Returns:
            logging.Logger
        """
        for arg in args:
            if isinstance(arg, logging.Logger):
                return arg
            if hasattr(arg, "logger") and isinstance(arg.logger, logging.Logger):
                return arg.logger

        return Logger(name="Observe")
