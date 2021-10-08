from chord_metadata_service.restapi.serializers import GenericSerializer
from .models import Experiment


__all__ = ["ExperimentSerializer"]


class ExperimentSerializer(GenericSerializer):
    class Meta:
        model = Experiment
        fields = '__all__'
