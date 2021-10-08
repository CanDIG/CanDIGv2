from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from .serializers import ExperimentSerializer
from .models import Experiment
from .schemas import EXPERIMENT_SCHEMA
from .filters import ExperimentFilter
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class ExperimentViewSet(viewsets.ModelViewSet):
    """
    get:
    Return a list of all existing experiments

    post:
    Create a new experiment
    """

    queryset = Experiment.objects.all().order_by("id")
    serializer_class = ExperimentSerializer
    pagination_class = LargeResultsSetPagination
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES)
    filter_backends = [DjangoFilterBackend]
    filter_class = ExperimentFilter


@api_view(["GET"])
@permission_classes([AllowAny])
def get_experiment_schema(_request):
    """
    get:
    Experiment schema
    """
    return Response(EXPERIMENT_SCHEMA)
