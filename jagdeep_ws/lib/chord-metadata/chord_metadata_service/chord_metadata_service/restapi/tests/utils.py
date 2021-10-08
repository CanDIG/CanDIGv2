import json
from django.urls import reverse
from rest_framework.test import APIClient


# Helper functions for tests

def get_response(viewname, obj):
    """ Generic POST function. """
    client = APIClient()
    return client.post(
        reverse(viewname),
        data=json.dumps(obj),
        content_type='application/json'
    )
