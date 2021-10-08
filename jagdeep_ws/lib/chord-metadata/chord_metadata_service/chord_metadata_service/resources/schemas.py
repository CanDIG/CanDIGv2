from chord_metadata_service.restapi.description_utils import describe_schema
from chord_metadata_service.restapi.schemas import EXTRA_PROPERTIES_SCHEMA

from . import descriptions


__all__ = ["RESOURCE_SCHEMA"]


RESOURCE_SCHEMA = describe_schema({
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",  # TODO
    "properties": {
        "id": {
            "type": "string",
        },
        "name": {
            "type": "string",
        },
        "namespace_prefix": {
            "type": "string",
        },
        "url": {
            "type": "string",
        },
        "version": {
            "type": "string",
        },
        "iri_prefix": {
            "type": "string",
        },
        "extra_properties": EXTRA_PROPERTIES_SCHEMA
    },
    "required": ["id", "name", "namespace_prefix", "url", "version", "iri_prefix"],
}, descriptions.RESOURCE)
