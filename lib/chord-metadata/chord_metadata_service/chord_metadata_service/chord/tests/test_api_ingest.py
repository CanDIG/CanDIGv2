import json

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from uuid import uuid4

from .constants import VALID_PROJECT_1, valid_dataset_1, valid_table_1
from ..views_ingest import METADATA_WORKFLOWS


def generate_phenopackets_ingest(table_id):
    return {
        "table_id": table_id,
        "workflow_id": "phenopackets_json",
        "workflow_metadata": METADATA_WORKFLOWS["ingestion"]["phenopackets_json"],
        "workflow_outputs": {
            "json_document": ""  # TODO
        },
        "workflow_params": {
            "json_document": ""  # TODO
        }
    }


class WorkflowTest(APITestCase):
    def test_workflows(self):
        r = self.client.get(reverse("workflows"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), METADATA_WORKFLOWS)

        # Non-existent workflow
        r = self.client.get(reverse("workflow-detail", args=("invalid_workflow",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        # Valid workflow
        r = self.client.get(reverse("workflow-detail", args=("phenopackets_json",)), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        self.assertDictEqual(r.json(), METADATA_WORKFLOWS["ingestion"]["phenopackets_json"])

        # Non-existent workflow file
        r = self.client.get(reverse("workflow-file", args=("invalid_workflow",)), content_type="text/plain")
        self.assertEqual(r.status_code, status.HTTP_404_NOT_FOUND)

        # Valid workflow file
        r = self.client.get(reverse("workflow-file", args=("phenopackets_json",)), content_type="text/plain")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        # TODO: Check file contents


class IngestTest(APITestCase):
    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def setUp(self) -> None:
        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        r = self.client.post(reverse("dataset-list"), data=json.dumps(valid_dataset_1(self.project["identifier"])),
                             content_type="application/json")
        self.dataset = r.json()

        table_ownership, table_record = valid_table_1(self.dataset["identifier"])
        self.client.post(reverse("tableownership-list"), data=json.dumps(table_ownership),
                         content_type="application/json")
        r = self.client.post(reverse("table-list"), data=json.dumps(table_record), content_type="application/json")
        self.table = r.json()

    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def test_phenopackets_ingest(self):
        # No ingestion body
        r = self.client.post(reverse("ingest"), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        bad_ingest_bodies = (
            # Invalid ingest request
            {},

            # Non-existent table ID
            generate_phenopackets_ingest(str(uuid4())),

            # Non-existent workflow ID
            {**generate_phenopackets_ingest(self.table["identifier"]), "workflow_id": "phenopackets_json_invalid"},

            # json_document not in output
            {**generate_phenopackets_ingest(self.table["identifier"]), "workflow_outputs": {}},
        )

        for data in bad_ingest_bodies:
            print(data, flush=True)
            r = self.client.post(reverse("ingest"), data=json.dumps(data), content_type="application/json")
            self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        # TODO: More
