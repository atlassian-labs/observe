"""Implements the observe decorator to standardize logging, metrics and notifications at the event level.
The provided metrics, logs and notifications are created based on the basic idea that each function call can be
categorized into one of the following four categories:
    * a. successful -> return response
    * b. raised an expected exception, to be acknowledged, see accept_on[] -> return True
    * c. raised an expected exception, NOT to be acknowledged, see decline_on[] -> return False
    * d. raised an unexpected exception, -> re-raise
"""
import time
import traceback
from functools import wraps
from typing import Any, Dict, List

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

            # setup
            identity: str = None
            all_tags: List[str] = []

            # iclients
            imetric = Provider.get_metric(*args)

            # start timing
            t0: float = time.monotonic()

            try:
                # actual function execution
                response: Any = func(*args, **kwargs)

                # send metrics, finished successfully
                imetric.timing("%s.time.finished" % metric, int(time.monotonic() - t0) * 1000, all_tags)
                imetric.increment("%s.finished" % metric, 1, all_tags)

            except Exception as ex:
                # append exception tags
                all_tags.append('exception:%s' % type(ex).__name__)

                # accept on, returns True
                if type(ex) in accept_on:
                    # log warning
                    Provider.get_logger(*args).warning(f"{identity}: {type(ex).__name__}({ex}) during '{func.__name__}' accepted.\n{traceback.format_exc()}")
                    # send metrics, raised but accepted
                    imetric.timing("%s.time.accepted" % metric, int(time.monotonic() - t0) * 1000, all_tags)
                    imetric.increment('%s.exception.accepted' % metric, 1, all_tags)
                    # return truthy as acknowledged
                    return True

                # decline on, returns False
                if type(ex) in decline_on:
                    # log error
                    Provider.get_logger(*args).error(f"{identity}: {type(ex).__name__}({ex}) during '{func.__name__}' declined.\n{traceback.format_exc()}")
                    # send metrics, raised but declined
                    imetric.timing("%s.time.declined" % metric, int(time.monotonic() - t0) * 1000, all_tags)
                    imetric.increment('%s.exception.declined' % metric, 1, all_tags)
                    # return falsy as not acknowledged
                    return False

                # unhandled exception, log
                Provider.get_logger(*args).error(f"{identity}: {type(ex).__name__}({ex}) during '{func.__name__}' raised.\n{traceback.format_exc()}")
                # send metrics, raised and unhandled
                imetric.timing("%s.time.raised" % metric, int(time.monotonic() - t0) * 1000, all_tags)
                imetric.increment('%s.exception.raised' % metric, 1, all_tags)
                # check if notification client available
                slack = Provider.get_slack(*args)
                if slack:
                    # notify
                    slack.error(header=identity, title=type(ex).__name__, text=f"{ex}\n{traceback.format_exc()}")
                # re-raise
                raise ex

            finally:
                # send metric, start
                imetric.increment("%s.start" % metric, 1, all_tags)

            # return actual response of the function
            return response
        return g
    return cet
