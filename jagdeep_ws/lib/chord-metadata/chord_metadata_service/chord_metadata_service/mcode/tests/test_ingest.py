import uuid
import os
import json

from django.test import TestCase

from chord_metadata_service.chord.data_types import DATA_TYPE_PHENOPACKET
from chord_metadata_service.chord.models import Project, Dataset, TableOwnership, Table
from chord_metadata_service.patients.models import Individual
# noinspection PyProtectedMember
from chord_metadata_service.chord.ingest import (
    WORKFLOW_INGEST_FUNCTION_MAP,
    WORKFLOW_MCODE_FHIR_JSON
)
from chord_metadata_service.chord.tests.constants import VALID_DATA_USE_1

from ..parse_fhir_mcode import parse_bundle, patient_to_individual
from ..models import MCodePacket


with open(os.path.join(os.path.dirname(__file__), "example_mcode_fhir.json"), "r") as pf:
    EXAMPLE_INGEST_MCODE_FHIR = json.load(pf)

EXAMPLE_INGEST_OUTPUTS = {
    "json_document": os.path.join(os.path.dirname(__file__), "example_mcode_fhir.json"),
}


class ParseMcodeFhirTest(TestCase):

    def test_patient_to_individual(self):
        for item in EXAMPLE_INGEST_MCODE_FHIR["entry"]:
            if item["resource"]["resourceType"] == "Patient":
                individual = patient_to_individual(item["resource"])
                self.assertEqual(individual["id"], "6fcf56ed-8ad8-4395-a966-9ebee3822656")
                self.assertEqual(type(individual["alternate_ids"]), list)
                self.assertEqual(individual["sex"], "FEMALE")
                self.assertIsNotNone(individual["deceased"])

    def test_parse_bundle(self):
        mcodepacket = parse_bundle(EXAMPLE_INGEST_MCODE_FHIR)
        self.assertEqual(type(mcodepacket["cancer_disease_status"]), dict)
        self.assertEqual(type(mcodepacket["cancer_condition"]), list)
        self.assertEqual(mcodepacket["cancer_condition"][0]["clinical_status"]["label"], "active")
        self.assertEqual(mcodepacket["cancer_condition"][0]["verification_status"]["label"], "confirmed")
        self.assertEqual(mcodepacket["cancer_condition"][0]["code"]["label"], "Malignant neoplasm of breast (disorder)")
        self.assertIsNotNone(mcodepacket["cancer_condition"][0]["date_of_diagnosis"])
        self.assertEqual(mcodepacket["cancer_condition"][0]["condition_type"], "primary")
        self.assertEqual(type(mcodepacket["cancer_condition"][0]["tnm_staging"]), list)
        tnms_categories = ["primary_tumor_category", "regional_nodes_category", "distant_metastases_category"]
        for tnms in mcodepacket["cancer_condition"][0]["tnm_staging"]:
            for category in tnms_categories:
                self.assertTrue(category in [key for key in tnms.keys()])
        self.assertEqual(type(mcodepacket["medication_statement"]), list)


class IngestMcodeFhirTest(TestCase):

    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1,
                                        project=p)
        # TODO: Real service ID
        to = TableOwnership.objects.create(table_id=uuid.uuid4(), service_id=uuid.uuid4(), service_artifact="metadata",
                                           dataset=self.d)
        self.t = Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

    def test_ingest_mcodepacket(self):
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_MCODE_FHIR_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)
        self.assertEqual(len(MCodePacket.objects.all()), 1)
        # ingest again
        WORKFLOW_INGEST_FUNCTION_MAP[WORKFLOW_MCODE_FHIR_JSON](EXAMPLE_INGEST_OUTPUTS, self.t.identifier)
        self.assertEqual(len(MCodePacket.objects.all()), 2)
        self.assertEqual(len(Individual.objects.all()), 1)
