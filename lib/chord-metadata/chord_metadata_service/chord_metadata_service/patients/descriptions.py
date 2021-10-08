from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES, ontology_class


# TODO: This is part of another app
INDIVIDUAL = {
    "description": "A subject of a phenopacket, representing either a human (typically) or another organism.",
    "properties": {
        # Phenopackets / shared
        "id": "A unique researcher-specified identifier for an individual.",
        "alternate_ids": {
            "description": "A list of alternative identifiers for an individual.",
            "items": "One of possibly many alternative identifiers for an individual."
        },
        "date_of_birth": "A timestamp representing an individual's date of birth; either exactly or imprecisely.",
        "age": "The age or age range of the individual.",
        "sex": "The phenotypic sex of an individual, as would be determined by a midwife or physician at birth.",
        "karyotypic_sex": "The karyotypic sex of an individual.",
        "taxonomy": ontology_class("specified when more than one organism may be studied. It is advised that codes"
                                   "from the NCBI Taxonomy resource are used, e.g. NCBITaxon:9606 for humans"),

        # FHIR-specific
        "active": {
            "description": "Whether a patient's record is in active use.",
            "help": "FHIR-specific property."
        },
        "deceased": {
            "description": "Whether a patient is deceased.",
            "help": "FHIR-specific property."
        },

        # mCode-specific
        "race": {
            "description": "A code for a person's race (mCode).",
            "help": "mCode-specific property."
        },
        "ethnicity": {
            "description": "A code for a person's ethnicity (mCode).",
            "help": "mCode-specific property."
        },
        "comorbid_condition": {
            "description": "One or more conditions that occur with primary condition.",
            "help": "mCode-specific property."
        },
        "ecog_performance_status": {
            "description": "Value representing the Eastern Cooperative Oncology Group performance status.",
            "help": "mCode-specific property."
        },
        "karnofsky": {
            "description": "Value representing the Karnofsky Performance status.",
            "help": "mCode-specific property."
        },
        **EXTRA_PROPERTIES
    }
}
