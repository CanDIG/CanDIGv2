from django.test import TestCase
from chord_metadata_service.patients.tests.es_mocks import es  # noqa: F401
from chord_metadata_service.phenopackets.tests import constants as c
from chord_metadata_service.phenopackets import models as m

from ..models import Individual
from ..filters import IndividualFilter


class IndividualTest(TestCase):
    """ Test module for Individual model """

    def setUp(self):
        self.individual_one = Individual.objects.create(id='patient:1', sex='FEMALE', age={"age": "P25Y3M2D"})
        self.individual_two = Individual.objects.create(id='patient:2', sex='FEMALE', age={"age": "P45Y3M2D"})
        self.meta_data = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.phenopacket = m.Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.individual_one,
            meta_data=self.meta_data,
        )
        self.phenotypic_feature_1 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )
        self.phenotypic_feature_2 = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(phenopacket=self.phenopacket)
        )
        self.disease_1 = m.Disease.objects.create(**c.VALID_DISEASE_1)
        self.phenopacket.diseases.set([self.disease_1])

    def test_individual(self):
        individual_one = Individual.objects.get(id='patient:1')
        individual_two = Individual.objects.get(id='patient:2')
        self.assertEqual(individual_one.sex, 'FEMALE')
        self.assertEqual(individual_two.age, {"age": "P45Y3M2D"})
        number_of_pf_one = len(m.PhenotypicFeature.objects.filter(phenopacket__subject=individual_one))
        self.assertEqual(number_of_pf_one, 2)
        number_of_pf_two = len(m.PhenotypicFeature.objects.filter(phenopacket__subject=individual_two))
        self.assertEqual(number_of_pf_two, 0)

    def test_filtering(self):
        f = IndividualFilter()
        # all phenotypic feature constants have negated=True
        result = f.filter_found_phenotypic_feature(Individual.objects.all(), "phenopackets", "proptosis")
        self.assertEqual(len(result), 0)
        result = f.filter_found_phenotypic_feature(Individual.objects.all(), "phenopackets", "HP:0000520")
        self.assertEqual(len(result), 0)
        result = f.filter_disease(Individual.objects.all(), "phenopackets", "OMIM:164400")
        self.assertEqual(len(result), 1)
        result = f.filter_disease(Individual.objects.all(), "phenopackets", "spinocerebellar ataxia")
        self.assertEqual(len(result), 1)
