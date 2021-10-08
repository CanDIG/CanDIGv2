from chord_metadata_service.phenopackets.serializers import BiosampleSerializer, SimplePhenopacketSerializer
from chord_metadata_service.restapi.serializers import GenericSerializer
from chord_metadata_service.restapi.fhir_utils import fhir_patient
from .models import Individual


class IndividualSerializer(GenericSerializer):
    biosamples = BiosampleSerializer(read_only=True, many=True, exclude_when_nested=['individual'])
    phenopackets = SimplePhenopacketSerializer(read_only=True, many=True, exclude_when_nested=['subject'])

    class Meta:
        model = Individual
        fields = "__all__"
        # meta info for converting to FHIR
        fhir_datatype_plural = 'patients'
        class_converter = fhir_patient
