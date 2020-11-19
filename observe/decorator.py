"""Implements the observe decorator to standardize logging, metrics and notifications at the event level.

The provided metrics, logs and notifications are created based on the basic idea that each function call can be
categorized into one of the following four categories:
    * a. successful -> return response
    * b. raised an expected exception, to be acknowledged, see accept_on[] -> return True
    * c. raised an expected exception, NOT to be acknowledged, see decline_on[] -> return False
    * d. raised an unexpected exception, -> re-raise
"""
from functools import wraps
from typing import Dict, List

from observe.lib.utils import Provider


def observe(metric: str,
            accept_on: List[Exception] = [],
            decline_on: List[Exception] = [],
            static_tags: List[str] = None,
            tags_from: Dict[str, List[str]] = None,
            trace_id_from: Dict[str, str] = None,
            verbose: bool = False):
    """[summary]

    Args:
        metric (str): [description]
        accept_on (List[Exception], optional): [description]. Defaults to None.
        decline_on (List[Exception], optional): [description]. Defaults to None.
        static_tags (List[str], optional): [description]. Defaults to None.
        tags_from (Dict[str, List[str]], optional): [description]. Defaults to None.
        trace_id_from (Dict[str, str], optional): [description]. Defaults to None.
        verbose (bool, optional): [description]. Defaults to False.
    """
    def cet(func):
        @wraps(func)
        def g(*args, **kwargs):

            identity = None

            try:
                response = func(*args, **kwargs)

            except Exception as ex:

                # accept on, returns True
                if type(ex) in accept_on:
                    text = f"{identity}: {type(ex).__name__}({ex}) during '{func.__name__}' accepted."
                    Provider.get_logger(*args).warning(text)
                    return True

                # decline on, returns False
                if type(ex) in decline_on:
                    text = f"{identity}: {type(ex).__name__}({ex}) during '{func.__name__}' declined."
                    Provider.get_logger(*args).error(text)
                    return False

                text = f"{identity}: {type(ex).__name__}({ex}) during '{func.__name__}' raised."
                Provider.get_logger(*args).error(text)
                # unhandled exception
                raise ex

            finally:
                pass

            return response
        return g
    return cet
