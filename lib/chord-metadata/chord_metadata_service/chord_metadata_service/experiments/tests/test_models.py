from django.test import TestCase
from django.core.exceptions import ValidationError
from rest_framework import serializers
from chord_metadata_service.patients.models import Individual
from chord_metadata_service.phenopackets.models import Biosample, Procedure
from ..models import Experiment
from chord_metadata_service.phenopackets.tests.constants import VALID_PROCEDURE_1, VALID_INDIVIDUAL_1, valid_biosample_1


class ExperimentTest(TestCase):
    """ Test module for Experiment model """

    def setUp(self):
        i = Individual.objects.create(**VALID_INDIVIDUAL_1)
        p = Procedure.objects.create(**VALID_PROCEDURE_1)
        self.biosample = Biosample.objects.create(**valid_biosample_1(i, p))
        Experiment.objects.create(
            id='experiment:1',
            reference_registry_id='some_id',
            qc_flags=['flag 1', 'flag 2'],
            experiment_type='Chromatin Accessibility',
            experiment_ontology=[{"id": "ontology:1", "label": "Ontology term 1"}],
            molecule_ontology=[{"id": "ontology:1", "label": "Ontology term 1"}],
            molecule='total RNA',
            library_strategy='Bisulfite-Seq',
            other_fields={"some_field": "value"},
            biosample=self.biosample
        )

    def create(self, **kwargs):
        e = Experiment(id="experiment:2", **kwargs)
        e.full_clean()
        e.save()

    def test_validation(self):
        # Invalid experiment_ontology
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy='Bisulfite-Seq',
            experiment_type='Chromatin Accessibility',
            experiment_ontology=["invalid_value"],
            biosample=self.biosample
        )

        # Invalid molecule_ontology
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy='Bisulfite-Seq',
            experiment_type='Chromatin Accessibility',
            molecule_ontology=[{"id": "some_id"}],
            biosample=self.biosample
        )

        # Invalid value in other_fields
        self.assertRaises(
            serializers.ValidationError,
            self.create,
            library_strategy='Bisulfite-Seq',
            experiment_type='Chromatin Accessibility',
            other_fields={"some_field": "value", "invalid_value": 42},
            biosample=self.biosample
        )

        # Missing biosample
        self.assertRaises(
            ValidationError,
            self.create,
            library_strategy='Bisulfite-Seq',
            experiment_type='Chromatin Accessibility'
        )
