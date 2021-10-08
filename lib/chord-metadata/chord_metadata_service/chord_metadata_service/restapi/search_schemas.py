from .schemas import ONTOLOGY_CLASS
from .schema_utils import search_optional_str, tag_schema_with_search_properties

__all__ = ["ONTOLOGY_SEARCH_SCHEMA"]

ONTOLOGY_SEARCH_SCHEMA = tag_schema_with_search_properties(ONTOLOGY_CLASS, {
    "properties": {
        "id": {
            "search": search_optional_str(0, multiple=True)
        },
        "label": {
            "search": search_optional_str(1, multiple=True)
        }
    },
    "search": {
        "database": {
            "type": "jsonb"  # TODO: parameterize?
        }
    }
})
