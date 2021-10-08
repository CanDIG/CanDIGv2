from bento_lib.schemas.bento import BENTO_DATA_USE_SCHEMA
from chord_metadata_service.restapi.serializers import GenericSerializer
from jsonschema import Draft7Validator, Draft4Validator
from rest_framework import serializers
from chord_metadata_service.restapi.dats_schemas import get_dats_schema, CREATORS
from chord_metadata_service.restapi.utils import transform_keys

from .models import Project, Dataset, TableOwnership, Table
from .schemas import LINKED_FIELD_SETS_SCHEMA


__all__ = ["ProjectSerializer", "DatasetSerializer", "TableOwnershipSerializer", "TableSerializer"]


BENTO_DATA_USE_SCHEMA_VALIDATOR = Draft7Validator(BENTO_DATA_USE_SCHEMA)
LINKED_FIELD_SETS_SCHEMA_VALIDATOR = Draft7Validator(LINKED_FIELD_SETS_SCHEMA)


#############################################################
#                                                           #
#              Project Management  Serializers              #
#                                                           #
#############################################################


class TableOwnershipSerializer(GenericSerializer):
    class Meta:
        model = TableOwnership
        fields = '__all__'


class DatasetSerializer(GenericSerializer):
    always_include = (
        "description",
        "contact_info",
        "linked_field_sets",
        "table_ownership",
    )

    table_ownership = TableOwnershipSerializer(read_only=True, many=True, exclude_when_nested=["dataset"])

    # noinspection PyMethodMayBeStatic
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value.strip()

    def validate_creators(self, value):
        if isinstance(value, list):
            transformed_value = [transform_keys(item) for item in value]
            validation = self.jsonschema_validation(transformed_value, CREATORS)
            if isinstance(validation, dict):
                raise serializers.ValidationError(validation)
        return value

    # noinspection PyMethodMayBeStatic
    def validate_data_use(self, value):
        validation = BENTO_DATA_USE_SCHEMA_VALIDATOR.is_valid(value)
        if not validation:
            raise serializers.ValidationError("Data use is not valid")
        return value

    # noinspection PyMethodMayBeStatic
    def validate_linked_field_sets(self, value):
        validation = LINKED_FIELD_SETS_SCHEMA_VALIDATOR.is_valid(value)
        if not validation:
            raise serializers.ValidationError([
                str(error.message) for error in LINKED_FIELD_SETS_SCHEMA_VALIDATOR.iter_errors(value)])
        return value

    def validate(self, data):
        """ Validate all fields against DATS schemas. """

        dataset_dats_fields = (
            'alternate_identifiers',
            'related_identifiers',
            'dates',
            'stored_in',
            'spatial_coverage',
            'types',
            'distributions',
            'dimensions',
            'primary_publications',
            'citations',
            'produced_by',
            'licenses',
            'acknowledges',
            'keywords',
        )

        errors = {}
        for field in dataset_dats_fields:
            if not data.get(field):
                continue

            if isinstance(data.get(field), list):
                for item in data.get(field):
                    call_validation = self.jsonschema_validation(
                        value=transform_keys(item),
                        schema=get_dats_schema(field),
                        field_name=field
                    )

                    if isinstance(call_validation, dict):
                        errors.update(call_validation)

            else:
                call_validation = self.jsonschema_validation(
                    value=data.get(field),
                    schema=get_dats_schema(field),
                    field_name=field
                )

                if isinstance(call_validation, dict):
                    errors.update(call_validation)
        if errors:
            raise serializers.ValidationError(errors)

        return data

    @staticmethod
    def jsonschema_validation(value, schema, field_name=None):
        """ Generic validation. Returns errors dict if validation is False. """

        errors = {}

        v = Draft4Validator(schema)
        validation = v.is_valid(value)
        if not validation:
            errors[field_name] = [str(error.message) for error in v.iter_errors(value)]
            return errors

        return validation

    n_of_tables = serializers.IntegerField(read_only=True)

    class Meta:
        model = Dataset
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    # Don't inherit GenericSerializer to not pop empty fields

    datasets = DatasetSerializer(read_only=True, many=True, exclude_when_nested=["project"])

    # noinspection PyMethodMayBeStatic
    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Name must be at least 3 characters")
        return value.strip()

    class Meta:
        model = Project
        fields = '__all__'


class TableSerializer(GenericSerializer):
    identifier = serializers.CharField(read_only=True)
    dataset = DatasetSerializer(read_only=True, exclude_when_nested=["table_ownership"])

    class Meta:
        model = Table
        fields = "__all__"
