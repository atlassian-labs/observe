"""This module provides utils for the @observe operator, to keep the actual implementation maintainable and readable.
"""
import logging
from typing import Any, Dict, List, Optional, Union

from datadog.dogstatsd.base import DogStatsd

from observe.lib.logger import Logger
from observe.lib.metrics import IMetric, Metric
from observe.lib.slack import MissingSlackWebhookException, Slack


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

    @staticmethod
    def resolve_tags_from(tags_from: Optional[Dict[str, List[str]]], **kwargs: Any) -> List[str]:

        # initialize default empty list
        tags: List[str] = []

        # ff15, we don't need to find additional tags
        if not tags_from:
            # return empty list
            return tags

        # iterate the tags from dictionary
        for lookup_key, tags_keys in tags_from.items():

            # ensure we work with types, we expected to get
            if not isinstance(lookup_key, str) or not isinstance(tags_keys, list):
                continue

            # try to get the message from kwargs
            message = kwargs.get(lookup_key)

            # ensure the message was available, and is a dictionary
            if not message or not isinstance(message, dict):
                continue

            # iterate all tags we supposed to find
            for tag_key in tags_keys:

                # ensure we work with types, we expected to get
                if not isinstance(tag_key, str):
                    continue

                # check if the tag was in the message
                tag_value = message.get(tag_key)

                # ensure we did get a value and the value is a string
                if not tag_value or not isinstance(tag_value, str):
                    continue

                # create the tag and append
                tags.append("%s:%s" % (tag_key, tag_value))

        return tags
