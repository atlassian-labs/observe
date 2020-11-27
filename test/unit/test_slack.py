"""Defines tests for slack.Slack class
"""
import os
from unittest import TestCase, skipIf

from mock import patch

from observe.lib.slack import MissingSlackWebhookException, Slack

slack_web_hook_required = skipIf(
    condition=bool(not os.environ.get('SLACK_WEB_HOOK')),
    reason="The SLACK_WEB_HOOK environment variable is not set.")


class TestSlackInitialization(TestCase):
    """Defines tests for the Slack.__init__ method.
    """

    def setUp(self) -> None:
        self.env_with_slack = patch.dict('os.environ', {'SLACK_WEB_HOOK': 'https://hooks.slack.com/services/top_secret_1'})
        self.env_without_slack = patch.dict('os.environ', {'SLACK_WEB_HOOK': ''})

    def test_successful_using_environment(self):
        # arrange os environ patch
        with self.env_with_slack:
            # arrange client, act initialize
            slack = Slack()
            # assert webhook from os
            self.assertEqual(slack.web_hook, os.environ.get("SLACK_WEB_HOOK"))

    def test_successful_using_injected(self):
        # arrange, act, assert, assertion provided by no exception
        slack = Slack(web_hook="https://hooks.slack.com/services/top_secret_2")
        # assert
        self.assertEqual(slack.web_hook, "https://hooks.slack.com/services/top_secret_2")

    def test_raises_missing(self):
        with self.env_without_slack:
            # arrange, act, assert, assertion provided by no exception
            self.assertRaises(MissingSlackWebhookException, Slack)


class TestSlackNotification(TestCase):
    """Defines tests for all Slack notifications, requires SLACK_WEB_HOOK to be set.
    """
    @slack_web_hook_required
    def test_logger_like(self):
        # arrange slack using os
        slack = Slack()
        # act
        slack.info("This is coming from https://github.com/atlassian-labs/observe build!")
        slack.warning("This is coming from https://github.com/atlassian-labs/observe build!")
        slack.error("This is coming from https://github.com/atlassian-labs/observe build!")
        # assert, assertion provided by no exception

    @slack_web_hook_required
    def test_slack_like(self):
        # arrange slack using os
        slack = Slack()
        # act
        slack.info(header="This is the header", title="This is the title", text="This is coming from https://github.com/atlassian-labs/observe build!")
        slack.warning(header="This is the header", title="This is the title", text="This is coming from https://github.com/atlassian-labs/observe build!")
        slack.error(header="This is the header", title="This is the title", text="This is coming from https://github.com/atlassian-labs/observe build!")
        # assert, assertion provided by no exception
