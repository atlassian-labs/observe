"""Defines tests for the @observe decorator.
"""
from typing import Any, Dict
from unittest import TestCase

from mock import Mock, patch

from atl_observe import observe
from atl_observe.lib.metrics import (IMetric, IncrementNotImplementedError,
                                     TimingNotTImplementedError)


class TestDecorator(TestCase):
    """Defines tests for @observe use-cases with basic setup.
    """

    def test_wraps_function_accepts_args_kwargs(self):
        """Test where @observe wraps a function which accepts *args, **kwargs.
        """
        # arrange, @observe args, kwargs
        @observe(metric="your_metric")
        def process(*args, **kwargs):
            pass
        # act, assert, assertion provided by no exception
        process(1, 2, 3, name="observe", message={})

    def test_wraps_function_no_args_no_kwargs(self):
        """Test where @observe wraps a function, no args, no kwargs.
        """
        # arrange, @observe args, kwargs
        @observe(metric="your_metric")
        def process():
            pass
        # act, assert, assertion provided by no exception
        process()

    def test_wraps_method_kwargs(self):
        """Test where @observe wraps a method, which did not get any args, kwargs.

        Note:
            The only arg is the class itself
        """
        # arrange, @observe args, kwargs
        class A:
            @observe(metric="your_metric")
            def process(self):
                pass

        # act, assert, assertion provided by no exception
        A().process()

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


class TestDecoratorLoaded(TestCase):
    """Defines tests for @observe use-cases with loaded setup.
    """

    def setUp(self) -> None:
        self.message = {
            "eventId": "1234-4321-abcd-dcba",
            "schema": "my_schema",
            "type": "my_type",
            "ingestionSource": "my_source",
            "payload": {
                "field_a": True,
            }
        }

    def test_loaded_function(self):

        # arrange function
        @observe(metric="function",
                 accept_on=[],
                 decline_on=[Exception],
                 static_tags=["test:loaded", "test:function"],
                 tags_from={"message": ["type", "schema", "ingestionSource"]},
                 trace_id_from={"message": "eventId"})
        def my_function(message: Dict[str, Any]):
            raise Exception("MyFunctionRaised")

        # act, assertion provided by no exception
        my_function(message=self.message)

    def test_loaded_method(self):

        # arrange class
        class MyClass:
            identity = "PewPew"

            @observe(metric="method",
                     accept_on=[],
                     decline_on=[Exception],
                     static_tags=["test:loaded", "test:function"],
                     tags_from={"message": ["type", "schema", "ingestionSource"]},
                     trace_id_from={"message": "eventId"})
            def my_method(self, message: Dict[str, Any]):
                raise Exception("MyMethodRaised")

        # act, assertion provided by no exception
        MyClass().my_method(message=self.message)


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

    @patch("atl_observe.lib.slack.requests")
    def test_function_raises(self, requests):
        # arrange patch
        requests.return_value = Mock(status_code=200)
        # arrange, @observe function which raises to accept

        @observe(metric="your_metric")
        def process() -> None:
            raise TestDecoratorExceptions.CustomException("... uhuh don't acknowledge me ...")
        # act
        self.assertRaises(TestDecoratorExceptions.CustomException, process)

    @patch("atl_observe.lib.slack.requests")
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


class TestDecoratorIMetricExceptions(TestCase):
    """Defines tests for @observe use-cases where IMetric was used incorrect
    """

    def test_observe_raises_on_metric_interface_incorrect_use(self):
        """This is an example of how a user can define their own metric client.
        Note:
            In this case, the interface ws used directly, you need to implement the actual methods.
        """
        # arrange class, implements metric wrong
        class A:
            def __init__(self):
                self.metric = IMetric()

            @observe(metric="my_metric")
            def process(self, message: Dict[str, Any]) -> Dict[str, Any]:
                return message

        kwargs = {
            "message": {"HelloWorld": True}
        }
        # act
        self.assertRaises((TimingNotTImplementedError, IncrementNotImplementedError), A().process, **kwargs)
