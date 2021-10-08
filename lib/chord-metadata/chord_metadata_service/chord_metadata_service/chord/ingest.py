import json
import os
import uuid

from dateutil.parser import isoparse
from typing import Callable

from chord_metadata_service.chord.data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_PHENOPACKET, DATA_TYPE_MCODEPACKET
from chord_metadata_service.chord.models import Table, TableOwnership
from chord_metadata_service.experiments import models as em
from chord_metadata_service.phenopackets import models as pm
from chord_metadata_service.resources import models as rm, utils as ru
from chord_metadata_service.restapi.fhir_ingest import (
    ingest_patients,
    ingest_observations,
    ingest_conditions,
    ingest_specimens
)
from chord_metadata_service.mcode.parse_fhir_mcode import parse_bundle
from chord_metadata_service.mcode.mcode_ingest import ingest_mcodepacket


__all__ = [
    "METADATA_WORKFLOWS",
    "WORKFLOWS_PATH",
    "IngestError",
    "ingest_resource",
    "ingest_experiments_workflow",
    "ingest_phenopacket_workflow",
    "WORKFLOW_INGEST_FUNCTION_MAP",
]

WORKFLOW_PHENOPACKETS_JSON = "phenopackets_json"
WORKFLOW_EXPERIMENTS_JSON = "experiments_json"
WORKFLOW_FHIR_JSON = "fhir_json"
WORKFLOW_MCODE_FHIR_JSON = "mcode_fhir_json"

METADATA_WORKFLOWS = {
    "ingestion": {
        WORKFLOW_PHENOPACKETS_JSON: {
            "name": "Bento Phenopackets-Compatible JSON",
            "description": "This ingestion workflow will validate and import a Phenopackets schema-compatible "
                           "JSON document.",
            "data_type": DATA_TYPE_PHENOPACKET,
            "file": "phenopackets_json.wdl",
            "inputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"]
                }
            ],
            "outputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "value": "{json_document}"
                }
            ]
        },
        WORKFLOW_EXPERIMENTS_JSON: {
            "name": "Bento Experiments JSON",
            "description": "This ingestion workflow will validate and import a Bento Experiments schema-compatible "
                           "JSON document.",
            "data_type": DATA_TYPE_EXPERIMENT,
            "file": "experiments_json.wdl",
            "inputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"]
                }
            ],
            "outputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "value": "{json_document}"
                }
            ]
        },
        WORKFLOW_FHIR_JSON: {
            "name": "FHIR Resources JSON",
            "description": "This ingestion workflow will validate and import a FHIR schema-compatible "
                           "JSON document, and convert it to the Bento metadata service's internal Phenopackets-based "
                           "data model.",
            "data_type": DATA_TYPE_PHENOPACKET,
            "file": "fhir_json.wdl",
            "inputs": [
                {
                    "id": "patients",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"]
                },
                {
                    "id": "observations",
                    "type": "file",
                    "required": False,
                    "extensions": [".json"]
                },
                {
                    "id": "conditions",
                    "type": "file",
                    "required": False,
                    "extensions": [".json"]
                },
                {
                    "id": "specimens",
                    "type": "file",
                    "required": False,
                    "extensions": [".json"]
                },
                {
                    "id": "created_by",
                    "required": False,
                    "type": "string"
                },

            ],
            "outputs": [
                {
                    "id": "patients",
                    "type": "file",
                    "value": "{patients}"
                },
                {
                    "id": "observations",
                    "type": "file",
                    "value": "{observations}"
                },
                {
                    "id": "conditions",
                    "type": "file",
                    "value": "{conditions}"
                },
                {
                    "id": "specimens",
                    "type": "file",
                    "value": "{specimens}"
                },
                {
                    "id": "created_by",
                    "type": "string",
                    "value": "{created_by}"
                },

            ]
        },
        WORKFLOW_MCODE_FHIR_JSON: {
            "name": "MCODE FHIR Resources JSON",
            "description": "This ingestion workflow will validate and import a mCODE FHIR 4.0. schema-compatible "
                           "JSON document, and convert it to the Bento metadata service's internal mCODE-based "
                           "data model.",
            "data_type": DATA_TYPE_MCODEPACKET,
            "file": "mcode_fhir_json.wdl",
            "inputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "required": True,
                    "extensions": [".json"]
                }
            ],
            "outputs": [
                {
                    "id": "json_document",
                    "type": "file",
                    "value": "{json_document}"
                }
            ]
        }
    },
    "analysis": {}
}

WORKFLOWS_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), "workflows")


class IngestError(Exception):
    pass


def create_phenotypic_feature(pf):
    pf_obj = pm.PhenotypicFeature(
        description=pf.get("description", ""),
        pftype=pf["type"],
        negated=pf.get("negated", False),
        severity=pf.get("severity"),
        modifier=pf.get("modifier", []),  # TODO: Validate ontology term in schema...
        onset=pf.get("onset"),
        evidence=pf.get("evidence"),  # TODO: Separate class?
        extra_properties=pf.get("extra_properties", {})
    )

    pf_obj.save()
    return pf_obj


def _query_and_check_nulls(obj: dict, key: str, transform: Callable = lambda x: x):
    value = obj.get(key)
    return {f"{key}__isnull": True} if value is None else {key: transform(value)}


def ingest_resource(resource: dict) -> rm.Resource:
    namespace_prefix = resource["namespace_prefix"].strip()
    version = resource.get("version", "").strip()
    assigned_resource_id = ru.make_resource_id(namespace_prefix, version)

    rs_obj, _ = rm.Resource.objects.get_or_create(
        # If this doesn't match assigned_resource_id, it'll throw anyway
        id=resource.get("id", assigned_resource_id),
        name=resource["name"],
        namespace_prefix=namespace_prefix,
        url=resource["url"],
        version=version,
        iri_prefix=resource["iri_prefix"],
        extra_properties=resource.get("extra_properties", {})
        # TODO extra_properties
    )

    return rs_obj


def ingest_experiment(experiment_data, table_id) -> em.Experiment:
    """Ingests a single experiment."""

    new_experiment_id = experiment_data.get("id", str(uuid.uuid4()))

    reference_registry_id = experiment_data.get("reference_registry_id")
    qc_flags = experiment_data.get("qc_flags", [])
    experiment_type = experiment_data["experiment_type"]
    experiment_ontology = experiment_data.get("experiment_ontology", [])
    molecule_ontology = experiment_data.get("molecule_ontology", [])
    molecule = experiment_data.get("molecule")
    library_strategy = experiment_data["library_strategy"]
    other_fields = experiment_data.get("other_fields", {})
    biosample = experiment_data.get("biosample")

    if biosample is not None:
        biosample = pm.Biosample.objects.get(id=biosample)  # TODO: Handle error nicer

    new_experiment = em.Experiment.objects.create(
        id=new_experiment_id,
        reference_registry_id=reference_registry_id,
        qc_flags=qc_flags,
        experiment_type=experiment_type,
        experiment_ontology=experiment_ontology,
        molecule_ontology=molecule_ontology,
        molecule=molecule,
        library_strategy=library_strategy,
        other_fields=other_fields,
        biosample=biosample,
        table=Table.objects.get(ownership_record_id=table_id, data_type=DATA_TYPE_EXPERIMENT)
    )

    return new_experiment


def ingest_phenopacket(phenopacket_data, table_id) -> pm.Phenopacket:
    """Ingests a single phenopacket."""

    new_phenopacket_id = phenopacket_data.get("id", str(uuid.uuid4()))

    subject = phenopacket_data.get("subject")
    phenotypic_features = phenopacket_data.get("phenotypic_features", [])
    biosamples = phenopacket_data.get("biosamples", [])
    genes = phenopacket_data.get("genes", [])
    diseases = phenopacket_data.get("diseases", [])
    hts_files = phenopacket_data.get("hts_files", [])
    meta_data = phenopacket_data["meta_data"]

    if subject:
        # Be a bit flexible with the subject date_of_birth field for Signature; convert blank strings to None.
        subject["date_of_birth"] = subject.get("date_of_birth") or None
        subject_query = _query_and_check_nulls(subject, "date_of_birth", transform=isoparse)
        for k in ("alternate_ids", "age", "sex", "karyotypic_sex", "taxonomy"):
            subject_query.update(_query_and_check_nulls(subject, k))
        subject, _ = pm.Individual.objects.get_or_create(id=subject["id"],
                                                         race=subject.get("race", ""),
                                                         ethnicity=subject.get("ethnicity", ""),
                                                         extra_properties=subject.get("extra_properties", {}),
                                                         **subject_query)

    phenotypic_features_db = [create_phenotypic_feature(pf) for pf in phenotypic_features]

    biosamples_db = []
    for bs in biosamples:
        # TODO: This should probably be a JSON field, or compound key with code/body_site
        procedure, _ = pm.Procedure.objects.get_or_create(**bs["procedure"])

        bs_query = _query_and_check_nulls(bs, "individual_id", lambda i: pm.Individual.objects.get(id=i))
        for k in ("sampled_tissue", "taxonomy", "individual_age_at_collection", "histological_diagnosis",
                  "tumor_progression", "tumor_grade"):
            bs_query.update(_query_and_check_nulls(bs, k))

        bs_obj, bs_created = pm.Biosample.objects.get_or_create(
            id=bs["id"],
            description=bs.get("description", ""),
            procedure=procedure,
            is_control_sample=bs.get("is_control_sample", False),
            diagnostic_markers=bs.get("diagnostic_markers", []),
            extra_properties=bs.get("extra_properties", {}),
            **bs_query
        )

        variants_db = []
        if "variants" in bs:
            for variant in bs["variants"]:
                variant_obj, _ = pm.Variant.objects.get_or_create(
                    allele_type=variant["allele_type"],
                    allele=variant["allele"],
                    zygosity=variant.get("zygosity", {}),
                    extra_properties=variant.get("extra_properties", {})
                )
                variants_db.append(variant_obj)

        if bs_created:
            bs_pfs = [create_phenotypic_feature(pf) for pf in bs.get("phenotypic_features", [])]
            bs_obj.phenotypic_features.set(bs_pfs)

            if variants_db:
                bs_obj.variants.set(variants_db)

        # TODO: Update phenotypic features otherwise?

        biosamples_db.append(bs_obj)

    # TODO: May want to augment alternate_ids
    genes_db = []
    for g in genes:
        # TODO: Validate CURIE
        # TODO: Rename alternate_id
        g_obj, _ = pm.Gene.objects.get_or_create(
            id=g["id"],
            alternate_ids=g.get("alternate_ids", []),
            symbol=g["symbol"],
            extra_properties=g.get("extra_properties", {})
        )
        genes_db.append(g_obj)

    diseases_db = []
    for disease in diseases:
        # TODO: Primary key, should this be a model?
        d_obj, _ = pm.Disease.objects.get_or_create(
            term=disease["term"],
            disease_stage=disease.get("disease_stage", []),
            tnm_finding=disease.get("tnm_finding", []),
            extra_properties=disease.get("extra_properties", {}),
            **_query_and_check_nulls(disease, "onset")
        )
        diseases_db.append(d_obj.id)

    hts_files_db = []
    for htsfile in hts_files:
        htsf_obj, _ = pm.HtsFile.objects.get_or_create(
            uri=htsfile["uri"],
            description=htsfile.get("description", None),
            hts_format=htsfile["hts_format"],
            genome_assembly=htsfile["genome_assembly"],
            individual_to_sample_identifiers=htsfile.get("individual_to_sample_identifiers", None),
            extra_properties=htsfile.get("extra_properties", {})
        )
        hts_files_db.append(htsf_obj)

    resources_db = [ingest_resource(rs) for rs in meta_data.get("resources", [])]

    meta_data_obj = pm.MetaData(
        created_by=meta_data["created_by"],
        submitted_by=meta_data.get("submitted_by"),
        phenopacket_schema_version="1.0.0-RC3",
        external_references=meta_data.get("external_references", []),
        extra_properties=meta_data.get("extra_properties", {})
    )
    meta_data_obj.save()

    meta_data_obj.resources.set(resources_db)

    new_phenopacket = pm.Phenopacket(
        id=new_phenopacket_id,
        subject=subject,
        meta_data=meta_data_obj,
        table=Table.objects.get(ownership_record_id=table_id, data_type=DATA_TYPE_PHENOPACKET)
    )

    new_phenopacket.save()

    new_phenopacket.phenotypic_features.set(phenotypic_features_db)
    new_phenopacket.biosamples.set(biosamples_db)
    new_phenopacket.genes.set(genes_db)
    new_phenopacket.diseases.set(diseases_db)
    new_phenopacket.hts_files.set(hts_files_db)

    return new_phenopacket


def _map_if_list(fn, data, *args):
    # TODO: Any sequence?
    return [fn(d, *args) for d in data] if isinstance(data, list) else fn(data, *args)


def _get_output_or_raise(workflow_outputs, key):
    if key not in workflow_outputs:
        raise IngestError(f"Missing workflow output: {key}")

    return workflow_outputs[key]


def ingest_experiments_workflow(workflow_outputs, table_id):
    with open(_get_output_or_raise(workflow_outputs, "json_document"), "r") as jf:
        json_data = json.load(jf)

        dataset = TableOwnership.objects.get(table_id=table_id).dataset

        for rs in json_data.get("resources", []):
            dataset.additional_resources.add(ingest_resource(rs))

        return [ingest_experiment(exp, table_id) for exp in json_data.get("experiments", [])]


def ingest_phenopacket_workflow(workflow_outputs, table_id):
    with open(_get_output_or_raise(workflow_outputs, "json_document"), "r") as jf:
        json_data = json.load(jf)
        return _map_if_list(ingest_phenopacket, json_data, table_id)


def ingest_fhir_workflow(workflow_outputs, table_id):
    with open(_get_output_or_raise(workflow_outputs, "patients"), "r") as pf:
        patients_data = json.load(pf)
        phenopacket_ids = ingest_patients(
            patients_data,
            table_id,
            workflow_outputs.get("created_by") or "Imported from file.",
        )

    if "observations" in workflow_outputs:
        with open(workflow_outputs["observations"], "r") as of:
            observations_data = json.load(of)
            ingest_observations(phenopacket_ids, observations_data)

    if "conditions" in workflow_outputs:
        with open(workflow_outputs["conditions"], "r") as cf:
            conditions_data = json.load(cf)
            ingest_conditions(phenopacket_ids, conditions_data)

    if "specimens" in workflow_outputs:
        with open(workflow_outputs["specimens"], "r") as sf:
            specimens_data = json.load(sf)
            ingest_specimens(phenopacket_ids, specimens_data)


def ingest_mcode_fhir_workflow(workflow_outputs, table_id):
    with open(_get_output_or_raise(workflow_outputs, "json_document"), "r") as jf:
        json_data = json.load(jf)
        mcodepacket = parse_bundle(json_data)
        ingest_mcodepacket(mcodepacket, table_id)


WORKFLOW_INGEST_FUNCTION_MAP = {
    WORKFLOW_EXPERIMENTS_JSON: ingest_experiments_workflow,
    WORKFLOW_PHENOPACKETS_JSON: ingest_phenopacket_workflow,
    WORKFLOW_FHIR_JSON: ingest_fhir_workflow,
    WORKFLOW_MCODE_FHIR_JSON: ingest_mcode_fhir_workflow,
}
