def mcode_structure(structure: str):
    return f"http://hl7.org/fhir/us/mcode/StructureDefinition/{structure}"


# Individual
MCODE_PATIENT = mcode_structure("mcode-cancer-patient")
MCODE_COMORBID_CONDITION = mcode_structure("mcode-comorbid-condition")
MCODE_ECOG_PERFORMANCE_STATUS = mcode_structure("mcode-ecog-performance-status")
MCODE_KARNOFSKY = mcode_structure("mcode-karnofsky-performance-status")

# GeneticSpecimen
MCODE_GENETIC_SPECIMEN = mcode_structure("mcode-genetic-specimen")

# GeneticVariant
MCODE_CANCER_GENETIC_VARIANT = mcode_structure("mcode-cancer-genetic-variant")

# GenomicRegionStudied
MCODE_GENOMIC_REGION_STUDIED = mcode_structure("mcode-genomic-region-studied")

# GenomicsReport
MCODE_GENOMICS_REPORT = mcode_structure("mcode-cancer-genomics-report")

# LabsVital
# the following are present in Ballout 1 version but not in 1.0.0 version
MCODE_TUMOR_MARKER = mcode_structure("mcode-tumor-marker")

# CancerCondition
MCODE_PRIMARY_CANCER_CONDITION = mcode_structure("mcode-primary-cancer-condition")
MCODE_SECONDARY_CANCER_CONDITION = mcode_structure("mcode-secondary-cancer-condition")

# TNMStaging
# CLINICAL
MCODE_TNM_CLINICAL_STAGE_GROUP = mcode_structure("mcode-tnm-clinical-stage-group")
MCODE_TNM_CLINICAL_PRIMARY_TUMOR_CATEGORY = mcode_structure("mcode-tnm-clinical-primary-tumor-category")
MCODE_TNM_CLINICAL_REGIONAL_NODES_CATEGORY = mcode_structure("mcode-tnm-clinical-regional-nodes-category")
MCODE_TNM_CLINICAL_DISTANT_METASTASES_CATEGORY = mcode_structure("mcode-tnm-clinical-distant-metastases-category")

# PATHOLOGIC
MCODE_TNM_PATHOLOGIC_STAGE_GROUP = mcode_structure("mcode-tnm-pathological-stage-group")
MCODE_TNM_PATHOLOGIC_PRIMARY_TUMOR_CATEGORY = mcode_structure("mcode-tnm-pathological-primary-tumor-category")
MCODE_TNM_PATHOLOGIC_REGIONAL_NODES_CATEGORY = mcode_structure("mcode-tnm-pathological-regional-nodes-category")
MCODE_TNM_PATHOLOGIC_DISTANT_METASTASES_CATEGORY = mcode_structure("mcode-tnm-pathological-distant-metastases-category")

# CancerRelatedProcedure
# CancerRelatedRadiationProcedure
MCODE_CANCER_RELATED_RADIATION_PROCEDURE = mcode_structure("mcode-cancer-related-radiation-procedure")
# CancerRelatedSurgicalProcedure
MCODE_CANCER_RELATED_SURGICAL_PROCEDURE = mcode_structure("mcode-cancer-related-surgical-procedure")

# MedicationStatement
MCODE_MEDICATION_STATEMENT = mcode_structure("mcode-cancer-related-medication-statement")

# mCodePacket
MCODE_CANCER_DISEASE_STATUS = mcode_structure("mcode-cancer-disease-status")

# Extension definitions
MCODE_LATERALITY = mcode_structure("mcode-laterality")

# CancerCondition histology_morphology_behavior
MCODE_HISTOLOGY_MORPHOLOGY_BEHAVIOR = mcode_structure("mcode-histology-morphology-behavior")

# MedicationStatement
MCODE_TERMINATION_REASON = mcode_structure("mcode-termination-reason")
MCODE_TREATMENT_INTENT = mcode_structure("mcode-treatment-intent")
