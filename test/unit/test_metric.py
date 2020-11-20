"""Defines tests for metric.Metric class
"""
from unittest import TestCase

from datadog import DogStatsd
from mock import patch

from observe.lib.metrics import IMetric, Metric


class TestMetricInitialization(TestCase):
    """Defines tests for the Metric.__init__ method, mainly interested that we did not break statsd.
    """

    def setUp(self) -> None:
        self.env_dd = patch.dict('os.environ', {
            'DD_AGENT_HOST': 'env_host',
            'DD_DOGSTATSD_PORT': '4321',
            'DATADOG_TAGS': 'my_tag_1,my_tag_2'
        })

    def test_successful_default(self):
        # arrange, act
        client = Metric()
        # assert interface
        self.assertIsInstance(client, DogStatsd)
        self.assertIsInstance(client, IMetric)
        # assert statsd
        self.assertEqual(client.host, "localhost")
        self.assertEqual(client.port, 8125)

    def test_successful_kwargs(self):
        # arrange, act
        client = Metric(**{
            "host": "myhost",
            "port": 1234
        })
        # assert interface
        self.assertIsInstance(client, DogStatsd)
        self.assertIsInstance(client, IMetric)
        # assert statsd
        self.assertEqual(client.host, "myhost")
        self.assertEqual(client.port, 1234)

    def test_successful_env(self):
        # arrange env
        with self.env_dd:
            # act
            client = Metric()

        # assert interface
        self.assertIsInstance(client, DogStatsd)
        self.assertIsInstance(client, IMetric)
        # assert statsd
        self.assertEqual(client.host, "env_host")
        self.assertEqual(client.port, 4321)
        self.assertEqual(client.constant_tags, ["my_tag_1", "my_tag_2"])

    def test_successful_overwrite(self):
        # arrange, act
        client = Metric()
        # act overwrite
        client.namespace = "observe"
        client.constant_tags.append("observe")
        client.host = "micros_host"
        client.port = 1337
        # assert interface
        self.assertIsInstance(client, DogStatsd)
        self.assertIsInstance(client, IMetric)
        # assert statsd
        self.assertEqual(client.host, "micros_host")
        self.assertEqual(client.port, 1337)
        self.assertEqual(client.constant_tags, ["observe"])
        self.assertEqual(client.namespace, "observe")
