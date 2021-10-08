# All fixed values provided by Phenopackets on FHIR Mapping guide
# Mappings from http://build.fhir.org/ig/HL7/genomics-reporting/index.html

HL7_GENOMICS_MAPPING = {
    "gene": {
        "url": "http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/region-studied",
        "gene_studied_code": {
            "system": "https://loinc.org",
            "id": "48018-6",
            "label": "Gene studied [ID]"
        },
        "gene_studied_value": {
            "system": "https://www.genenames.org/"
        }
    },
    "variant": {
        "url": "http://hl7.org/fhir/uv/genomics-reporting/StructureDefinition/variant",
        "variant_length_code": {
            "system": "https://loinc.org",
            "id": "81300-6",
            "label": "Structural variant [Length]"
        }
    }
}
