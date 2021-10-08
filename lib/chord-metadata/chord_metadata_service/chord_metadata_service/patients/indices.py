from django.conf import settings
from chord_metadata_service.metadata.elastic import es
from chord_metadata_service.patients.serializers import IndividualSerializer
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.restapi.fhir_utils import fhir_patient


def build_individual_index(individual: Individual) -> str:
    if es:
        ind_json = IndividualSerializer(individual)
        fhir_ind_json = fhir_patient(ind_json.data)

        res = es.index(index=settings.FHIR_INDEX_NAME, id=individual.index_id, body=fhir_ind_json)
        return res['result']


def remove_individual_index(individual: Individual) -> str:
    if es:
        res = es.delete(index=settings.FHIR_INDEX_NAME, id=individual.index_id)
        return res['result']
