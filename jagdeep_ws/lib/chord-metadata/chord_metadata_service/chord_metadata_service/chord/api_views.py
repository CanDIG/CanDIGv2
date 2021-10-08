from rest_framework import viewsets
from rest_framework.permissions import BasePermission, SAFE_METHODS
from rest_framework.settings import api_settings

from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer, JSONLDDatasetRenderer, RDFDatasetRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination
from .models import Project, Dataset, TableOwnership, Table
from .permissions import OverrideOrSuperUserOnly
from .serializers import ProjectSerializer, DatasetSerializer, TableOwnershipSerializer, TableSerializer


__all__ = ["ProjectViewSet", "DatasetViewSet", "TableOwnershipViewSet", "TableViewSet"]


class ReadOnly(BasePermission):
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS


class CHORDModelViewSet(viewsets.ModelViewSet):
    renderer_classes = tuple(api_settings.DEFAULT_RENDERER_CLASSES) + (PhenopacketsRenderer,)
    pagination_class = LargeResultsSetPagination
    permission_classes = [OverrideOrSuperUserOnly]  # Explicit


class CHORDPublicModelViewSet(CHORDModelViewSet):
    permission_classes = [OverrideOrSuperUserOnly | ReadOnly]


class ProjectViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of all existing projects

    post:
    Create a new project
    """

    queryset = Project.objects.all().order_by("identifier")
    serializer_class = ProjectSerializer


class DatasetViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of all existing datasets

    post:
    Create a new dataset
    """

    queryset = Dataset.objects.all().order_by("identifier")
    serializer_class = DatasetSerializer
    renderer_classes = tuple(CHORDModelViewSet.renderer_classes) + (JSONLDDatasetRenderer, RDFDatasetRenderer,)


class TableOwnershipViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of table-(dataset|dataset,biosample) relationships

    post:
    Create a new relationship between a dataset (and optionally a specific biosample) and a table
    in a data service
    """

    queryset = TableOwnership.objects.all().order_by("table_id")
    serializer_class = TableOwnershipSerializer


class TableViewSet(CHORDPublicModelViewSet):
    """
    get:
    Return a list of tables

    post:
    Create a new table
    """

    # TODO: Create TableOwnership if needed - here or model?

    queryset = Table.objects.all().prefetch_related("ownership_record").order_by("ownership_record_id")
    serializer_class = TableSerializer
