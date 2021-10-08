from rest_framework import status
from rest_framework.test import APITestCase
from . import constants as c
from .. import models as m, serializers as s
from chord_metadata_service.restapi.tests.utils import get_response


class CreateBiosampleTest(APITestCase):
    """ Test module for creating an Biosample. """

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.procedure = c.VALID_PROCEDURE_1
        self.valid_payload = c.valid_biosample_1(self.individual.id, self.procedure)
        self.invalid_payload = {
            "id": "biosample:1",
            "individual": self.individual.id,
            "procedure": self.procedure,
            "description": "This is a test description.",
            "sampled_tissue": {
                "id": "UBERON_0001256"
            },
            "individual_age_at_collection": "P67Y3M2D",
            "histological_diagnosis": {
                "id": "NCIT:C39853",
                "label": "Infiltrating Urothelial Carcinoma"
            },
            "tumor_progression": {
                "id": "NCIT:C84509",
                "label": "Primary Malignant Neoplasm"
            },
            "tumor_grade": {
                "id": "NCIT:C48766",
                "label": "pT2b Stage Finding"
            },
            "diagnostic_markers": [
                {
                    "id": "NCIT:C49286",
                    "label": "Hematology Test"
                },
                {
                    "id": "NCIT:C15709",
                    "label": "Genetic Testing"
                }
            ]
        }

    def test_create_biosample(self):
        """ POST a new biosample. """

        response = get_response('biosample-list', self.valid_payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Biosample.objects.count(), 1)
        self.assertEqual(m.Biosample.objects.get().id, 'biosample_id:1')

    def test_create_invalid_biosample(self):
        """ POST a new biosample with invalid data. """

        invalid_response = get_response('biosample-list', self.invalid_payload)
        self.assertEqual(
            invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(m.Biosample.objects.count(), 0)

    def test_seriliazer_validate_invalid(self):
        serializer = s.BiosampleSerializer(data=self.invalid_payload)
        self.assertEqual(serializer.is_valid(), False)

    def test_seriliazer_validate_valid(self):
        serializer = s.BiosampleSerializer(data=self.valid_payload)
        self.assertEqual(serializer.is_valid(), True)


class CreatePhenotypicFeatureTest(APITestCase):

    def setUp(self):
        valid_payload = c.valid_phenotypic_feature()
        valid_payload.pop('pftype', None)
        valid_payload['type'] = {
            "id": "HP:0000520",
            "label": "Proptosis"
        }
        self.valid_phenotypic_feature = valid_payload
        invalid_payload = c.invalid_phenotypic_feature()
        invalid_payload['type'] = {
            "id": "HP:0000520",
            "label": "Proptosis"
        }
        self.invalid_phenotypic_feature = invalid_payload

    def test_create_phenotypic_feature(self):
        """ POST a new phenotypic feature. """

        response = get_response('phenotypicfeature-list', self.valid_phenotypic_feature)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.PhenotypicFeature.objects.count(), 1)

    def test_modifier(self):
        serializer = s.PhenotypicFeatureSerializer(data=self.invalid_phenotypic_feature)
        self.assertEqual(serializer.is_valid(), False)


class CreateProcedureTest(APITestCase):

    def setUp(self):
        self.valid_procedure = c.VALID_PROCEDURE_1
        self.duplicate_procedure = c.VALID_PROCEDURE_1
        self.valid_procedure_duplicate_code = c.VALID_PROCEDURE_2

    def test_procedure(self):
        response = get_response('procedure-list', self.valid_procedure)
        response_duplicate = get_response(
            'procedure-list', self.duplicate_procedure)
        response_duplicate_code = get_response(
            'procedure-list', self.valid_procedure_duplicate_code)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_duplicate.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_duplicate_code.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Procedure.objects.count(), 2)


class CreateHtsFileTest(APITestCase):

    def setUp(self):
        self.hts_file = c.VALID_HTS_FILE

    def test_hts_file(self):
        response = get_response('htsfile-list', self.hts_file)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.HtsFile.objects.count(), 1)


class CreateGeneTest(APITestCase):

    def setUp(self):
        self.gene = c.VALID_GENE_1
        self.duplicate_gene = c.DUPLICATE_GENE_2
        self.invalid_gene = c.INVALID_GENE_2

    def test_gene(self):
        response = get_response('gene-list', self.gene)
        response_duplicate = get_response('htsfile-list', self.duplicate_gene)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response_duplicate.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(m.Gene.objects.count(), 1)

    def test_alternate_ids(self):
        serializer = s.GeneSerializer(data=self.invalid_gene)
        self.assertEqual(serializer.is_valid(), False)


class CreateVariantTest(APITestCase):

    def setUp(self):
        self.variant = c.VALID_VARIANT_1
        self.variant_2 = c.VALID_VARIANT_2

    def test_variant(self):
        response = get_response('variant-list', self.variant)
        serializer = s.VariantSerializer(data=self.variant)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Variant.objects.count(), 1)

    def test_to_represenation(self):
        response = get_response('variant-list', self.variant_2)
        serializer = s.VariantSerializer(data=self.variant)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Variant.objects.count(), 1)


class CreateDiseaseTest(APITestCase):

    def setUp(self):
        self.disease = c.VALID_DISEASE_1
        self.invalid_disease = c.INVALID_DISEASE_2

    def test_disease(self):
        response = get_response('disease-list', self.disease)
        serializer = s.DiseaseSerializer(data=self.disease)
        self.assertEqual(serializer.is_valid(), True)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Disease.objects.count(), 1)

    def test_invalid_disease(self):
        serializer = s.DiseaseSerializer(data=self.invalid_disease)
        self.assertEqual(serializer.is_valid(), False)
        self.assertEqual(m.Disease.objects.count(), 0)


class CreateMetaDataTest(APITestCase):

    def setUp(self):
        self.metadata = c.VALID_META_DATA_2

    def test_metadata(self):
        response = get_response('metadata-list', self.metadata)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.MetaData.objects.count(), 1)

    def test_serializer(self):
        # is_valid() calls validation on serializer
        serializer = s.MetaDataSerializer(data=self.metadata)
        self.assertEqual(serializer.is_valid(), True)


class CreatePhenopacketTest(APITestCase):

    def setUp(self):
        individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.subject = individual.id
        meta = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.metadata = meta.id
        self.phenopacket = c.valid_phenopacket(
            subject=self.subject,
            meta_data=self.metadata)

    def test_phenopacket(self):
        response = get_response('phenopacket-list', self.phenopacket)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.Phenopacket.objects.count(), 1)

    def test_serializer(self):
        serializer = s.PhenopacketSerializer(data=self.phenopacket)
        self.assertEqual(serializer.is_valid(), True)


class CreateGenomicInterpretationTest(APITestCase):

    def setUp(self):
        self.gene = m.Gene.objects.create(**c.VALID_GENE_1).id
        self.variant = m.Variant.objects.create(**c.VALID_VARIANT_1).id
        self.genomic_interpretation = c.valid_genomic_interpretation(
            gene=self.gene,
            variant=self.variant
        )

    def test_genomic_interpretation(self):
        response = get_response('genomicinterpretation-list',
                                self.genomic_interpretation)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(m.GenomicInterpretation.objects.count(), 1)

    def test_serializer(self):
        serializer = s.GenomicInterpretationSerializer(data=self.genomic_interpretation)
        self.assertEqual(serializer.is_valid(), True)


class CreateDiagnosisTest(APITestCase):

    def setUp(self):
        self.disease = m.Disease.objects.create(**c.VALID_DISEASE_1).id
        self.diagnosis = c.valid_diagnosis(self.disease)

    def test_diagnosis(self):
        response = get_response('diagnosis-list',
                                self.diagnosis)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        serializer = s.DiagnosisSerializer(data=self.diagnosis)
        self.assertEqual(serializer.is_valid(), True)


class CreateInterpretationTest(APITestCase):

    def setUp(self):
        self.individual = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.metadata = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.phenopacket = m.Phenopacket.objects.create(**c.valid_phenopacket(
            subject=self.individual,
            meta_data=self.metadata)
            ).id
        self.metadata_interpretation = m.MetaData.objects.create(**c.VALID_META_DATA_2).id
        self.disease = m.Disease.objects.create(**c.VALID_DISEASE_1)
        self.diagnosis = m.Diagnosis.objects.create(**c.valid_diagnosis(self.disease)).id
        self.interpretation = c.valid_interpretation(
            phenopacket=self.phenopacket,
            meta_data=self.metadata_interpretation
        )
        self.interpretation['diagnosis'] = [self.diagnosis]

    def test_interpretation(self):
        response = get_response('interpretation-list',
                                self.interpretation)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class OverviewTest(APITestCase):

    def setUp(self) -> None:
        # create 2 phenopackets for 2 individuals; each individual has 1 biosample;
        # one of phenopackets has 1 phenotypic feature and 1 disease
        self.individual_1 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_1)
        self.individual_2 = m.Individual.objects.create(**c.VALID_INDIVIDUAL_2)
        self.metadata_1 = m.MetaData.objects.create(**c.VALID_META_DATA_1)
        self.metadata_2 = m.MetaData.objects.create(**c.VALID_META_DATA_2)
        self.phenopacket_1 = m.Phenopacket.objects.create(
            **c.valid_phenopacket(subject=self.individual_1, meta_data=self.metadata_1)
        )
        self.phenopacket_2 = m.Phenopacket.objects.create(
            id='phenopacket:2', subject=self.individual_2, meta_data=self.metadata_2
        )
        self.disease = m.Disease.objects.create(**c.VALID_DISEASE_1)
        self.procedure = m.Procedure.objects.create(**c.VALID_PROCEDURE_1)
        self.biosample_1 = m.Biosample.objects.create(**c.valid_biosample_1(self.individual_1, self.procedure))
        self.biosample_2 = m.Biosample.objects.create(**c.valid_biosample_2(self.individual_2, self.procedure))
        self.phenotypic_feature = m.PhenotypicFeature.objects.create(
            **c.valid_phenotypic_feature(self.biosample_1, self.phenopacket_1)
        )
        self.phenopacket_1.biosamples.set([self.biosample_1])
        self.phenopacket_2.biosamples.set([self.biosample_2])
        self.phenopacket_1.diseases.set([self.disease])

    def test_overview(self):
        response = self.client.get('/api/overview')
        response_obj = response.json()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response_obj, dict)
        self.assertEqual(response_obj['phenopackets'], 2)
        self.assertEqual(response_obj['data_type_specific']['individuals']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['biosamples']['count'], 2)
        self.assertEqual(response_obj['data_type_specific']['phenotypic_features']['count'], 1)
        self.assertEqual(response_obj['data_type_specific']['diseases']['count'], 1)
