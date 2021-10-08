from .semantic_mappings.context import CONTEXT_TYPES, CONTEXT


# utils to convert dataset json to json-ld

def obj_to_jsonld(obj: dict, mapping: str) -> dict:
    obj['@type'] = CONTEXT_TYPES[mapping]['type']
    return obj


def dates_to_jsonld(dates) -> list:
    for date in dates:
        obj_to_jsonld(date, 'dates')
        # the date always will be only object in our mapping
        obj_to_jsonld(date['type'], 'annotation')
    return dates


def creators_to_jsonld(creators) -> list:
    for creator in creators:
        if 'name' in creator.keys():
            obj_to_jsonld(creator, 'organization')
        else:
            obj_to_jsonld(creator, 'person')
    return creators


def extra_properties_to_jsonld(extra_properties) -> list:
    for ep in extra_properties:
        obj_to_jsonld(ep, 'extra_properties')
        if ep['values']:
            for value in ep['values']:
                obj_to_jsonld(value, 'annotation')
    return extra_properties


def _obj_identifiers_to_jsonld(obj):
    if "identifier" in obj:
        obj_to_jsonld(obj['identifier'], 'identifier')
    if "alternate_identifiers" in obj:
        for alt_id in obj["alternate_identifiers"]:
            obj_to_jsonld(alt_id, "alternate_identifiers")
    if "related_identifiers" in obj:
        for rel_id in obj["related_identifiers"]:
            obj_to_jsonld(rel_id, "related_identifiers")


def spatial_coverage_to_jsonld(spatial_coverage) -> list:
    for sc in spatial_coverage:
        obj_to_jsonld(sc, 'spatial_coverage')
        _obj_identifiers_to_jsonld(sc)
    return spatial_coverage


def distributions_to_jsonld(distributions) -> list:
    for distribution in distributions:
        obj_to_jsonld(distribution, 'distributions')
        _obj_identifiers_to_jsonld(distribution)
        if 'stored_in' in distribution:
            obj_to_jsonld(distribution['stored_in'], 'stored_in')
        if 'dates' in distribution.keys():
            dates_to_jsonld(distribution['dates'])
        if 'licenses' in distribution:
            for license_ in distribution['liceses']:
                obj_to_jsonld(license_, 'licenses')
        # access
    return distributions


def dataset_to_jsonld(dataset):
    """
    The function adds semantic context to json elements
    :param dataset: json serialization of dataset
    :return: enriched json with linked data context
    """
    dataset['@context'] = CONTEXT
    dataset['@type'] = CONTEXT_TYPES['dataset']['type']

    if 'dates' in dataset.keys():
        dates_to_jsonld(dataset['dates'])
    if 'stored_in' in dataset.keys():
        obj_to_jsonld(dataset['stored_in'], 'stored_in')
    if 'creators' in dataset.keys():
        creators_to_jsonld(dataset['creators'])
    if 'types' in dataset.keys():
        for t in dataset['types']:
            obj_to_jsonld(t, 'types')
            if 'information' in t.keys():
                obj_to_jsonld(t['information'], 'annotation')
    if 'licenses' in dataset.keys():
        for license_ in dataset['licenses']:
            obj_to_jsonld(license_, 'licenses')
    if 'extra_properties' in dataset.keys():
        extra_properties_to_jsonld(dataset['extra_properties'])
    if 'alternate_identifiers' in dataset.keys():
        for identifier in dataset['alternate_identifiers']:
            obj_to_jsonld(identifier, 'alternate_identifiers')
    if 'related_identifiers' in dataset.keys():
        for rel_id in dataset['related_identifiers']:
            obj_to_jsonld(rel_id, 'related_identifiers')
    if 'spatial_coverage' in dataset.keys():
        spatial_coverage_to_jsonld(dataset['spatial_coverage'])
    if 'distributions' in dataset.keys():
        distributions_to_jsonld(dataset['distributions'])
    if 'dimensions' in dataset.keys():
        for dimension in dataset['dimensions']:
            obj_to_jsonld(dimension, 'dimensions')
    if 'primary_publications' in dataset.keys():
        for pp in dataset['primary_publications']:
            obj_to_jsonld(pp, 'primary_publications')
            if 'identifier' in pp.keys():
                obj_to_jsonld(pp['identifier'], 'identifier')
            if 'authors' in pp.keys():
                creators_to_jsonld(pp['authors'])
            if 'dates' in pp.keys():
                dates_to_jsonld(pp['dates'])

    return dataset
