from chord_metadata_service.restapi.schema_utils import customize_schema
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, AGE_OR_AGE_RANGE, EXTRA_PROPERTIES_SCHEMA
from chord_metadata_service.restapi.description_utils import describe_schema

from .descriptions import INDIVIDUAL


COMORBID_CONDITION = customize_schema(
    first_typeof=ONTOLOGY_CLASS,
    second_typeof=ONTOLOGY_CLASS,
    first_property="clinical_status",
    second_property="code",
    schema_id="chord_metadata_service:comorbid_condition_schema",
    title="Comorbid Condition schema",
    description="Comorbid condition schema."
)


INDIVIDUAL_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
            "description": "Unique researcher-specified identifier for the individual.",
        },
        "alternate_ids": {
            "type": "array",
            "items": {
                "type": "string",
            },
            "description": "A list of alternative identifiers for the individual.",  # TODO: More specific
        },
        "date_of_birth": {
            # TODO: This is a special ISO format... need UI for this
            "type": "string",
        },
        "age": AGE_OR_AGE_RANGE,
        "sex": {
            "type": "string",
            "enum": ["UNKNOWN_SEX", "FEMALE", "MALE", "OTHER_SEX"],
            "description": "An individual's phenotypic sex.",
        },
        "karyotypic_sex": {
            "type": "string",
            "enum": [
                "UNKNOWN_KARYOTYPE",
                "XX",
                "XY",
                "XO",
                "XXY",
                "XXX",
                "XXYY",
                "XXXY",
                "XXXX",
                "XYY",
                "OTHER_KARYOTYPE"
            ],
            "description": "An individual's karyotypic sex.",
        },
        "taxonomy": ONTOLOGY_CLASS,
        "active": {
            "type": "boolean"
        },
        "deceased": {
            "type": "boolean"
        },
        "race": {
            "type": "string"
        },
        "ethnicity": {
            "type": "string"
        },
        "comorbid_condition": COMORBID_CONDITION,
        "ecog_performance_status": ONTOLOGY_CLASS,
        "karnofsky": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA,
    },
    "required": ["id"]
}, INDIVIDUAL)
