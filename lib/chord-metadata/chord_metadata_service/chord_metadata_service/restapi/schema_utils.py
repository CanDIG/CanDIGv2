from typing import List, Optional

__all__ = [
    "merge_schema_dictionaries",
    "search_optional_eq",
    "search_optional_str",
    "tag_schema_with_search_properties",
    "customize_schema",
    "schema_list",
]


def merge_schema_dictionaries(dict1: dict, dict2: dict):
    """
    Merges two dictionaries with the ~same structure (in this case, keys that
    are dictionaries in one should be dictionaries in the other.) Replaces any
    conflicts with the second dictionary's value.
    """
    res_dict = {**dict1}
    for k2, v2 in dict2.items():
        res_dict[k2] = merge_schema_dictionaries(dict1.get(k2, {}), v2) if isinstance(v2, dict) else v2
    return res_dict


def _searchable_field(operations: List[str], order: int, queryable: str = "all", multiple: bool = False):
    return {
        "operations": operations,
        "queryable": queryable,
        "canNegate": True,
        "required": False,
        "order": order,
        "type": "multiple" if multiple else "single"
    }


def search_optional_eq(order: int, queryable: str = "all"):
    return _searchable_field(["eq"], order, queryable, multiple=False)


def search_optional_str(order: int, queryable: str = "all", multiple: bool = False):
    return _searchable_field(["eq", "co"], order, queryable, multiple)


def tag_schema_with_search_properties(schema, search_descriptions: Optional[dict]):
    if not isinstance(schema, dict) or not search_descriptions:
        return schema

    if "type" not in schema:
        # TODO: handle oneOf, allOf, etc.
        return schema

    schema_with_search = {
        **schema,
        **({"search": search_descriptions["search"]} if "search" in search_descriptions else {}),
    }

    if schema["type"] == "object":
        return {
            **schema_with_search,
            **({
                "properties": {
                    p: tag_schema_with_search_properties(s, search_descriptions["properties"].get(p))
                    for p, s in schema["properties"].items()
                }
            } if "properties" in schema and "properties" in search_descriptions else {})
        }

    if schema["type"] == "array":
        return {
            **schema_with_search,
            **({"items": tag_schema_with_search_properties(schema["items"], search_descriptions["items"])}
               if "items" in schema and "items" in search_descriptions else {})
        }

    return schema_with_search


def customize_schema(first_typeof: dict, second_typeof: dict, first_property: str, second_property: str,
                     schema_id: str = None, title: str = None, description: str = None,
                     additional_properties: bool = False, required=None) -> dict:
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": schema_id,
        "title": title,
        "description": description,
        "type": "object",
        "properties": {
            first_property: first_typeof,
            second_property: second_typeof
        },
        "required": required or [],
        "additionalProperties": additional_properties
    }


def schema_list(schema):
    """ Schema to validate JSON array values. """

    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "$id": "chord_metadata_service:schema_list",
        "title": "Schema list",
        "type": "array",
        "items": schema
    }
