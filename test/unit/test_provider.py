"""Defines tests for utils.Provider class
"""
import logging
from logging import Logger
from unittest import TestCase

from observe.lib.logger import Logger as CustomLogger
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
