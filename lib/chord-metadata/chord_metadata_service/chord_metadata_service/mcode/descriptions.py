# Most parts of this text are taken from the mCODE:Minimal Common Oncology Data Elements Data Dictionary.
# The mCODE is made available under the Creative Commons 0 "No Rights Reserved" license
# https://creativecommons.org/share-your-work/public-domain/cc0/

# Portions of this text copyright (c) 2019-2020 the Canadian Centre for Computational Genomics; licensed under the
# GNU Lesser General Public License version 3.

from chord_metadata_service.restapi.description_utils import EXTRA_PROPERTIES

GENETIC_SPECIMEN = {
    "description": "Class to describe a biosample used for genomics testing or analysis.",
    "properties": {
        "id": "An arbitrary identifier for the genetic specimen.",
        "specimen_type": "The kind of material that forms the specimen.",
        "collection_body": "The anatomical collection site.",
        "laterality": "Body side of the collection site, if needed to distinguish from a similar "
                      "location on the other side of the body.",
        **EXTRA_PROPERTIES
    }
}

CANCER_GENETIC_VARIANT = {
    "description": "Class to record an alteration in DNA.",
    "properties": {
        "id": "An arbitrary identifier for the cancer genetic variant.",
        "data_value": "The overall result of the genetic test; specifically, whether a variant is present, "
                      "absent, no call, or indeterminant.",
        "method": "The method used to perform the genetic test.",
        "amino_acid_change": "The symbolic representation of an amino acid variant reported using "
                             "HGVS nomenclature (pHGVS).",
        "amino_acid_change_type": "The type of change related to the amino acid variant.",
        "cytogenetic_location": "The cytogenetic (chromosome) location.",
        "cytogenetic_nomenclature": "The cytogenetic (chromosome) location, represented using the International "
                                    "System for Human Cytogenetic Nomenclature (ISCN).",
        "gene_studied": "A gene targeted for mutation analysis, identified in "
                        "HUGO Gene Nomenclature Committee (HGNC) notation.",
        "genomic_dna_change": "The symbolic representation of a genetic structural variant reported "
                              "using HGVS nomenclature (gHGVS).",
        "genomic_source_class": "The genomic class of the specimen being analyzed, for example, germline for "
                                "inherited genome, somatic for cancer genome, and prenatal for fetal genome.",
        "variation_code": "The variation ID assigned by ClinVar.",
        **EXTRA_PROPERTIES
    }
}

GENOMIC_REGION_STUDIED = {
    "description": "Class to describe the area of the genome region referenced in testing for variants.",
    "properties": {
        "id": "An arbitrary identifier for the genomic region studied.",
        "dna_ranges_examined": "The range(s) of the DNA sequence examined.",
        "dna_region_description": "The description for the DNA region studied in the genomics report.",
        "gene_mutation": "The gene mutations tested for in blood or tissue by molecular genetics methods.",
        "gene_studied": "The ID for the gene studied.",
        "genomic_reference_sequence_id": "Range(s) of DNA sequence examined.",
        "genomic_region_coordinate_system": "The method of counting along the genome.",
        **EXTRA_PROPERTIES
    }
}

GENOMICS_REPORT = {
    "description": "Genetic Analysis Summary.",
    "properties": {
        "id": "An arbitrary identifier for the genetics report.",
        "code": "An ontology or controlled vocabulary term to identify the laboratory test. "
                "Accepted value sets: LOINC, GTR.",
        "performing_organization_name": "The name of the organization  producing the genomics report.",
        "issued": "The date/time this report was issued.",
        "genetic_specimen": "List of related genetic specimens.",
        "genetic_variant": "Related genetic variant.",
        "genomic_region_studied": "Related genomic region studied.",
        **EXTRA_PROPERTIES
    }
}

LABS_VITAL = {
    "description": "A description of tests performed on patient.",
    "properties": {
        "id": "An arbitrary identifier for the labs/vital tests.",
        "individual": "The individual who is the subject of the tests.",
        "tumor_marker_code": "A code identifying the type of tumor marker test.",
        "tumor_marker_data_value": "The result of a tumor marker test.",
        **EXTRA_PROPERTIES
    }
}

CANCER_CONDITION = {
    "description": "A description of history of primary or secondary cancer conditions.",
    "properties": {
        "id": "An arbitrary identifier for the cancer condition.",
        "condition_type": "Cancer condition type: primary or secondary.",
        "body_site": "Code for the body location, optionally pre-coordinating laterality or direction. "
                     "Accepted ontologies: SNOMED CT, ICD-O-3 and others.",
        "laterality": "Body side of the body location, if needed to distinguish from a similar location "
                      "on the other side of the body.",
        "clinical_status": "A flag indicating whether the condition is active or inactive, recurring, in remission, "
                           "or resolved (as of the last update of the Condition). Accepted code system: "
                           "http://terminology.hl7.org/CodeSystem/condition-clinical",
        "code": "A code describing the type of primary or secondary malignant neoplastic disease.",
        "date_of_diagnosis": "The date the disease was first clinically recognized with sufficient certainty, "
                             "regardless of whether it was fully characterized at that time.",
        "histology_morphology_behavior": "A description of the morphologic and behavioral characteristics of "
                                         "the cancer. Accepted ontologies: SNOMED CT, ICD-O-3 and others.",
        "verification_status": "A flag indicating whether the condition is unconfirmed, provisional, differential, "
                               "confirmed, refuted, or entered-in-error.",
        **EXTRA_PROPERTIES
    }
}

TNM_STAGING = {
    "description": "A description of the cancer spread in a patient's body.",
    "properties": {
        "id": "An arbitrary identifier for the TNM staging.",
        "tnm_type": "TNM type: clinical or pathological.",
        "stage_group": "The extent of the cancer in the body, according to the TNM classification system."
                       "Accepted ontologies: SNOMED CT, AJCC and others.",
        "primary_tumor_category": "Category of the primary tumor, based on its size and extent. "
                                  "Accepted ontologies: SNOMED CT, AJCC and others.",
        "regional_nodes_category": "Category of the presence or absence of metastases in regional lymph nodes. "
                                   "Accepted ontologies: SNOMED CT, AJCC and others.",
        "distant_metastases_category": "Category describing the presence or absence of metastases in remote "
                                       "anatomical locations. Accepted ontologies: SNOMED CT, AJCC and others.",
        "cancer_condition": "Cancer condition.",
        **EXTRA_PROPERTIES
    }
}

CANCER_RELATED_PROCEDURE = {
    "description": "Description of radiological treatment or surgical action addressing a cancer condition.",
    "properties": {
        "id": "An arbitrary identifier for the procedure.",
        "procedure_type": "Type of cancer related procedure: radiation or surgical.",
        "code": "Code for the procedure performed.",
        "body_site": "The body location(s) where the procedure was performed.",
        "laterality": "Body side of the body location, if needed to distinguish from a similar location "
                      "on the other side of the body.",
        "treatment_intent": "The purpose of a treatment.",
        "reason_code": "The explanation or justification for why the surgical procedure was performed.",
        "reason_reference": "Reference to a primary or secondary cancer condition.",
        **EXTRA_PROPERTIES
    }
}

MEDICATION_STATEMENT = {
    "description": "Description of medication use.",
    "properties": {
        "id": "An arbitrary identifier for the medication statement.",
        "medication_code": "A code for medication. Accepted code systems: Medication Clinical Drug (RxNorm) and other.",
        "termination_reason": "A code explaining unplanned or premature termination of a course of medication. "
                              "Accepted ontologies: SNOMED CT.",
        "treatment_intent": "The purpose of a treatment. Accepted ontologies: SNOMED CT.",
        "start_date": "The start date/time of the medication.",
        "end_date": "The end date/time of the medication.",
        **EXTRA_PROPERTIES
    }
}

MCODEPACKET = {
    "description": "Collection of cancer related metadata.",
    "properties": {
        "id": "An arbitrary identifier for the mcodepacket.",
        "subject": "An individual who is a subject of mcodepacket.",
        "genomics_report": "A genomics report associated with an Individual.",
        "cancer_condition": "An Individual's cancer condition.",
        "cancer_related_procedures": "A radiological or surgical procedures addressing a cancer condition.",
        "medication_statement": "Medication treatment addressed to an Individual.",
        "date_of_death": "An indication that the patient is no longer living, given by a date of death or boolean.",
        "cancer_disease_status": "A clinician's qualitative judgment on the current trend of the cancer, e.g., "
                                 "whether it is stable, worsening (progressing), or improving (responding).",
        **EXTRA_PROPERTIES
    }
}
