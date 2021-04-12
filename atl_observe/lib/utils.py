"""This module provides utils for the @observe operator, to keep the actual implementation maintainable and readable.
"""
import logging
from typing import Any, Dict, List, Optional, Union

from datadog.dogstatsd.base import DogStatsd

from atl_observe.lib.logger import Logger
from atl_observe.lib.metrics import IMetric, Metric
from atl_observe.lib.slack import MissingSlackWebhookException, Slack

# mapping milliseconds to tag
observe_threshold_map: Dict[int, str] = {
    0: "100ms",
    100: "200ms",
    200: "300ms",
    300: "400ms",
    400: "500ms",
    500: "1s",
    1000: "2s",
    2000: "3s",
    3000: "4s",
    4000: "5s",
    5000: "10s",
    10000: "20s",
    20000: "30s",
    30000: "40s",
    40000: "50s",
    50000: "1min",
    60000: "2min",
    120000: "3min",
    180000: "4min",
    240000: "5min",
    300000: "10min",
    600000: "20min",
    1200000: "30min",
    1800000: "OVER_30min"
}


class Provider:
    """The Provider defines methods to find a client or default to one.
    """
    @staticmethod
    def get_logger(*args: Any) -> logging.Logger:
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

    @staticmethod
    def get_slack(*args: Any) -> Union[Slack, None]:  # pylint: disable=E1136
        """Searches the parameter list *args for an instance of Slack.

        Returns:
            Slack
        """
        for arg in args:
            if isinstance(arg, Slack):
                return arg
            if hasattr(arg, "slack") and isinstance(arg.slack, Slack):
                return arg.slack
        try:
            return Slack()
        except MissingSlackWebhookException:
            Provider.get_logger().debug(
                "@observe: can't send notification to slack, add 'SLACK_WEB_HOOK' to os.environ to activate.")

    @staticmethod
    def get_metric(*args: Any) -> Union[IMetric, DogStatsd]:  # pylint: disable=E1136
        """Searches the parameter list *args for an instance of IMetric or DogStatsd

        Returns:
            IMetric | DogStatsd
        """
        for arg in args:
            if isinstance(arg, (IMetric, DogStatsd)):
                return arg
            if hasattr(arg, "metric") and isinstance(arg.metric, IMetric):
                return arg.metric
            if hasattr(arg, "statsd") and isinstance(arg.statsd, DogStatsd):
                return arg.statsd

        return Metric()


class Resolver:
    """The Resolver provides methods used to process parameter passed to the @observe decorater.
    """

    @staticmethod
    def _get_str_value(key: str, message: Dict[str, Any]) -> Union[str, None]:  # pylint: disable=E1136
        value = message.get(str(key))
        if isinstance(value, str):
            return value
        return None

    @staticmethod
    def resolve_identity(*args: Any, func: Any, trace_id: Optional[str] = "") -> str:  # pylint: disable=E1136

        identity = "observe(%s)" % trace_id

        try:
            identity = "%s(%s)" % (args[0].identity, trace_id)
            return identity
        except Exception:
            pass

        try:
            identity = "%s(%s)" % (args[0].__class__.__name__, trace_id)
            return identity
        except Exception:
            pass

        try:
            identity = "%s(%s)" % (func.__name__, trace_id)
            return identity
        except Exception:
            pass

        return identity

    @staticmethod
    def resolve_tags_from(tags_from: Optional[Dict[str, List[str]]], **kwargs: Any) -> List[str]:  # pylint: disable=E1136
        """This methods helps to identify and create tags from **kwargs dictionaries based on 'tags_from' setup.

        Args:
            tags_from (Optional[Dict[str, List[str]]]): this is the actual `tags_from` argument from @observe decoration.

        Returns:
            List[str]: a list of tags if found any, else empty list
        """
        # initialize default empty list
        tags: List[str] = []

        # ff15, we don't need to find additional tags
        if not tags_from:
            # return empty list
            return tags

        # iterate the tags from dictionary
        for lookup_key, tags_keys in tags_from.items():

            # ensure we work with types, we expected to get
            if not isinstance(tags_keys, list):
                continue

            # try to get the message from kwargs
            message = kwargs.get(str(lookup_key))

            # ensure the message was available, and is a dictionary
            if not isinstance(message, dict):
                continue

            # iterate all tags we supposed to find
            for tag_key in tags_keys:

                # check if the tag was in the message
                tag_value = Resolver._get_str_value(key=tag_key, message=message)

                # ensure we did get a value and the value is a string
                if not tag_value:
                    continue

                # create the tag and append
                tags.append("%s:%s" % (tag_key, tag_value))

        return tags

    @staticmethod
    def resolve_trace_id(trace_id_from: Optional[Dict[str, str]], **kwargs: Any) -> str:  # pylint: disable=E1136
        """This method attempts to get a trace_id from **kwargs dictionaries based on 'trace_id_from' setup.

        Args:
            trace_id_from (Optional[Dict[str, str]]): contains the keyword and the field to be used.

        Returns:
            str: [description]
        """
        trace_id = ""

        if not isinstance(trace_id_from, dict):
            return trace_id

        for key, value in trace_id_from.items():
            try:
                # try to get the message from kwargs
                message = kwargs.get(str(key))
                trace_id = Resolver._get_str_value(key=value, message=message)
                if trace_id:
                    return trace_id
            except Exception:
                pass

        return trace_id

    @staticmethod
    def resolve_observed_sli_tag(process_time: int, threshold_map: Dict[int, str] = observe_threshold_map) -> str:  # pylint: disable=E1136
        """This method returns an `observed_sli` tag based on the processing time (ms) provided.

        Args:
            process_time (int): the measured processing time in ms.
            threshold_map (Dict[int, str], optional): a map with defined thresholds. Defaults to observe_threshold_map.

        Returns:
            str: `observed_sli:[tag]`
        """
        # set the current value to fastest threshold
        current_value = threshold_map[0]
        # iterate the hash map
        for key, value in threshold_map.items():
            # if the processing time is smaller or equal to the value in the hashmap
            if process_time <= key:
                # return the current value
                return "observed_sli:%s" % current_value
            # update the current value
            current_value = value
        # return the last updated current value (slowest threshold)
        return "observed_sli:%s" % current_value
