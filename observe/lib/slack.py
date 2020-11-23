"""This module defines a basic colorcoded slack client, following a default Logger approach.
To setup your slack app, and get a webhook see:
- https://api.slack.com/messaging/webhooks
Ensure to add the slack web hook to the environment as "SLACK_WEB_HOOK"
"""

import json
import os
import time
from typing import Any, Dict, List, Optional

import requests


class MissingSlackWebhookException(Exception):
    """This exception is raised when no slack web hook was provided/found.
    """


class Slack:
    """This class implements a default Slack client used by @observe decorator.
    """

    def __init__(self, web_hook: Optional[str] = None) -> None:  # pylint: disable=E1136
        """Initializes the Slack client.

        Args:
            web_hook (str, optional): the slack web hook to be used for notifications. Defaults to None.

        Raises:
            MissingSlackWebhookException
        """
        _web_hook = web_hook or os.environ.get("SLACK_WEB_HOOK")
        if not _web_hook:
            raise MissingSlackWebhookException("Failed to determine the slack web hook, please inject or add to os.environ as 'SLACK_WEB_HOOK'.\nsee: https://api.slack.com/messaging/webhooks")
        self.web_hook: str = _web_hook
        self.footer = "app_name=%s" % os.environ.get("APP_NAME", "@observe")

    def info(self, text: str, header: Optional[str] = None, title: Optional[str] = None) -> requests.Response:  # pylint: disable=E1136
        """Creates a colorcoded and formatted info message and pushes it to slack.
        """
        message = self._parse(header=header, title=title, text=text, color="#00BFFF")
        return self._post(payload=message)

    def warning(self, text: str, header: Optional[str] = None, title: Optional[str] = None) -> requests.Response:  # pylint: disable=E1136
        """Creates a colorcoded and formatted warning message and pushes it to slack.
        """
        message = self._parse(header=header, title=title, text=text, color="#FFD700")
        return self._post(payload=message)

    def error(self, text: str, header: Optional[str] = None, title: Optional[str] = None) -> requests.Response:  # pylint: disable=E1136
        """Creates a colorcoded and formatted error message and pushes it to slack.
        """
        message = self._parse(header=header, title=title, text=text, color="#FF4500")
        return self._post(payload=message)

    def _parse(
            self, text: str, color: str, header: Optional[str] = None, title: Optional[str] = None  # pylint: disable=E1136
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Translates the incoming arguments to a slack defined format.
        """
        return {
            "attachments": [{
                "color": color,
                "author_name": header or "",
                "title": title or "",
                "text": text,
                "footer": self.footer,
                "ts": int(time.time())
            }]
        }

    def _post(self, payload: Dict[str, Any]) -> requests.Response:
        """Posts the payload to the provided SLACK_WEB_HOOK.
        """
        kwargs = {
            "data": json.dumps(payload),
            "headers": {
                "content-type": "application/json"
            }
        }
        return requests.post(url=self.web_hook, **kwargs)
