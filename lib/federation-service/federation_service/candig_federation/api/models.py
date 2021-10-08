"""
API Data Model definitions
From Swagger file, with python classes via Bravado
"""

import pkg_resources
import yaml
from openapi_core import create_spec

# Read in the API definition, and parse it with Bravado

_API_DEF = pkg_resources.resource_filename('candig_federation',
                                           'api/federation.yaml')

_SPEC_DICT = yaml.safe_load(open(_API_DEF, 'r'))

_BRAVADO_CONFIG = {
    'validate_requests': False,
    'validate_responses': False,
    'use_models': True,
    'validate_swagger_spec': True
}

_SWAGGER_SPEC = create_spec(_SPEC_DICT, spec_url='federation.yaml')


# _SWAGGER_SPEC = Spec.from_dict(_SPEC_DICT, config=_BRAVADO_CONFIG)

# Generate the Python models from the spec

# BASEPATH = _SWAGGER_SPEC.flattened_spec['basePath']
# PostObject = _SWAGGER_SPEC.definitions['PostObject']
# Error = _SWAGGER_SPEC.definitions['Error']

BASEPATH = _SWAGGER_SPEC.servers[0].url

