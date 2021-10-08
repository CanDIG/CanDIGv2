from django.test import TestCase
from uuid import uuid4
from ..data_types import DATA_TYPE_PHENOPACKET
from ..models import Project, Dataset, TableOwnership, Table
from .constants import VALID_DATA_USE_1


P2_DESC = "This is a good project..."


class ProjectTest(TestCase):
    def setUp(self) -> None:
        Project.objects.create(title="Project 1", description="")
        Project.objects.create(title="Project 2", description=P2_DESC)

    def test_project(self):
        p1 = Project.objects.get(title="Project 1")
        p2 = Project.objects.get(title="Project 2")

        self.assertEqual(p1.description, "")
        self.assertEqual(p2.description, P2_DESC)

        self.assertEqual(str(p1), f"Project 1 (ID: {str(p1.identifier)})")


class DatasetTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        Dataset.objects.create(title="Dataset 1", description="Some dataset", data_use=VALID_DATA_USE_1, project=p)

    def test_dataset(self):
        p = Project.objects.get(title="Project 1")
        d = Dataset.objects.get(title="Dataset 1")

        self.assertEqual(d.description, "Some dataset")
        self.assertDictEqual(d.data_use, VALID_DATA_USE_1)
        self.assertEqual(d.project, p)

        self.assertEqual(str(d), f"Dataset 1 (ID: {str(d.identifier)})")

        self.assertIn(d.identifier, set(d2.identifier for d2 in p.datasets.all()))


TABLE_ID = str(uuid4())
SERVICE_ID = str(uuid4())


class TableOwnershipTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        d = Dataset.objects.create(title="Dataset 1", description="", data_use=VALID_DATA_USE_1, project=p)
        TableOwnership.objects.create(
            table_id=TABLE_ID,
            service_id=SERVICE_ID,
            service_artifact="variant",
            dataset=d
        )

    def test_table_ownership(self):
        d = Dataset.objects.get(title="Dataset 1")
        t = TableOwnership.objects.get(table_id=TABLE_ID, service_id=SERVICE_ID)

        self.assertEqual(t.service_artifact, "variant")
        self.assertEqual(t.dataset, d)

        self.assertIn(t, d.table_ownership.all())

        self.assertEqual(str(t), f"{str(d)} -> {t.table_id}")


class TableTest(TestCase):
    def setUp(self) -> None:
        p = Project.objects.create(title="Project 1", description="")
        self.d = Dataset.objects.create(title="Dataset 1", description="", data_use=VALID_DATA_USE_1, project=p)
        to = TableOwnership.objects.create(
            table_id=TABLE_ID,
            service_id=SERVICE_ID,
            service_artifact="variant",
            dataset=self.d
        )
        Table.objects.create(ownership_record=to, name="Table 1", data_type=DATA_TYPE_PHENOPACKET)

    def test_table(self):
        t = Table.objects.get(ownership_record_id=TABLE_ID)

        self.assertEqual(t.data_type, DATA_TYPE_PHENOPACKET)
        self.assertEqual(t.identifier, TABLE_ID)
        self.assertEqual(t.dataset, self.d)

        self.assertEqual(str(t), f"{t.name} (ID: {TABLE_ID}, Type: {DATA_TYPE_PHENOPACKET})")
