"""Defines tests for utils.Provider class
"""
import logging
from logging import Logger
from unittest import TestCase

from datadog.dogstatsd.base import DogStatsd
from mock import patch

from observe.lib.logger import Logger as CustomLogger
from observe.lib.metrics import IMetric, Metric
from observe.lib.slack import Slack
from observe.lib.utils import Provider


class TestProviderGetLogger(TestCase):
    """Defines tests for the Provider.get_logger staticmethod.
    """

    def test_when_args_are_falsy(self):
        # arrange, act
        logger = Provider.get_logger(None, object, {}, [])
        # assert
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, "Observe")

    def test_when_args_have_logger(self):
        # arrange, act
        logger = Provider.get_logger(Logger("ArgLogger"))
        # assert
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, "ArgLogger")

    def test_when_args_is_class_with_Logger(self):
        # arrange
        class A:
            def __init__(self):
                self.logger = Logger(name="Logger")
        # act
        logger = Provider.get_logger(*(A(),))
        # assert
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, "Logger")

    def test_when_args_is_class_with_getLogger(self):
        # arrange
        class A:
            def __init__(self):
                self.logger = logging.getLogger("getLogger")
        # act
        logger = Provider.get_logger(*(0, A()))
        # assert
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, "getLogger")

    def test_when_args_is_class_with_CustomLogger(self):
        # arrange
        class A:
            def __init__(self):
                self.logger = CustomLogger(name="CustomLogger")
        # act
        logger = Provider.get_logger(*(A(),))
        # assert
        self.assertIsInstance(logger, Logger)
        self.assertEqual(logger.name, "CustomLogger")


class TestProviderGetSlack(TestCase):
    """Defines tests for the Provider.get_slack staticmethod.
    """

    def setUp(self) -> None:
        self.env_with_slack = patch.dict('os.environ', {'SLACK_WEB_HOOK': 'http://slack-web-hook'})

    def test_when_args_are_falsy(self):
        # arrange os environ patch
        with self.env_with_slack:
            # arrange, act
            slack = Provider.get_slack(None, object, {}, [])
        # assert
        self.assertIsInstance(slack, Slack)
        self.assertEqual(slack.web_hook, "http://slack-web-hook")

    def test_when_args_have_slack(self):
        # arrange, act
        slack = Provider.get_slack(Slack(web_hook="slack-web-hook"))
        # assert
        self.assertIsInstance(slack, Slack)
        self.assertEqual(slack.web_hook, "slack-web-hook")

    def test_when_args_is_class_with_slack(self):
        # arrange
        class A:
            def __init__(self):
                self.slack = Slack(web_hook="slack-web-hook-2")
        # act
        slack = Provider.get_slack(A())
        # assert
        self.assertIsInstance(slack, Slack)
        self.assertEqual(slack.web_hook, "slack-web-hook-2")

    def test_when_no_args_no_slack_web_hook(self):
        # arrange, act
        slack = Provider.get_slack()
        # assert
        self.assertIsNone(slack)


class TestProviderGetMetric(TestCase):

    def test_when_args_are_falsy(self):

        metric = Provider.get_metric(None, object, {}, [])
        # assert
        self.assertIsInstance(metric, IMetric)
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.host, "localhost")

    def test_when_args_have_metric(self):
        # arrange, act
        metric = Provider.get_metric(Metric(host="custom_metric"))
        # assert
        self.assertIsInstance(metric, IMetric)
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.host, "custom_metric")

    def test_when_args_have_dogstatsd(self):
        # arrange, act
        metric = Provider.get_metric(DogStatsd(host="custom_dog"))
        # assert
        self.assertIsInstance(metric, DogStatsd)
        self.assertEqual(metric.host, "custom_dog")

    def test_when_args_is_class_with_metric(self):
        # arrange
        class A:
            def __init__(self):
                self.metric = Metric(host="custom_metric_in_class")
        # act
        metric = Provider.get_metric(A())
        # assert
        self.assertIsInstance(metric, IMetric)
        self.assertIsInstance(metric, Metric)
        self.assertEqual(metric.host, "custom_metric_in_class")

    def test_when_args_is_class_with_dogstatsd(self):
        # arrange
        class A:
            def __init__(self):
                self.statsd = DogStatsd(host="custom_dog_in_class")
        # act
        metric = Provider.get_metric(A())
        # assert
        self.assertIsInstance(metric, DogStatsd)
        self.assertEqual(metric.host, "custom_dog_in_class")
