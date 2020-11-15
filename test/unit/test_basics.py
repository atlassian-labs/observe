"""Defines basic tests where the assertion is provided by no exception being raised.
"""
from unittest import TestCase

from observe.decorator import observe


class TestDecoratorWraps(TestCase):
    """Defines tests for @observe use-cases with minimum setup.
    """

    def test_function(self):
        """Test where @observe wraps a function.
        """
        # arrange, @observe function
        @observe(metric="your_metric")
        def process(message: dict) -> dict:
            return message

        # act, process
        process(message={})

        # assert, assertion provided by no exception

    def test_method(self):
        """Test where @observe wraps a method in a class.
        """
        # arrange, @observe method
        class A:
            @observe(metric="your_metric")
            def process(self, message: dict) -> dict:
                return message

        # arrange, class
        a = A()

        # act, process
        a.process(message={})

        # assert, assertion provided by no exception
