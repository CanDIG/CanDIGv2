import json
import csv
import io
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from ..models import Individual
from . import constants as c


class CreateIndividualTest(APITestCase):
    """ Test module for creating an Individual. """

    def setUp(self):

        self.valid_payload = c.VALID_INDIVIDUAL
        self.invalid_payload = c.INVALID_INDIVIDUAL

    def test_create_individual(self):
        """ POST a new individual. """

        response = self.client.post(
            reverse('individual-list'),
            data=json.dumps(self.valid_payload),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Individual.objects.count(), 1)
        self.assertEqual(Individual.objects.get().id, 'patient:1')

    def test_create_invalid_individual(self):
        """ POST a new individual with invalid data. """

        invalid_response = self.client.post(
            reverse('individual-list'),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
        )
        self.assertEqual(invalid_response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Individual.objects.count(), 0)


class UpdateIndividualTest(APITestCase):
    """ Test module for updating an existing Individual record. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)

        self.put_valid_payload = {
            "id": "patient:1",
            "taxonomy": {
                "id": "NCBITaxon:9606",
                "label": "human"
            },
            "date_of_birth": "2001-01-01",
            "age": {
                "start": {
                    "age": "P45Y"
                },
                "end": {
                    "age": "P49Y"
                }
            },
            "sex": "FEMALE",
            "active": False
        }

        self.invalid_payload = c.INVALID_INDIVIDUAL

    def test_update_individual(self):
        """ PUT new data in an existing Individual record. """

        response = self.client.put(
            reverse(
                'individual-detail',
                kwargs={'pk': self.individual_one.id}
                ),
            data=json.dumps(self.put_valid_payload),
            content_type='application/json'
            )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_update_invalid_individual(self):
        """ PUT new invalid data in an existing Individual record. """

        response = self.client.put(
            reverse(
                'individual-detail',
                kwargs={'pk': self.individual_one.id}
                ),
            data=json.dumps(self.invalid_payload),
            content_type='application/json'
            )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)


class DeleteIndividualTest(APITestCase):
    """ Test module for deleting an existing Individual record. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)

    def test_delete_individual(self):
        """ DELETE an existing Individual record. """

        response = self.client.delete(
            reverse(
                'individual-detail',
                kwargs={'pk': self.individual_one.id}
                )
            )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_non_existing_individual(self):
        """ DELETE a non-existing Individual record. """

        response = self.client.delete(
            reverse(
                'individual-detail',
                kwargs={'pk': 'patient:what'}
                )
            )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)


class IndividualCSVRendererTest(APITestCase):
    """ Test csv export for Individuals. """

    def setUp(self):
        self.individual_one = Individual.objects.create(**c.VALID_INDIVIDUAL)

    def test_csv_export(self):
        get_resp = self.client.get('/api/individuals?format=csv')
        self.assertEqual(get_resp.status_code, status.HTTP_200_OK)
        content = get_resp.content.decode('utf-8')
        cvs_reader = csv.reader(io.StringIO(content))
        body = list(cvs_reader)
        self.assertEqual(body[1][1], c.VALID_INDIVIDUAL['sex'])
        headers = body.pop(0)
        for column in ['id', 'sex', 'date of birth', 'taxonomy', 'karyotypic sex',
                       'race', 'ethnicity', 'age', 'diseases', 'created', 'updated']:
            self.assertIn(column, [column_name.lower() for column_name in headers])
