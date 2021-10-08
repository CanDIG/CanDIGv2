VALID_INDIVIDUAL = {
    "id": "patient:1",
    "taxonomy": {
        "id": "NCBITaxon:9606",
        "label": "human"
    },
    "date_of_birth": "1960-01-01",
    "age": {
        "age": {
            "start": {
                "age": "P45Y"
            },
            "end": {
                "age": "P49Y"
            }
        }
    },
    "sex": "FEMALE",
    "active": True
}


def valid_genetic_report():
    return {
        "id": "genomics_report:01",
        "code": {
            "id": "GTR000567625.2",
            "label": "PREVENTEST",
        },
        "issued": "2018-11-13T20:20:39+00:00",
        "performing_organization_name": "Test organization"
    }


def valid_labs_vital(individual):
    return {
        "id": "labs_vital:01",
        "tumor_marker_code": {
            "id": "50610-5",
            "label": "Alpha-1-Fetoprotein"
        },
        "individual": individual,
    }


def valid_cancer_condition():
    return {
        "id": "cancer_condition:01",
        "condition_type": "primary",
        "body_site": [
            {
                "id": "442083009",
                "label": "Anatomical or acquired body structure (body structure)"
            }
        ],
        "clinical_status": {
            "id": "active",
            "label": "Active"
        },
        "code": {
            "id": "404087009",
            "label": "Carcinosarcoma of skin (disorder)"
        },
        "date_of_diagnosis": "2018-11-13T20:20:39+00:00",
        "histology_morphology_behavior": {
            "id": "372147008",
            "label": "Kaposi's sarcoma - category (morphologic abnormality)"
        }
    }


def invalid_tnm_staging(cancer_condition):
    return {
        "id": "tnm_staging:01",
        "tnm_type": "clinical",
        "stage_group": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test",
                        "system": "https://example.com/path/resource.txt#fragment"
                    }
                ]
            }
        },
        "primary_tumor_category": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test",
                        "system": "https://example.com/path/resource.txt#fragment"
                    }
                ]
            }
        },
        "regional_nodes_category": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test",
                        "system": "https://example.com/path/resource.txt#fragment"
                    }
                ]
            }
        },
        "distant_metastases_category": {
            "data_value": {
                "coding": [
                    {
                        "code": "123",
                        "display": "test"
                    }
                ]
            }
        },
        "cancer_condition": cancer_condition,
    }


def valid_cancer_related_procedure():
    return {
        "id": "cancer_related_procedure:01",
        "procedure_type": "radiation",
        "code": {
            "id": "33356009",
            "label": "Betatron teleradiotherapy (procedure)"
        },
        "body_site": [
            {
                "id": "74805009",
                "label": "Mammary gland sinus"
            }
        ],
        "treatment_intent": {
            "id": "373808002",
            "label": "Curative - procedure intent"
        }
    }


def valid_medication_statement():
    return {
        "id": "medication_statement:01",
        "medication_code": {
            "id": "92052",
            "label": "Verapamil Oral Tablet [Calan]"
        },
        "termination_reason": [
            {
                "id": "182992009",
                "label": "Treatment completed"
            }
        ],
        "treatment_intent": {
            "id": "373808002",
            "label": "Curative - procedure intent"
        },
        "start_date": "2018-11-13T20:20:39+00:00",
        "end_date": "2019-04-13T20:20:39+00:00"
    }
