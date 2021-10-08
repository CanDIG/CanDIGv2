# schema.org jsonld context https://schema.org/docs/jsonldcontext.json
# schema.org context to dats provided here https://github.com/datatagsuite/context

# context from dataset to schema.org
CONTEXT = [
    {
      "sdo": "https://schema.org/",
      "Dataset": "sdo:Dataset",
      "title": {
        "@id": "sdo:name",
        "@type": "sdo:Text"
      },
      "description": {
        "@id": "sdo:description",
        "@type": "sdo:Text"
      },
      "DatasetDistribution": "sdo:DataDownload",
      "distributions": {
        "@id": "sdo:distribution",
        "@type": "sdo:DataDownload"
      },
      "formats": "sdo:fileFormat",
      "unit": "sdo:unitCode",
      "access": {
        "@id": "sdo:accessMode",
        "@type": "sdo:EntryPoint"
      },
      "landing_page": {
        "@id": "sdo:url",
        "@type": "sdo:URL"
      },
      "size": {
        "@id": "sdo:contentSize",
        "@type": "sdo:Text"
      },
      "primary_publications": "sdo:citation",
      "Publication": "sdo:ScholarlyArticle",
      "citations": "sdo:citation",
      "produced_by": "sdo:producer",
      "creators": {
        "@id": "sdo:creator",
        "@type": "sdo:Thing"
      },
      "licenses": "sdo:license",
      "is_about": "sdo:about",
      "has_part": {
        "@id": "sdo:hasPart",
        "@type": "sdo:Dataset"
      },
      "acknowledges": "sdo:funder",
      "keywords": "sdo:keywords",
      "dates": "sdo:temporalCoverage",
      "stored_in": {
        "@id": "sdo:includedInDataCatalog",
        "@type": "sdo:DataCatalog"
      },
      "version": "sdo:version",
      "identifier": {
        "@id": "sdo:identifier",
        "@type": "sdo:Text"
      },
      "DataType": "sdo:Thing",
      "information": {
        "@id": "sdo:Property"
      },
      "Annotation": "sdo:Thing",
      "TaxonomicInformation": "sdo:Thing",
      "Identifier": "sdo:Thing",
      "identifier_source": {
        "@id": "sdo:Property",
        "@type": "sdo:Text"
      },
      "AlternateIdentifier": "sdo:Thing",
      "RelatedIdentifier": "sdo:Thing",
      "CategoryValuesPair": "sdo:PropertyValue",
      "category": {
        "@id": "sdo:value",
        "@type": "sdo:Text"
      },
      "category_iri": {
        "@id": "sdo:url",
        "@type": "sdo:URL"
      },
      "Organization": "sdo:Organization",
      "Person": "sdo:Person",
      "full_name": "sdo:name",
      "first_name": "sdo:givenName",
      "last_name": "sdo:familyName",
      "affiliation": "sdo:affiliation",
      "value": {
        "@id": "sdo:value",
        "@type": "sdo:DataType"
      },
      "types": "sdo:contentType",
      "value_iri": {
        "@id": "sdo:url",
        "@type": "sdo:URL"
      },
      "name": {
        "@id": "sdo:name",
        "@type": "sdo:Text"
      },
      "Date": "sdo:DateTime",
      "date": {
        "@id": "sdo:Property"
      },
      "type": {
        "@id": "sdo:Property"
      },
      "Disease": "sdo:MedicalCondition",
      "MolecularEntity": "sdo:Thing",
      "characteristics": {
        "@id": "sdo:additionalProperty",
        "@type": "sdo:Thing"
      },
      "disease_status": "sdo:status",
      "Material": "sdo:Thing",
      "derives_from": "sdo:relatedTo",
      "License": "sdo:CreativeWork",
      "DataRepository": "sdo:DataCatalog",
      "DataAcquisition": "sdo:CreateAction",
      "uses": "sdo:relatedTo",
      "Software": "sdo:SoftwareApplication",
      "values": "sdo:value",
      "extra_properties": "sdo:additionalProperty",
      "Place": "sdo:Place",
      "Dimension": "sdo:Thing",
      "dimensions": "sdo:additionalProperty"
    }
  ]


# context types according to dats schema
CONTEXT_TYPES = {
    'dataset': {
        'schema': 'https://w3id.org/dats/schema/dataset_schema.json',
        'type': 'Dataset'
    },
    'dates': {
        'schema': 'https://w3id.org/dats/schema/date_info_schema.json',
        'type': 'Date'
    },
    'licenses': {
        'schema': 'https://w3id.org/dats/schema/license_schema.json',
        'type': 'License'
    },
    'distributions': {
        'schema': 'https://w3id.org/dats/schema/dataset_distribution_schema.json',
        'type': 'DatasetDistribution'
    },
    'dimensions': {
        'schema': 'https://w3id.org/dats/schema/dimension_schema.json',
        'type': 'Dimension'
    },
    'types': {
        'schema': 'https://w3id.org/dats/schema/data_type_schema.json',
        'type': 'DataType'
    },
    'stored_in': {
        'schema': 'https://w3id.org/dats/schema/data_repository_schema.json',
        'type': 'DataRepository'
    },
    'spatial_coverage': {
        'schema': 'https://w3id.org/dats/schema/place_schema.json',
        'type': 'Place'
    },
    'organization': {
        'schema': 'https://w3id.org/dats/schema/organization_schema.json',
        'type': 'Organization'
    },
    'person': {
        'schema': 'https://w3id.org/dats/schema/person_schema.json',
        'type': 'Person'
    },
    'identifier': {
        'schema': 'https://w3id.org/dats/schema/identifier_info_schema.json',
        'type': 'Identifier'
    },
    'primary_publications': {
        'schema': 'https://w3id.org/dats/schema/publication_schema.json',
        'type': 'Publication'
    },
    'alternate_identifiers': {
        'schema': 'https://w3id.org/dats/schema/alternate_identifier_info_schema.json',
        'type': 'AlternateIdentifier'
    },
    'related_identifiers': {
        'schema': 'https://w3id.org/dats/schema/related_identifier_info_schema.json',
        'type': 'RelatedIdentifier'
    },
    'annotation': {
        'schema': 'https://w3id.org/dats/schema/annotation_schema.json',
        'type': 'Annotation'
    },
    'extra_properties': {
        'schema': 'https://w3id.org/dats/schema/category_values_pair_schema.json',
        'type': 'CategoryValuesPair'
    }
}
