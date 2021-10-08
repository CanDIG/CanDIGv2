from rest_framework import viewsets
from rest_framework.settings import api_settings
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .schemas import MCODE_SCHEMA
from . import models as m, serializers as s
from chord_metadata_service.restapi.api_renderers import PhenopacketsRenderer
from chord_metadata_service.restapi.pagination import LargeResultsSetPagination


class McodeModelViewSet(viewsets.ModelViewSet):
    pagination_class = LargeResultsSetPagination
    renderer_classes = (*api_settings.DEFAULT_RENDERER_CLASSES, PhenopacketsRenderer)


class GeneticSpecimenViewSet(McodeModelViewSet):
    queryset = m.GeneticSpecimen.objects.all()
    serializer_class = s.GeneticSpecimenSerializer


class CancerGeneticVariantViewSet(McodeModelViewSet):
    queryset = m.CancerGeneticVariant.objects.all()
    serializer_class = s.CancerGeneticVariantSerializer


class GenomicRegionStudiedViewSet(McodeModelViewSet):
    queryset = m.GenomicRegionStudied.objects.all()
    serializer_class = s.GenomicRegionStudiedSerializer


class GenomicsReportViewSet(McodeModelViewSet):
    queryset = m.GenomicsReport.objects.all()
    serializer_class = s.GenomicsReportSerializer


class LabsVitalViewSet(McodeModelViewSet):
    queryset = m.LabsVital.objects.all()
    serializer_class = s.LabsVitalSerializer


class CancerConditionViewSet(McodeModelViewSet):
    queryset = m.CancerCondition.objects.all()
    serializer_class = s.CancerConditionSerializer


class TNMStagingViewSet(McodeModelViewSet):
    queryset = m.TNMStaging.objects.all()
    serializer_class = s.TNMStagingSerializer


class CancerRelatedProcedureViewSet(McodeModelViewSet):
    queryset = m.CancerRelatedProcedure.objects.all()
    serializer_class = s.CancerRelatedProcedureSerializer


class MedicationStatementViewSet(McodeModelViewSet):
    queryset = m.MedicationStatement.objects.all()
    serializer_class = s.MedicationStatementSerializer


class MCodePacketViewSet(McodeModelViewSet):
    queryset = m.MCodePacket.objects.all()
    serializer_class = s.MCodePacketSerializer


@api_view(["GET"])
@permission_classes([AllowAny])
def get_mcode_schema(_request):
    """
    get:
    Mcodepacket schema
    """
    return Response(MCODE_SCHEMA)
