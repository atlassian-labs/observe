"""This module provides utils for the @observe operator, to keep the actual implementation maintainable and readable.
"""
import logging
from typing import Any, Union

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
            Provider.get_logger().info(
                "@observe: slack is disabled, add 'SLACK_WEB_HOOK' to os.environ in order to use.")

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
