# Individual schemas for validation of JSONField values

from chord_metadata_service.patients.schemas import INDIVIDUAL_SCHEMA
from chord_metadata_service.resources.schemas import RESOURCE_SCHEMA
from chord_metadata_service.restapi.description_utils import describe_schema
from chord_metadata_service.restapi.schemas import (
    AGE,
    AGE_RANGE,
    AGE_OR_AGE_RANGE,
    EXTRA_PROPERTIES_SCHEMA,
    ONTOLOGY_CLASS,
)

from . import descriptions


__all__ = [
    "ALLELE_SCHEMA",
    "PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA",
    "PHENOPACKET_UPDATE_SCHEMA",
    "PHENOPACKET_META_DATA_SCHEMA",
    "PHENOPACKET_EVIDENCE_SCHEMA",
    "PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA",
    "PHENOPACKET_GENE_SCHEMA",
    "PHENOPACKET_HTS_FILE_SCHEMA",
    "PHENOPACKET_VARIANT_SCHEMA",
    "PHENOPACKET_BIOSAMPLE_SCHEMA",
    "PHENOPACKET_DISEASE_ONSET_SCHEMA",
    "PHENOPACKET_DISEASE_SCHEMA",
    "PHENOPACKET_SCHEMA",
]


ALLELE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:allele_schema",
    "title": "Allele schema",
    "description": "Variant allele types",
    "type": "object",
    "properties": {
        "id": {"type": "string"},

        "hgvs": {"type": "string"},

        "genome_assembly": {"type": "string"},
        "chr": {"type": "string"},
        "pos": {"type": "integer"},
        "ref": {"type": "string"},
        "alt": {"type": "string"},
        "info": {"type": "string"},

        "seq_id": {"type": "string"},
        "position": {"type": "integer"},
        "deleted_sequence": {"type": "string"},
        "inserted_sequence": {"type": "string"},

        "iscn": {"type": "string"}
    },
    "additionalProperties": False,
    "oneOf": [
        {"required": ["hgvs"]},
        {"required": ["genome_assembly"]},
        {"required": ["seq_id"]},
        {"required": ["iscn"]}
    ],
    "dependencies": {
        "genome_assembly": ["chr", "pos", "ref", "alt", "info"],
        "seq_id": ["position", "deleted_sequence", "inserted_sequence"]
    }
}, descriptions.ALLELE)


PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:external_reference_schema",
    "title": "External reference schema",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "description": {
            "type": "string",
        }
    },
    "required": ["id"]
}, descriptions.EXTERNAL_REFERENCE)


PHENOPACKET_UPDATE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:update_schema",
    "title": "Updates schema",
    "type": "object",
    "properties": {
        "timestamp": {
            "type": "string",
            "format": "date-time"
        },
        "updated_by": {
            "type": "string",
        },
        "comment": {
            "type": "string",
        }
    },
    "additionalProperties": False,
    "required": ["timestamp", "comment"],
}, descriptions.UPDATE)


# noinspection PyProtectedMember
PHENOPACKET_META_DATA_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "created": {
            "type": "string",
            "format": "date-time"
        },
        "created_by": {
            "type": "string",
        },
        "submitted_by": {
            "type": "string",
        },
        "resources": {
            "type": "array",
            "items": RESOURCE_SCHEMA,
        },
        "updates": {
            "type": "array",
            "items": PHENOPACKET_UPDATE_SCHEMA,
        },
        "phenopacket_schema_version": {
            "type": "string",
        },
        "external_references": {
            "type": "array",
            "items": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
}, descriptions.META_DATA)

PHENOPACKET_EVIDENCE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:evidence_schema",
    "title": "Evidence schema",
    "type": "object",
    "properties": {
        "evidence_code": ONTOLOGY_CLASS,
        "reference": PHENOPACKET_EXTERNAL_REFERENCE_SCHEMA
    },
    "additionalProperties": False,
    "required": ["evidence_code"],
}, descriptions.EVIDENCE)

PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "description": {
            "type": "string",
        },
        "type": ONTOLOGY_CLASS,
        "negated": {
            "type": "boolean",
        },
        "severity": ONTOLOGY_CLASS,
        "modifier": {  # TODO: Plural?
            "type": "array",
            "items": ONTOLOGY_CLASS
        },
        "onset": ONTOLOGY_CLASS,
        "evidence": PHENOPACKET_EVIDENCE_SCHEMA,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
}, descriptions.PHENOTYPIC_FEATURE)


# TODO: search
PHENOPACKET_GENE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "alternate_ids": {
            "type": "array",
            "items": {
                "type": "string",
            }
        },
        "symbol": {
            "type": "string",
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "symbol"]
}, descriptions.GENE)


PHENOPACKET_HTS_FILE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "uri": {
            "type": "string"  # TODO: URI pattern
        },
        "description": {
            "type": "string"
        },
        "hts_format": {
            "type": "string",
            "enum": ["SAM", "BAM", "CRAM", "VCF", "BCF", "GVCF", "FASTQ", "UNKNOWN"]
        },
        "genome_assembly": {
            "type": "string"
        },
        "individual_to_sample_identifiers": {
            "type": "object"  # TODO
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    }
}, descriptions.HTS_FILE)


# TODO: search??
PHENOPACKET_VARIANT_SCHEMA = describe_schema({
    "type": "object",  # TODO
    "properties": {
        "allele": ALLELE_SCHEMA,  # TODO
        "zygosity": ONTOLOGY_CLASS,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    }
}, descriptions.VARIANT)

# noinspection PyProtectedMember
PHENOPACKET_BIOSAMPLE_SCHEMA = describe_schema({
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "individual_id": {
            "type": "string",
        },
        "description": {
            "type": "string",
        },
        "sampled_tissue": ONTOLOGY_CLASS,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA,
        },
        "taxonomy": ONTOLOGY_CLASS,
        "individual_age_at_collection": AGE_OR_AGE_RANGE,
        "histological_diagnosis": ONTOLOGY_CLASS,
        "tumor_progression": ONTOLOGY_CLASS,
        "tumor_grade": ONTOLOGY_CLASS,  # TODO: Is this a list?
        "diagnostic_markers": {
            "type": "array",
            "items": ONTOLOGY_CLASS,
        },
        "procedure": {
            "type": "object",
            "properties": {
                "code": ONTOLOGY_CLASS,
                "body_site": ONTOLOGY_CLASS
            },
            "required": ["code"],
        },
        "hts_files": {
            "type": "array",
            "items": PHENOPACKET_HTS_FILE_SCHEMA
        },
        "variants": {
            "type": "array",
            "items": PHENOPACKET_VARIANT_SCHEMA
        },
        "is_control_sample": {
            "type": "boolean"
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "sampled_tissue", "procedure"],
}, descriptions.BIOSAMPLE)


PHENOPACKET_DISEASE_ONSET_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:disease_onset_schema",
    "title": "Onset age",
    "description": "Schema for the age of the onset of the disease.",
    "type": "object",
    "anyOf": [
        AGE,
        AGE_RANGE,
        ONTOLOGY_CLASS
    ]
}

PHENOPACKET_DISEASE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:disease_schema",
    "title": "Disease schema",
    "type": "object",
    "properties": {
        "term": ONTOLOGY_CLASS,
        "onset": PHENOPACKET_DISEASE_ONSET_SCHEMA,
        "disease_stage": {
            "type": "array",
            "items": ONTOLOGY_CLASS,
        },
        "tnm_finding": {
            "type": "array",
            "items": ONTOLOGY_CLASS,
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["term"],
}, descriptions.DISEASE)

# Deduplicate with other phenopacket representations
# noinspection PyProtectedMember
PHENOPACKET_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "$id": "chord_metadata_service:phenopacket_schema",
    "title": "Phenopacket schema",
    "description": "Schema for metadata service datasets",
    "type": "object",
    "properties": {
        "id": {
            "type": "string",
        },
        "subject": INDIVIDUAL_SCHEMA,
        "phenotypic_features": {
            "type": "array",
            "items": PHENOPACKET_PHENOTYPIC_FEATURE_SCHEMA
        },
        "biosamples": {
            "type": "array",
            "items": PHENOPACKET_BIOSAMPLE_SCHEMA
        },
        "genes": {
            "type": "array",
            "items": PHENOPACKET_GENE_SCHEMA
        },
        "variants": {
            "type": "array",
            "items": PHENOPACKET_VARIANT_SCHEMA
        },
        "diseases": {  # TODO: Too sensitive for search?
            "type": "array",
            "items": PHENOPACKET_DISEASE_SCHEMA,
        },  # TODO
        "hts_files": {
            "type": "array",
            "items": PHENOPACKET_HTS_FILE_SCHEMA  # TODO
        },
        "meta_data": PHENOPACKET_META_DATA_SCHEMA,
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "meta_data"],
}, descriptions.PHENOPACKET)
