from rest_framework import status
from rest_framework.test import APITestCase
from chord_metadata_service.restapi.tests.utils import get_response

from ..models import Resource
from ..serializers import ResourceSerializer
from .constants import VALID_RESOURCE_2, DUPLICATE_RESOURCE_3


class CreateResourceTest(APITestCase):

    def setUp(self):
        self.resource = VALID_RESOURCE_2
        self.duplicate_resource = DUPLICATE_RESOURCE_3

    def test_resource(self):
        response = get_response('resource-list', self.resource)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Resource.objects.count(), 1)

    def test_serializer(self):
        serializer = ResourceSerializer(data=self.resource)
        self.assertEqual(serializer.is_valid(), True)
