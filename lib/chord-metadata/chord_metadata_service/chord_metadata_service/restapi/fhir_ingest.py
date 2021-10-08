import uuid
import jsonschema
import logging

from django.core.exceptions import ValidationError
from typing import Dict

from .schemas import FHIR_BUNDLE_SCHEMA
from .fhir_utils import (
    patient_to_individual,
    observation_to_phenotypic_feature,
    condition_to_disease,
    specimen_to_biosample
)
from chord_metadata_service.chord.models import Table
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import (
    Biosample,
    Disease,
    MetaData,
    Phenopacket,
    PhenotypicFeature,
    Procedure,
)


logger = logging.getLogger("fhir_ingest")
logger.setLevel(logging.INFO)


def _parse_reference(ref):
    """ FHIR test data has reference object in a format "ResourceType/uuid" """
    return ref.split('/')[-1]


def check_schema(schema, obj, additional_info=None):
    """ Validates schema and catches errors. """
    try:
        jsonschema.validate(obj, schema)
    except jsonschema.exceptions.ValidationError:
        v = jsonschema.Draft7Validator(schema)
        errors = [e for e in v.iter_errors(obj)]
        error_messages = [
            f"{i} validation error {'.'.join(str(v) for v in error.path)}: {error.message}"
            for i, error in enumerate(errors, 1)
        ]
        raise ValidationError(f"{additional_info + ' ' if additional_info else None}errors: {error_messages}")


def ingest_patients(patients_data, table_id, created_by):
    """ Takes FHIR Bundle containing Patient resources. """
    # check if Patients data follows FHIR Bundle schema
    check_schema(FHIR_BUNDLE_SCHEMA, patients_data, 'patients data')

    phenopacket_ids = {}
    for item in patients_data["entry"]:
        individual_data = patient_to_individual(item["resource"])
        individual, _ = Individual.objects.get_or_create(**individual_data)
        # create metadata for Phenopacket
        meta_data_obj, _ = MetaData.objects.get_or_create(
            created_by=created_by,
            phenopacket_schema_version="1.0.0-RC3",
            external_references=[]
        )
        # create new phenopacket for each individual
        phenopacket_ids[individual.id] = str(uuid.uuid4())
        phenopacket = Phenopacket.objects.create(
            id=phenopacket_ids[individual.id],
            subject=individual,
            meta_data=meta_data_obj,
            table=Table.objects.get(ownership_record_id=table_id)
        )
        logger.info(f'Phenopacket {phenopacket.id} created')

    return phenopacket_ids


def ingest_observations(phenopacket_ids: Dict[str, str], observations_data):
    """ Takes FHIR Bundle containing Observation resources. """
    # check if Observations data follows FHIR Bundle schema
    check_schema(FHIR_BUNDLE_SCHEMA, observations_data, 'observations data')

    for item in observations_data["entry"]:
        phenotypic_feature_data = observation_to_phenotypic_feature(item["resource"])

        # Observation must have a subject
        try:
            item["resource"]["subject"]
        except KeyError:
            raise KeyError(f"Observation {item['resource']['id']} doesn't have a subject.")

        subject = _parse_reference(item["resource"]["subject"]["reference"])
        phenotypic_feature, _ = PhenotypicFeature.objects.get_or_create(
            phenopacket=Phenopacket.objects.get(id=phenopacket_ids[subject]),
            **phenotypic_feature_data
        )

        logger.info(f'PhenotypicFeature {phenotypic_feature.id} created')


def ingest_conditions(phenopacket_ids: Dict[str, str], conditions_data):
    """ Takes FHIR Bundle containing Condition resources. """
    # check if Conditions data follows FHIR Bundle schema
    check_schema(FHIR_BUNDLE_SCHEMA, conditions_data, 'conditions data')

    for item in conditions_data["entry"]:
        disease_data = condition_to_disease(item["resource"])
        disease = Disease.objects.create(**disease_data)

        # Condition must have a subject
        try:
            item["resource"]["subject"]
        except KeyError:
            raise KeyError(f"Condition {item['resource']['id']} doesn't have a subject.")

        subject = _parse_reference(item["resource"]["subject"]["reference"])

        phenopacket = Phenopacket.objects.get(id=phenopacket_ids[subject])
        phenopacket.diseases.add(disease)

        logger.info(f'Disease {disease.id} created')


def ingest_specimens(phenopacket_ids: Dict[str, str], specimens_data):
    """ Takes FHIR Bundle containing Specimen resources. """
    # check if Specimens data follows FHIR Bundle schema
    check_schema(FHIR_BUNDLE_SCHEMA, specimens_data, 'specimens data')

    for item in specimens_data["entry"]:
        biosample_data = specimen_to_biosample(item["resource"])
        procedure, _ = Procedure.objects.get_or_create(**biosample_data["procedure"])

        # Specimen must have a subject
        if not biosample_data.get("individual"):
            raise KeyError(f"Specimen {item['resource']['id']} doesn't have a subject.")

        individual_id = _parse_reference(biosample_data["individual"])
        biosample, _ = Biosample.objects.get_or_create(
            id=biosample_data["id"],
            procedure=procedure,
            individual=Individual.objects.get(id=individual_id),
            sampled_tissue=biosample_data["sampled_tissue"]
        )

        phenopacket = Phenopacket.objects.get(id=phenopacket_ids[individual_id])
        phenopacket.biosamples.add(biosample)

        logger.info(f'Biosample {biosample.id} created')
