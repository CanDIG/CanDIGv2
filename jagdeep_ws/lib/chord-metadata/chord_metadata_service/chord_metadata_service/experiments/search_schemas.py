from . import models, schemas
from chord_metadata_service.restapi.schema_utils import (
    search_optional_eq,
    search_optional_str,
    tag_schema_with_search_properties,
)
from chord_metadata_service.restapi.search_schemas import ONTOLOGY_SEARCH_SCHEMA


__all__ = ["EXPERIMENT_SEARCH_SCHEMA"]


EXPERIMENT_SEARCH_SCHEMA = tag_schema_with_search_properties(schemas.EXPERIMENT_SCHEMA, {
    "properties": {
        "id": {
            "search": {"order": 0, "database": {"field": models.Experiment._meta.pk.column}}
        },
        "reference_registry_id": {
            "search": search_optional_str(1, queryable="internal"),
        },
        "qc_flags": {
            "items": {
                "search": search_optional_str(0),
            },
            "search": {"order": 2, "database": {"type": "array"}}
        },
        "experiment_type": {
            "search": search_optional_str(3),
        },
        "experiment_ontology": {
            "items": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Specific ontology?
            "search": {"order": 4, "database": {"type": "jsonb"}}
        },
        "molecule": {
            "search": search_optional_eq(5),
        },
        "molecule_ontology": {
            "items": ONTOLOGY_SEARCH_SCHEMA,  # TODO: Specific ontology?
            "search": {"order": 6, "database": {"type": "jsonb"}}
        },
        "library_strategy": {
            "search": search_optional_eq(7),
        },
        # TODO: other_fields: ?
        "biosample": {
            "search": search_optional_eq(8, queryable="internal"),
        },
    },
    "search": {
        "database": {
            "relation": models.Experiment._meta.db_table,
            "primary_key": models.Experiment._meta.pk.column,
        }
    }
})
