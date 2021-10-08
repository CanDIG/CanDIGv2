from chord_metadata_service.restapi.schema_utils import customize_schema
from chord_metadata_service.restapi.schemas import ONTOLOGY_CLASS, ONTOLOGY_CLASS_LIST, EXTRA_PROPERTIES_SCHEMA
from chord_metadata_service.restapi.description_utils import describe_schema
from chord_metadata_service.patients.schemas import INDIVIDUAL_SCHEMA
from . import descriptions as d

# ========================= mCode/FHIR based schemas =========================

# === FHIR datatypes ===

# FHIR Quantity https://www.hl7.org/fhir/datatypes.html#Quantity
QUANTITY = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:quantity_schema",
    "title": "Quantity schema",
    "description": "Schema for the datatype Quantity.",
    "type": "object",
    "properties": {
        "value": {
            "type": "number"
        },
        "comparator": {
            "enum": ["<", ">", "<=", ">=", "="]
        },
        "unit": {
            "type": "string"
        },
        "system": {
            "type": "string",
            "format": "uri"
        },
        "code": {
            "type": "string"
        }
    },
    "additionalProperties": False
}

# FHIR CodeableConcept https://www.hl7.org/fhir/datatypes.html#CodeableConcept
CODEABLE_CONCEPT = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:codeable_concept_schema",
    "title": "Codeable Concept schema",
    "description": "Schema for the datatype Concept.",
    "type": "object",
    "properties": {
        "coding": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "system": {"type": "string", "format": "uri"},
                    "version": {"type": "string"},
                    "code": {"type": "string"},
                    "display": {"type": "string"},
                    "user_selected": {"type": "boolean"}
                }
            }
        },
        "text": {
            "type": "string"
        }
    },
    "additionalProperties": False
}

# FHIR Period https://www.hl7.org/fhir/datatypes.html#Period
PERIOD = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:period_schema",
    "title": "Period",
    "description": "Period schema.",
    "type": "object",
    "properties": {
        "start": {
            "type": "string",
            "format": "date-time"
        },
        "end": {
            "type": "string",
            "format": "date-time"
        }
    },
    "additionalProperties": False
}

# FHIR Ratio https://www.hl7.org/fhir/datatypes.html#Ratio
RATIO = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:ratio",
    "title": "Ratio",
    "description": "Ratio schema.",
    "type": "object",
    "properties": {
        "numerator": QUANTITY,
        "denominator": QUANTITY
    },
    "additionalProperties": False
}

# === FHIR based mCode elements ===

TIME_OR_PERIOD = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:time_or_period",
    "title": "Time of Period",
    "description": "Time of Period schema.",
    "type": "object",
    "properties": {
        "value": {
            "anyOf": [
                {"type": "string", "format": "date-time"},
                PERIOD
            ]
        }
    },
    "additionalProperties": False
}

TUMOR_MARKER_DATA_VALUE = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:tumor_marker_data_value",
    "title": "Tumor marker data value",
    "description": "Tumor marker data value schema.",
    "type": "object",
    "properties": {
        "value": {
            "anyOf": [
                ONTOLOGY_CLASS,
                QUANTITY,
                RATIO
            ]
        }
    },
    "additionalProperties": False
}

# TODO this is definitely should be changed, fhir datatypes are too complex use Ontology_ class
COMPLEX_ONTOLOGY = customize_schema(
    first_typeof=ONTOLOGY_CLASS,
    second_typeof=ONTOLOGY_CLASS,
    first_property="data_value",
    second_property="staging_system",
    schema_id="chord_metadata_service:complex_ontology_schema",
    title="Complex ontology",
    description="Complex object to combine data value and staging system.",
    required=["data_value"]
)


# =================== Metadata service mCode based schemas ===================


MCODE_GENETIC_SPECIMEN_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "specimen_type": ONTOLOGY_CLASS,
        "collection_body": ONTOLOGY_CLASS,
        "laterality": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "specimen_type"]
}, d.GENETIC_SPECIMEN)


MCODE_CANCER_GENETIC_VARIANT_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "data_value": ONTOLOGY_CLASS,
        "method": ONTOLOGY_CLASS,
        "amino_acid_change": ONTOLOGY_CLASS,
        "amino_acid_change_type": ONTOLOGY_CLASS,
        "cytogenetic_location": {
            "type": "object"
        },
        "cytogenetic_nomenclature": ONTOLOGY_CLASS,
        "gene_studied": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "genomic_dna_change": ONTOLOGY_CLASS,
        "genomic_source_class": ONTOLOGY_CLASS,
        "variation_code": ONTOLOGY_CLASS_LIST,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "specimen_type"]
}, d.CANCER_GENETIC_VARIANT)


MCODE_GENOMIC_REGION_STUDIED_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "dna_ranges_examined": ONTOLOGY_CLASS_LIST,
        "dna_region_description": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "gene_mutation": ONTOLOGY_CLASS_LIST,
        "gene_studied": ONTOLOGY_CLASS_LIST,
        "genomic_reference_sequence_id": {
            "type": "object"
        },
        "genomic_region_coordinate_system": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "specimen_type"]
}, d.GENOMIC_REGION_STUDIED)


MCODE_GENOMICS_REPORT_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "code": ONTOLOGY_CLASS,
        "performing_organization_name": {
            "type": "string"
        },
        "issued": {
            "type": "string",
            "format": "date-time"
        },
        "genetic_specimen": {
            "type": "array",
            "items": MCODE_GENETIC_SPECIMEN_SCHEMA
        },
        "genetic_variant": MCODE_CANCER_GENETIC_VARIANT_SCHEMA,
        "genomic_region_studied": MCODE_GENOMIC_REGION_STUDIED_SCHEMA,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "code", "issued"]
}, d.GENOMICS_REPORT)


MCODE_LABS_VITAL_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "individual": {
            "type": "string"
        },
        "tumor_marker_code": ONTOLOGY_CLASS,
        "tumor_marker_data_value": TUMOR_MARKER_DATA_VALUE,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "individual", "tumor_marker_code"]
}, d.LABS_VITAL)


MCODE_TNM_STAGING_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "tnm_type": {
            "type": "string",
            "enum": [
                "clinical",
                "pathologic"
            ]
        },
        "stage_group": COMPLEX_ONTOLOGY,
        "primary_tumor_category": COMPLEX_ONTOLOGY,
        "regional_nodes_category": COMPLEX_ONTOLOGY,
        "distant_metastases_category": COMPLEX_ONTOLOGY,
        "cancer_condition": {
            "type": "string"
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": [
        "id",
        "tnm_type",
        "stage_group",
        "primary_tumor_category",
        "regional_nodes_category",
        "distant_metastases_category",
        "cancer_condition"
    ]
}, d.TNM_STAGING)


MCODE_CANCER_CONDITION_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "condition_type": {
            "type": "string",
            "enum": [
                "primary",
                "secondary"
            ]
        },
        "body_site": ONTOLOGY_CLASS_LIST,
        "clinical_status": ONTOLOGY_CLASS,
        "code": ONTOLOGY_CLASS,
        "date_of_diagnosis": {
            "type": "string",
            "format": "date-time"
        },
        "histology_morphology_behavior": ONTOLOGY_CLASS,
        "tnm_staging": {
            "type": "array",
            "items": MCODE_TNM_STAGING_SCHEMA
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "condition_type", "code"]
}, d.LABS_VITAL)


MCODE_CANCER_RELATED_PROCEDURE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "procedure_type": {
            "type": "string",
            "enum": [
                "radiation",
                "surgical"
            ]
        },
        "code": ONTOLOGY_CLASS,
        "body_site": ONTOLOGY_CLASS_LIST,
        "laterality": ONTOLOGY_CLASS,
        "treatment_intent": ONTOLOGY_CLASS,
        "reason_code": ONTOLOGY_CLASS,
        "reason_reference": {
            "type": "array",
            "items": {
                "type": "string"
            }
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "procedure_type", "code"]
}, d.CANCER_RELATED_PROCEDURE)


MCODE_MEDICATION_STATEMENT_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "medication_code": ONTOLOGY_CLASS,
        "termination_reason": ONTOLOGY_CLASS_LIST,
        "treatment_intent": ONTOLOGY_CLASS,
        "start_date": {
            "type": "string",
            "format": "date-time"
        },
        "end_date": {
            "type": "string",
            "format": "date-time"
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "medication_code"]
}, d.MEDICATION_STATEMENT)


MCODE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:mcode_schema",
    "title": "Metadata service customized mcode schema",
    "description": "Schema for describe mcode data elements in metadata service.",
    "type": "object",
    "properties": {
        "id": {
            "type": "string"
        },
        "subject": INDIVIDUAL_SCHEMA,
        "genomics_report": MCODE_GENOMICS_REPORT_SCHEMA,
        "cancer_condition": MCODE_CANCER_CONDITION_SCHEMA,
        "cancer_related_procedures": MCODE_CANCER_RELATED_PROCEDURE_SCHEMA,
        "medication_statement": {
            "type": "array",
            "items": MCODE_MEDICATION_STATEMENT_SCHEMA
        },
        "date_of_death": {
            "type": "string"
        },
        "tumor_marker": {
            "type": "array",
            "items": MCODE_LABS_VITAL_SCHEMA
        },
        "cancer_disease_status": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    }
}, d.MCODEPACKET)
