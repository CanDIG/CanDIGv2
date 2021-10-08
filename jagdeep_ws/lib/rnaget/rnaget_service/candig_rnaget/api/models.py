"""
API Data Model definitions
From Swagger file, with python classes via Bravado
"""

import pkg_resources
import yaml
from openapi_core import create_spec

#
# Read in the API definition, and parse it with Bravado
#
_API_DEF = pkg_resources.resource_filename('candig_rnaget',
                                           'api/rnaget.yaml')
_SPEC_DICT = yaml.safe_load(open(_API_DEF, 'r'))
_SWAGGER_SPEC = create_spec(_SPEC_DICT, spec_url='api/rnaget.yaml')

BasePath = _SWAGGER_SPEC.servers[0].url
Version = _SWAGGER_SPEC.info.version  # pylint:disable=invalid-name
