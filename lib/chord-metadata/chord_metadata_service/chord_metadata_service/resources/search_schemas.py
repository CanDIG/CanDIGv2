from chord_metadata_service.restapi.schema_utils import (
    search_optional_str,
    tag_schema_with_search_properties,
)

from . import schemas


__all__ = ["RESOURCE_SEARCH_SCHEMA"]


RESOURCE_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.RESOURCE_SCHEMA, {
    "properties": {
        "id": {
            "search": search_optional_str(0)
        },
        "name": {
            "search": search_optional_str(1, multiple=True)
        },
        "namespace_prefix": {
            "search": search_optional_str(2, multiple=True)
        },
        "url": {
            "search": search_optional_str(3, multiple=True)
        },
        "version": {
            "search": search_optional_str(4, multiple=True)
        },
        "iri_prefix": {
            "search": search_optional_str(5, multiple=True)
        }
    },
    "search": {
        "database": {
            "relationship": {
                "type": "MANY_TO_ONE",  # TODO: Only in some cases - phenopacket
                "foreign_key": "resource_id"  # TODO: No hard-code, from M2M
            }
        }
    }
})
