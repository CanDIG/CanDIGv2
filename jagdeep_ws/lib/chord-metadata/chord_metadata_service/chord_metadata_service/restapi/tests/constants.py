INVALID_FHIR_BUNDLE_1 = {
    "resourceType": "NotBundle",
    "entry": [
        {
            "test": "required resource is not present"
        }
    ]
}

INVALID_SUBJECT_NOT_PRESENT = {
    "resourceType": "Bundle",
    "entry": [
        {
            "resource": {
                "id": "1c8d2ee3-2a7e-47f9-be16-abe4e9fa306b",
                "resourceType": "Observation",
                "status": "final",
                "code": {
                    "coding": [
                        {
                            "code": "718-7",
                            "display": "Hemoglobin [Mass/volume] in Blood",
                            "system": "http://loinc.org"
                        }
                    ],
                    "text": "Hemoglobin [Mass/volume] in Blood"
                }
            }
        }
    ]
}
