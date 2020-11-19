"""Defines tests for the @observe decorator.
"""
from unittest import TestCase

from mock import Mock, patch

from observe.decorator import observe


class TestDecorator(TestCase):
    """Defines tests for @observe use-cases with basic setup.
    """

    def test_wraps_function(self):
        """Test where @observe wraps a function.
        """
        # arrange, @observe function
        @observe(metric="your_metric")
        def process(message: dict) -> dict:
            return message
        # act, assert, assertion provided by no exception
        process(message={})

    def test_wraps_method(self):
        """Test where @observe wraps a method in a class.
        """
        # arrange, @observe method
        class A:
            def __init__(self, name="A"):
                self.name = name

            @observe(metric="your_metric")
            def process(self, message: dict) -> dict:
                return message
        # act, assert, assertion provided by no exception
        A().process(message={})


class TestDecoratorExceptions(TestCase):
    """Defines tests for @observe use-cases with accept_on, decline_on setup.
    """

    class AcceptOnException(Exception):
        """If raised, message should be acknowledged.
        """

    class DeclineOnException(Exception):
        """If raised, message should not be acknowledged.
        """

    class CustomException(Exception):
        """If raised, message should not be acknowledged, notify also.
        """

    def setUp(self) -> None:
        self.env_with_slack = patch.dict('os.environ', {'SLACK_WEB_HOOK': 'https://hooks.slack.com/services/top_secret_1'})

    def test_function_accepts_on(self):
        # arrange, @observe function which raises to accept
        @observe(metric="your_metric", accept_on=[TestDecoratorExceptions.AcceptOnException])
        def process() -> None:
            raise TestDecoratorExceptions.AcceptOnException("... acknowledge me ...")
        # act
        response = process()
        # assert
        self.assertEqual(response, True)

    def test_method_accepts_on(self):
        # arrange, @observe function which raises to accept
        class A:
            @observe(metric="your_metric", accept_on=[TestDecoratorExceptions.AcceptOnException])
            def process(self) -> None:
                raise TestDecoratorExceptions.AcceptOnException("... acknowledge me ...")
        # act
        response = A().process()
        # assert
        self.assertEqual(response, True)

    def test_function_declines_on(self):
        # arrange, @observe function which raises to accept
        @observe(metric="your_metric", decline_on=[TestDecoratorExceptions.DeclineOnException])
        def process() -> None:
            raise TestDecoratorExceptions.DeclineOnException("... don't acknowledge me ...")
        # act
        response = process()
        # assert
        self.assertEqual(response, False)

    def test_method_declines_on(self):
        # arrange, @observe function which raises to accept
        class A:
            @observe(metric="your_metric", decline_on=[TestDecoratorExceptions.DeclineOnException])
            def process(self) -> None:
                raise TestDecoratorExceptions.DeclineOnException("... don't acknowledge me ...")
        # act
        response = A().process()
        # assert
        self.assertEqual(response, False)

    @patch("observe.lib.slack.requests")
    def test_function_raises(self, requests):
        # arrange patch
        requests.return_value = Mock(status_code=200)
        # arrange, @observe function which raises to accept

        @observe(metric="your_metric")
        def process() -> None:
            raise TestDecoratorExceptions.CustomException("... uhuh don't acknowledge me ...")
        # act
        self.assertRaises(TestDecoratorExceptions.CustomException, process)

    @patch("observe.lib.slack.requests")
    def test_method_raises(self, requests):
        # arrange patch
        requests.return_value = Mock(status_code=200)
        # arrange, @observe function which raises to accept

        class A:
            @observe(metric="your_metric")
            def process(self) -> None:
                raise TestDecoratorExceptions.CustomException("... uhuh don't acknowledge me ...")
        # act
        with self.env_with_slack:
            self.assertRaises(TestDecoratorExceptions.CustomException, A().process)
