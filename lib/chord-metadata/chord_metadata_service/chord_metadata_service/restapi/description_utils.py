def describe_schema(schema, descriptions):
    if schema is None:
        return {}  # TODO: If none is specified, should we still annotate it?

    if descriptions is None:
        return schema

    schema_description = (descriptions.get("description", None)
                          if isinstance(descriptions, dict) else descriptions)
    schema_help = (descriptions.get("help", descriptions.get("description", None))
                   if isinstance(descriptions, dict) else descriptions)

    new_schema = schema.copy()

    if schema_description is not None:
        new_schema["description"] = schema_description

    if schema_help is not None:
        new_schema["help"] = schema_help

    if all((schema["type"] == "object", "properties" in schema, isinstance(descriptions, dict),
            "properties" in descriptions)):
        new_schema["properties"] = {p: describe_schema(schema["properties"].get(p, None),
                                                       descriptions["properties"].get(p, None))
                                    for p in schema["properties"]}

    elif all((schema["type"] == "array", "items" in schema, isinstance(descriptions, dict), "items" in descriptions)):
        new_schema["items"] = describe_schema(schema["items"], descriptions["items"])

    return new_schema


def get_help(description):
    if isinstance(description, str):
        return description

    elif "help" in description:
        return description["help"]

    return description["description"]


def rec_help(description, *args):
    if len(args) == 0:
        return get_help(description)

    elif args[0] == "[item]":
        return rec_help(description["items"], *args[1:])

    return rec_help(description["properties"][args[0]], *args[1:])


EXTRA_PROPERTIES = {"extra_properties": {
    # This isn't in the JSON schema, so no description needed
    "help": "Extra properties that are not supported by current schema."
}}


def ontology_class(purpose=""):
    padded_purpose = f" {purpose}" if purpose.strip() != "" else ""
    return {
        "description": f"An ontology term{padded_purpose}.",
        "properties": {
            "id": f"A CURIE-style identifier for an ontology term{padded_purpose}.",
            "label": f"A human readable class name for an ontology term{padded_purpose}."
        }
    }


ONTOLOGY_CLASS = ontology_class()
