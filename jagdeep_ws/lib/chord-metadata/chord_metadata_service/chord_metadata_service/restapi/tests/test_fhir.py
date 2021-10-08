from rest_framework import status
from rest_framework.test import APITestCase

from chord_metadata_service.patients.models import Individual
from chord_metadata_service.patients.tests.constants import VALID_INDIVIDUAL, VALID_INDIVIDUAL_2
from chord_metadata_service.phenopackets.models import (
    MetaData,
    Procedure,
    Biosample,
    Phenopacket,
    PhenotypicFeature,
)
from chord_metadata_service.phenopackets.tests.constants import (
    VALID_INDIVIDUAL_1,
    VALID_META_DATA_2,
    VALID_PROCEDURE_1,
    VALID_HTS_FILE,
    VALID_DISEASE_1,
    VALID_GENE_1,
    VALID_VARIANT_1,
    valid_biosample_1,
    valid_biosample_2,
    valid_phenotypic_feature,
)
from chord_metadata_service.restapi.tests.utils import get_response


# Tests for FHIR conversion functions


class FHIRPhenopacketTest(APITestCase):

    def setUp(self):
        self.subject = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.metadata = MetaData.objects.create(**VALID_META_DATA_2)
        self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)
        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.subject, self.procedure))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(None, self.procedure))
        self.phenopacket = Phenopacket.objects.create(
            id="phenopacket_id:1",
            subject=self.subject,
            meta_data=self.metadata,
        )
        self.phenopacket.biosamples.set([self.biosample_1, self.biosample_2])

    def test_get_fhir(self):
        get_resp = self.client.get('/api/phenopackets?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['compositions'][0]['resourceType'], 'Composition')
        self.assertEqual(get_resp_obj['compositions'][0]['title'], 'Phenopacket')
        self.assertEqual(get_resp_obj['compositions'][0]['type']['coding'][0]['system'],
                         'http://ga4gh.org/fhir/phenopackets/CodeSystem/document-type')
        self.assertEqual(get_resp_obj['compositions'][0]['status'], 'preliminary')
        self.assertIsInstance(get_resp_obj['compositions'][0]['subject']['reference'], str)
        self.assertIsInstance(get_resp_obj['compositions'][0]['section'], list)
        self.assertIsInstance(get_resp_obj['compositions'][0]['section'][0]['code']['coding'], list)
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['code'],
                         'biosamples')
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['display'],
                         'Biosamples')
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['system'],
                         'http://ga4gh.org/fhir/phenopackets/CodeSystem/section-type')
        self.assertEqual(get_resp_obj['compositions'][0]['section'][0]['code']['coding'][0]['version'],
                         '0.1.0')
        self.assertIsInstance(get_resp_obj['compositions'][0]['section'][0]['entry'], list)
        self.assertEqual(len(get_resp_obj['compositions'][0]['section'][0]['entry']), 2)


class FHIRIndividualTest(APITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):
        self.individual = VALID_INDIVIDUAL
        self.individual_second = VALID_INDIVIDUAL_2

    def test_get_fhir(self):
        response_1 = get_response('individual-list', self.individual)
        response_2 = get_response('individual-list', self.individual_second)
        print(response_1.data, response_2.data)
        get_resp = self.client.get('/api/individuals?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['patients'][0]['resourceType'], 'Patient')
        self.assertIsInstance(get_resp_obj['patients'][0]['extension'], list)
        self.assertEqual(get_resp_obj['patients'][1]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/individual-age')
        self.assertIsInstance(get_resp_obj['patients'][1]['extension'][0]['valueAge'], dict)


class FHIRPhenotypicFeatureTest(APITestCase):

    def setUp(self):
        self.individual_1 = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.individual_2 = Individual.objects.create(**VALID_INDIVIDUAL_2)
        self.procedure = Procedure.objects.create(**VALID_PROCEDURE_1)
        self.biosample_1 = Biosample.objects.create(**valid_biosample_1(self.individual_1, self.procedure))
        self.biosample_2 = Biosample.objects.create(**valid_biosample_2(
            self.individual_2, self.procedure))
        self.phenotypic_feature_1 = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(biosample=self.biosample_1))
        self.phenotypic_feature_2 = PhenotypicFeature.objects.create(
            **valid_phenotypic_feature(biosample=self.biosample_2))

    def test_get_fhir(self):
        get_resp = self.client.get('/api/phenotypicfeatures?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        severity = {
            'url': 'http://ga4gh.org/fhir/phenopackets/StructureDefinition/phenotypic-feature-severity',
            'valueCodeableConcept': {
                'coding': [
                    {
                        'code': 'HP: 0012825',
                        'display': 'Mild'
                    }
                ]
            }
        }
        self.assertEqual(get_resp_obj['observations'][0]['resourceType'], 'Observation')
        self.assertIsInstance(get_resp_obj['observations'][0]['extension'], list)
        self.assertIn(severity, get_resp_obj['observations'][0]['extension'])
        self.assertEqual(get_resp_obj['observations'][0]['status'], 'unknown')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['display'], 'Proptosis')
        self.assertEqual(get_resp_obj['observations'][0]['interpretation']['coding'][0]['code'], 'POS')
        self.assertEqual(get_resp_obj['observations'][0]['extension'][3]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/evidence')
        self.assertEqual(get_resp_obj['observations'][0]['extension'][3]['extension'][1]['extension'][1]['url'],
                         'description')
        self.assertIsNotNone(get_resp_obj['observations'][0]['specimen'])
        self.assertIsInstance(get_resp_obj['observations'][0]['specimen'], dict)
        self.assertEqual(get_resp_obj['observations'][0]['specimen']['reference'], 'biosample_id:1')


class FHIRProcedureTest(APITestCase):

    def setUp(self):
        self.valid_procedure = VALID_PROCEDURE_1

    def test_get_fhir(self):
        get_response('procedure-list', self.valid_procedure)
        get_resp = self.client.get('/api/procedures?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsNotNone(get_resp_obj['specimen.collections'][0]['method'])
        self.assertIsInstance(get_resp_obj['specimen.collections'][0]['bodySite'], dict)
        self.assertIsNot(get_resp_obj['specimen.collections'][0]['method']['coding'], [])


class FHIRBiosampleTest(APITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = Individual.objects.create(**VALID_INDIVIDUAL_1)
        self.procedure = VALID_PROCEDURE_1
        self.valid_payload = valid_biosample_1(self.individual.id, self.procedure)

    def test_get_fhir(self):
        """ POST a new biosample. """

        get_response('biosample-list', self.valid_payload)
        get_resp = self.client.get('/api/biosamples?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['specimens'][0]['resourceType'], 'Specimen')
        self.assertIsNotNone(get_resp_obj['specimens'][0]['type']['coding'][0])
        self.assertIsNotNone(get_resp_obj['specimens'][0]['collection'])
        self.assertIsInstance(get_resp_obj['specimens'][0]['extension'][0]['valueRange'], dict)
        self.assertEqual(get_resp_obj['specimens'][0]['extension'][4]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/biosample-diagnostic-markers')
        self.assertIsInstance(get_resp_obj['specimens'][0]['extension'][4]['valueCodeableConcept']['coding'],
                              list)
        self.assertTrue(get_resp_obj['specimens'][0]['extension'][5]['valueBoolean'])


class FHIRHtsFileTest(APITestCase):

    def setUp(self):
        self.hts_file = VALID_HTS_FILE

    def test_get_fhir(self):
        get_response('htsfile-list', self.hts_file)
        get_resp = self.client.get('/api/htsfiles?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['document_references'][0]['resourceType'], 'DocumentReference')
        self.assertIsInstance(get_resp_obj['document_references'][0]['content'], list)
        self.assertIsNotNone(get_resp_obj['document_references'][0]['content'][0]['attachment']['url'])
        self.assertEqual(get_resp_obj['document_references'][0]['status'], 'current')
        self.assertEqual(get_resp_obj['document_references'][0]['type']['coding'][0]['code'],
                         get_resp_obj['document_references'][0]['type']['coding'][0]['display'])
        self.assertEqual(get_resp_obj['document_references'][0]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/htsfile-genome-assembly')


class FHIRGeneTest(APITestCase):

    def setUp(self):
        self.gene = VALID_GENE_1

    def test_get_fhir(self):
        get_response('gene-list', self.gene)
        get_resp = self.client.get('/api/genes?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsInstance(get_resp_obj['observations'], list)
        self.assertIsInstance(get_resp_obj['observations'][0]['code']['coding'], list)
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['code'], '48018-6')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['display'], 'Gene studied [ID]')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['system'], 'https://loinc.org')
        self.assertIsInstance(get_resp_obj['observations'][0]['valueCodeableConcept']['coding'], list)
        self.assertEqual(get_resp_obj['observations'][0]['valueCodeableConcept']['coding'][0]['system'],
                         'https://www.genenames.org/')


class FHIRVariantTest(APITestCase):

    def setUp(self):
        self.variant = VALID_VARIANT_1

    def test_get_fhir(self):
        get_response('variant-list', self.variant)
        get_resp = self.client.get('/api/variants?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertIsInstance(get_resp_obj['observations'], list)
        self.assertIsInstance(get_resp_obj['observations'][0]['code']['coding'], list)
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['code'], '81300-6')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['display'], 'Structural variant [Length]')
        self.assertEqual(get_resp_obj['observations'][0]['code']['coding'][0]['system'], 'https://loinc.org')
        self.assertEqual(get_resp_obj['observations'][0]['valueCodeableConcept']['coding'][0]['code'],
                         get_resp_obj['observations'][0]['valueCodeableConcept']['coding'][0]['display'])


class FHIRDiseaseTest(APITestCase):

    def setUp(self):
        self.disease = VALID_DISEASE_1

    def test_get_fhir(self):
        get_response('disease-list', self.disease)
        get_resp = self.client.get('/api/diseases?format=fhir')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        get_resp_obj = get_resp.json()
        self.assertEqual(get_resp_obj['conditions'][0]['resourceType'], 'Condition')
        self.assertIsNotNone(get_resp_obj['conditions'][0]['code']['coding'][0])
        self.assertIsInstance(get_resp_obj['conditions'][0]['extension'], list)
        self.assertEqual(get_resp_obj['conditions'][0]['extension'][0]['url'],
                         'http://ga4gh.org/fhir/phenopackets/StructureDefinition/disease-tumor-stage')
        self.assertEqual(get_resp_obj['conditions'][0]['subject']['reference'], 'unknown')
