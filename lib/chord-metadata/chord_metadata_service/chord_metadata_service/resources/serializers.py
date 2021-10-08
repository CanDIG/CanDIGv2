from chord_metadata_service.restapi.serializers import GenericSerializer

from .models import Resource


__all__ = ["ResourceSerializer"]


class ResourceSerializer(GenericSerializer):
    class Meta:
        model = Resource
        fields = '__all__'
