from django.test import TestCase
from jsonschema import Draft7Validator

from ..data_types import DATA_TYPES


class SchemaTest(TestCase):
    @staticmethod
    def test_data_type_schemas():
        for d in DATA_TYPES.values():
            Draft7Validator.check_schema(d["schema"])
            Draft7Validator.check_schema(d["metadata_schema"])
