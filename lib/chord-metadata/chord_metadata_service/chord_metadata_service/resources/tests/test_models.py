from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError
from django.test import TestCase

from ..models import Resource
from .constants import VALID_RESOURCE_1, VALID_RESOURCE_2, DUPLICATE_RESOURCE_3


class ResourceTest(TestCase):
    """
    Test class for Resource model.
    """

    def setUp(self):
        self.resource_1 = Resource.objects.create(**VALID_RESOURCE_1)
        self.resource_2 = Resource.objects.create(**VALID_RESOURCE_2)

    def test_resource(self):
        self.assertEqual(Resource.objects.count(), 2)
        with self.assertRaises(IntegrityError):
            Resource.objects.create(**DUPLICATE_RESOURCE_3)

    def test_resource_str(self):
        self.assertEqual(str(self.resource_1), f"{self.resource_1.namespace_prefix}:{self.resource_1.version}")
        self.assertEqual(str(self.resource_2), f"{self.resource_2.namespace_prefix}:{self.resource_2.version}")

    def test_invalid_id(self):
        with self.assertRaises(ValidationError):
            Resource.objects.create(
                id="SO",
                name="Sequence types and features",
                namespace_prefix="SO",
                url="https://raw.githubusercontent.com/The-Sequence-Ontology/SO-Ontologies/v3.1/so.owl",
                version="3.1",
                iri_prefix="http://purl.obolibrary.org/obo/SO_",
            )
