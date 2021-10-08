from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.metadata.service_info import SERVICE_INFO


class ServiceInfoTest(APITestCase):
    def test_service_info(self):
        r = self.client.get(reverse("service-info"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), SERVICE_INFO)

        # TODO: Test compliance with spec
