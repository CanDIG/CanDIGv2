SEARCH_SUCCESS = {
    "_shards": {
        "failed": 0,
        "skipped": 0,
        "successful": 1,
        "total": 1
    },
    "hits": {
        "hits": [
            {
                "_id": "Individual|patient:1",
                "_index": "fhir_metadata",
                "_score": 6.334576,
                "_source": {
                    "birthDate": "1994-09-11",
                    "extension": [
                        {
                            "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-karyotypic-sex",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "code": "XX",
                                        "display": "XX",
                                        "system": "http://ga4gh.org/fhir/phenopackets/CodeSystem/karyotypic-sex"
                                    }
                                ]
                            }
                        },
                        {
                            "url": "http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-taxonomy",
                            "valueCodeableConcept": {
                                "coding": [
                                    {
                                        "code": "FAKE_CODE",
                                        "display": "Homo sapiens"
                                    }
                                ]
                            }
                        }
                    ],
                    "gender": "FEMALE",
                    "id": "patient:1",
                    "resourceType": "Patient"
                },
                "_type": "_doc"
            }
        ],
        "max_score": 6.334576,
        "total": {
            "relation": "eq",
            "value": 1
        }
    },
    "timed_out": False,
    "took": 5
}
