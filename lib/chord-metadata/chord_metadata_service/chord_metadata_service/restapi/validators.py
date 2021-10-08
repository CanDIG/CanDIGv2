from rest_framework import serializers
from jsonschema import Draft7Validator, FormatChecker
from chord_metadata_service.restapi.schemas import (
    AGE_OR_AGE_RANGE,
    ONTOLOGY_CLASS,
    ONTOLOGY_CLASS_LIST,
    KEY_VALUE_OBJECT,
)


class JsonSchemaValidator:
    """ Custom class based validator to validate against Json schema for JSONField """

    def __init__(self, schema, formats=None):
        self.schema = schema
        self.formats = formats
        self.validator = Draft7Validator(self.schema, format_checker=FormatChecker(formats=self.formats))

    def __call__(self, value):
        if not self.validator.is_valid(value):
            raise serializers.ValidationError("Not valid JSON schema for this field.")
        return value

    def __eq__(self, other):
        return self.schema == other.schema

    def deconstruct(self):
        return (
            'chord_metadata_service.restapi.validators.JsonSchemaValidator',
            [self.schema],
            {"formats": self.formats}
        )


age_or_age_range_validator = JsonSchemaValidator(AGE_OR_AGE_RANGE)
ontology_validator = JsonSchemaValidator(ONTOLOGY_CLASS)
ontology_list_validator = JsonSchemaValidator(ONTOLOGY_CLASS_LIST)
key_value_validator = JsonSchemaValidator(KEY_VALUE_OBJECT)
