# Observe

[![Atlassian license](https://img.shields.io/badge/license-Apache%202.0-blue.svg?style=flat-square)](LICENSE)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](CONTRIBUTING.md)
![Build](https://github.com/atlassian-labs/observe/workflows/Build/badge.svg)
[![codecov](https://codecov.io/gh/atlassian-labs/observe/branch/main/graph/badge.svg?token=SIUqRd2bsW)](https://codecov.io/gh/atlassian-labs/observe)

**@observe** is a decorator for Python methods, which allows Python developers to collect all basic metrics about the decorated method, generate unified logs and notifications on failure which are easy to trace.


## Installation

```sh
pip install atl-observe
```

## Usage
Decorating the process method and assigning a metic name and static_tags, all tags are added to all metrics generated, used to filter on your dashboards.

```python
from atl_observe import observe

class Engine:

    @observe(metric="process",
             static_tags=["layer:process"])
    def process(self, message: dict):
        pass
```

Decorating the process method and assigning a metric and trace_id_from, the trace_id will now appear in all logs and notifications, used to search your logs.

```python
from atl_observe import observe

class Engine:

    @observe(metric="process",
             trace_id_from={"message": "eventId"})
    def process(self, message: dict):
        pass
```

## Logs, Metrics and Notifications

All logs, metrics and notifications are divided into three categories:

* **Default:** no exceptions were raised.
* **Expected:** an expected Exception was raised.
* **Unexpected Exceptions:** an unexpected / unhandled Exception was raised

### Default
```python
# optional: debug logs
logger.debug("... start.")
logger.debug("... finished.")

# increments
statsd.increment("%s.start" % metric, 1, tags=all_tags)
statsd.increment("%s.finished" % metric, 1, tags=all_tags)

# timing
statsd.timing("%s.time.finished" % metric, dt, tags=all_tags)
```

### Expected
Expected exceptions are managed via ```accept_on``` and ```decline_on``` lists. If the raised exception is part of `accept_on`, the decorator will return a Truthy value, if the exception is part of `decline_on` a Falsy value is returned.

```python
# warning logs
logger.warning("... accepted.")
logger.warning("... declined.")

# increments
statsd.increment('%s.exception.accepted' % metric, tags=all_tags)
statsd.increment('%s.exception.declined' % metric, tags=all_tags)

# timing
statsd.timing("%s.time.accepted" % metric, dt, tags=all_tags)
statsd.timing("%s.time.declined" % metric, dt, tags=all_tags)
```

### Unexpected
```python
# error logs
logger.error("... raised.")

# slack
slack.error("... raised.")

# increments
statsd.increment('%s.exception.raised' % metric, tags=all_tags)

# timing
statsd.timing("%s.time.raised" % metric, dt, tags=all_tags)
```

## Documentation

* `make install` will install all required packages
* `make format` will auto format the project
* `make lint` will run the linter
* `make tests` will run all unit tests




## Contributions

Contributions to **@observe** are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## License

Copyright (c) [2020] Atlassian and others.
Apache 2.0 licensed, see [LICENSE](LICENCE) file.

<br/>

[![With ❤️ from Atlassian](https://raw.githubusercontent.com/atlassian-internal/oss-assets/master/banner-cheers.png)](https://www.atlassian.com)
