from chord_metadata_service.restapi.validators import JsonSchemaValidator
from .schemas import COMORBID_CONDITION


comorbid_condition_validator = JsonSchemaValidator(COMORBID_CONDITION)
