from django.test import TestCase
from .. import description_utils as du


TEST_SCHEMA_1 = {"type": "string"}
TEST_SCHEMA_2 = {
    "type": "array",
    "items": {"type": "string"}
}

TEST_HELP_2 = {
    "description": "1",
    "items": "2"
}


class TestDescriptions(TestCase):
    def test_descriptions(self):
        assert isinstance(du.describe_schema(None, "Test"), dict)
        self.assertDictEqual(du.describe_schema(TEST_SCHEMA_1, None), TEST_SCHEMA_1)

        d = du.describe_schema(TEST_SCHEMA_2, TEST_HELP_2)
        assert d["description"] == d["help"]
        assert d["help"] == "1"
        assert d["items"]["description"] == d["items"]["help"]
        assert d["items"]["description"] == "2"

    def test_help_get(self):
        assert du.rec_help(TEST_HELP_2, "[item]") == "2"
