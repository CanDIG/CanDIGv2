import json

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from .constants import (
    VALID_PROJECT_1,
    VALID_DATA_USE_1,
    valid_dataset_1,
    dats_dataset,
    VALID_DATS_CREATORS,
    INVALID_DATS_CREATORS,
)
from ..models import Project, Dataset


class CreateProjectTest(APITestCase):
    def setUp(self) -> None:
        self.valid_payloads = [
            VALID_PROJECT_1,
            {
                "title": "Project 2",
                "description": "",
                "data_use": VALID_DATA_USE_1
            }
        ]

        self.invalid_payloads = [
            {
                "title": "Project 1",
                "description": "",
                "data_use": {}
            },
            {
                "title": "aa",
                "description": "",
                "data_use": VALID_DATA_USE_1
            }
        ]

    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def test_create_project(self):
        for i, p in enumerate(self.valid_payloads, 1):
            r = self.client.post(reverse("project-list"), data=json.dumps(p), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Project.objects.count(), i)
            self.assertEqual(Project.objects.get(title=p["title"]).description, p["description"])

        for p in self.invalid_payloads:
            r = self.client.post(reverse("project-list"), data=json.dumps(p), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Project.objects.count(), len(self.valid_payloads))


# TODO: Update Project
# TODO: Delete Project

class CreateDatasetTest(APITestCase):
    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def setUp(self) -> None:
        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        self.valid_payloads = [
            valid_dataset_1(self.project["identifier"])
        ]

        self.dats_valid_payload = dats_dataset(self.project["identifier"], VALID_DATS_CREATORS)
        self.dats_invalid_payload = dats_dataset(self.project["identifier"], INVALID_DATS_CREATORS)

        self.invalid_payloads = [
            {
                "title": "aa",
                "description": "Test Dataset",
                "project": self.project["identifier"]
            },
            {
                "title": "Dataset 1",
                "description": "Test Dataset",
                "project": None
            }
        ]

    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def test_create_dataset(self):
        for i, d in enumerate(self.valid_payloads, 1):
            r = self.client.post(reverse("dataset-list"), data=json.dumps(d), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_201_CREATED)
            self.assertEqual(Dataset.objects.count(), i)
            self.assertEqual(Dataset.objects.get(title=d["title"]).description, d["description"])
            self.assertDictEqual(Dataset.objects.get(title=d["title"]).data_use, d["data_use"])

        for d in self.invalid_payloads:
            r = self.client.post(reverse("dataset-list"), data=json.dumps(d), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(Dataset.objects.count(), len(self.valid_payloads))

    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def test_dats(self):
        r = self.client.post(reverse("dataset-list"), data=json.dumps(self.dats_valid_payload),
                             content_type="application/json")
        r_invalid = self.client.post(reverse("dataset-list"), data=json.dumps(self.dats_invalid_payload),
                                     content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(r_invalid.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Dataset.objects.count(), 1)


# TODO: Update Dataset
# TODO: Delete Dataset
# TODO: Create TableOwnership
# TODO: Update TableOwnership
# TODO: Delete TableOwnership
# TODO: Create Table
# TODO: Update Table
# TODO: Delete Table
