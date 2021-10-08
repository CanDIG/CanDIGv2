from . import mcode_profiles as mp

MCODE_PROFILES_MAPPING = {
    "patient": {
        "profile": mp.MCODE_PATIENT,
        "properties_profile": {
            "comorbid_condition": mp.MCODE_COMORBID_CONDITION,
            "ecog_performance_status": mp.MCODE_ECOG_PERFORMANCE_STATUS,
            "karnofsky": mp.MCODE_KARNOFSKY
        }
    },
    "genetic_specimen": {
        "profile": mp.MCODE_GENETIC_SPECIMEN,
        "properties_profile": {
            "laterality": mp.MCODE_LATERALITY
        }
    },
    "cancer_genetic_variant": {
        "profile": mp.MCODE_CANCER_GENETIC_VARIANT
    },
    "genomic_region_studied": {
        "profile": mp.MCODE_GENOMIC_REGION_STUDIED
    },
    "genomics_report": {
        "profile": mp.MCODE_GENOMICS_REPORT
    },
    "labs_vital": {
        "profile": mp.MCODE_TUMOR_MARKER
    },
    "cancer_condition": {
        "profile": {
            "primary": mp.MCODE_PRIMARY_CANCER_CONDITION,
            "secondary": mp.MCODE_SECONDARY_CANCER_CONDITION
        },
        "properties_profile": {
            "histology_morphology_behavior": mp.MCODE_HISTOLOGY_MORPHOLOGY_BEHAVIOR
        }
    },
    "tnm_staging": {
        "properties_profile": {
            "stage_group": {
                "clinical": mp.MCODE_TNM_CLINICAL_STAGE_GROUP,
                "pathologic": mp.MCODE_TNM_PATHOLOGIC_STAGE_GROUP
            },
            "primary_tumor_category": {
                "clinical": mp.MCODE_TNM_CLINICAL_PRIMARY_TUMOR_CATEGORY,
                "pathologic": mp.MCODE_TNM_PATHOLOGIC_PRIMARY_TUMOR_CATEGORY
            },
            "regional_nodes_category": {
                "clinical": mp.MCODE_TNM_CLINICAL_REGIONAL_NODES_CATEGORY,
                "pathologic": mp.MCODE_TNM_PATHOLOGIC_REGIONAL_NODES_CATEGORY
            },
            "distant_metastases_category": {
                "clinical": mp.MCODE_TNM_CLINICAL_DISTANT_METASTASES_CATEGORY,
                "pathologic": mp.MCODE_TNM_PATHOLOGIC_DISTANT_METASTASES_CATEGORY
            }
        }
    },
    "cancer_related_procedure": {
        "profile": {
            "radiation": mp.MCODE_CANCER_RELATED_RADIATION_PROCEDURE,
            "surgical": mp.MCODE_CANCER_RELATED_SURGICAL_PROCEDURE
        }
    },
    "medication_statement": {
        "profile": mp.MCODE_MEDICATION_STATEMENT,
        "properties_profile": {
            "termination_reason": mp.MCODE_TERMINATION_REASON,
            "treatment_intent": mp.MCODE_TREATMENT_INTENT
        }
    },
    "mcodepacket": {
        "properties_profile": {
            "cancer_disease_status": mp.MCODE_CANCER_DISEASE_STATUS
        }
    }
}
