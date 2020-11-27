"""Defines tests for utils.Resolver class
"""

from unittest import TestCase

from observe.lib.utils import Resolver


class TestResolverTagsFromEmpty(TestCase):
    """Defines tests for the Resolver.resolve_tags_from staticmethod, where no tags were resolved
    """

    def test_tags_from_returns_empty_list_on_no_kwargs(self):
        # act
        tags = Resolver.resolve_tags_from(tags_from=None)
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": None, "another_message": None})
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": [], "another_message": []})
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": [None, "adsad", [], {}], "another_message": [None, "adsad", [], {}]})
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema"], "another_message": ["type", "schema"]})
        # assert
        self.assertEqual(tags, [])

    def test_tags_from_returns_empty_list_on_no_match(self):
        # arrange kwargs
        my_kwargs = {
            "message": {
                "payload": {}
            },
            "another_message": {
                "payload": {}
            }
        }

        # act
        tags = Resolver.resolve_tags_from(tags_from=None, **my_kwargs)
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": None, "another_message": None}, **my_kwargs)
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": [], "another_message": []}, **my_kwargs)
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": [None, "adsad", [], {}], "another_message": [None, "adsad", [], {}]}, **my_kwargs)
        # assert
        self.assertEqual(tags, [])

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema"], "another_message": ["type", "schema"]}, **my_kwargs)
        # assert
        self.assertEqual(tags, [])


class TestResolverTagsFromFound(TestCase):
    """Defines tests for the Resolver.resolve_tags_from staticmethod, where tags were resolved
    """

    def test_tags_from_returns_tags_from_message(self):
        # arrange kwargs
        my_kwargs = {
            "message": {
                "type": "this_is_the_event_type_from_message",
                "schema": "this_is_the_event_schema_from_message",
                "payload": {}
            },
            "another_message": {
                "payload": {}
            }
        }

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema"], "another_message": ["type", "schema"]}, **my_kwargs)
        # assert
        self.assertEqual(tags, ["type:this_is_the_event_type_from_message", "schema:this_is_the_event_schema_from_message"])

    def test_tags_from_returns_tags_from_another_message(self):
        # arrange kwargs
        my_kwargs = {
            "message": {
                "payload": {}
            },
            "another_message": {
                "type": "this_is_the_event_type_from_another_message",
                "schema": "this_is_the_event_schema_from_another_message",
                "payload": {}
            }
        }

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema"], "another_message": ["type", "schema"]}, **my_kwargs)
        # assert
        self.assertEqual(tags, ["type:this_is_the_event_type_from_another_message", "schema:this_is_the_event_schema_from_another_message"])

    def test_tags_from_returns_tags_from_message_and_another_message(self):
        # arrange kwargs
        my_kwargs = {
            "message": {
                "type": "this_is_the_event_type_from_message",
                "schema": "this_is_the_event_schema_from_message",
                "payload": {}
            },
            "another_message": {
                "type": "this_is_the_event_type_from_another_message",
                "schema": "this_is_the_event_schema_from_another_message",
                "payload": {}
            }
        }

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema"], "another_message": ["type", "schema"]}, **my_kwargs)
        # assert
        self.assertEqual(tags, ["type:this_is_the_event_type_from_message", "schema:this_is_the_event_schema_from_message", "type:this_is_the_event_type_from_another_message", "schema:this_is_the_event_schema_from_another_message"])


class TestResolverTagsFromFoundPartially(TestCase):
    """Defines tests for the Resolver.resolve_tags_from staticmethod, where tags were resolved partially
    """

    def test_tags_from_returns_tags_from_message_type_only(self):
        # arrange kwargs
        my_kwargs = {
            "message": {
                "type": "this_is_the_event_type_from_message"
            }
        }

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema"]}, **my_kwargs)
        # assert
        self.assertEqual(tags, ["type:this_is_the_event_type_from_message"])

    def test_tags_from_returns_tags_from_message_no_payload_of_message(self):
        """This tests that even if the user requests tags from the payload, it still just resolves the first level tags.
        Note:
            This can be implemented later if desired.
        """
        # arrange kwargs
        my_kwargs = {
            "message": {
                "type": "this_is_the_event_type_from_message",
                "schema": "this_is_the_event_schema_from_message",
                "payload": {"name": "observe"}
            }
        }

        # act
        tags = Resolver.resolve_tags_from(tags_from={"message": ["type", "schema", {"payload": ["name"]}]}, **my_kwargs)
        # assert
        self.assertEqual(tags, ["type:this_is_the_event_type_from_message", "schema:this_is_the_event_schema_from_message"])
