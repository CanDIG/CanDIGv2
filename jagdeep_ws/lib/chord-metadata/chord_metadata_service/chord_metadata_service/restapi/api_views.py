from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from chord_metadata_service.metadata.service_info import SERVICE_INFO


@api_view()
@permission_classes([AllowAny])
def service_info(_request):
    """
    get:
    Return service info
    """

    return Response(SERVICE_INFO)
