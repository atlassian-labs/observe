"""This module defines an example of a custom IMetric implementation.
"""
from typing import Any, List, Optional, Text

from datadog import DogStatsd


class TimingNotTImplementedError(NotImplementedError):
    """[summary]
    """


class IncrementNotImplementedError(NotImplementedError):
    """[summary]
    """


class IMetric:
    """This interface defines methods the @observe decorator is going to call, it is a sub-set of DogStatsd.
    """

    def timing(
            self,
            metric: Text,
            value: float,
            tags: Optional[List[str]] = None,  # pylint: disable=E1136
            sample_rate: Optional[float] = None) -> Any:  # pylint: disable=E1136
        """Record the timing value for the metric, appends tags.
        """
        raise TimingNotTImplementedError("%s: the method is not implemented." % self.__class__.__name__)

    def increment(
            self,
            metric: Text,
            value: float = 1,
            tags: Optional[List[str]] = None,  # pylint: disable=E1136
            sample_rate: Optional[float] = None) -> Any:  # pylint: disable=E1136
        """Increment the metric by the provided value, appends tags.
        """
        raise IncrementNotImplementedError("%s: the method is not implemented." % self.__class__.__name__)


class Metric(DogStatsd, IMetric):
    """This is an example of a custom IMetric implementation, using the actual DogStatsd client which @observers would
    support natively.

    Note: we do not need to overwrite the timing, increment methods since the interfaces match 100%.

    Args:
        DogStatsd (class): this is the class as provided by the datadog package (from datadog import DogStatsd)
        IMetric (interface): this is the interface class provided by @observe for users who don't want to use DogStatsd
    """

    def __init__(self, **kwargs: Any):
        """Initializes the Metric client.
        """
        super(Metric, self).__init__(**kwargs)
