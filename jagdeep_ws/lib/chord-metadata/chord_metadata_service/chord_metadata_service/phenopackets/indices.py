from django.conf import settings
from chord_metadata_service.metadata.elastic import es
from chord_metadata_service.phenopackets.serializers import (
    HtsFileSerializer,
    DiseaseSerializer,
    BiosampleSerializer,
    PhenotypicFeatureSerializer,
    PhenopacketSerializer
)
from chord_metadata_service.phenopackets.models import (
    HtsFile,
    Disease,
    Biosample,
    PhenotypicFeature,
    Phenopacket
)
from chord_metadata_service.restapi.fhir_utils import (
    fhir_document_reference,
    fhir_condition,
    fhir_specimen,
    fhir_observation,
    fhir_composition
)


def build_htsfile_index(htsfile: HtsFile) -> str:
    if es:
        htsfile_json = HtsFileSerializer(htsfile)
        fhir_htsfile_json = fhir_document_reference(htsfile_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=htsfile.index_id, body=fhir_htsfile_json)
        return res['result']


def remove_htsfile_index(htsfile: HtsFile) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=htsfile.index_id)
        return res['result']


def build_disease_index(disease: Disease) -> str:
    if es:
        disease_json = DiseaseSerializer(disease)
        fhir_disease_json = fhir_condition(disease_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=disease.index_id, body=fhir_disease_json)
        return res['result']


def remove_disease_index(disease: Disease) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=disease.index_id)
        return res['result']


def build_biosample_index(biosample: Biosample) -> str:
    if es:
        biosample_json = BiosampleSerializer(biosample)
        fhir_biosample_json = fhir_specimen(biosample_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=biosample.index_id, body=fhir_biosample_json)
        return res['result']


def remove_biosample_index(biosample: Biosample) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=biosample.index_id)
        return res['result']


def build_phenotypicfeature_index(feature: PhenotypicFeature) -> str:
    if es:
        feature_json = PhenotypicFeatureSerializer(feature)
        fhir_feature_json = fhir_observation(feature_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=feature.index_id, body=fhir_feature_json)
        return res['result']


def remove_phenotypicfeature_index(feature: PhenotypicFeature) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=feature.index_id)
        return res['result']


def build_phenopacket_index(phenopacket: Phenopacket) -> str:
    if es:
        phenopacket_json = PhenopacketSerializer(phenopacket)
        fhir_phenopacket_json = fhir_composition(phenopacket_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=phenopacket.index_id, body=fhir_phenopacket_json)
        return res['result']


def remove_phenopacket_index(phenopacket: Phenopacket) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=phenopacket.index_id)
        return res['result']
