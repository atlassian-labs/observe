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
from typing import Any, Callable, Dict, List, Optional

from atl_observe.lib.utils import Provider, Resolver


def observe(metric: str,
            accept_on: List[Exception] = [],  # pylint: disable=E1136
            decline_on: List[Exception] = [],  # pylint: disable=E1136
            static_tags: List[str] = [],  # pylint: disable=E1136
            tags_from: Optional[Dict[str, List[str]]] = None,  # pylint: disable=E1136
            trace_id_from: Optional[Dict[str, str]] = None):  # pylint: disable=E1136
    """This operator will, based on the provided setup generate logs, metrics, notifications on each call for that execution.

    Args:
        metric (str): The root-metric which will be updated during execution in e.g. DogStatsd.
        accept_on (Optional[List[Exception]], optional): A list of exceptions on which the message will be acknowledged.
        decline_on (Optional[List[Exception]], optional): A list of exceptions on which the message will be declined.
        static_tags (Optional[List[str]], optional): A list of tags to be appended on each metric update.
        tags_from (Optional[Dict[str, List[str]]], optional): A list of tags to be dynamically extracted from the key dictionary.
        trace_id_from (Optional[Dict[str, str]], optional): A trace_id to be appended on each log from the key dictionary.
    """
    def arrange(func: Callable[..., Any]):
        @wraps(func)
        def inner(*args: Any, **kwargs: Any) -> Any:

            # setup tracing and tags
            trace_id = Resolver.resolve_trace_id(trace_id_from=trace_id_from, **kwargs)
            identity = Resolver.resolve_identity(*args, func=func, trace_id=trace_id)
            additional_tags = Resolver.resolve_tags_from(tags_from=tags_from, **kwargs)
            all_tags = additional_tags + static_tags

            imetric = Provider.get_metric(*args)

            # start timing
            time_start: float = time.monotonic()

            try:
                # actual function execution
                response: Any = func(*args, **kwargs)

                # send metrics, finished successfully
                imetric.timing("%s.time.finished" % metric, int(time.monotonic() - time_start) * 1000, all_tags)
                imetric.increment("%s.finished" % metric, 1, all_tags)

            except Exception as ex:
                # append exception tags
                all_tags.append('exception:%s' % type(ex).__name__)

                # accept on, returns True
                if type(ex) in accept_on:
                    # log warning
                    Provider.get_logger(*args).warning("%s: %s(%s) during '%s' accepted.\n%s" % (
                        identity, type(ex).__name__, ex, func.__name__, traceback.format_exc()))
                    # send metrics, raised but accepted
                    imetric.timing("%s.time.accepted" % metric, int(time.monotonic() - time_start) * 1000, all_tags)
                    imetric.increment('%s.exception.accepted' % metric, 1, all_tags)
                    # return truthy as acknowledged
                    return True

                # decline on, returns False
                if type(ex) in decline_on:
                    # log error
                    Provider.get_logger(*args).error("%s: %s(%s) during '%s' declined.\n%s" % (
                        identity, type(ex).__name__, ex, func.__name__, traceback.format_exc()))
                    # send metrics, raised but declined
                    imetric.timing("%s.time.declined" % metric, int(time.monotonic() - time_start) * 1000, all_tags)
                    imetric.increment('%s.exception.declined' % metric, 1, all_tags)
                    # return falsy as not acknowledged
                    return False

                # unhandled exception, log
                Provider.get_logger(*args).error("%s: %s(%s) during '%s' raised.\n%s" % (
                    identity, type(ex).__name__, ex, func.__name__, traceback.format_exc()))
                # send metrics, raised and unhandled
                imetric.timing("%s.time.raised" % metric, int(time.monotonic() - time_start) * 1000, all_tags)
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
        return inner
    return arrange
