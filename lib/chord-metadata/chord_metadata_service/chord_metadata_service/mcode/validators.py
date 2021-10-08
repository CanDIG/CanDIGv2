from chord_metadata_service.restapi.validators import JsonSchemaValidator
from . import schemas as s


quantity_validator = JsonSchemaValidator(schema=s.QUANTITY, formats=['uri'])
tumor_marker_data_value_validator = JsonSchemaValidator(schema=s.TUMOR_MARKER_DATA_VALUE)
complex_ontology_validator = JsonSchemaValidator(schema=s.COMPLEX_ONTOLOGY, formats=['uri'])
# TODO delete?
time_or_period_validator = JsonSchemaValidator(schema=s.TIME_OR_PERIOD, formats=['date-time'])
