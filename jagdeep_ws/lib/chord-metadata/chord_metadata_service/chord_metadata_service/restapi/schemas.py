from . import descriptions
from .description_utils import describe_schema, EXTRA_PROPERTIES, ONTOLOGY_CLASS as ONTOLOGY_CLASS_DESC

# Individual schemas for validation of JSONField values


__all__ = [
    "ONTOLOGY_CLASS",
    "ONTOLOGY_CLASS_LIST",
    "KEY_VALUE_OBJECT",
    "AGE_STRING",
    "AGE",
    "AGE_RANGE",
    "AGE_OR_AGE_RANGE",
    "EXTRA_PROPERTIES_SCHEMA",
    "FHIR_BUNDLE_SCHEMA",
]


# ======================== Phenopackets based schemas =========================


ONTOLOGY_CLASS = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:ontology_class_schema",
    "title": "Ontology class schema",
    "type": "object",
    "properties": {
        "id": {"type": "string"},
        "label": {"type": "string"}
    },
    "additionalProperties": False,
    "required": ["id", "label"]
}, ONTOLOGY_CLASS_DESC)

ONTOLOGY_CLASS_LIST = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:ontology_class_list_schema",
    "title": "Ontology class list",
    "description": "Ontology class list",
    "type": "array",
    "items": ONTOLOGY_CLASS,
}


KEY_VALUE_OBJECT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:key_value_object_schema",
    "title": "Key-value object",
    "description": "The schema represents a key-value object.",
    "type": "object",
    "patternProperties": {
        "^.*$": {"type": "string"}
    },
    "additionalProperties": False
}

EXTRA_PROPERTIES_SCHEMA = describe_schema({
    "type": "object"
}, EXTRA_PROPERTIES)


AGE_STRING = describe_schema({"type": "string"}, descriptions.AGE)

AGE = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:age_schema",
    "title": "Age schema",
    "type": "object",
    "properties": {
        "age": AGE_STRING
    },
    "additionalProperties": False,
    "required": ["age"]
}, descriptions.AGE_NESTED)


AGE_RANGE = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:age_range_schema",
    "title": "Age range schema",
    "type": "object",
    "properties": {
        "start": AGE,
        "end": AGE,
    },
    "additionalProperties": False,
    "required": ["start", "end"]
}, descriptions.AGE_RANGE)


AGE_OR_AGE_RANGE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:age_or_age_range_schema",
    "title": "Age schema",
    "description": "An age object describing the age of the individual at the time of collection of biospecimens or "
                   "phenotypic observations.",
    "type": "object",
    "oneOf": [
        AGE,
        AGE_RANGE
    ]
}

DISEASE_ONSET = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:disease_onset_schema",
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "oneOf": [
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS
    ]
}


# ============================ FHIR INGEST SCHEMAS ============================
# The schema used to validate FHIR data for ingestion


FHIR_BUNDLE_SCHEMA = {
    "$id": "chord_metadata_service_fhir_bundle_schema",
    "$schema": "http://json-schema.org/draft-07/schema#",
    "description": "FHIR Bundle schema",
    "type": "object",
    "properties": {
        "resourceType": {
            "type": "string",
            "const": "Bundle",
            "description": "Collection of resources."
        },
        "entry": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "resource": {"type": "object"}
                },
                "additionalProperties": True,
                "required": ["resource"]
            }
        }
    },
    "additionalProperties": True,
    "required": ["resourceType", "entry"]
}
