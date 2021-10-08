from django.test import TestCase
from ..schema_utils import merge_schema_dictionaries


class TestSchemaMerge(TestCase):
    def test_merge_1(self):
        self.assertDictEqual(
            merge_schema_dictionaries({"a": 1}, {"b": 2}),
            {"a": 1, "b": 2})

    def test_merge_2(self):
        self.assertDictEqual(
            merge_schema_dictionaries({"a": 1, "d": 4}, {"a": 2, "b": {"c": 3}}),
            {"a": 2, "d": 4, "b": {"c": 3}})

    def test_merge_3(self):
        self.assertDictEqual(
            merge_schema_dictionaries(
                {"a": {"b": 1}, "c": {"d": {"e": 1}, "f": 5}},
                {"c": {"d": {"g": 8}}}),
            {"a": {"b": 1}, "c": {"d": {"e": 1, "g": 8}, "f": 5}})
