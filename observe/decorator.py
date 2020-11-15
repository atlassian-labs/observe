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


def observe(metric: str,
            accept_on: List[Exception] = None,
            decline_on: List[Exception] = None,
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

    def cet(f):
        @wraps(f)
        def g(*args, **kwargs):
            try:
                response = f(*args, **kwargs)

            except Exception as ex:

                # accept on, returns True
                if type(ex) in accept_on:
                    return True

                # decline on, returns False
                if type(ex) in decline_on:
                    return False

                # unhandled exception
                raise ex

            finally:
                pass

            return response
        return g
    return cet
