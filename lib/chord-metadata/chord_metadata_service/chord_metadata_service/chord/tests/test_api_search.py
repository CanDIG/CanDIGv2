import json
import uuid

from unittest.mock import patch

from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_PROCEDURE_1,
    valid_biosample_1,
    valid_biosample_2,
    VALID_META_DATA_1,
)
from chord_metadata_service.phenopackets.models import Biosample, MetaData, Phenopacket, Procedure, PhenotypicFeature

from chord_metadata_service.chord.tests.es_mocks import SEARCH_SUCCESS
from .constants import (
    VALID_PROJECT_1,
    valid_dataset_1,
    valid_table_1,
    valid_phenotypic_feature,
    TEST_SEARCH_QUERY_1,
    TEST_SEARCH_QUERY_2,
    TEST_SEARCH_QUERY_3,
    TEST_SEARCH_QUERY_4,
    TEST_FHIR_SEARCH_QUERY,
)
from ..models import Project, Dataset, TableOwnership, Table
from ..data_types import DATA_TYPE_EXPERIMENT, DATA_TYPE_MCODEPACKET, DATA_TYPE_PHENOPACKET, DATA_TYPES


class DataTypeTest(APITestCase):
    def test_data_type_list(self):
        r = self.client.get(reverse("data-type-list"))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c), 3)
        ids = (c[0]["id"], c[1]["id"], c[2]["id"])
        self.assertIn(DATA_TYPE_EXPERIMENT, ids)
        self.assertIn(DATA_TYPE_MCODEPACKET, ids)
        self.assertIn(DATA_TYPE_PHENOPACKET, ids)

    def test_data_type_detail(self):
        r = self.client.get(reverse("data-type-detail", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, {
            "id": DATA_TYPE_PHENOPACKET,
            **DATA_TYPES[DATA_TYPE_PHENOPACKET],
        })

    def test_data_type_schema(self):
        r = self.client.get(reverse("data-type-schema", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, DATA_TYPES[DATA_TYPE_PHENOPACKET]["schema"])

    def test_data_type_metadata_schema(self):
        r = self.client.get(reverse("data-type-metadata-schema", kwargs={"data_type": DATA_TYPE_PHENOPACKET}))
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertDictEqual(c, DATA_TYPES[DATA_TYPE_PHENOPACKET]["metadata_schema"])


class TableTest(APITestCase):
    @staticmethod
    def table_rep(table, created, updated):
        return {
            "id": table["identifier"],
            "name": table["name"],
            "metadata": {
                "dataset_id": table["dataset"]["identifier"],
                "created": created,
                "updated": updated
            },
            "data_type": table["data_type"],
            "schema": DATA_TYPES[table["data_type"]]["schema"],
        }

    @override_settings(AUTH_OVERRIDE=True)  # For permissions
    def setUp(self) -> None:
        # Add example data

        r = self.client.post(reverse("project-list"), data=json.dumps(VALID_PROJECT_1), content_type="application/json")
        self.project = r.json()

        r = self.client.post(reverse("dataset-list"), data=json.dumps(valid_dataset_1(self.project["identifier"])),
                             content_type="application/json")
        self.dataset = r.json()

        to, tr = valid_table_1(self.dataset["identifier"])
        self.client.post(reverse("tableownership-list"), data=json.dumps(to), content_type="application/json")
        r = self.client.post(reverse("table-list"), data=json.dumps(tr), content_type="application/json")
        self.table = r.json()

    def test_chord_table_list(self):
        # No data type specified
        r = self.client.get(reverse("chord-table-list"))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        r = self.client.get(reverse("chord-table-list"), {"data-type": DATA_TYPE_PHENOPACKET})
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c), 1)
        self.assertEqual(c[0], self.table_rep(self.table, c[0]["metadata"]["created"], c[0]["metadata"]["updated"]))

    def test_table_summary(self):
        r = self.client.get(reverse("table-summary", kwargs={"table_id": str(uuid.uuid4())}))
        self.assertEqual(r.status_code, 404)

        r = self.client.get(reverse("table-summary", kwargs={"table_id": self.table["identifier"]}))
        s = r.json()
        self.assertEqual(s["count"], 0)  # No phenopackets
        self.assertIn("data_type_specific", s)


class SearchTest(APITestCase):
    def setUp(self) -> None:
        self.project = Project.objects.create(**VALID_PROJECT_1)
        self.dataset = Dataset.objects.create(**valid_dataset_1(self.project))
        to, tr = valid_table_1(self.dataset.identifier, model_compatible=True)
        TableOwnership.objects.create(**to)
        self.table = Table.objects.create(**tr)

        # Set up a dummy phenopacket

        self.individual, _ = Individual.objects.get_or_create(
            id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})

        self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)

        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual, self.procedure))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, self.procedure))

        self.meta_data = MetaData.objects.create(**VALID_META_DATA_1)

        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual,
            meta_data=self.meta_data,
            table=self.table
        )

        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

        self.phenotypic_feature = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(phenopacket=self.phenopacket)
        )

    def test_common_search_1(self):
        # No body
        r = self.client.post(reverse("search"))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_2(self):
        # No data type
        r = self.client.post(reverse("search"), data=json.dumps({"query": TEST_SEARCH_QUERY_1}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_3(self):
        # No query
        r = self.client.post(reverse("search"), data=json.dumps({"data_type": DATA_TYPE_PHENOPACKET}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_4(self):
        # Bad data type
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": "bad_data_type",
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_common_search_5(self):
        # Bad syntax for query
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": DATA_TYPE_PHENOPACKET,
            "query": ["hello", "world"]
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_search_with_result(self):
        # Valid search with result
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": DATA_TYPE_PHENOPACKET,
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertDictEqual(c["results"][0], {
            "id": str(self.table.identifier),
            "data_type": DATA_TYPE_PHENOPACKET
        })

    def test_search_without_result(self):
        # Valid search without result
        r = self.client.post(reverse("search"), data=json.dumps({
            "data_type": DATA_TYPE_PHENOPACKET,
            "query": TEST_SEARCH_QUERY_2
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 0)

    def test_private_search(self):
        # Valid search with result
        r = self.client.post(reverse("private-search"), data=json.dumps({
            "data_type": DATA_TYPE_PHENOPACKET,
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertIn(str(self.table.identifier), c["results"])
        self.assertEqual(c["results"][str(self.table.identifier)]["data_type"], DATA_TYPE_PHENOPACKET)
        self.assertEqual(self.phenopacket.id, c["results"][str(self.table.identifier)]["matches"][0]["id"])
        # TODO: Check schema?

    def test_private_table_search_1(self):
        # No body

        r = self.client.post(reverse("public-table-search", args=[str(self.table.identifier)]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]))
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_private_table_search_2(self):
        # No query

        r = self.client.post(reverse("public-table-search", args=[str(self.table.identifier)]), data=json.dumps({}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]), data=json.dumps({}),
                             content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_private_table_search_3(self):
        # Bad syntax for query

        r = self.client.post(reverse("public-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": ["hello", "world"]
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": ["hello", "world"]
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)

    def test_private_table_search_4(self):
        # Valid query with one result

        r = self.client.post(reverse("public-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(c, True)

        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": TEST_SEARCH_QUERY_1
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertEqual(self.phenopacket.id, c["results"][0]["id"])

    def test_private_table_search_5(self):
        # Valid query: literal "true"
        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": True
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertEqual(self.phenopacket.id, c["results"][0]["id"])

    def test_private_table_search_6(self):
        # Valid query to search for phenotypic feature type

        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": TEST_SEARCH_QUERY_3
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertEqual(len(c["results"][0]["phenotypic_features"]), 1)
        self.assertEqual(c["results"][0]["phenotypic_features"][0]["type"]["label"], "Proptosis")

    def test_private_table_search_7(self):
        # Valid query to search for biosample sampled tissue term (this is exact match now only)

        r = self.client.post(reverse("private-table-search", args=[str(self.table.identifier)]), data=json.dumps({
            "query": TEST_SEARCH_QUERY_4
        }), content_type="application/json")
        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()
        self.assertEqual(len(c["results"]), 1)
        self.assertEqual(len(c["results"][0]["biosamples"]), 2)
        self.assertIn("bladder", c["results"][0]["biosamples"][0]["sampled_tissue"]["label"])

    @patch('chord_metadata_service.chord.views_search.es')
    def test_fhir_search(self, mocked_es):
        mocked_es.search.return_value = SEARCH_SUCCESS
        # Valid search with result
        r = self.client.post(reverse("fhir-search"), data=json.dumps({
            "data_type": DATA_TYPE_PHENOPACKET,
            "query": TEST_FHIR_SEARCH_QUERY
        }), content_type="application/json")

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()

        self.assertEqual(len(c["results"]), 1)
        self.assertDictEqual(c["results"][0], {
            "id": str(self.table.identifier),
            "data_type": DATA_TYPE_PHENOPACKET
        })

    @patch('chord_metadata_service.chord.views_search.es')
    def test_private_fhir_search(self, mocked_es):
        mocked_es.search.return_value = SEARCH_SUCCESS
        # Valid search with result
        r = self.client.post(reverse("fhir-private-search"), data=json.dumps({
            "data_type": DATA_TYPE_PHENOPACKET,
            "query": TEST_FHIR_SEARCH_QUERY
        }), content_type="application/json")

        self.assertEqual(r.status_code, status.HTTP_200_OK)
        c = r.json()

        self.assertIn(str(self.table.identifier), c["results"])
        self.assertEqual(c["results"][str(self.table.identifier)]["data_type"], DATA_TYPE_PHENOPACKET)
        self.assertEqual(self.phenopacket.id, c["results"][str(self.table.identifier)]["matches"][0]["id"])
